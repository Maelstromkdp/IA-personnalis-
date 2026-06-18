"""Recherche web — abstraction au-dessus du backend choisi.

Par défaut : recherche web NATIVE de Claude (aucune dépendance, aucune clé en
plus). Alternative : Tavily (`MAELSTROM_WEB_SEARCH=tavily` + TAVILY_API_KEY).

Le Market Research Agent appelle simplement `web_search(query, llm=...)` et reçoit
une synthèse textuelle, sans connaître le backend.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..config import get_settings

if TYPE_CHECKING:
    from ..llm import LLM


def web_search(query: str, *, llm: "LLM", system: str = "") -> str:
    """Effectue une recherche et renvoie une synthèse textuelle.

    - backend "claude" : utilise l'outil serveur natif via `llm.research`.
    - backend "tavily"  : interroge l'API Tavily puis fait synthétiser par le LLM.
    """
    settings = get_settings()
    sys = system or "Tu es un analyste de marché. Recherche et synthétise des faits récents et utiles."

    if settings.web_search == "tavily":
        return _tavily_search(query, llm=llm, system=sys)

    return llm.research(system=sys, user=query)


def _tavily_search(query: str, *, llm: "LLM", system: str) -> str:  # pragma: no cover
    """Branche Tavily si configuré ; sinon, dégrade vers la recherche native."""
    try:
        import os

        from tavily import TavilyClient

        client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        results = client.search(query, max_results=8)
        findings = "\n\n".join(
            f"- {r.get('title', '')}\n  {r.get('content', '')}\n  ({r.get('url', '')})"
            for r in results.get("results", [])
        )
        return llm.write(
            system=system,
            user=f"Synthétise ces résultats de recherche pour la requête « {query} » :\n\n{findings}",
            effort="medium",
        )
    except Exception:
        # Tavily indisponible/mal configuré : on retombe proprement sur le natif.
        return llm.research(system=system, user=query)
