"""Marketing Amazon Agent — fiche produit, mots-clés, catégories, A+ Content."""

from __future__ import annotations

import json

from ..prompts import marketing as prompt
from ..state import BookState, log
from .base import brief_block, llm, market_of

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "title": {"type": "string"},
        "subtitle": {"type": "string"},
        "description_html": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "categories": {"type": "array", "items": {"type": "string"}},
        "author_bio": {"type": "string"},
        "a_plus_content": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "title",
        "subtitle",
        "description_html",
        "keywords",
        "categories",
        "author_bio",
        "a_plus_content",
    ],
}


def marketing_agent(state: BookState) -> dict:
    market = market_of(state)
    system = prompt.SYSTEM.format(market=market)
    outline = state.get("outline", {})
    research = state.get("research", {})
    user = (
        f"{brief_block(state)}\n\n"
        f"## Promesse du livre\n{outline.get('promise', '')}\n"
        f"## Titre de travail\n{outline.get('working_title', '')}\n\n"
        "## Recherche de marché (angle, mots-clés, concurrence)\n"
        f"{json.dumps(research, ensure_ascii=False, indent=2)}\n\n"
        "Produis tous les actifs marketing optimisés pour la conversion et le SEO Amazon."
    )
    marketing = llm().structured(system=system, user=user, schema=SCHEMA)

    return {
        "marketing": marketing,
        "stage": "done",
        **log("marketing", f"Fiche produit prête : « {marketing.get('title', '?')} »"),
    }
