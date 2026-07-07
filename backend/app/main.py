"""FastAPI application factory for StadiumIQ.

Configures:
- Fast body size checks in custom middleware (64 KB cap)
- Standard HTTP security response headers
- JSON structured logs
- Endpoint routers registration
"""

from __future__ import annotations

import logging
import sys
import time
from typing import Any, Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pythonjsonlogger import jsonlogger
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import get_settings
from app.rate_limit import limiter
from app.routes import assist, crowd, health, sustainability, wayfinding

# ── Logging Configuration ──
# Custom structured JSON logger output configuration
logger = logging.getLogger("stadiumiq")
logger.setLevel(logging.INFO)
log_handler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    "%(timestamp)s %(severity)s %(name)s %(message)s",
    rename_fields={"asctime": "timestamp", "levelname": "severity"},
)
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)

# ── Constants ──
# Generous size for normal stadium queries, but guards against large body DOS attacks
_MAX_BODY_BYTES = 64 * 1024  # 64 KB

_SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self' *;",
}


def create_app() -> FastAPI:
    """Instantiate and configure the FastAPI application instance."""
    app = FastAPI(
        title="StadiumIQ API",
        version="1.0.0",
        description="Operations and Fan Experience APIs for FIFA World Cup 2026",
    )

    settings = get_settings()

    # Rate limiting middleware registration
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.parsed_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom size limiter and security headers middlewares
    @app.middleware("http")
    async def body_size_and_security_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # Fast header check for content size
        content_length = request.headers.get("Content-Length")
        if content_length is not None:
            try:
                if int(content_length) > _MAX_BODY_BYTES:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Request body too large"},
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header"},
                )

        # Streaming check to catch spoofed Content-Length headers
        original_receive = request._receive
        body_bytes = 0
        async def mock_receive() -> dict[str, Any]:
            nonlocal body_bytes
            message = await original_receive()
            if message["type"] == "http.request":
                body_bytes += len(message.get("body", b""))
                if body_bytes > _MAX_BODY_BYTES:
                    # Throw direct error to trigger fallback handler
                    raise ValueError("Oversized payload")
            return message

        # Intercept receive channel with limit checking wrapper
        request._receive = mock_receive

        start_time = time.monotonic()
        try:
            response = await call_next(request)
        except ValueError as err:
            if "Oversized payload" in str(err):
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body too large"},
                )
            raise err

        # Latency tracking
        duration_ms = int((time.monotonic() - start_time) * 1000)

        # Apply security headers to output response
        for header, val in _SECURITY_HEADERS.items():
            response.headers.setdefault(header, val)

        # Structured log print
        logger.info(
            f"HTTP {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": duration_ms,
            },
        )
        return response

    # 429 Rate Limit Custom Error Handler
    @app.exception_handler(RateLimitExceeded)
    def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please retry later."},
            headers={"Retry-After": "60"},
        )

    # Routers mapping
    app.include_router(health.router, prefix="/api")
    app.include_router(crowd.router, prefix="/api")
    app.include_router(wayfinding.router, prefix="/api")
    app.include_router(sustainability.router, prefix="/api")
    app.include_router(assist.router, prefix="/api")

    return app


app = create_app()
