from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Dict

class CommunityService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.threads_collection = db.get_collection("forum_threads")
        self.comments_collection = db.get_collection("comments")

    async def create_thread(self, author_id: str, title: str, content: str, media_id: str = None, tags: list = []):
        thread = {
            "title": title,
            "content": content,
            "author_id": str(author_id),
            "media_id": str(media_id) if media_id else None,
            "tags": tags,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        try:
            result = await self.threads_collection.insert_one(thread)
            thread["_id"] = str(result.inserted_id)
            return thread
        except Exception as e:
            from fastapi import HTTPException
            import logging
            logging.getLogger("backend").error(f"Failed to create thread: {e}")
            raise HTTPException(status_code=503, detail="Community database is currently unavailable.")

    async def get_threads(self, skip: int = 0, limit: int = 20) -> List[Dict]:
        try:
            cursor = self.threads_collection.find().sort("created_at", -1).skip(skip).limit(limit)
            threads = await cursor.to_list(length=limit)
            for thread in threads:
                thread["_id"] = str(thread["_id"])
            return threads
        except Exception as e:
            import logging
            logging.getLogger("backend").warning(f"MongoDB unavailable, returning empty threads: {e}")
            return []

    async def create_comment(self, thread_id: str, author_id: str, content: str, parent_id: str = None):
        comment = {
            "thread_id": str(thread_id),
            "parent_id": str(parent_id) if parent_id else None,
            "author_id": str(author_id),
            "content": content,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        try:
            result = await self.comments_collection.insert_one(comment)
            comment["_id"] = str(result.inserted_id)
            return comment
        except Exception as e:
            from fastapi import HTTPException
            import logging
            logging.getLogger("backend").error(f"Failed to create comment: {e}")
            raise HTTPException(status_code=503, detail="Community database is currently unavailable.")

    async def get_comments(self, thread_id: str):
        try:
            cursor = self.comments_collection.find({"thread_id": thread_id}).sort("created_at", 1)
            comments = []
            async for document in cursor:
                document["_id"] = str(document["_id"])
                comments.append(document)
            return comments
        except Exception as e:
            import logging
            logging.getLogger("backend").warning(f"MongoDB unavailable, returning empty comments: {e}")
            return []
