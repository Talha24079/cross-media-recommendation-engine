from datetime import datetime, timezone
import uuid
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.media import MediaItem


class UserPreferencesService:
    def __init__(self, mongo_db: AsyncIOMotorDatabase):
        self.collection = mongo_db.get_collection("user_preferences")

    async def list_favorites(self, user_id: str) -> list[dict[str, Any]]:
        doc = await self.collection.find_one({"user_id": user_id})
        if not doc:
            return []
        return doc.get("favorites", [])

    async def add_manual_favorite(
        self,
        user_id: str,
        title: str,
        media_type: str,
    ) -> list[dict[str, Any]]:
        favorite = {
            "title": title.strip(),
            "media_type": media_type.strip().lower(),
            "media_id": None,
            "source": "manual",
            "added_at": datetime.now(timezone.utc),
        }
        return await self._upsert_favorite(user_id, favorite)

    async def add_favorite_from_media(
        self,
        user_id: str,
        media_id: str,
        db: AsyncSession,
    ) -> list[dict[str, Any]]:
        try:
            media_uuid = uuid.UUID(media_id)
        except ValueError:
            return await self.list_favorites(user_id)

        result = await db.execute(select(MediaItem).where(MediaItem.id == media_uuid))
        media = result.scalars().first()
        if not media:
            return await self.list_favorites(user_id)

        favorite = {
            "title": media.title,
            "media_type": media.type,
            "media_id": str(media.id),
            "source": "interaction",
            "added_at": datetime.now(timezone.utc),
        }
        return await self._upsert_favorite(user_id, favorite)

    async def favorite_media_ids(self, user_id: str) -> set[str]:
        favorites = await self.list_favorites(user_id)
        return {
            str(item.get("media_id"))
            for item in favorites
            if item.get("media_id")
        }

    async def preference_seed_text(self, user_id: str) -> str:
        favorites = await self.list_favorites(user_id)
        parts = [
            f"{item.get('title', '')} {item.get('media_type', '')}".strip()
            for item in favorites
            if item.get("title")
        ]
        return " ".join(parts).strip()

    async def favorite_titles(self, user_id: str) -> list[str]:
        favorites = await self.list_favorites(user_id)
        return [str(item.get("title")) for item in favorites if item.get("title")]

    async def remove_favorite(
        self,
        user_id: str,
        media_id: str | None = None,
        title: str | None = None,
        media_type: str | None = None,
    ) -> list[dict[str, Any]]:
        doc = await self.collection.find_one({"user_id": user_id})
        if not doc:
            return []

        favorites = doc.get("favorites", [])
        if not favorites:
            return []

        normalized_title = (title or "").strip().lower()
        normalized_type = (media_type or "").strip().lower()

        filtered: list[dict[str, Any]] = []
        for item in favorites:
            remove = False
            if media_id and str(item.get("media_id")) == media_id:
                remove = True
            elif normalized_title and normalized_type:
                remove = (
                    str(item.get("title", "")).strip().lower() == normalized_title
                    and str(item.get("media_type", "")).strip().lower() == normalized_type
                )

            if not remove:
                filtered.append(item)

        await self.collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "favorites": filtered,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
        return filtered

    async def _upsert_favorite(
        self,
        user_id: str,
        favorite: dict[str, Any],
    ) -> list[dict[str, Any]]:
        doc = await self.collection.find_one({"user_id": user_id})
        now = datetime.now(timezone.utc)

        if not doc:
            await self.collection.insert_one(
                {
                    "user_id": user_id,
                    "favorites": [favorite],
                    "created_at": now,
                    "updated_at": now,
                }
            )
            return [favorite]

        favorites = doc.get("favorites", [])
        normalized_title = favorite["title"].strip().lower()
        normalized_type = favorite["media_type"].strip().lower()

        already_exists = False
        for item in favorites:
            if favorite.get("media_id") and item.get("media_id") == favorite.get("media_id"):
                already_exists = True
                break
            if (
                str(item.get("title", "")).strip().lower() == normalized_title
                and str(item.get("media_type", "")).strip().lower() == normalized_type
            ):
                already_exists = True
                break

        if not already_exists:
            favorites.insert(0, favorite)

        await self.collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "favorites": favorites,
                    "updated_at": now,
                }
            },
        )
        return favorites
