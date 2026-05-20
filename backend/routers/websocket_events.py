import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from core.security import verify_token
from services import realtime_broadcast

logger = logging.getLogger(__name__)

router = APIRouter(tags=["realtime"])


@router.websocket("/ws")
async def websocket_events(websocket: WebSocket, token: str | None = Query(None)):
    if not token:
        await websocket.close(code=1008)
        return

    user_sub = verify_token(token)
    if user_sub is None:
        await websocket.close(code=1008)
        return

    await realtime_broadcast.register(websocket)
    logger.debug("WebSocket connected user=%s", user_sub)

    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        realtime_broadcast.unregister(websocket)
        logger.debug("WebSocket disconnected user=%s", user_sub)
    except Exception as exc:
        logger.debug("WebSocket error: %s", exc)
        realtime_broadcast.unregister(websocket)
