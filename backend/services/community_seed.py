import logging
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

SYSTEM_AUTHOR_ID = "crossmedia-community"

STARTER_THREADS = [
    {
        "title": "Welcome — introduce yourself",
        "content": (
            "New here? Tell us your name, what you are into (movies, books, games, anime), "
            "and one title you would recommend to a friend."
        ),
        "tags": ["welcome", "introductions"],
    },
    {
        "title": "What are you watching / playing / reading this week?",
        "content": (
            "Share your current rotation. Bonus points if you explain why it hooked you "
            "and who else might like it."
        ),
        "tags": ["weekly", "discussion"],
    },
    {
        "title": "Cross-media recommendations exchange",
        "content": (
            "Loved a book and want a game that feels the same? Finished a show and need a novel? "
            "Post one thing you enjoyed and the vibe you want next — the community will suggest matches."
        ),
        "tags": ["recommendations", "cross-media"],
    },
    {
        "title": "Hidden gems nobody talks about",
        "content": (
            "Pitch an underrated movie, book, or game. Include genre, platform, and why more people "
            "should try it."
        ),
        "tags": ["hidden-gems", "recommendations"],
    },
    {
        "title": "Books that deserve a movie or series adaptation",
        "content": (
            "Which book would you greenlight tomorrow? Describe the tone, ideal cast vibe, "
            "and why it would work on screen."
        ),
        "tags": ["books", "adaptations"],
    },
    {
        "title": "Manhwa & webtoon picks",
        "content": (
            "Recommend manhwa or webtoons for fans of progression fantasy, romance, or action. "
            "If you liked The Greatest Estate Developer, say what you want more of."
        ),
        "tags": ["manhwa", "webtoon", "anime"],
    },
    {
        "title": "Soundtracks that outshine the story",
        "content": (
            "Share albums or scores you keep replaying from games, films, or anime. "
            "What mood do they capture?"
        ),
        "tags": ["music", "scores", "discussion"],
    },
    {
        "title": "Ideas for CrossMedia (bugs & features)",
        "content": (
            "What would make this app better for you? Report bugs, wish lists, or integrations "
            "you would like to see."
        ),
        "tags": ["meta", "feedback"],
    },
]


async def seed_starter_threads(db: AsyncIOMotorDatabase) -> int:
    collection = db.get_collection("forum_threads")
    now = datetime.now(timezone.utc)
    inserted = 0

    for thread in STARTER_THREADS:
        exists = await collection.find_one({"title": thread["title"]})
        if exists:
            continue

        await collection.insert_one(
            {
                "title": thread["title"],
                "content": thread["content"],
                "author_id": SYSTEM_AUTHOR_ID,
                "media_id": None,
                "tags": thread["tags"],
                "created_at": now,
                "updated_at": now,
                "seeded": True,
            }
        )
        inserted += 1

    if inserted:
        logger.info("Inserted %s new starter forum threads", inserted)
    else:
        logger.info("Starter forum threads already present; no new rows inserted")

    return inserted
