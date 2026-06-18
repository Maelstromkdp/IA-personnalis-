"""Wrapper Anthropic partagé par les agents.

Centralise les bonnes pratiques 2026 :
- `thinking={"type": "adaptive"}` pour tout raisonnement non trivial ;
- `output_config={"effort": ...}` pour arbitrer qualité / coût ;
- streaming systématique pour la rédaction longue (évite les timeouts) ;
- sorties JSON contraintes via `output_config.format` ;
- recherche web via l'outil serveur natif de Claude (`web_search`), avec gestion
  de `pause_turn` (le modèle peut faire plusieurs tours de recherche).
"""

from __future__ import annotations

from typing import Any

import anthropic

from .config import get_settings


class LLM:
    def __init__(self, client: anthropic.Anthropic | None = None) -> None:
        self._settings = get_settings()
        self._client = client or anthropic.Anthropic()

    # ------------------------------------------------------------------ #
    # Texte long (chapitres, transcréation) — streaming.
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
    # Sortie structurée (JSON contraint).
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
        import json

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
        return json.loads(_first_text(message))

    # ------------------------------------------------------------------ #
    # Recherche web (outil serveur natif Claude).
    # ------------------------------------------------------------------ #
    def research(
        self,
        *,
        system: str,
        user: str,
        max_uses: int = 6,
        max_continuations: int = 5,
        model: str | None = None,
    ) -> str:
        """Lance une recherche web et renvoie la synthèse textuelle de Claude.

        N.B. : la recherche web renvoie des citations, incompatibles avec la
        sortie structurée. On récupère donc du texte ici ; la mise en forme
        structurée se fait dans un second appel `structured` côté agent.
        """
        tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": max_uses}]
        messages: list[dict[str, Any]] = [{"role": "user", "content": user}]

        for _ in range(max_continuations + 1):
            response = self._client.messages.create(
                model=model or self._settings.model_main,
                max_tokens=self._settings.max_tokens_short,
                thinking={"type": "adaptive"},
                system=system,
                tools=tools,
                messages=messages,
            )
            if response.stop_reason == "pause_turn":
                # Le modèle a atteint la limite d'itérations serveur : on relance.
                messages = [
                    {"role": "user", "content": user},
                    {"role": "assistant", "content": response.content},
                ]
                continue
            return _join_text(response)
        return _join_text(response)


def _first_text(message: anthropic.types.Message) -> str:
    for block in message.content:
        if block.type == "text":
            return block.text
    return ""


def _join_text(message: anthropic.types.Message) -> str:
    return "\n".join(b.text for b in message.content if getattr(b, "type", None) == "text")
