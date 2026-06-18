"""Configuration centralisée (environnement + valeurs par défaut)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MAELSTROM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Modèles
    model_main: str = "claude-opus-4-8"
    model_fast: str = "claude-haiku-4-5"
    effort_default: str = "high"

    # Tokens
    max_tokens_long: int = 32000  # rédaction d'un chapitre (streaming)
    max_tokens_short: int = 8000  # sorties structurées

    # Recherche web : "claude" (natif) ou "tavily"
    web_search: str = "claude"

    # Qualité
    max_revisions: int = 2  # réécritures max par chapitre avant escalade

    # RAG (optionnel)
    rag_enabled: bool = False

    # Sortie
    output_dir: str = "./output"


@lru_cache
def get_settings() -> Settings:
    return Settings()
