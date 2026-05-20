"""
Add popular titles that should definitely be in the database.
"""

import asyncio
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentence_transformers import SentenceTransformer
from core.database import AsyncSessionLocal
from models.media import MediaItem

model = SentenceTransformer('all-MiniLM-L6-v2')

POPULAR_TITLES = [
    {
        'title': 'Game of Thrones',
        'type': 'book',
        'description': 'A Song of Ice and Fire series. Epic medieval fantasy with political intrigue, dragons, and complex characters across multiple kingdoms.',
        'genre': 'Fantasy, Adventure, Medieval',
        'rating': 9.1,
        'external_id': 'game-of-thrones-grrm',
        'source': 'openlibrary',
        'poster_url': None,
    },
    {
        'title': 'Game of Thrones',
        'type': 'book',
        'description': 'The first novel in A Song of Ice and Fire. Follows multiple POV characters as political power struggles unfold in the Seven Kingdoms.',
        'genre': 'Fantasy, Adventure',
        'rating': 8.8,
        'external_id': 'a-game-of-thrones-book',
        'source': 'openlibrary',
        'poster_url': 'https://covers.openlibrary.org/b/id/7705344-M.jpg',
    },
    {
        'title': 'The Elden Ring',
        'type': 'game',
        'description': 'An action role-playing game set in the Lands Between. Defeat demigods and claim the Elden Ring in this challenging fantasy adventure.',
        'genre': 'Action, RPG, Adventure',
        'rating': 9.0,
        'external_id': 'elden-ring-fromsoft',
        'source': 'rawg',
        'poster_url': None,
    },
    {
        'title': 'Baldurs Gate 3',
        'type': 'game',
        'description': 'A story-rich, party-based RPG set in the Dungeons & Dragons world. Make choices that shape your adventure with companions.',
        'genre': 'RPG, Adventure, Strategy',
        'rating': 9.4,
        'external_id': 'baldurs-gate-3-larian',
        'source': 'rawg',
        'poster_url': None,
    },
    {
        'title': 'The Lord of the Rings: The Fellowship of the Ring',
        'type': 'book',
        'description': 'Epic fantasy by J.R.R. Tolkien. Frodo Baggins embarks on a perilous journey to destroy the One Ring in the fires of Mount Doom.',
        'genre': 'Fantasy, Adventure, Classic',
        'rating': 9.2,
        'external_id': 'fellowship-ring-tolkien',
        'source': 'openlibrary',
        'poster_url': None,
    },
    {
        'title': 'Dune',
        'type': 'book',
        'description': 'A science fiction masterpiece by Frank Herbert. Paul Atreides becomes embroiled in political intrigue on the desert planet Arrakis.',
        'genre': 'Science Fiction, Space Opera, Adventure',
        'rating': 8.9,
        'external_id': 'dune-herbert',
        'source': 'openlibrary',
        'poster_url': None,
    },
    {
        'title': 'Cyberpunk 2077',
        'type': 'game',
        'description': 'An open-world action RPG set in a dystopian future. Play as V, a mercenary seeking immortality in the neon-lit Night City.',
        'genre': 'Action, RPG, Science Fiction',
        'rating': 7.5,
        'external_id': 'cyberpunk-2077-cdpr',
        'source': 'rawg',
        'poster_url': None,
    },
    {
        'title': 'Harry Potter and the Philosophers Stone',
        'type': 'book',
        'description': 'A young wizard discovers his magical heritage and attends Hogwarts School. The beginning of an epic 7-book series.',
        'genre': 'Fantasy, Adventure, Young Adult',
        'rating': 8.4,
        'external_id': 'hp-philosophers-stone',
        'source': 'openlibrary',
        'poster_url': None,
    },
]


async def add_popular_titles():
    """Add popular titles to the database."""
    print("Adding popular titles...")
    
    async with AsyncSessionLocal() as db:
        added = 0
        updated = 0
        
        for item in POPULAR_TITLES:
            try:
                # Check if already exists
                existing = await db.execute(
                    select(MediaItem).where(
                        MediaItem.external_id == item['external_id'],
                        MediaItem.source == item['source']
                    )
                )
                existing_item = existing.scalars().first()
                
                # Generate embedding
                embedding = model.encode(item['description']).tolist()
                
                if existing_item:
                    # Update
                    existing_item.title = item['title']
                    existing_item.description = item['description']
                    existing_item.genre = item['genre']
                    existing_item.poster_url = item['poster_url']
                    existing_item.rating = item['rating']
                    existing_item.embedding = embedding
                    updated += 1
                    print(f"  ✓ Updated: {item['title']}")
                else:
                    # Create new
                    new_item = MediaItem(
                        id=uuid.uuid4(),
                        title=item['title'],
                        type=item['type'],
                        description=item['description'],
                        genre=item['genre'],
                        poster_url=item['poster_url'],
                        rating=item['rating'],
                        external_id=item['external_id'],
                        source=item['source'],
                        embedding=embedding,
                    )
                    db.add(new_item)
                    added += 1
                    print(f"  ✓ Added: {item['title']}")
            except Exception as e:
                print(f"  ✗ Error with {item['title']}: {e}")
        
        if added + updated > 0:
            await db.commit()
        
        print(f"\n✓ Added {added} new titles, updated {updated} existing")


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/home/talha/This PC/cross-media-recommendation-engine/backend')
    asyncio.run(add_popular_titles())
