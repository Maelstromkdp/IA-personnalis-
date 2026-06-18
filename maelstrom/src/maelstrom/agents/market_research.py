"""Market Research & Niche Agent — recherche web + concepts MAELSTRÖM."""

from __future__ import annotations

from ..book_state import BookState, log
from ..prompts import market_research as prompt
from ..tools import web_search
from .base import compose_system, llm

CONCEPTS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"},
        "market_keywords": {"type": "array", "items": {"type": "string"}},
        "competitors": {"type": "array", "items": {"type": "string"}},
        "winning_tropes": {"type": "array", "items": {"type": "string"}},
        "concepts": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "working_title": {"type": "string"},
                    "premise": {"type": "string"},
                    "hook": {"type": "string"},
                    "threat": {"type": "string"},
                    "setting": {"type": "string"},
                    "tropes": {"type": "array", "items": {"type": "string"}},
                    "target_keywords": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "working_title",
                    "premise",
                    "hook",
                    "threat",
                    "setting",
                    "tropes",
                    "target_keywords",
                ],
            },
        },
    },
    "required": ["summary", "market_keywords", "competitors", "winning_tropes", "concepts"],
}


def market_research_agent(state: BookState) -> dict:
    seed = state["brief"].get("seed", "")
    lang_market = "amazon.fr (FR)" if state.get("language") == "FR" else "amazon.com / amazon.co.uk (US/UK)"

    # 1) Recherche web (texte + citations) — outil natif Claude par défaut.
    query = (
        f"Marché actuel du thriller psychologique court / domestic noir sur {lang_market} : "
        f"niches porteuses, tropes qui marchent, mots-clés Amazon, auteurs comparables. "
        + (f"Angle de départ : {seed}." if seed else "")
    )
    findings = web_search(query, llm=llm(), system=prompt.RESEARCH_SYSTEM)

    # 2) Synthèse structurée en concepts MAELSTRÖM (sortie JSON, sans outil).
    system = compose_system(prompt.SYNTHESIS_SYSTEM, state=state)
    user = (
        "Synthèse de recherche :\n---\n" + findings + "\n---\n\n"
        + (f"Contrainte de départ : {seed}\n" if seed else "")
        + "Propose des concepts MAELSTRÖM exploitables (prémisse serrure sans spoiler, "
        "menace de proche, tropes, mots-clés)."
    )
    research = llm().structured(system=system, user=user, schema=CONCEPTS_SCHEMA)

    # Choisit le premier concept comme concept de travail (modifiable plus tard).
    concepts = research.get("concepts", [])
    concept = concepts[0] if concepts else {}

    return {
        "research_data": research,
        "book_concept": concept,
        "stage": "outline",
        **log(
            "market_research",
            f"{len(concepts)} concept(s) proposé(s). Retenu : "
            f"« {concept.get('working_title', '?')} »",
        ),
    }
