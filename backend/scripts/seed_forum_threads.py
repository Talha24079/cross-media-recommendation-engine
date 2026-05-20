#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.database import mongodb
from services.community_seed import seed_starter_threads


async def main() -> None:
    inserted = await seed_starter_threads(mongodb)
    if inserted:
        print(f"Seeded {inserted} starter forum threads.")
    else:
        print("No threads seeded (collection already has documents).")


if __name__ == "__main__":
    asyncio.run(main())
