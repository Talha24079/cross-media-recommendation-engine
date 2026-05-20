from fastapi import APIRouter
router = APIRouter()
@router.get("/test-error")
async def test_error():
    raise Exception("Test error")
