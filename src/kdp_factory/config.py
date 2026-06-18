"""Configuration centralisée (variables d'environnement + valeurs par défaut)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres globaux. Chargés depuis l'environnement / le fichier `.env`."""

    model_config = SettingsConfigDict(
        env_prefix="KDP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Modèles -----------------------------------------------------------
    # Opus 4.8 = modèle le plus capable, idéal pour rédaction longue et raisonnement.
    model_main: str = "claude-opus-4-8"
    # Haiku 4.5 = rapide/économique pour le routage et les tâches simples.
    model_fast: str = "claude-haiku-4-5"

    # Effort par défaut (pensée adaptative). low | medium | high | xhigh | max
    effort_default: str = "high"

    # max_tokens par défaut pour la génération longue (chapitres) — streaming requis.
    max_tokens_long: int = 32000
    max_tokens_short: int = 8000

    # --- RAG (optionnel) ---------------------------------------------------
    rag_enabled: bool = False
    rag_dir: str = "./.rag_store"

    # --- Divers ------------------------------------------------------------
    output_dir: str = "./output"


@lru_cache
def get_settings() -> Settings:
    """Retourne l'instance unique de configuration (mise en cache)."""
    return Settings()
