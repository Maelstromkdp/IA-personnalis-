"""Helpers partagés par les agents : LLM singleton, RAG, formatage de prompts."""

from __future__ import annotations

from functools import lru_cache

from ..llm import LLM
from ..rag import Retriever, get_retriever
from ..state import BookState


@lru_cache
def llm() -> LLM:
    """Instance LLM partagée (un seul client Anthropic pour tout le process)."""
    return LLM()


@lru_cache
def retriever() -> Retriever:
    """Retriever RAG partagé (NullRetriever tant que le RAG n'est pas activé)."""
    return get_retriever()


def market_of(state: BookState) -> str:
    return state["brief"].get("market", "FR")


def language_label(state: BookState) -> str:
    lang = state["brief"].get("language", "fr")
    return "français" if lang == "fr" else "anglais"


def style_of(state: BookState) -> str:
    return state["brief"].get("style", "clair, professionnel, accessible et engageant")


def brief_block(state: BookState) -> str:
    """Bloc texte récapitulant le brief, injecté dans les prompts utilisateur."""
    b = state["brief"]
    return (
        f"Sujet : {b.get('topic', '(non précisé)')}\n"
        f"Marché : {market_of(state)} (langue : {language_label(state)})\n"
        f"Style souhaité : {style_of(state)}\n"
        f"Contraintes : {b.get('constraints', '(aucune)')}\n"
        f"Chapitres visés : {b.get('target_chapters', '(au choix de l’agent)')}"
    )


def rag_block(state: BookState, *, kind: str = "style") -> str:
    """Récupère un contexte RAG et le formate pour injection (vide si désactivé)."""
    query = state["brief"].get("topic", "")
    if kind == "style":
        ctx = retriever().style_context(query)
        header = "## Échantillons de votre style à imiter"
    else:
        ctx = retriever().reference_context(query)
        header = "## Références issues de vos livres précédents"
    if not ctx.strip():
        return ""
    return f"\n{header}\n{ctx}\n"
