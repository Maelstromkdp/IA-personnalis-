"""Editor & Style Agent — révise chaque chapitre rédigé."""

from __future__ import annotations

from ..prompts import editor as prompt
from ..state import BookState, log
from .base import llm, market_of, rag_block, style_of

_NOTES_SEP = "---NOTES---"


def _next_drafted(chapters: list[dict]) -> dict | None:
    for ch in chapters:
        if ch["status"] == "drafted":
            return ch
    return None


def editor_agent(state: BookState) -> dict:
    chapters = [dict(c) for c in state.get("chapters", [])]
    target = _next_drafted(chapters)
    if target is None:
        return {**log("editor", "Aucun chapitre à éditer.")}

    system = prompt.SYSTEM.format(market=market_of(state))
    user = (
        f"Style cible du livre : {style_of(state)}\n"
        f"{rag_block(state, kind='style')}\n"
        f"## Chapitre à réviser\n{target['content']}\n\n"
        f"Renvoie le chapitre révisé, puis `{_NOTES_SEP}`, puis tes notes éditoriales."
    )
    result = llm().write(system=system, user=user)

    if _NOTES_SEP in result:
        revised, notes = result.split(_NOTES_SEP, 1)
    else:
        revised, notes = result, ""

    target["content"] = revised.strip()
    target["word_count"] = len(revised.split())
    target["editor_notes"] = notes.strip()
    target["status"] = "edited"

    remaining = sum(1 for c in chapters if c["status"] == "drafted")
    return {
        "chapters": chapters,
        **log("editor", f"Chapitre {target['index']} édité. Restants : {remaining}."),
    }
