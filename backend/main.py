from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, recommendation, economy, community
from contextlib import asynccontextmanager
from core.database import AsyncSessionLocal
from core.exceptions import add_exception_handlers
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

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add global exception handlers
add_exception_handlers(app)

# Include routers
app.include_router(auth.router)
app.include_router(recommendation.router)
app.include_router(economy.router)
app.include_router(community.router)

@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}
