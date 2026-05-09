from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.media import MediaItem
from schemas.recommendation import MediaItemCreate, MediaItemResponse, RecommendationResponse
from services import recommendation_service

router = APIRouter(prefix="/recommendation", tags=["recommendation"])

@router.post("/media", response_model=MediaItemResponse, status_code=status.HTTP_201_CREATED)
async def add_media_item(item: MediaItemCreate, db: AsyncSession = Depends(get_db)):
    if recommendation_service.model is None:
        recommendation_service.init_model()
        
    # Generate embedding
    try:
        embedding = recommendation_service.model.encode(f"{item.title} {item.description or ''}")
        # Convert to list for pgvector compatibility in asyncpg
        embedding_list = embedding.tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {str(e)}")

    db_item = MediaItem(
        title=item.title,
        type=item.media_type,
        description=item.description,
        embedding=embedding_list
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    
    # Update cache
    recommendation_service.add_to_cache(db_item, embedding)
    
    return MediaItemResponse(
        id=db_item.id,
        title=db_item.title,
        media_type=db_item.type,
        description=db_item.description
    )

@router.get("/search", response_model=List[RecommendationResponse])
async def recommend(query: str, top_k: int = 10):
    if recommendation_service.model is None:
        recommendation_service.init_model()
        
    try:
        results = recommendation_service.search_similar(query, top_k=top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
