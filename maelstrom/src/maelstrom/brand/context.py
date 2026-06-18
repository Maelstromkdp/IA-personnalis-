"""Assemble le contexte de marque injecté dans le prompt système de chaque agent."""

from __future__ import annotations

from .maelstrom import brand_bible
from .transcreation import transcreation_protocol


def full_brand_context() -> str:
    """Contexte de marque commun à TOUS les agents (toujours injecté)."""
    return (
        brand_bible()
        + "\n\n# RAPPEL PRIORITAIRE\n"
        + "La règle ZÉRO SPOILER prime sur toute autre considération. En cas de doute, "
        "ne révèle rien. Qualité éditoriale > volume : mieux vaut refuser que produire "
        "du médiocre ou du non conforme."
    )


def transcreation_context() -> str:
    """Contexte additionnel injecté uniquement en mode transcréation."""
    return transcreation_protocol()
