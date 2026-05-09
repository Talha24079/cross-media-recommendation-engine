import numpy as np
import logging
from datetime import datetime
from sklearn.cluster import KMeans
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.media import MediaItem
from core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

FACTION_NAMES = {
    0: "The Cosmonauts",
    1: "The Chroniclers",
    2: "The Architects",
    3: "The Phantoms",
    4: "The Alchemists"
}


async def build_taste_profile(user_id, media_ids: list, db: AsyncSession):
    """
    Averages the embeddings of all media items the user has interacted with
    and stores the result as the user's taste_vector.
    """
    if not media_ids:
        return

    result = await db.execute(
        select(MediaItem).where(MediaItem.id.in_(media_ids))
    )
    items = result.scalars().all()

    embeddings = []
    for item in items:
        if item.embedding is not None:
            embeddings.append(item.embedding)

    if not embeddings:
        return

    # Average all embeddings into a single taste vector
    taste_vector = np.mean(np.array(embeddings, dtype=np.float32), axis=0).tolist()

    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(taste_vector=taste_vector)
    )
    await db.commit()
    logger.info(f"Updated taste profile for user {user_id}")


async def run_faction_clustering():
    """
    Fetches all users with a taste_vector, runs KMeans with 5 clusters,
    and assigns each user a faction_id.
    """
    logger.info("Starting faction clustering...")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.taste_vector.isnot(None))
        )
        users = result.scalars().all()

        if len(users) < 2:
            logger.info(f"Only {len(users)} users with taste vectors. Need at least 2 for clustering. Skipping.")
            return

        user_ids = [u.id for u in users]
        vectors = np.array([u.taste_vector for u in users], dtype=np.float32)

        n_clusters = min(5, len(users))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(vectors)

        for user_id, label in zip(user_ids, labels):
            await db.execute(
                update(User)
                .where(User.id == user_id)
                .values(faction_id=int(label))
            )

        await db.commit()
        logger.info(f"Faction clustering complete at {datetime.utcnow()}. Assigned {len(users)} users to {n_clusters} factions.")


async def get_faction_info(user_id, db: AsyncSession):
    """Returns the user's faction info and popular media in that faction."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or user.faction_id is None:
        return {
            "faction_id": None,
            "faction_name": "Unassigned",
            "message": "Interact with more media to be assigned a faction!",
            "faction_members": [],
            "popular_media": []
        }

    # Get other users in the same faction
    result = await db.execute(
        select(User).where(User.faction_id == user.faction_id)
    )
    faction_users = result.scalars().all()

    faction_name = FACTION_NAMES.get(user.faction_id, f"Faction {user.faction_id}")

    return {
        "faction_id": user.faction_id,
        "faction_name": faction_name,
        "faction_members": [
            {"user_id": str(u.id), "username": u.username}
            for u in faction_users
        ],
        "popular_media": []  # Could be expanded to show faction-popular media
    }
