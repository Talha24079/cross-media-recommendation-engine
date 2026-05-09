from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

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
        result = await self.threads_collection.insert_one(thread)
        thread["_id"] = str(result.inserted_id)
        return thread

    async def get_threads(self, skip: int = 0, limit: int = 20):
        cursor = self.threads_collection.find().sort("created_at", -1).skip(skip).limit(limit)
        threads = []
        async for document in cursor:
            document["_id"] = str(document["_id"])
            threads.append(document)
        return threads

    async def create_comment(self, thread_id: str, author_id: str, content: str, parent_id: str = None):
        comment = {
            "thread_id": str(thread_id),
            "parent_id": str(parent_id) if parent_id else None,
            "author_id": str(author_id),
            "content": content,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        result = await self.comments_collection.insert_one(comment)
        comment["_id"] = str(result.inserted_id)
        return comment

    async def get_comments(self, thread_id: str):
        cursor = self.comments_collection.find({"thread_id": str(thread_id)}).sort("created_at", 1)
        comments = []
        async for document in cursor:
            document["_id"] = str(document["_id"])
            comments.append(document)
        return comments
