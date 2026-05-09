import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.faction_service import run_faction_clustering

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def start_background_jobs():
    """Start all background scheduled jobs."""

    # Run faction clustering every 24 hours
    scheduler.add_job(
        run_faction_clustering,
        'interval',
        hours=24,
        id='faction_clustering',
        name='Faction KMeans Clustering',
        replace_existing=True
    )

    scheduler.start()
    logger.info("Background scheduler started. Faction clustering runs every 24 hours.")


def stop_background_jobs():
    """Shutdown the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Background scheduler stopped.")
