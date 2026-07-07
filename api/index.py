"""Vercel serverless entry point for StadiumIQ FastAPI backend.

Vercel's Python runtime detects the ASGI `app` variable automatically
and wraps it as a serverless function for every request to /api/*.

Path resolution adds backend/ to sys.path so all `from app.*` imports
within the backend package resolve correctly in the serverless environment.
"""

from __future__ import annotations

import os
import sys

# ---------------------------------------------------------------------------
# Ensure the backend package is importable from the serverless function path.
# In Vercel, __file__ is at /var/task/api/index.py, so the repo root is one
# level up.
# ---------------------------------------------------------------------------
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_backend = os.path.join(_root, "backend")
if _backend not in sys.path:
    sys.path.insert(0, _backend)

# ---------------------------------------------------------------------------
# Import the FastAPI application factory.
# create_app() wires all middleware, routers, and rate limiting.
# ---------------------------------------------------------------------------
from app.main import create_app  # noqa: E402

app = create_app()
