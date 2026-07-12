"""Validated application settings loaded from environment.

Uses pydantic-settings for type-safe configuration at startup.
No secret values live here — all authentication uses Application Default Credentials.
"""

from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration with validated defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gcp_project_id: str = "stadiumiq-dev"
    gcp_region: str = "us-central1"
    use_gemini: bool = False
    use_firestore: bool = False
    gemini_prompt_version: str = "v1"
    allowed_origins: str = "http://localhost:5173,http://localhost:3000,https://fifa-check.netlify.app"
    # Vercel injects VERCEL_URL automatically (e.g. "my-app.vercel.app")
    vercel_url: str = ""

    def parsed_origins(self) -> list[str]:
        """Return allowed CORS origins including the Vercel deployment URL."""
        origins = [o.strip() for o in self.allowed_origins.split(",") if o.strip()]
        # Add Vercel deployment URL when running on Vercel
        if self.vercel_url:
            origins.append(f"https://{self.vercel_url}")
        # Also allow any *.vercel.app origin for preview deployments
        vercel_env_url = os.environ.get("VERCEL_URL", "")
        if vercel_env_url and f"https://{vercel_env_url}" not in origins:
            origins.append(f"https://{vercel_env_url}")
        return origins


@lru_cache
def get_settings() -> Settings:
    """Return the singleton validated settings instance."""
    return Settings()
