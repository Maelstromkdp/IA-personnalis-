"""Marketing & Amazon Agent — actifs commerciaux, puis contrôle anti-spoiler obligatoire."""

from __future__ import annotations

import json

from ..book_state import BookState, log
from ..prompts import marketing as prompt
from .base import compose_system, llm, spoiler_guard

_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "title": {"type": "string"},
        "subtitle": {"type": "string"},
        "amazon_description": {"type": "string"},
        "backend_keywords": {"type": "array", "items": {"type": "string"}},
        "frontend_keywords": {"type": "array", "items": {"type": "string"}},
        "categories": {"type": "array", "items": {"type": "string"}},
        "social_hooks": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "tiktok": {"type": "array", "items": {"type": "string"}},
                "instagram": {"type": "array", "items": {"type": "string"}},
                "threads": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["tiktok", "instagram", "threads"],
        },
    },
    "required": [
        "title",
        "subtitle",
        "amazon_description",
        "backend_keywords",
        "frontend_keywords",
        "categories",
        "social_hooks",
    ],
}


def marketing_agent(state: BookState) -> dict:
    system = compose_system(prompt.SYSTEM, state=state)
    concept = state.get("book_concept", {})
    outline = state.get("outline", {})
    user = (
        f"## Concept (peut contenir le twist — NE JAMAIS publier la révélation)\n"
        f"{json.dumps(concept, ensure_ascii=False, indent=2)}\n\n"
        f"## Logline / structure\n{outline.get('logline', outline.get('structure', ''))}\n\n"
        "Produis tous les actifs marketing dans la voix de marque, sans le moindre spoiler."
    )
    assets = llm().structured(system=system, user=user, schema=_SCHEMA)

    # ----- Contrôle anti-spoiler OBLIGATOIRE sur chaque texte public --------
    guard = spoiler_guard()
    # Contexte de l'intrigue (avec twist) fourni au gardien pour qu'il sache quoi protéger.
    context = json.dumps(concept, ensure_ascii=False) + "\n" + json.dumps(
        {"beats": outline.get("beats", [])}, ensure_ascii=False
    )

    flagged: list[str] = []

    def _guard_text(field: str, value: str) -> str:
        safe, verdict = guard.enforce(value, context=context)
        if verdict.get("spoils"):
            flagged.append(f"{field} ({verdict.get('severity')})")
        return safe

    assets["title"] = _guard_text("title", assets.get("title", ""))
    assets["subtitle"] = _guard_text("subtitle", assets.get("subtitle", ""))
    assets["amazon_description"] = _guard_text(
        "amazon_description", assets.get("amazon_description", "")
    )
    hooks = assets.get("social_hooks", {})
    for network in ("tiktok", "instagram", "threads"):
        hooks[network] = [
            _guard_text(f"{network}#{i}", h) for i, h in enumerate(hooks.get(network, []))
        ]
    assets["social_hooks"] = hooks

    assets["spoiler_audit"] = {
        "flagged_fields": flagged,
        "clean": not flagged,
        "note": "Tout champ signalé a été réécrit sans spoiler par le SpoilerGuard.",
    }

    update = {
        "marketing_assets": assets,
        "stage": "done",
        **log(
            "marketing",
            "Actifs marketing générés. "
            + ("Aucun spoiler détecté." if not flagged else f"Corrigés : {', '.join(flagged)}."),
        ),
    }
    if flagged:
        update["errors"] = [f"Spoilers interceptés et corrigés : {', '.join(flagged)}."]
    return update
