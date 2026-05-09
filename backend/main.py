from fastapi import FastAPI
from routers import auth, recommendation, economy, community

app = FastAPI(
    title="Gamified Cross-Media Recommendation Engine",
    description="Backend API",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router)
app.include_router(recommendation.router)
app.include_router(economy.router)
app.include_router(community.router)

@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}
