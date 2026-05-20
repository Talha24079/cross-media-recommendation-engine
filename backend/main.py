import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, community, test_error, economy, recommendation, websocket_events
from contextlib import asynccontextmanager
from core.database import AsyncSessionLocal, mongodb
from core.exceptions import add_exception_handlers
from services import recommendation_service
from services.background_jobs import start_background_jobs, stop_background_jobs
from services.community_seed import seed_starter_threads

_log = logging.getLogger("backend")

# Cap Mongo seed so a bad / unreachable Atlas URL does not block HTTP ready for tens of seconds.
_MONGO_SEED_TIMEOUT_S = 12.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load recommendation cache on startup
    try:
        async with AsyncSessionLocal() as db:
            await recommendation_service.load_cache(db)
    except Exception as e:
        _log.warning("Failed to load recommendation cache on startup: %s", e)
    try:
        await asyncio.wait_for(
            seed_starter_threads(mongodb),
            timeout=_MONGO_SEED_TIMEOUT_S,
        )
    except asyncio.TimeoutError:
        _log.warning(
            "Starter forum thread seed timed out after %ss (MongoDB unreachable or slow); "
            "skipping seed so the API can start.",
            _MONGO_SEED_TIMEOUT_S,
        )
    except Exception as e:
        _log.warning("Failed to seed starter forum threads: %s", e)
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
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add global exception handlers
add_exception_handlers(app)

# Include routers
app.include_router(auth.router)
app.include_router(test_error.router)
app.include_router(recommendation.router)
app.include_router(economy.router)
app.include_router(community.router)
app.include_router(websocket_events.router)

@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}
