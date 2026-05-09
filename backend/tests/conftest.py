from __future__ import annotations

import copy
import re
import uuid
from datetime import date, datetime, timezone
from types import SimpleNamespace

import numpy as np
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

import main
from core.database import get_db, get_mongodb
from models.bounty import Bounty, BountyStatus, CentralLedger
from models.media import MediaItem
from models.user import User
from services import faction_service, recommendation_service


class FakeResult:
    def __init__(self, items):
        self._items = list(items)

    def scalars(self):
        return self

    def first(self):
        return self._items[0] if self._items else None

    def all(self):
        return list(self._items)

    def scalar_one_or_none(self):
        return self.first()


class FakeAsyncSession:
    def __init__(self):
        self.users: list[User] = []
        self.media_items: list[MediaItem] = []
        self.bounties: list[Bounty] = []
        self.ledger_entries: list[CentralLedger] = []

    def seed_user(self, user: User):
        self.add(user)

    def seed_media(self, media_item: MediaItem):
        self.add(media_item)

    def seed_bounty(self, bounty: Bounty):
        self.add(bounty)

    def get_user(self, user_id: uuid.UUID | str):
        target = str(user_id)
        for user in self.users:
            if str(user.id) == target:
                return user
        return None

    def get_bounty(self, bounty_id: uuid.UUID | str):
        target = str(bounty_id)
        for bounty in self.bounties:
            if str(bounty.id) == target:
                return bounty
        return None

    def _ensure_defaults(self, obj):
        now = datetime.now(timezone.utc)
        if hasattr(obj, "id") and getattr(obj, "id", None) is None:
            obj.id = uuid.uuid4()
        if isinstance(obj, User):
            if getattr(obj, "reputation_points", None) is None:
                obj.reputation_points = 100
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "updated_at", None) is None:
                obj.updated_at = now
        if isinstance(obj, MediaItem):
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "updated_at", None) is None:
                obj.updated_at = now
        if isinstance(obj, Bounty):
            if getattr(obj, "status", None) is None:
                obj.status = BountyStatus.OPEN
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now
            if getattr(obj, "updated_at", None) is None:
                obj.updated_at = now
        if isinstance(obj, CentralLedger):
            if getattr(obj, "created_at", None) is None:
                obj.created_at = now

    def add(self, obj):
        self._ensure_defaults(obj)
        if isinstance(obj, User) and obj not in self.users:
            self.users.append(obj)
        elif isinstance(obj, MediaItem) and obj not in self.media_items:
            self.media_items.append(obj)
        elif isinstance(obj, Bounty) and obj not in self.bounties:
            self.bounties.append(obj)
        elif isinstance(obj, CentralLedger) and obj not in self.ledger_entries:
            self.ledger_entries.append(obj)

    async def execute(self, statement):
        compiled = statement.compile()
        sql = str(compiled)
        for name, value in compiled.params.items():
            token = f":{name}"
            postcompile_token = f"__[POSTCOMPILE_{name}]"
            if isinstance(value, (list, tuple, set)):
                if postcompile_token in sql:
                    rendered_values = ", ".join(self._render_literal(item) for item in value)
                    sql = sql.replace(postcompile_token, rendered_values)
                else:
                    rendered_values = "[" + ", ".join(self._render_literal(item) for item in value) + "]"
                    sql = sql.replace(token, rendered_values)
                    sql = sql.replace(postcompile_token, rendered_values)
            else:
                rendered_value = self._render_literal(value)
                sql = sql.replace(token, rendered_value)
                sql = sql.replace(postcompile_token, rendered_value)

        if sql.startswith("SELECT") and "FROM users" in sql:
            return FakeResult(self._select_users(sql))

        if sql.startswith("SELECT") and "FROM media_items" in sql:
            return FakeResult(self._select_media(sql))

        if sql.startswith("SELECT") and "FROM bounties" in sql:
            return FakeResult(self._select_bounties(sql))

        if sql.startswith("UPDATE users"):
            self._apply_user_update(sql)
            return FakeResult([])

        if sql.startswith("UPDATE bounties"):
            self._apply_bounty_update(sql)
            return FakeResult([])

        raise AssertionError(f"Unsupported SQL in fake session: {sql}")

    def _select_users(self, sql: str):
        username = self._match(sql, r"users\.username\s*=\s*'([^']+)'")
        email = self._match(sql, r"users\.email\s*=\s*'([^']+)'")
        user_id = self._match(sql, r"users\.id\s*=\s*'([^']+)'")
        faction_id = self._match(sql, r"users\.faction_id\s*=\s*(\d+)")
        taste_vector_not_null = "users.taste_vector IS NOT NULL" in sql

        results = []
        for user in self.users:
            if user_id and str(user.id) != user_id:
                continue
            if username and email:
                if user.username != username and user.email != email:
                    continue
            elif username and user.username != username:
                continue
            elif email and user.email != email:
                continue
            if faction_id and user.faction_id != int(faction_id):
                continue
            if taste_vector_not_null and user.taste_vector is None:
                continue
            results.append(user)
        return results

    def _select_media(self, sql: str):
        media_id = self._match(sql, r"media_items\.id\s*=\s*'([^']+)'")
        title = self._match(sql, r"media_items\.title\s*=\s*'([^']+)'")
        media_type = self._match(sql, r"media_items\.type\s*=\s*'([^']+)'")
        if media_id:
            return [item for item in self.media_items if str(item.id) == media_id]
        if title and media_type:
            return [
                item for item in self.media_items
                if item.title == title and item.type == media_type
            ]
        in_ids = re.findall(r"'([0-9a-fA-F-]{36})'", sql)
        if "IN" in sql and in_ids:
            wanted = set(in_ids)
            return [item for item in self.media_items if str(item.id) in wanted]
        return list(self.media_items)

    def _select_bounties(self, sql: str):
        bounty_id = self._match(sql, r"bounties\.id\s*=\s*'([^']+)'")
        status = self._match(sql, r"bounties\.status\s*=\s*'([^']+)'")
        results = []
        for bounty in self.bounties:
            if bounty_id and str(bounty.id) != bounty_id:
                continue
            if status:
                normalized_status = status.split(".")[-1]
                if getattr(bounty.status, "value", str(bounty.status)) != normalized_status:
                    continue
            results.append(bounty)
        return results

    def _apply_user_update(self, sql: str):
        user_id = self._match(sql, r"users\.id\s*=\s*'([^']+)'")
        if not user_id:
            return
        user = self.get_user(user_id)
        if user is None:
            return

        amount = self._match(sql, r"reputation_points\s*=\s*\(users\.reputation_points\s*([+-])\s*(\d+)\)")
        if amount:
            sign, raw_amount = amount
            delta = int(raw_amount)
            if sign == "-":
                delta *= -1
            user.reputation_points += delta

        streak_date = self._match(sql, r"last_streak_date\s*=\s*'([^']+)'")
        if streak_date:
            user.last_streak_date = date.fromisoformat(streak_date)

        faction_id = self._match(sql, r"faction_id\s*=\s*(\d+)")
        if faction_id and "faction_id" in sql and "users.reputation_points" not in sql:
            user.faction_id = int(faction_id)

        taste_vector = self._match(sql, r"taste_vector\s*=\s*(\[[^\]]*\])")
        if taste_vector:
            import ast

            user.taste_vector = ast.literal_eval(taste_vector)

    def _apply_bounty_update(self, sql: str):
        bounty_id = self._match(sql, r"bounties\.id\s*=\s*'([^']+)'")
        if not bounty_id:
            return
        bounty = self.get_bounty(bounty_id)
        if bounty is None:
            return
        status = self._match(sql, r"status\s*=\s*'([^']+)'")
        if status:
            normalized_status = status.split(".")[-1]
            bounty.status = BountyStatus[normalized_status]

    @staticmethod
    def _render_literal(value):
        if value is None:
            return "NULL"
        if isinstance(value, str):
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        if isinstance(value, uuid.UUID):
            return f"'{value}'"
        if isinstance(value, (datetime, date)):
            return f"'{value.isoformat()}'"
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        return str(value)

    @staticmethod
    def _match(sql: str, pattern: str):
        match = re.search(pattern, sql)
        if not match:
            return None
        if len(match.groups()) == 1:
            return match.group(1)
        return match.groups()

    async def commit(self):
        return None

    async def refresh(self, obj):
        return None


