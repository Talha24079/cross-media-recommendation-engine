import asyncio
import httpx
import uuid

BASE_URL = "http://127.0.0.1:8000"

async def run_tests():
    unique = uuid.uuid4().hex[:8]
    client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
    
    try:
        print("=== Production Hardening Integration Tests ===\n")
        
        # 1. Registration Validation
        print("Test 1: Weak password registration")
        user_weak = {"username": f"user_{unique}", "email": f"user_{unique}@test.com", "password": "123"}
        r = await client.post("/auth/register", json=user_weak)
        assert r.status_code == 422, "Should fail weak password"
        print("✅ Correctly rejected weak password")

        print("\nTest 2: Bad username format")
        user_bad_name = {"username": f"user space!", "email": f"user_{unique}@test.com", "password": "password1"}
        r = await client.post("/auth/register", json=user_bad_name)
        assert r.status_code == 422, "Should fail bad username"
        print("✅ Correctly rejected bad username")
        
        print("\nTest 3: Valid Registration")
        user_valid = {"username": f"test_{unique}", "email": f"test_{unique}@test.com", "password": "password1"}
        r = await client.post("/auth/register", json=user_valid)
        assert r.status_code == 201, f"Failed to register: {r.text}"
        print("✅ Registered valid user")
        
        print("\nTest 4: Duplicate Registration")
        r = await client.post("/auth/register", json=user_valid)
        assert r.status_code == 400, "Should reject duplicate"
        print("✅ Correctly rejected duplicate user")
        
        # 2. Login & /auth/me
        print("\nTest 5: Valid Login")
        r = await client.post("/auth/login", json={"username": user_valid["username"], "password": user_valid["password"]})
        assert r.status_code == 200, "Login failed"
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Logged in")
        
        print("\nTest 6: GET /auth/me")
        r = await client.get("/auth/me", headers=headers)
        assert r.status_code == 200, "GET /me failed"
        profile = r.json()
        assert profile["reputation_points"] == 100, "Initial balance should be 100"
        print(f"✅ /auth/me returned profile: {profile['username']}, Points: {profile['reputation_points']}")
        
        # 3. Media & Search Validation
        print("\nTest 7: Add invalid media type")
        r = await client.post("/recommendation/media", headers=headers, json={
            "title": "Invalid Type Media",
            "media_type": "invalid_type",
            "description": "Test"
        })
        assert r.status_code == 422, "Should reject invalid media_type enum"
        print("✅ Correctly rejected invalid media_type")
        
        print("\nTest 8: Add valid media (+5 points)")
        r = await client.post("/recommendation/media", headers=headers, json={
            "title": f"The Hardened Matrix {unique}",
            "media_type": "movie",
            "description": "A cyberpunk classic."
        })
        assert r.status_code == 201, f"Failed to add media: {r.text}"
        media_id = r.json()["id"]
        print("✅ Added media item")
        
        print("\nTest 9: Duplicate Media Detection")
        r = await client.post("/recommendation/media", headers=headers, json={
            "title": f"The Hardened Matrix {unique}", # Same title
            "media_type": "movie",
            "description": "A cyberpunk classic."
        })
        assert r.status_code == 409, f"Should reject duplicate media via similarity score, got {r.status_code}: {r.text}"
        print("✅ Correctly blocked duplicate media")
        
        print("\nTest 10: Search param limits")
        r = await client.get("/recommendation/search?query=matrix&top_k=100")
        assert r.status_code == 422, "Should cap top_k at 50"
        print("✅ Correctly rejected top_k > 50")
        
        # 4. Community & Points Generation
        print("\nTest 11: Create Thread (+3 points)")
        r = await client.post("/community/threads", headers=headers, json={
            "title": "Discussion on The Hardened Matrix",
            "content": "What a great movie!",
            "media_id": media_id
        })
        assert r.status_code == 201, f"Failed to create thread: {r.text}"
        thread_id = r.json()["_id"]
        print("✅ Created thread")
        
        print("\nTest 12: Create Comment (+2 points)")
        r = await client.post(f"/community/threads/{thread_id}/comments", headers=headers, json={
            "content": "I agree!"
        })
        assert r.status_code == 201, f"Failed to create comment: {r.text}"
        print("✅ Created comment")
        
        print("\nTest 13: Interact with Media (+1 point)")
        r = await client.post(f"/community/interact/{media_id}", headers=headers)
        assert r.status_code == 200, f"Failed to interact: {r.text}"
        print("✅ Interacted with media")
        
        print("\nTest 14: Verify Points Generation")
        r = await client.get("/auth/me", headers=headers)
        profile = r.json()
        expected_points = 100 + 5 + 3 + 2 + 1
        assert profile["reputation_points"] == expected_points, f"Expected {expected_points}, got {profile['reputation_points']}"
        print(f"✅ Points generated correctly: {expected_points}")
        
        # 5. Security & SQL Injection Protection
        print("\nTest 15: Invalid UUID format in route (SQL Injection protection)")
        r = await client.post("/economy/bounties/invalid-id-here/resolve", headers=headers, json={
            "winner_id": profile["id"]
        })
        assert r.status_code == 422, "Should reject malformed UUID before hitting DB"
        print("✅ Correctly blocked invalid UUID")

        print("\nTest 16: Invalid ObjectId format in MongoDB route")
        r = await client.post("/community/threads/invalid-id-here/comments", headers=headers, json={
            "content": "I agree!"
        })
        assert r.status_code == 400, "Should reject malformed ObjectId before hitting DB"
        print("✅ Correctly blocked invalid ObjectId")
        
        print("\n🎉 ALL HARDENING TESTS PASSED!")
        
    finally:
        await client.aclose()

asyncio.run(run_tests())
