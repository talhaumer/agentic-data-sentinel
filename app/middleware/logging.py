"""Logging middleware for request/response tracking."""

import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())

        # Add request ID to request state
        request.state.request_id = request_id

        # Log request
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log response
        logger.info(
            "Request completed",
            request_id=request_id,
            status_code=response.status_code,
            process_time=process_time,
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