class FakeEmbeddingModel:
    def __init__(self, vector: np.ndarray | None = None):
        self.vector = vector if vector is not None else np.zeros(384, dtype=np.float32)

    def encode(self, text: str):
        return np.array(self.vector, dtype=np.float32)


class FakeInsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class FakeCursor:
    def __init__(self, documents):
        self._documents = list(documents)
        self._index = 0

    def sort(self, key, direction):
        reverse = direction < 0
        self._documents.sort(key=lambda document: document.get(key), reverse=reverse)
        return self

    def skip(self, amount):
        self._documents = self._documents[amount:]
        return self

    def limit(self, amount):
        self._documents = self._documents[:amount]
        return self

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index >= len(self._documents):
            raise StopAsyncIteration
        document = self._documents[self._index]
        self._index += 1
        return copy.deepcopy(document)


class FakeCollection:
    def __init__(self):
        self.documents: list[dict] = []

    async def insert_one(self, document):
        stored_document = copy.deepcopy(document)
        stored_document["_id"] = ObjectId()
        self.documents.append(stored_document)
        return FakeInsertOneResult(stored_document["_id"])

    def find(self, filter=None):
        filter = filter or {}
        results = []
        for document in self.documents:
            matches = True
            for key, value in filter.items():
                if document.get(key) != value:
                    matches = False
                    break
            if matches:
                results.append(copy.deepcopy(document))
        return FakeCursor(results)


class FakeMongoDB:
    def __init__(self):
        self._collections = {
            "forum_threads": FakeCollection(),
            "comments": FakeCollection(),
        }

    def get_collection(self, name):
        return self._collections[name]


@pytest.fixture
def fake_session():
    return FakeAsyncSession()


@pytest.fixture
def fake_mongo():
    return FakeMongoDB()


@pytest.fixture
def api(monkeypatch, fake_session, fake_mongo):
    async def fake_load_cache(db):
        return None

    async def fake_build_taste_profile(*args, **kwargs):
        return None

    monkeypatch.setattr(main, "start_background_jobs", lambda: None)
    monkeypatch.setattr(main, "stop_background_jobs", lambda: None)
    monkeypatch.setattr(recommendation_service, "load_cache", fake_load_cache)
    monkeypatch.setattr(faction_service, "build_taste_profile", fake_build_taste_profile)
    recommendation_service.model = FakeEmbeddingModel()
    recommendation_service.embedding_matrix = np.empty((0, 384), dtype=np.float32)
    recommendation_service.metadata_list = []

    async def override_get_db():
        yield fake_session

    async def override_get_mongodb():
        yield fake_mongo

    main.app.dependency_overrides[get_db] = override_get_db
    main.app.dependency_overrides[get_mongodb] = override_get_mongodb

    with TestClient(main.app) as client:
        yield SimpleNamespace(client=client, session=fake_session, mongo=fake_mongo)

    main.app.dependency_overrides.clear()
