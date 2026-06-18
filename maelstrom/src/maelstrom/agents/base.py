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


def compose_system(role_prompt: str, *, state: BookState) -> list[dict]:
    """Construit le prompt système sous forme de blocs, avec **mise en cache**.

    Le 1er bloc = contexte de marque (bible + protocole). Il est IDENTIQUE pour
    tous les agents d'un même run : on y pose un point de cache (`cache_control`)
    pour qu'Anthropic le serve depuis le cache à chaque appel suivant (coût ~÷10,
    latence réduite). Le 2e bloc (rôle + langue) varie selon l'agent.

    NB : sur Opus, le cache ne se déclenche qu'au-delà d'un préfixe minimal
    (~4096 tokens). Avec tes documents de marque complets collés dans `brand/`,
    le seuil est franchi et le cache s'active automatiquement.
    """
    brand = full_brand_context()
    if state.get("mode") == "transcreation":
        brand += "\n\n" + transcreation_context()

    role = (
        "# RÔLE DE L'AGENT\n"
        + role_prompt
        + f"\n\n# LANGUE DE SORTIE : {state.get('language', 'FR')}"
    )
    return [
        {"type": "text", "text": brand, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": role},
    ]



def language_label(state: BookState) -> str:
    return "français" if state.get("language", "FR") == "FR" else "anglais US"
