import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.media import MediaItem

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
            metadata_list.append({
                "id": item.id,
                "title": item.title,
                "media_type": item.type
            })
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
    
    metadata_list.append({
        "id": media_item.id,
        "title": media_item.title,
        "media_type": media_item.type
    })
    
    if embedding_matrix.shape[0] == 0:
        embedding_matrix = np.array([embedding], dtype=np.float32)
    else:
        embedding_matrix = np.vstack((embedding_matrix, embedding))

def search_similar(query_text: str, top_k: int = 10):
    global model, embedding_matrix, metadata_list
    
    if embedding_matrix is None or embedding_matrix.shape[0] == 0:
        return []
        
    # Generate embedding for the query
    query_embedding = model.encode(query_text)
    
    # Compute cosine similarity
    # Since all-MiniLM-L6-v2 embeddings are normalized, dot product is equivalent to cosine similarity
    scores = np.dot(embedding_matrix, query_embedding)
    
    # Get top_k indices
    top_indices = np.argsort(scores)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        meta = metadata_list[idx]
        results.append({
            "id": meta["id"],
            "title": meta["title"],
            "media_type": meta["media_type"],
            "score": float(scores[idx])
        })
        
    return results
