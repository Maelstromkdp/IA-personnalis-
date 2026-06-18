"""Outline & Structure Agent — structuration (création) / segmentation (transcréation)."""

from __future__ import annotations

import json

from ..book_state import BookState, Chapter, log
from ..prompts import outline as prompt
from ..tools import read_text
from .base import compose_system, llm

CREATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "structure": {"type": "string"},
        "logline": {"type": "string"},
        "beats": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "act": {"type": "integer"},
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "tension_goal": {"type": "string"},
                },
                "required": ["act", "title", "summary", "tension_goal"],
            },
        },
        "chapters": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "index": {"type": "integer"},
                    "title": {"type": "string"},
                    "beats": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["index", "title", "beats"],
            },
        },
    },
    "required": ["structure", "logline", "beats", "chapters"],
}

TRANSCREATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "chapters": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "index": {"type": "integer"},
                    "title": {"type": "string"},
                    "beats": {"type": "array", "items": {"type": "string"}},
                    "source_text": {"type": "string"},
                },
                "required": ["index", "title", "beats", "source_text"],
            },
        }
    },
    "required": ["chapters"],
}


def _chapter_slots(chapters_outline: list[dict]) -> list[Chapter]:
    return [
        {
            "index": ch["index"],
            "title": ch["title"],
            "content": "",
            "word_count": 0,
            "status": "pending",
            "editor_notes": "",
            "revisions": 0,
        }
        for ch in sorted(chapters_outline, key=lambda c: c["index"])
    ]


def _load_source(state: BookState) -> str:
    brief = state["brief"]
    if brief.get("source_text"):
        return brief["source_text"]
    if brief.get("source_path"):
        return read_text(brief["source_path"])
    return ""


def outline_agent(state: BookState) -> dict:
    if state.get("mode") == "transcreation":
        return _transcreation_outline(state)
    return _creation_outline(state)


def _creation_outline(state: BookState) -> dict:
    system = compose_system(prompt.CREATION_SYSTEM, state=state)
    concept = state.get("book_concept", {})
    user = (
        "Concept du livre :\n"
        + json.dumps(concept, ensure_ascii=False, indent=2)
        + "\n\nConstruis l'outline détaillé (structure en actes, logline, beats, chapitres)."
    )
    outline = llm().structured(system=system, user=user, schema=CREATION_SCHEMA)
    chapters = _chapter_slots(outline.get("chapters", []))
    return {
        "outline": outline,
        "chapters": chapters,
        "stage": "writing",
        **log("outline", f"Outline {outline.get('structure', '?')} — {len(chapters)} chapitres."),
    }


def _transcreation_outline(state: BookState) -> dict:
    source = _load_source(state)
    if not source.strip():
        return {
            "errors": ["Transcréation : aucun manuscrit source fourni (source_text/source_path)."],
            "stage": "done",
            **log("outline", "ERREUR : manuscrit source manquant."),
        }

    system = compose_system(prompt.TRANSCREATION_SYSTEM, state=state)
    user = (
        "Manuscrit source (français) à découper en chapitres, en recopiant le texte "
        "intégral de chaque chapitre dans `source_text` :\n---\n" + source + "\n---"
    )
    # Manuscrit potentiellement long → on autorise une sortie ample.
    outline = llm().structured(
        system=system, user=user, schema=TRANSCREATION_SCHEMA, max_tokens=32000
    )

    chapters = _chapter_slots(outline.get("chapters", []))
    # On conserve le texte source dans l'outline pour que le Writer le transcrée.
    return {
        "outline": {"structure": "transcréation", "chapters": outline.get("chapters", [])},
        "chapters": chapters,
        "stage": "writing",
        **log("outline", f"Manuscrit source segmenté en {len(chapters)} chapitres."),
    }
