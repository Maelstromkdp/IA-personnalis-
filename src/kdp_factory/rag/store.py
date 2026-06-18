"""Backend RAG concret — SQUELETTE à compléter quand vous activerez le RAG.

Ce fichier n'est importé que si `KDP_RAG_ENABLED=true`. Il documente l'approche
recommandée sans imposer de dépendance lourde tant que vous n'en avez pas besoin.

Plan d'implémentation suggéré (Chroma) :
- `ingest(paths)` : découper vos livres .md/.txt en chunks (~500–1000 tokens),
  calculer les embeddings, stocker dans deux collections : `style` et `reference`.
- `style_context` / `reference_context` : recherche par similarité (top-k) puis
  concaténation des extraits, prête à injecter dans le prompt des agents.

Pensez à utiliser le même modèle d'embedding pour l'ingestion et la requête.
"""

from __future__ import annotations


class ChromaRetriever:
    """Implémentation Chroma (à compléter)."""

    def __init__(self, directory: str) -> None:
        self._directory = directory
        # import chromadb ; self._client = chromadb.PersistentClient(path=directory)
        # self._style = self._client.get_or_create_collection("style")
        # self._reference = self._client.get_or_create_collection("reference")
        raise NotImplementedError(
            "RAG activé mais non implémenté. Renseignez ChromaRetriever dans rag/store.py "
            "ou laissez KDP_RAG_ENABLED=false."
        )

    # --- Ingestion (à appeler hors ligne, p.ex. via un script) -------------
    def ingest(self, paths: list[str]) -> None:  # pragma: no cover - squelette
        raise NotImplementedError

    # --- Requêtes utilisées par les agents ---------------------------------
    def style_context(self, query: str, *, k: int = 4) -> str:  # pragma: no cover
        raise NotImplementedError

    def reference_context(self, query: str, *, k: int = 4) -> str:  # pragma: no cover
        raise NotImplementedError
