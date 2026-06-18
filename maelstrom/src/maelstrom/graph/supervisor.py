"""Superviseur / Orchestrateur.

Ne produit aucun contenu : il lit l'état (mode + étape + avancement des chapitres)
et décide quel agent agit ensuite. Toute la logique de flux est ici — on peut
réordonner le pipeline ou ajouter une étape sans toucher aux agents.

Gère les deux modes :
- création       : research → outline → (writer ⇄ editor) → formatting → marketing
- transcréation  : outline(segmentation) → (writer ⇄ editor) → formatting → marketing
"""

from __future__ import annotations

from langgraph.graph import END

from ..book_state import BookState, log

RESEARCH = "market_research"
OUTLINE = "outline"
WRITER = "writer"
EDITOR = "editor"
FORMATTING = "formatting"
MARKETING = "marketing"


def _has_status(state: BookState, status: str) -> bool:
    return any(c["status"] == status for c in state.get("chapters", []))


def decide_next(state: BookState) -> str:
    """Fonction pure de routage : renvoie le nom du prochain nœud (ou END)."""
    stage = state.get("stage", "research")

    if stage == "research":
        return RESEARCH
    if stage == "outline":
        return OUTLINE
    if stage in ("writing", "editing"):
        # Boucle qualité pilotée par l'état : écrire/réécrire puis contrôler.
        if _has_status(state, "pending"):
            return WRITER
        if _has_status(state, "drafted"):
            return EDITOR
        return FORMATTING  # tous les chapitres validés
    if stage == "formatting":
        return FORMATTING
    if stage == "marketing":
        return MARKETING
    return END


def supervisor(state: BookState) -> dict:
    """Nœud superviseur : calcule la destination et l'inscrit dans l'état."""
    nxt = decide_next(state)

    stage_label = state.get("stage")
    if nxt == EDITOR:
        stage_label = "editing"
    elif nxt == WRITER and state.get("stage") == "editing":
        stage_label = "writing"  # retour en rédaction (réécriture)
    elif nxt == FORMATTING:
        stage_label = "formatting"

    update: dict = {"next_agent": nxt}
    if stage_label != state.get("stage"):
        update["stage"] = stage_label
    update.update(log("supervisor", "→ " + ("FIN" if nxt == END else nxt)))
    return update


def route(state: BookState) -> str:
    """Lue par les arêtes conditionnelles : renvoie la décision du superviseur."""
    return state.get("next_agent", END)
