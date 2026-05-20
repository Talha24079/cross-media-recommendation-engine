import asyncio
import os
import httpx
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sentence_transformers import SentenceTransformer

from core.database import AsyncSessionLocal
from models.media import MediaItem

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
RAWG_API_KEY = os.getenv("RAWG_API_KEY")

model = SentenceTransformer('all-MiniLM-L6-v2')

async def fetch_movies():
    print("Fetching movies from TMDB...")
    items = []
    try:
        async with httpx.AsyncClient() as client:
            for page in range(1, 11):
                url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&page={page}"
                response = await client.get(url, timeout=10.0)
                if response.status_code != 200:
                    print(f"TMDB API Error: {response.status_code} - {response.text}")
                    continue
                    
                results = response.json().get("results", [])
                for m in results:
                    genres_str = "" # Not fetching genre names here without extra API call, but let's assume we can skip or it's fine.
                    desc = m.get("overview", "")
                    if not desc:
                        continue
                        
                    items.append({
                        "title": m.get("title"),
                        "type": "movie",
                        "description": desc,
                        "genre": genres_str,
                        "poster_url": f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get("poster_path") else None,
                        "rating": m.get("vote_average"),
                        "external_id": str(m.get("id")),
                        "source": "tmdb"
                    })
    except Exception as e:
        print(f"TMDB Fetch Failed: {e}")
    return items

async def fetch_books():
    print("Fetching books from Open Library...")
    items = []
    try:
        async with httpx.AsyncClient() as client:
            url = "https://openlibrary.org/subjects/fiction.json?limit=200"
            response = await client.get(url, timeout=15.0)
            if response.status_code != 200:
                print(f"OpenLibrary API Error: {response.status_code} - {response.text}")
                return items
                
            works = response.json().get("works", [])
            for b in works:
                subjects = b.get("subject", [])
                genre = ", ".join(subjects[:5]) if subjects else ""
                desc = b.get("title") + " " + " ".join(subjects[:5])
                
                cover_id = b.get("cover_id")
                poster = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None
                
                # Use key as external_id e.g. /works/OL45883W
                external_id = b.get("key", "").split("/")[-1]
                
                items.append({
                    "title": b.get("title"),
                    "type": "book",
                    "description": desc,
                    "genre": genre,
                    "poster_url": poster,
                    "rating": None,
                    "external_id": external_id,
                    "source": "openlibrary"
                })
    except Exception as e:
        print(f"OpenLibrary Fetch Failed: {e}")
    return items

async def fetch_games():
    print("Fetching games from RAWG...")
    items = []
    try:
        async with httpx.AsyncClient() as client:
            for page in range(1, 6):
                url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&page_size=40&page={page}"
                response = await client.get(url, timeout=10.0)
                if response.status_code != 200:
                    print(f"RAWG API Error: {response.status_code} - {response.text}")
                    continue
                    
                results = response.json().get("results", [])
                for g in results:
                    genres = [x.get("name") for x in g.get("genres", [])]
                    genre_str = ", ".join(genres)
                    desc = g.get("name") + " " + genre_str
                    
                    items.append({
                        "title": g.get("name"),
                        "type": "game",
                        "description": desc,
                        "genre": genre_str,
                        "poster_url": g.get("background_image"),
                        "rating": float(g.get("rating", 0.0)),
                        "external_id": str(g.get("id")),
                        "source": "rawg"
                    })
    except Exception as e:
        print(f"RAWG Fetch Failed: {e}")
    return items

async def seed_data():
    if not TMDB_API_KEY or not RAWG_API_KEY:
        print("Missing API keys. Check your .env file.")
        return

    movies = await fetch_movies()
    books = await fetch_books()
    games = await fetch_games()
    
    all_items = movies + books + games
    print(f"Total items fetched: {len(all_items)}")
    
    async with AsyncSessionLocal() as session:
        for item in all_items:
            try:
                embedding = model.encode(item["description"]).tolist()
                
                stmt = insert(MediaItem).values(
                    title=item["title"],
                    type=item["type"],
                    description=item["description"],
                    genre=item["genre"],
                    poster_url=item["poster_url"],
                    rating=item["rating"],
                    external_id=item["external_id"],
                    source=item["source"],
                    embedding=embedding
                ).on_conflict_do_nothing(
                    index_elements=['external_id', 'source']
                )
                
                await session.execute(stmt)
                await session.commit()
                print(f"Inserted: {item['title']} ({item['type']}) ✓")
            except Exception as e:
                print(f"Failed to insert {item['title']}: {e}")
                await session.rollback()

if __name__ == "__main__":
    asyncio.run(seed_data())
