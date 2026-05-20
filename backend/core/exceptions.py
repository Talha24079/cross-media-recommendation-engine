from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)

def add_exception_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        if isinstance(exc, HTTPException):
            return await app.default_exception_handler(request, exc)

        logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
        origin = request.headers.get("origin")
        headers = {}
        if origin:
            headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Allow-Credentials"] = "true"
            headers["Access-Control-Allow-Methods"] = "*"
            headers["Access-Control-Allow-Headers"] = "*"
            
        if "ServerSelectionTimeoutError" in str(type(exc)) or "ConnectionFailure" in str(type(exc)):
            return JSONResponse(
                status_code=503,
                content={"detail": "Database is currently unreachable. Please try again later."},
                headers=headers
            )
            
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred."},
            headers=headers
        )
