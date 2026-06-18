"""Formatting & Kindle Agent — assemble le manuscrit final + consignes d'export."""

from __future__ import annotations

import json

from ..prompts import formatting as prompt
from ..state import BookState, log
from .base import llm, market_of

_EXPORT_SEP = "---EXPORT---"


def formatting_agent(state: BookState) -> dict:
    outline = state.get("outline", {})
    chapters = sorted(state.get("chapters", []), key=lambda c: c["index"])

    # On fournit à l'agent le contenu édité de chaque chapitre + les éléments de
    # structure. L'agent produit un manuscrit Markdown unique et propre.
    chapters_block = "\n\n".join(
        f"<!-- Chapitre {c['index']} -->\n{c['content']}" for c in chapters
    )
    system = prompt.SYSTEM.format(market=market_of(state))
    user = (
        f"## Métadonnées du livre\n"
        f"Titre de travail : {outline.get('working_title', '')}\n"
        f"Promesse : {outline.get('promise', '')}\n"
        f"Front matter prévu : {json.dumps(outline.get('front_matter', []), ensure_ascii=False)}\n"
        f"Back matter prévu : {json.dumps(outline.get('back_matter', []), ensure_ascii=False)}\n\n"
        f"## Chapitres édités (dans l'ordre)\n{chapters_block}\n\n"
        f"Assemble le manuscrit Markdown final, puis `{_EXPORT_SEP}`, puis les consignes d'export Kindle."
    )
    result = llm().write(system=system, user=user)

    if _EXPORT_SEP in result:
        manuscript, export = result.split(_EXPORT_SEP, 1)
    else:
        manuscript, export = result, ""

    return {
        "manuscript_md": manuscript.strip(),
        "export_instructions": export.strip(),
        "stage": "marketing",
        **log("formatting", f"Manuscrit assemblé ({len(manuscript.split())} mots)."),
    }
