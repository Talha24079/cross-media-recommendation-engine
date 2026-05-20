from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)

_connections: set[WebSocket] = set()


async def register(websocket: WebSocket) -> None:
    await websocket.accept()
    _connections.add(websocket)


def unregister(websocket: WebSocket) -> None:
    _connections.discard(websocket)


async def broadcast(event: str, payload: dict[str, Any] | None = None) -> None:
    message: dict[str, Any] = {"event": event}
    if payload:
        message.update(payload)
    text = json.dumps(message, default=str)
    dead: list[WebSocket] = []
    for ws in list(_connections):
        try:
            await ws.send_text(text)
        except Exception as exc:
            logger.debug("WebSocket send failed, dropping client: %s", exc)
            dead.append(ws)
    for ws in dead:
        unregister(ws)


async def notify_thread_comments(thread_id: str) -> None:
    await broadcast("thread_comments_changed", {"thread_id": thread_id})


async def notify_threads_list() -> None:
    await broadcast("threads_changed")


async def notify_bounty(bounty_id: str) -> None:
    await broadcast("bounty_changed", {"bounty_id": bounty_id})


async def notify_bounties_list() -> None:
    await broadcast("bounties_changed")
