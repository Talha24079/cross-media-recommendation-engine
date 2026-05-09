from __future__ import annotations

import uuid

import numpy as np
import pytest

from models.media import MediaItem
from services import recommendation_service


@pytest.mark.asyncio
async def test_load_cache_populates_matrix_and_metadata(fake_session):
    first = MediaItem(title="Dune", type="book", embedding=np.array([1.0] + [0.0] * 383, dtype=np.float32).tolist())
    second = MediaItem(title="Interstellar", type="movie", embedding=np.array([0.0, 1.0] + [0.0] * 382, dtype=np.float32).tolist())
    fake_session.seed_media(first)
    fake_session.seed_media(second)

    class StubModel:
        def encode(self, text: str):
            return np.array([1.0] + [0.0] * 383, dtype=np.float32)

    recommendation_service.model = StubModel()
    recommendation_service.embedding_matrix = None
    recommendation_service.metadata_list = []

    await recommendation_service.load_cache(fake_session)

    assert recommendation_service.embedding_matrix.shape == (2, 384)
    assert recommendation_service.metadata_list[0]["title"] == "Dune"
    assert recommendation_service.metadata_list[1]["media_type"] == "movie"


def test_add_to_cache_appends_media_and_embeddings():
    recommendation_service.embedding_matrix = np.empty((0, 384), dtype=np.float32)
    recommendation_service.metadata_list = []

    media = MediaItem(title="The Matrix", type="movie")
    media.id = media.id or uuid.uuid4()
    embedding = np.array([1.0] + [0.0] * 383, dtype=np.float32)

    recommendation_service.add_to_cache(media, embedding)

    assert recommendation_service.embedding_matrix.shape == (1, 384)
    assert recommendation_service.metadata_list[0]["title"] == "The Matrix"


def test_search_similar_orders_by_score():
    class StubModel:
        def encode(self, text: str):
            return np.array([1.0, 0.0, 0.0], dtype=np.float32)

    recommendation_service.model = StubModel()
    recommendation_service.embedding_matrix = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.4, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=np.float32,
    )
    recommendation_service.metadata_list = [
        {"id": "a", "title": "Best Match", "media_type": "book"},
        {"id": "b", "title": "Medium Match", "media_type": "movie"},
        {"id": "c", "title": "Weak Match", "media_type": "game"},
    ]

    results = recommendation_service.search_similar("query", top_k=2)

    assert [result["id"] for result in results] == ["a", "b"]
    assert results[0]["score"] >= results[1]["score"]
