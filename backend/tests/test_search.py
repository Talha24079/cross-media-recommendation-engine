import pytest
from services import recommendation_service

@pytest.mark.asyncio
async def test_search_with_fake_session(fake_session):
    # Seed fake data
    from models.media import MediaItem
    item1 = MediaItem(title="Dune", type="book", genre="sci-fi, epic space battle", embedding=[1.0] + [0.0]*383)
    item2 = MediaItem(title="Harry Potter", type="book", genre="magic, young wizard attending a magical school", embedding=[0.0, 1.0] + [0.0]*382)
    fake_session.seed_media(item1)
    fake_session.seed_media(item2)
    
    # Need to load_cache manually or test logic
    await recommendation_service.load_cache(fake_session)
    
    # Mock encode to return specific vectors based on query
    def mock_encode(text):
        if "space" in text:
            return [1.0] + [0.0]*383
        return [0.0, 1.0] + [0.0]*382
    recommendation_service.model.encode = mock_encode

    query = "epic space battle and intergalactic empire"
    results = recommendation_service.search_similar(query, top_k=5)
    assert len(results) > 0
    assert results[0]['title'] == "Dune"
    
    query2 = "a young wizard attending a magical school"
    results = recommendation_service.search_similar(query2, top_k=5)
    assert len(results) > 0
    assert results[0]['title'] == "Harry Potter"
