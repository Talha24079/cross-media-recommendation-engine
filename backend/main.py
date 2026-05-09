from fastapi import FastAPI
from routers import auth, recommendation, economy, community
from contextlib import asynccontextmanager
from core.database import AsyncSessionLocal
from services import recommendation_service
from services.background_jobs import start_background_jobs, stop_background_jobs

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load recommendation cache on startup
    async with AsyncSessionLocal() as db:
        await recommendation_service.load_cache(db)
    # Start background jobs (faction clustering every 24h)
    start_background_jobs()
    yield
    # Shutdown background jobs
    stop_background_jobs()

app = FastAPI(
    title="Gamified Cross-Media Recommendation Engine",
    description="Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(auth.router)
app.include_router(recommendation.router)
app.include_router(economy.router)
app.include_router(community.router)

@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}
