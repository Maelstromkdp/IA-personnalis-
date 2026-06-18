"""Interface de récupération (RAG) et implémentation neutre par défaut.

Pour activer un vrai RAG plus tard :
1. `pip install "kdp-factory[rag]"` (ajoute chromadb).
2. Implémenter `ChromaRetriever(Retriever)` dans `store.py` (indexation de vos
   livres + échantillons de style, embeddings, recherche par similarité).
3. Mettre `KDP_RAG_ENABLED=true` dans `.env`.

Les agents appellent simplement `retriever.style_context(...)` et
`retriever.reference_context(...)` ; ils ignorent totalement le backend.
"""

from __future__ import annotations

from typing import Protocol

from ..config import get_settings


class Retriever(Protocol):
    """Contrat minimal qu'un backend RAG doit respecter."""

    def style_context(self, query: str, *, k: int = 4) -> str:
        """Extraits illustrant le style d'écriture cible (vos livres)."""
        ...

    def reference_context(self, query: str, *, k: int = 4) -> str:
        """Extraits de référence (faits, passages réutilisables de vos livres)."""
        ...


class NullRetriever:
    """Implémentation par défaut : ne renvoie aucun contexte.

    Permet au reste du système de fonctionner identiquement, RAG activé ou non.
    """

    def style_context(self, query: str, *, k: int = 4) -> str:  # noqa: ARG002
        return ""

    def reference_context(self, query: str, *, k: int = 4) -> str:  # noqa: ARG002
        return ""


def get_retriever() -> Retriever:
    """Fabrique le retriever selon la configuration.

    Tant que le RAG n'est pas activé (ou pas implémenté), renvoie `NullRetriever`.
    """
    settings = get_settings()
    if not settings.rag_enabled:
        return NullRetriever()

    # Branchement futur : importer et instancier le backend réel.
    try:
        from .store import ChromaRetriever  # import paresseux (dépendance optionnelle)

        return ChromaRetriever(directory=settings.rag_dir)
    except Exception:
        # En cas de RAG mal configuré, on dégrade proprement plutôt que de planter.
        return NullRetriever()
