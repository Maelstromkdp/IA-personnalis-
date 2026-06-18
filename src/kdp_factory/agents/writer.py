"""Writer Agent — rédige les chapitres un par un.

Écrit le prochain chapitre `pending`, puis rend la main au superviseur. Le
superviseur le rappelle tant qu'il reste des chapitres à rédiger : c'est une
boucle pilotée par l'état (pas d'appel direct entre agents).
"""

from __future__ import annotations

import json

from ..prompts import writer as prompt
from ..state import BookState, log
from .base import brief_block, llm, market_of, rag_block, style_of


def _next_pending(chapters: list[dict]) -> dict | None:
    for ch in chapters:
        if ch["status"] == "pending":
            return ch
    return None


def _already_written_summary(chapters: list[dict]) -> str:
    done = [c for c in chapters if c["status"] != "pending"]
    if not done:
        return "(aucun chapitre rédigé pour l'instant)"
    return "\n".join(f"- Ch.{c['index']} « {c['title']} » : {c['word_count']} mots" for c in done)


def writer_agent(state: BookState) -> dict:
    chapters = [dict(c) for c in state.get("chapters", [])]  # copie mutable
    outline = state.get("outline", {})
    target = _next_pending(chapters)
    if target is None:
        # Rien à écrire (sécurité) — on laisse le superviseur router.
        return {**log("writer", "Aucun chapitre en attente.")}

    plan = next(
        (c for c in outline.get("chapters", []) if c["index"] == target["index"]),
        {},
    )

    system = prompt.SYSTEM.format(market=market_of(state), chapter_title=target["title"])
    user = (
        f"{brief_block(state)}\n"
        f"Style à respecter : {style_of(state)}\n"
        f"{rag_block(state, kind='style')}"
        f"{rag_block(state, kind='reference')}\n"
        f"## Titre du livre\n{outline.get('working_title', '')}\n"
        f"## Promesse au lecteur\n{outline.get('promise', '')}\n\n"
        f"## Chapitres déjà rédigés\n{_already_written_summary(chapters)}\n\n"
        f"## Chapitre à rédiger maintenant (n°{target['index']})\n"
        f"Titre : {target['title']}\n"
        f"Plan du chapitre :\n{json.dumps(plan, ensure_ascii=False, indent=2)}\n\n"
        "Rédige ce chapitre en Markdown, en respectant le plan, le style et la longueur cible."
    )

    content = llm().write(system=system, user=user)
    target["content"] = content
    target["word_count"] = len(content.split())
    target["status"] = "drafted"

    remaining = sum(1 for c in chapters if c["status"] == "pending")
    return {
        "chapters": chapters,
        **log(
            "writer",
            f"Chapitre {target['index']} rédigé ({target['word_count']} mots). "
            f"Restants : {remaining}.",
        ),
    }
