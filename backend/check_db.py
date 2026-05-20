import asyncio
from core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine

async def main():
    print('Using DATABASE_URL:', settings.DATABASE_URL)
    eng = create_async_engine(settings.DATABASE_URL, echo=False)
    from sqlalchemy import text
    try:
        async with eng.connect() as conn:
            res = await conn.execute(text('SELECT 1'))
            print('DB response:', res.scalar())
            cnt = await conn.execute(text('SELECT count(*) FROM media_items'))
            print('media_items count:', cnt.scalar())
    except Exception as e:
        print('ERROR:', type(e).__name__, e)
    finally:
        await eng.dispose()

if __name__ == '__main__':
    asyncio.run(main())
