"""Wrapper léger autour du SDK Anthropic.

Centralise les appels au modèle pour que les agents n'aient pas à connaître les
détails (pensée adaptative, effort, streaming, sorties structurées). Cela rend
les agents testables et facilement remplaçables.

Bonnes pratiques 2026 appliquées :
- `thinking={"type": "adaptive"}` pour tout raisonnement non trivial.
- `output_config={"effort": ...}` pour arbitrer qualité / coût.
- Streaming systématique pour les longues générations (évite les timeouts HTTP).
- Sorties JSON contraintes via `output_config.format` (json_schema).
"""

from __future__ import annotations

import json
from typing import Any

import anthropic

from .config import get_settings


class LLM:
    """Client Claude réutilisable, partagé par tous les agents."""

    def __init__(self, client: anthropic.Anthropic | None = None) -> None:
        self._settings = get_settings()
        # Le client lit ANTHROPIC_API_KEY depuis l'environnement.
        self._client = client or anthropic.Anthropic()

    # ------------------------------------------------------------------ #
    # Génération texte (longue) — streaming.
    # ------------------------------------------------------------------ #
    def write(
        self,
        *,
        system: str,
        user: str,
        effort: str | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> str:
        """Génère du texte libre (ex. un chapitre). Streame puis renvoie le texte complet."""
        with self._client.messages.stream(
            model=model or self._settings.model_main,
            max_tokens=max_tokens or self._settings.max_tokens_long,
            thinking={"type": "adaptive"},
            output_config={"effort": effort or self._settings.effort_default},
            system=system,
            messages=[{"role": "user", "content": user}],
        ) as stream:
            message = stream.get_final_message()
        return _first_text(message)

    # ------------------------------------------------------------------ #
    # Sortie structurée (JSON) — pour recherche, plan, marketing.
    # ------------------------------------------------------------------ #
    def structured(
        self,
        *,
        system: str,
        user: str,
        schema: dict[str, Any],
        effort: str | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Renvoie un dict validé contre `schema` (JSON Schema)."""
        with self._client.messages.stream(
            model=model or self._settings.model_main,
            max_tokens=max_tokens or self._settings.max_tokens_short,
            thinking={"type": "adaptive"},
            output_config={
                "effort": effort or self._settings.effort_default,
                "format": {"type": "json_schema", "schema": schema},
            },
            system=system,
            messages=[{"role": "user", "content": user}],
        ) as stream:
            message = stream.get_final_message()
        text = _first_text(message)
        return json.loads(text)


def _first_text(message: anthropic.types.Message) -> str:
    """Extrait le premier bloc de texte d'une réponse (ignore les blocs thinking)."""
    for block in message.content:
        if block.type == "text":
            return block.text
    return ""
