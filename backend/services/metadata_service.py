import logging
from typing import Any

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


def _merge_meta(primary: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    out = dict(primary)
    for key, val in fallback.items():
        if val is None:
            continue
        if key not in out or out.get(key) in (None, "", {}):
            out[key] = val
    return out


async def fetch_metadata(title: str, media_type: str) -> dict[str, Any]:
    normalized_type = media_type.lower().strip()
    if normalized_type in {"movie", "anime"}:
        meta = await _fetch_tmdb(title, normalized_type)
        if not meta.get("poster_url"):
            itunes_media = "tvShow" if normalized_type == "anime" else "movie"
            meta = _merge_meta(meta, await _fetch_itunes(title, itunes_media))
        return meta
    if normalized_type == "game":
        return await _fetch_rawg(title)
    if normalized_type == "book":
        return await _fetch_openlibrary(title)
    if normalized_type == "music":
        return await _fetch_itunes(title, "music")
    if normalized_type == "podcast":
        return await _fetch_itunes(title, "podcast")
    return {}


async def _fetch_itunes(title: str, media: str) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://itunes.apple.com/search",
                params={"term": title, "media": media, "limit": 1},
            )
            if response.status_code != 200:
                return {}
            results = response.json().get("results", [])
            if not results:
                return {}
            item = results[0]
            art = item.get("artworkUrl100") or item.get("artworkUrl60") or ""
            if art:
                art = art.replace("100x100bb", "600x600bb").replace("60x60bb", "600x600bb")
            desc = (
                item.get("longDescription")
                or item.get("shortDescription")
                or item.get("description")
                or item.get("trackName")
                or item.get("collectionName")
            )
            return {
                "poster_url": art or None,
                "rating": None,
                "description": str(desc) if desc else None,
                "genre": item.get("primaryGenreName"),
                "external_id": str(item.get("trackId") or item.get("collectionId") or ""),
                "source": "itunes",
            }
    except Exception as exc:
        logger.warning("iTunes metadata fetch failed for %s: %s", title, exc)
        return {}


async def _fetch_tmdb(title: str, media_type: str) -> dict[str, Any]:
    if not settings.TMDB_API_KEY:
        return {}

    search_type = "tv" if media_type == "anime" else "movie"
    url = f"https://api.themoviedb.org/3/search/{search_type}"
    params = {"api_key": settings.TMDB_API_KEY, "query": title, "page": 1}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                return {}
            results = response.json().get("results", [])
            if not results:
                if search_type == "tv":
                    return {}
                return await _fetch_tmdb_tv_fallback(title)

            best = results[0]
            poster_path = best.get("poster_path")
            overview = best.get("overview") or ""
            return {
                "poster_url": (
                    f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                ),
                "rating": float(best.get("vote_average") or 0) or None,
                "description": overview or None,
                "genre": None,
                "external_id": str(best.get("id")),
                "source": "tmdb",
            }
    except Exception as exc:
        logger.warning("TMDB metadata fetch failed for %s: %s", title, exc)
        return {}


async def _fetch_tmdb_tv_fallback(title: str) -> dict[str, Any]:
    if not settings.TMDB_API_KEY:
        return {}
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": settings.TMDB_API_KEY, "query": title, "page": 1}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                return {}
            results = response.json().get("results", [])
            if not results:
                return {}
            best = results[0]
            poster_path = best.get("poster_path")
            return {
                "poster_url": (
                    f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                ),
                "rating": float(best.get("vote_average") or 0) or None,
                "description": best.get("overview") or None,
                "genre": None,
                "external_id": str(best.get("id")),
                "source": "tmdb",
            }
    except Exception as exc:
        logger.warning("TMDB movie fallback failed for %s: %s", title, exc)
        return {}


async def _fetch_rawg(title: str) -> dict[str, Any]:
    if not settings.RAWG_API_KEY:
        return {}

    url = "https://api.rawg.io/api/games"
    params = {"key": settings.RAWG_API_KEY, "search": title, "page_size": 1}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                return {}
            results = response.json().get("results", [])
            if not results:
                return {}
            best = results[0]
            genres = ", ".join(g.get("name", "") for g in best.get("genres", []) if g.get("name"))
            return {
                "poster_url": best.get("background_image"),
                "rating": float(best.get("rating") or 0) or None,
                "description": best.get("name") or None,
                "genre": genres or None,
                "external_id": str(best.get("id")),
                "source": "rawg",
            }
    except Exception as exc:
        logger.warning("RAWG metadata fetch failed for %s: %s", title, exc)
        return {}


async def _fetch_openlibrary(title: str) -> dict[str, Any]:
    url = "https://openlibrary.org/search.json"
    params = {"title": title, "limit": 1}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                return {}
            docs = response.json().get("docs", [])
            if not docs:
                return {}
            best = docs[0]
            cover_id = best.get("cover_i")
            subjects = best.get("subject", [])[:5]
            return {
                "poster_url": (
                    f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None
                ),
                "rating": None,
                "description": best.get("title"),
                "genre": ", ".join(subjects) if subjects else None,
                "external_id": str(best.get("key", "")).split("/")[-1] or None,
                "source": "openlibrary",
            }
    except Exception as exc:
        logger.warning("OpenLibrary metadata fetch failed for %s: %s", title, exc)
        return {}
