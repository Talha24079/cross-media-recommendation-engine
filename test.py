import asyncio
import httpx

async def test_recommendations():
    base_url = "http://127.0.0.1:8000"
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        print("=== 1. Adding 'Dune' (Book) ===")
        res1 = await client.post("/recommendation/media", json={
            "title": "Dune",
            "media_type": "book",
            "description": "A science fiction epic set on a desert planet, involving politics, religion, and ecology."
        })
        if res1.status_code == 201:
            print("✅ Added Dune successfully.")
        else:
            print("❌ Failed to add Dune:", res1.text)
            
        print("\n=== 2. Adding 'Star Wars' (Movie) ===")
        res2 = await client.post("/recommendation/media", json={
            "title": "Star Wars: A New Hope",
            "media_type": "movie",
            "description": "A science fiction space opera about a farm boy who becomes a hero and fights an evil empire."
        })
        if res2.status_code == 201:
            print("✅ Added Star Wars successfully.")
        else:
            print("❌ Failed to add Star Wars:", res2.text)
            
        print("\n=== 3. Adding 'The Godfather' (Movie) ===")
        res3 = await client.post("/recommendation/media", json={
            "title": "The Godfather",
            "media_type": "movie",
            "description": "A crime drama about the aging patriarch of an organized crime dynasty transferring control of his empire to his reluctant son."
        })
        if res3.status_code == 201:
            print("✅ Added The Godfather successfully.")
        else:
            print("❌ Failed to add The Godfather:", res3.text)

        print("\n=== 4. Testing Semantic Search ===")
        query = "sci-fi space adventure"
        print(f"Searching for: '{query}'")
        search_res = await client.get(f"/recommendation/search?query={query}&top_k=5")
        
        if search_res.status_code == 200:
            results = search_res.json()
            print(f"✅ Found {len(results)} matches!")
            for i, item in enumerate(results):
                print(f"  {i+1}. {item['title']} ({item['media_type']}) - Score: {item['score']:.4f}")
        else:
            print("❌ Search failed:", search_res.text)

asyncio.run(test_recommendations())

