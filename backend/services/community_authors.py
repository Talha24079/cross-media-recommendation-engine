import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


SYSTEM_AUTHORS: dict[str, tuple[str, str]] = {
    "crossmedia-community": (
        "CrossMedia Team",
        "https://api.dicebear.com/7.x/shapes/svg?seed=crossmedia&backgroundColor=1c2330",
    ),
}


def avatar_url_for_username(username: str) -> str:
    safe = username.strip() or "user"
    return (
        "https://api.dicebear.com/7.x/avataaars/svg"
        f"?seed={safe}&backgroundColor=141820"
    )


def _author_tuple_for_id(author_id: str, username: str) -> tuple[str, str]:
    return username, avatar_url_for_username(username)


async def enrich_threads(threads: list[dict], db: AsyncSession) -> list[dict]:
    if not threads:
        return []
    uuid_ids: set[uuid.UUID] = set()
    for t in threads:
        aid = str(t.get("author_id", ""))
        if aid in SYSTEM_AUTHORS:
            continue
        try:
            uuid_ids.add(uuid.UUID(aid))
        except (ValueError, TypeError):
            continue

    user_map: dict[str, tuple[str, str]] = {}
    if uuid_ids:
        result = await db.execute(select(User.id, User.username).where(User.id.in_(uuid_ids)))
        for row in result.all():
            # Handle both tuple (from real DB) and User object (from test fake DB)
            if isinstance(row, tuple):
                uid, uname = row[0], row[1]
            else:
                uid, uname = row.id, row.username
            user_map[str(uid)] = _author_tuple_for_id(str(uid), uname)

    out: list[dict] = []
    for t in threads:
        tid = dict(t)
        aid = str(tid.get("author_id", ""))
        if aid in SYSTEM_AUTHORS:
            uname, av = SYSTEM_AUTHORS[aid]
        elif aid in user_map:
            uname, av = user_map[aid]
        else:
            uname, av = ("Member", avatar_url_for_username(aid[:8] if aid else "guest"))
        tid["author_username"] = uname
        tid["author_avatar_url"] = av
        out.append(tid)
    return out


async def enrich_comments(comments: list[dict], db: AsyncSession) -> list[dict]:
    if not comments:
        return []
    uuid_ids: set[uuid.UUID] = set()
    for c in comments:
        aid = str(c.get("author_id", ""))
        if aid in SYSTEM_AUTHORS:
            continue
        try:
            uuid_ids.add(uuid.UUID(aid))
        except (ValueError, TypeError):
            continue

    user_map: dict[str, tuple[str, str]] = {}
    if uuid_ids:
        result = await db.execute(select(User.id, User.username).where(User.id.in_(uuid_ids)))
        for row in result.all():
            # Handle both tuple (from real DB) and User object (from test fake DB)
            if isinstance(row, tuple):
                uid, uname = row[0], row[1]
            else:
                uid, uname = row.id, row.username
            user_map[str(uid)] = _author_tuple_for_id(str(uid), uname)

    out: list[dict] = []
    for c in comments:
        cid = dict(c)
        aid = str(cid.get("author_id", ""))
        if aid in SYSTEM_AUTHORS:
            uname, av = SYSTEM_AUTHORS[aid]
        elif aid in user_map:
            uname, av = user_map[aid]
        else:
            uname, av = ("Member", avatar_url_for_username(aid[:8] if aid else "guest"))
        cid["author_username"] = uname
        cid["author_avatar_url"] = av
        out.append(cid)
    return out


async def enrich_single_thread(thread: dict, db: AsyncSession) -> dict:
    enriched = await enrich_threads([thread], db)
    return enriched[0]


async def enrich_single_comment(comment: dict, db: AsyncSession) -> dict:
    enriched = await enrich_comments([comment], db)
    return enriched[0]


def user_avatar_url(username: str) -> str:
    return avatar_url_for_username(username)
