from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db, get_mongodb
from core.security import get_current_user
from models.user import User
from models.media import MediaItem
from schemas.recommendation import (
    MediaItemCreate,
    MediaItemResponse,
    MetadataPreviewResponse,
    RecommendationResponse,
)
from services import recommendation_service, economy_service, metadata_service, safety_service
from services.user_preferences_service import UserPreferencesService

router = APIRouter(tags=["recommendation"])

router = APIRouter(tags=["recommendation"])


def _media_item_response(item: MediaItem) -> MediaItemResponse:
    return MediaItemResponse(
        id=item.id,
        title=item.title,
        media_type=item.type,
        description=item.description,
        genre=item.genre,
        poster_url=item.poster_url,
        rating=item.rating,
    )


async def _apply_metadata_to_item(
    db_item: MediaItem,
    item: MediaItemCreate,
    metadata: dict,
) -> None:
    if metadata.get("poster_url"):
        db_item.poster_url = metadata["poster_url"]
    if metadata.get("rating") is not None:
        db_item.rating = metadata["rating"]
    if metadata.get("external_id"):
        db_item.external_id = metadata["external_id"]
    if metadata.get("source"):
        db_item.source = metadata["source"]
    if not item.description and metadata.get("description"):
        db_item.description = metadata["description"]
    if not item.genre and metadata.get("genre"):
        db_item.genre = metadata["genre"]


async def _enrich_result_posters(results: list[dict], db: AsyncSession) -> list[dict]:
    enriched: list[dict] = []
    for result in results:
        if result.get("poster_url"):
            enriched.append(result)
            continue

        metadata = await metadata_service.fetch_metadata(
            result["title"],
            result["media_type"],
        )
        poster_url = metadata.get("poster_url")
        if not poster_url:
            enriched.append(result)
            continue

        result = {**result, "poster_url": poster_url}
        if metadata.get("rating") is not None and result.get("rating") is None:
            result["rating"] = metadata["rating"]

        item_id = result.get("id")
        if item_id is not None:
            db_result = await db.execute(select(MediaItem).where(MediaItem.id == item_id))
            db_item = db_result.scalars().first()
            if db_item and not db_item.poster_url:
                db_item.poster_url = poster_url
                if metadata.get("rating") is not None and db_item.rating is None:
                    db_item.rating = metadata["rating"]
                
                ext_id = metadata.get("external_id")
                source = metadata.get("source")
                if ext_id and source:
                    # Check if this combination is already used by another item
                    dup_check = await db.execute(
                        select(MediaItem).where(
                            MediaItem.external_id == ext_id,
                            MediaItem.source == source,
                            MediaItem.id != item_id
                        )
                    )
                    if not dup_check.scalars().first():
                        db_item.external_id = ext_id
                        db_item.source = source
                
                try:
                    await db.commit()
                    recommendation_service.update_cache_item(db_item)
                except Exception:
                    await db.rollback()

        enriched.append(result)
    return enriched


@router.get("/recommendation/metadata/preview", response_model=MetadataPreviewResponse)
async def preview_metadata(
    title: str = Query(..., min_length=1, max_length=300),
    media_type: str = Query(..., max_length=50),
    current_user: User = Depends(get_current_user),
):
    metadata = await metadata_service.fetch_metadata(title, media_type)
    return MetadataPreviewResponse(
        title=title,
        media_type=media_type,
        poster_url=metadata.get("poster_url"),
        rating=metadata.get("rating"),
        description=metadata.get("description"),
        genre=metadata.get("genre"),
        source=metadata.get("source"),
    )


@router.post("/recommendation/media", response_model=MediaItemResponse, status_code=status.HTTP_201_CREATED)
async def add_media_item(
    item: MediaItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if recommendation_service.model is None:
        recommendation_service.init_model()

    existing_media = await db.execute(
        select(MediaItem).where(
            MediaItem.title == item.title,
            MediaItem.type == item.media_type,
        )
    )
    if existing_media.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Media item already exists: '{item.title}'",
        )

    try:
        search_text = f"{item.title} {item.description or ''}"
        similar_items = recommendation_service.search_similar(search_text, top_k=1)
        if similar_items and similar_items[0]["score"] > 0.90:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Similar media item already exists: '{similar_items[0]['title']}' "
                    f"(Score: {similar_items[0]['score']:.2f})"
                ),
            )
    except HTTPException:
        raise
    except Exception:
        pass

    metadata = await metadata_service.fetch_metadata(item.title, item.media_type.value)
    description = item.description or metadata.get("description") or item.title
    genre = item.genre or metadata.get("genre")

    # Check for duplicate external_id + source
    ext_id = metadata.get("external_id")
    source = metadata.get("source")
    if ext_id and source:
        dup_check = await db.execute(
            select(MediaItem).where(
                MediaItem.external_id == ext_id,
                MediaItem.source == source,
            )
        )
        if dup_check.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Media item with this external ID already exists in the catalog.",
            )

    try:
        embedding = recommendation_service.model.encode(f"{item.title} {description}")
        embedding_list = embedding.tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {str(e)}") from e

    db_item = MediaItem(
        title=item.title,
        type=item.media_type,
        description=description,
        genre=genre,
        embedding=embedding_list,
    )
    await _apply_metadata_to_item(db_item, item, metadata)

    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)

    recommendation_service.add_to_cache(db_item, embedding)

    await economy_service.award_points(
        current_user.id, 5, "MEDIA_CONTRIBUTION", db, reference_id=db_item.id
    )
    await db.commit()

    return _media_item_response(db_item)


