import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.media import MediaItem
from typing import Iterable

# Global state for in-memory cache
model = None
embedding_matrix = None
metadata_list = []

def init_model():
    global model
    if model is None:
        print("Loading sentence-transformers model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded.")

async def load_cache(db: AsyncSession):
    global embedding_matrix, metadata_list
    init_model()
    
    print("Loading media items into memory cache...")
    result = await db.execute(select(MediaItem))
    items = result.scalars().all()
    
    metadata_list = []
    embeddings = []
    
    for item in items:
        if item.embedding is not None:
            metadata_list.append(_metadata_from_item(item))
            # asyncpg with pgvector returns the embedding as a list/array
            embeddings.append(item.embedding)
            
    if embeddings:
        embedding_matrix = np.array(embeddings, dtype=np.float32)
        print(f"Loaded {len(embeddings)} items into cache. Matrix shape: {embedding_matrix.shape}")
    else:
        # Initialize an empty matrix of shape (0, 384)
        embedding_matrix = np.empty((0, 384), dtype=np.float32)
        print("Cache loaded. 0 items found.")

def add_to_cache(media_item: MediaItem, embedding: np.ndarray):
    global embedding_matrix, metadata_list

    metadata_list.append(_metadata_from_item(media_item))

    if embedding_matrix.shape[0] == 0:
        embedding_matrix = np.array([embedding], dtype=np.float32)
    else:
        embedding_matrix = np.vstack((embedding_matrix, embedding))


def _metadata_from_item(media_item: MediaItem) -> dict:
    return {
        "id": media_item.id,
        "title": media_item.title,
        "media_type": media_item.type,
        "genre": media_item.genre,
        "poster_url": media_item.poster_url,
        "rating": media_item.rating,
    }


def update_cache_item(media_item: MediaItem) -> None:
    global metadata_list
    for index, meta in enumerate(metadata_list):
        if meta.get("id") == media_item.id:
            metadata_list[index] = _metadata_from_item(media_item)
            break

def _split_genres(raw_genre: str | None) -> list[str]:
    if not raw_genre:
        return []
    normalized = raw_genre.replace("/", ",").replace(";", ",")
    return [part.strip().lower() for part in normalized.split(",") if part.strip()]


def _normalize_selected_genres(genres: Iterable[str] | None) -> list[str]:
    if not genres:
        return []
    return [genre.strip().lower() for genre in genres if genre and genre.strip()]


def search_similar(
    query_text: str,
    top_k: int = 10,
    media_type: str | None = None,
    genres: Iterable[str] | None = None,
):
    global model, embedding_matrix, metadata_list
    
    if embedding_matrix is None or embedding_matrix.shape[0] == 0:
        return []
        
    # Generate embedding for the query
    query_embedding = model.encode(query_text)

    # Optionally filter items by media_type
    indices = list(range(len(metadata_list)))
    if media_type is not None:
        indices = [i for i, m in enumerate(metadata_list) if m.get("media_type") == media_type]

    selected_genres = _normalize_selected_genres(genres)
    if selected_genres:
        filtered_indices = []
        for i in indices:
            item_genres = set(_split_genres(metadata_list[i].get("genre")))
            if item_genres.intersection(selected_genres):
                filtered_indices.append(i)
        indices = filtered_indices

    if not indices:
        return []

    # Build filtered embedding matrix and metadata
    filtered_embeddings = np.array([embedding_matrix[i] for i in indices], dtype=np.float32)
    filtered_meta = [metadata_list[i] for i in indices]

    # Compute cosine similarity (dot product with normalized embeddings)
    scores = np.dot(filtered_embeddings, query_embedding)

    # Get top_k indices within the filtered set
    top_filtered = np.argsort(scores)[::-1][:top_k]

    results = []
    for pos in top_filtered:
        meta = filtered_meta[pos]
        results.append({
            "id": meta["id"],
            "title": meta["title"],
            "media_type": meta["media_type"],
            "genre": meta.get("genre"),
            "poster_url": meta.get("poster_url"),
            "rating": meta.get("rating"),
            "score": float(scores[pos])
        })

    return results


def search_by_vector(
    user_vector: Iterable[float],
    top_k: int = 10,
    media_type: str | None = None,
    genres: Iterable[str] | None = None,
):
    global embedding_matrix, metadata_list

    if embedding_matrix is None or embedding_matrix.shape[0] == 0:
        return []

    query_embedding = np.array(list(user_vector), dtype=np.float32)

    indices = list(range(len(metadata_list)))
    if media_type is not None:
        indices = [i for i, m in enumerate(metadata_list) if m.get("media_type") == media_type]

    selected_genres = _normalize_selected_genres(genres)
    if selected_genres:
        filtered_indices = []
        for i in indices:
            item_genres = set(_split_genres(metadata_list[i].get("genre")))
            if item_genres.intersection(selected_genres):
                filtered_indices.append(i)
        indices = filtered_indices

    if not indices:
        return []

    filtered_embeddings = np.array([embedding_matrix[i] for i in indices], dtype=np.float32)
    filtered_meta = [metadata_list[i] for i in indices]
    scores = np.dot(filtered_embeddings, query_embedding)
    top_filtered = np.argsort(scores)[::-1][:top_k]

    results = []
    for pos in top_filtered:
        meta = filtered_meta[pos]
        results.append(
            {
                "id": meta["id"],
                "title": meta["title"],
                "media_type": meta["media_type"],
                "genre": meta.get("genre"),
                "poster_url": meta.get("poster_url"),
                "rating": meta.get("rating"),
                "score": float(scores[pos]),
            }
        )

    return results
