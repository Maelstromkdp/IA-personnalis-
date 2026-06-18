"""Superviseur / Orchestrateur.

Cerveau du pipeline : il ne produit aucun contenu, il **décide qui agit ensuite**
en lisant l'état partagé (étape courante + avancement des chapitres). Chaque agent
revient au superviseur après son tour ; le superviseur réévalue et route.

Cela découple totalement les agents les uns des autres et concentre la logique de
flux à un seul endroit — on peut réordonner le pipeline, ajouter une étape ou une
boucle de relecture sans toucher au code des agents.
"""

from __future__ import annotations

from langgraph.graph import END

from .state import BookState, log

# Destinations possibles (noms des nœuds du graphe).
MARKET_RESEARCH = "market_research"
OUTLINE = "outline"
WRITER = "writer"
EDITOR = "editor"
FORMATTING = "formatting"
MARKETING = "marketing"


def _has_status(state: BookState, status: str) -> bool:
    return any(c["status"] == status for c in state.get("chapters", []))


def decide_next(state: BookState) -> str:
    """Pure fonction de routage : renvoie le nom du prochain nœud (ou END)."""
    stage = state.get("stage", "market_research")

    if stage == "market_research":
        return MARKET_RESEARCH
    if stage == "outline":
        return OUTLINE
    if stage in ("writing", "editing"):
        # Boucle pilotée par l'état : rédiger tous les chapitres, puis tous les éditer.
        if _has_status(state, "pending"):
            return WRITER
        if _has_status(state, "drafted"):
            return EDITOR
        return FORMATTING  # tous édités
    if stage == "formatting":
        return FORMATTING
    if stage == "marketing":
        return MARKETING
    return END


def supervisor(state: BookState) -> dict:
    """Nœud superviseur : calcule la prochaine destination et l'inscrit dans l'état."""
    nxt = decide_next(state)

    # Étiquette d'étape lisible pour l'observabilité (n'altère pas le routage).
    stage_label = state.get("stage", "market_research")
    if nxt == EDITOR:
        stage_label = "editing"
    elif nxt == FORMATTING:
        stage_label = "formatting"

    update: dict = {"next_agent": nxt}
    if stage_label != state.get("stage"):
        update["stage"] = stage_label

    dest = "FIN" if nxt == END else nxt
    update.update(log("supervisor", f"→ {dest}"))
    return update


def route(state: BookState) -> str:
    """Fonction utilisée par les arêtes conditionnelles : lit la décision du superviseur."""
    return state.get("next_agent", END)