@router.get("/recommend/trending", response_model=List[RecommendationResponse])
async def trending_media(
    top_k: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns trending media based on high ratings and recency.
    """
    try:
        # Trending = Order by rating DESC, then created_at DESC
        query = select(MediaItem).order_by(MediaItem.rating.desc().nulls_last(), MediaItem.created_at.desc()).limit(top_k * 2)
        result = await db.execute(query)
        items = result.scalars().all()
        
        # Apply safety filter
        safe_items = safety_service.filter_media_items(items)
        
        results = []
        for item in safe_items[:top_k]:
            results.append({
                "id": item.id,
                "title": item.title,
                "media_type": item.type,
                "score": item.rating or 0.0,
                "genre": item.genre,
                "poster_url": item.poster_url,
                "rating": item.rating,
                "recommended_because": "Trending Now"
            })
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending media: {str(e)}") from e


@router.get("/recommend", response_model=List[RecommendationResponse])
async def recommend(
    query: str = Query(..., min_length=1, max_length=500),
    top_k: int = Query(10, ge=1, le=50),
    media_type: str | None = Query(None, max_length=50),
    genres: str | None = Query(None, description="Comma-separated genre list"),
    db: AsyncSession = Depends(get_db),
):
    if recommendation_service.model is None:
        recommendation_service.init_model()

    try:
        genre_list = [genre.strip() for genre in genres.split(",")] if genres else None
        results = recommendation_service.search_similar(
            query,
            top_k=top_k,
            media_type=media_type,
            genres=genre_list,
        )
        
        # The results from search_similar are dicts. We need to check safety.
        # We can filter by title in the results list.
        safe_results = [r for r in results if safety_service.is_safe(r.get("title", ""))]
        
        results = await _enrich_result_posters(safe_results, db)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}") from e


@router.get("/recommend/personalized", response_model=List[RecommendationResponse])
async def personalized_recommend(
    top_k: int = Query(20, ge=1, le=50),
    media_type: str | None = Query(None, max_length=50),
    genres: str | None = Query(None, description="Comma-separated genre list"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    if recommendation_service.model is None:
        recommendation_service.init_model()

    preferences_service = UserPreferencesService(mongo_db)
    try:
        favorite_ids = await preferences_service.favorite_media_ids(str(current_user.id))
        favorite_titles = await preferences_service.favorite_titles(str(current_user.id))
        seed_text = await preferences_service.preference_seed_text(str(current_user.id))
    except Exception as e:
        import logging
        logging.getLogger("backend").warning(f"Failed to fetch preferences for recommendations: {e}")
        favorite_ids = set()
        favorite_titles = []
        seed_text = ""
    genre_list = [genre.strip() for genre in genres.split(",")] if genres else None

    if seed_text:
        raw_results = recommendation_service.search_similar(
            seed_text,
            top_k=min(50, top_k + len(favorite_ids) + 10),
            media_type=media_type,
            genres=genre_list,
        )
    elif current_user.taste_vector is not None and len(current_user.taste_vector) > 0:
        raw_results = recommendation_service.search_by_vector(
            current_user.taste_vector,
            top_k=min(50, top_k + len(favorite_ids) + 10),
            media_type=media_type,
            genres=genre_list,
        )
    else:
        return []

    # Filter out unsafe content
    safe_results = [r for r in raw_results if safety_service.is_safe(r.get("title", ""))]
    
    filtered = [r for r in safe_results if str(r.get("id")) not in favorite_ids][:top_k]

    if favorite_titles:
        for index, result in enumerate(filtered):
            liked_title = favorite_titles[index % len(favorite_titles)]
            result["recommended_because"] = f"Because you liked {liked_title}"
    elif current_user.taste_vector:
        for result in filtered:
            result["recommended_because"] = "Based on your activity"

    return await _enrich_result_posters(filtered, db)
