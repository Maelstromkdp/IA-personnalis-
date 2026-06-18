"""Outline & Structure Agent — plan détaillé du livre."""

from __future__ import annotations

import json

from ..prompts import outline as prompt
from ..state import BookState, Chapter, log
from .base import brief_block, llm, market_of

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "working_title": {"type": "string"},
        "promise": {"type": "string"},
        "front_matter": {"type": "array", "items": {"type": "string"}},
        "back_matter": {"type": "array", "items": {"type": "string"}},
        "chapters": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "index": {"type": "integer"},
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "key_points": {"type": "array", "items": {"type": "string"}},
                    "target_words": {"type": "integer"},
                },
                "required": ["index", "title", "summary", "key_points", "target_words"],
            },
        },
    },
    "required": ["working_title", "promise", "front_matter", "back_matter", "chapters"],
}


def outline_agent(state: BookState) -> dict:
    market = market_of(state)
    system = prompt.SYSTEM.format(market=market)
    research = state.get("research", {})
    user = (
        "Construis le plan détaillé du livre à partir du brief et de la recherche.\n\n"
        f"{brief_block(state)}\n\n"
        "## Dossier de recherche de marché\n"
        f"{json.dumps(research, ensure_ascii=False, indent=2)}\n\n"
        "Produis titre de travail, promesse, chapitres détaillés (résumé + points clés "
        "+ longueur cible) et éléments de début/fin d'ouvrage."
    )
    outline = llm().structured(system=system, user=user, schema=SCHEMA)

    # Pré-remplit la liste des chapitres dans l'état (statut "pending").
    chapters: list[Chapter] = [
        {
            "index": ch["index"],
            "title": ch["title"],
            "content": "",
            "word_count": 0,
            "status": "pending",
            "editor_notes": "",
        }
        for ch in sorted(outline.get("chapters", []), key=lambda c: c["index"])
    ]

    return {
        "outline": outline,
        "chapters": chapters,
        "stage": "writing",
        **log("outline", f"Plan de {len(chapters)} chapitres : {outline.get('working_title', '?')}"),
    }
