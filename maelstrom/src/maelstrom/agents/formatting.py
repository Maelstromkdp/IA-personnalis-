"""Formatting & Kindle Agent — assemble le manuscrit final + consignes d'export."""

from __future__ import annotations

from ..book_state import BookState, log
from ..prompts import formatting as prompt
from .base import compose_system, llm

_EXPORT_SEP = "---EXPORT---"


def formatting_agent(state: BookState) -> dict:
    chapters = sorted(state.get("chapters", []), key=lambda c: c["index"])
    concept = state.get("book_concept", {})
    title = concept.get("working_title", "(titre provisoire)")

    chapters_block = "\n\n".join(
        f"<!-- Chapitre {c['index']} -->\n{c['content']}" for c in chapters
    )
    system = compose_system(prompt.SYSTEM, state=state)
    user = (
        f"Titre de travail : {title}\n"
        f"Marque : MAELSTRÖM (sans visage, jamais de nom d'auteur)\n\n"
        f"## Chapitres édités (dans l'ordre)\n{chapters_block}\n\n"
        f"Assemble le manuscrit Markdown final, puis `{_EXPORT_SEP}`, puis les consignes d'export Kindle."
    )
    result = llm().write(system=system, user=user)

    if _EXPORT_SEP in result:
        manuscript, export = result.split(_EXPORT_SEP, 1)
    else:
        manuscript, export = result, ""

    return {
        "full_manuscript": manuscript.strip(),
        "export_instructions": export.strip(),
        "stage": "marketing",
        **log("formatting", f"Manuscrit assemblé ({len(manuscript.split())} mots)."),
    }
