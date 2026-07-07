"""Rate limiting registration helper for StadiumIQ APIs.

Defines a rate limit singleton instance to prevent circular dependency imports.
Identifies clients by request IP addresses.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

# Limit endpoint queries keyed on caller IP address
limiter = Limiter(key_func=get_remote_address)
