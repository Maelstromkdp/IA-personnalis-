"""Writer Agent — rédige/transcrée le prochain chapitre (et réécrit sur demande de l'Editor)."""

from __future__ import annotations

import json

from ..book_state import BookState, log
from ..prompts import writer as prompt
from .base import compose_system, llm


def _next_pending(chapters: list[dict]) -> dict | None:
    for ch in chapters:
        if ch["status"] == "pending":
            return ch
    return None


def _written_summary(chapters: list[dict]) -> str:
    done = [c for c in chapters if c["status"] != "pending"]
    if not done:
        return "(aucun chapitre encore rédigé)"
    return "\n".join(f"- Ch.{c['index']} « {c['title']} » ({c['word_count']} mots)" for c in done)


def writer_agent(state: BookState) -> dict:
    chapters = [dict(c) for c in state.get("chapters", [])]
    target = _next_pending(chapters)
    if target is None:
        return {**log("writer", "Aucun chapitre en attente.")}

    outline = state.get("outline", {})
    plan = next(
        (c for c in outline.get("chapters", []) if c["index"] == target["index"]),
        {},
    )
    is_transcreation = state.get("mode") == "transcreation"

    role = prompt.TRANSCREATION_SYSTEM if is_transcreation else prompt.CREATION_SYSTEM
    system = compose_system(role.format(chapter_title=target["title"]), state=state)

    # Consignes de réécriture éventuelles laissées par l'Editor.
    rewrite_note = ""
    if target.get("editor_notes"):
        rewrite_note = (
            "\n## Consignes de réécriture (Editor) — à corriger impérativement\n"
            + target["editor_notes"]
            + "\n"
        )

    if is_transcreation:
        user = (
            f"## Chapitre {target['index']} : {target['title']}\n"
            f"{rewrite_note}"
            "## Texte source (français) à transcréer en anglais US\n"
            "---\n" + plan.get("source_text", "") + "\n---\n\n"
            "Transcrée ce chapitre selon le Protocole de Transcréation. Renvoie uniquement le Markdown."
        )
    else:
        user = (
            f"## Concept\n{json.dumps(state.get('book_concept', {}), ensure_ascii=False)}\n\n"
            f"## Logline\n{outline.get('logline', '')}\n\n"
            f"## Chapitres déjà écrits\n{_written_summary(chapters)}\n\n"
            f"## Chapitre à écrire (n°{target['index']} : {target['title']})\n"
            f"Battements : {json.dumps(plan.get('beats', []), ensure_ascii=False)}\n"
            f"{rewrite_note}\n"
            "Rédige ce chapitre. Renvoie uniquement le Markdown."
        )

    content = llm().write(system=system, user=user)
    target["content"] = content
    target["word_count"] = len(content.split())
    target["status"] = "drafted"
    target["editor_notes"] = ""  # consignes consommées

    action = "transcréé" if is_transcreation else "rédigé"
    remaining = sum(1 for c in chapters if c["status"] == "pending")
    return {
        "chapters": chapters,
        "current_chapter": target["index"],
        **log("writer", f"Chapitre {target['index']} {action} ({target['word_count']} mots). "
                         f"En attente : {remaining}."),
    }
