"""Editor & Quality Agent — applique les 8 contrôles qualité, renvoie au Writer si besoin."""

from __future__ import annotations

from ..book_state import BookState, log
from ..brand import QUALITY_TESTS
from ..config import get_settings
from ..prompts import editor as prompt
from .base import compose_system, llm

# Schéma : un verdict par test + consignes de réécriture si échec.
_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "test_id": {"type": "string"},
                    "passed": {"type": "boolean"},
                    "notes": {"type": "string"},
                },
                "required": ["test_id", "passed", "notes"],
            },
        },
        "rewrite_instructions": {"type": "string"},
    },
    "required": ["verdicts", "rewrite_instructions"],
}

_BLOCKING = {t["id"] for t in QUALITY_TESTS if t["blocking"]}


def _tests_block() -> str:
    lines = []
    for t in QUALITY_TESTS:
        flag = "BLOQUANT" if t["blocking"] else "indicatif"
        lines.append(f"- [{t['id']}] {t['label']} ({flag}) : {t['description']}")
    return "\n".join(lines)


def _next_drafted(chapters: list[dict]) -> dict | None:
    for ch in chapters:
        if ch["status"] == "drafted":
            return ch
    return None


def editor_agent(state: BookState) -> dict:
    settings = get_settings()
    chapters = [dict(c) for c in state.get("chapters", [])]
    target = _next_drafted(chapters)
    if target is None:
        return {**log("editor", "Aucun chapitre à contrôler.")}

    system = compose_system(prompt.SYSTEM.format(tests_block=_tests_block()), state=state)
    user = (
        f"Chapitre {target['index']} : {target['title']}\n\n"
        f"## Texte à contrôler\n{target['content']}\n\n"
        "Applique les 8 contrôles qualité et rends un verdict par test "
        "(utilise exactement les `test_id` fournis). Si des tests bloquants échouent, "
        "fournis des consignes de réécriture concrètes."
    )
    result = llm().structured(system=system, user=user, schema=_SCHEMA)

    verdicts = result.get("verdicts", [])
    failed_blocking = [
        v for v in verdicts if v["test_id"] in _BLOCKING and not v.get("passed", False)
    ]
    quality_check = {
        "chapter_index": target["index"],
        "passed": not failed_blocking,
        "verdicts": verdicts,
    }

    if not failed_blocking:
        # Chapitre validé.
        target["status"] = "edited"
        target["editor_notes"] = ""
        msg = f"Chapitre {target['index']} validé (8/8 contrôles bloquants OK)."
        return {
            "chapters": chapters,
            "quality_checks": [quality_check],
            **log("editor", msg),
        }

    # Échec sur tests bloquants.
    if target.get("revisions", 0) < settings.max_revisions:
        # Renvoi au Writer pour réécriture (quota compté PAR chapitre).
        target["status"] = "pending"
        target["revisions"] = target.get("revisions", 0) + 1
        target["editor_notes"] = result.get("rewrite_instructions", "") or (
            "Échecs : " + ", ".join(v["test_id"] for v in failed_blocking)
        )
        failing = ", ".join(v["test_id"] for v in failed_blocking)
        return {
            "chapters": chapters,
            "quality_checks": [quality_check],
            "revision_count": state.get("revision_count", 0) + 1,
            **log("editor", f"Chapitre {target['index']} REFUSÉ ({failing}). "
                            f"Réécriture {target['revisions']}/{settings.max_revisions} demandée."),
        }

    # Plafond de réécritures atteint : on escalade (qualité > volume → on signale fort).
    target["status"] = "edited"
    target["editor_notes"] = "ESCALADE QUALITÉ : échecs persistants — " + result.get(
        "rewrite_instructions", ""
    )
    failing = ", ".join(v["test_id"] for v in failed_blocking)
    return {
        "chapters": chapters,
        "quality_checks": [quality_check],
        "errors": [
            f"Chapitre {target['index']} : échecs qualité persistants après "
            f"{settings.max_revisions} réécritures ({failing}). Validé sous réserve — "
            "revue humaine recommandée."
        ],
        **log("editor", f"Chapitre {target['index']} : plafond de réécritures atteint → escalade."),
    }
