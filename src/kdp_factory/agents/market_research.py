"""Market Research Agent — recherche de niche, concurrence, mots-clés."""

from __future__ import annotations

from ..prompts import market_research as prompt
from ..state import BookState, log
from .base import brief_block, llm, market_of

# Schéma JSON contraint (sortie structurée). Reflète state.MarketResearch.
SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "niche": {"type": "string"},
        "market": {"type": "string", "enum": ["FR", "UK"]},
        "audience": {"type": "string"},
        "rationale": {"type": "string"},
        "angle": {"type": "string"},
        "keywords": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "term": {"type": "string"},
                    "intent": {"type": "string"},
                    "competition": {"type": "string"},
                    "relevance": {"type": "string"},
                },
                "required": ["term", "intent", "competition", "relevance"],
            },
        },
        "competitors": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {"type": "string"},
                    "angle": {"type": "string"},
                    "weakness": {"type": "string"},
                },
                "required": ["title", "angle", "weakness"],
            },
        },
        "suggested_categories": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "niche",
        "market",
        "audience",
        "rationale",
        "angle",
        "keywords",
        "competitors",
        "suggested_categories",
    ],
}


def market_research_agent(state: BookState) -> dict:
    market = market_of(state)
    system = prompt.SYSTEM.format(market=market)
    user = (
        "Réalise la recherche de marché pour le livre suivant.\n\n"
        f"{brief_block(state)}\n\n"
        "Fournis une niche précise, l'audience, des mots-clés Amazon, l'analyse "
        "concurrentielle, des catégories et l'angle différenciant."
    )
    research = llm().structured(system=system, user=user, schema=SCHEMA)
    research.setdefault("market", market)

    return {
        "research": research,
        "stage": "outline",
        **log("market_research", f"Niche retenue : {research.get('niche', '?')}"),
    }
