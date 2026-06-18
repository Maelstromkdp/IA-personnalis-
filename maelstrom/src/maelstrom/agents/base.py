"""Helpers partagés par les agents.

`compose_system` garantit que CHAQUE agent reçoit la bible de marque MAELSTRÖM
(et, en transcréation, le Protocole de Transcréation) en tête de son prompt
système. C'est le mécanisme qui rend les règles « connues de tous les agents ».
"""

from __future__ import annotations

from functools import lru_cache

from ..book_state import BookState
from ..brand import SpoilerGuard, full_brand_context, transcreation_context
from ..llm import LLM


@lru_cache
def llm() -> LLM:
    return LLM()


@lru_cache
def spoiler_guard() -> SpoilerGuard:
    return SpoilerGuard(llm())


def compose_system(role_prompt: str, *, state: BookState) -> str:
    """Assemble : contexte de marque (+ protocole si transcréation) + rôle de l'agent."""
    parts = [full_brand_context()]
    if state.get("mode") == "transcreation":
        parts.append(transcreation_context())
    parts.append("# RÔLE DE L'AGENT\n" + role_prompt)
    parts.append(f"# LANGUE DE SORTIE : {state.get('language', 'FR')}")
    return "\n\n".join(parts)


def language_label(state: BookState) -> str:
    return "français" if state.get("language", "FR") == "FR" else "anglais US"
