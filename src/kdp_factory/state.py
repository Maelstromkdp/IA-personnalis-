"""État partagé du graphe — le « livre en cours » qui circule entre les agents.

C'est le **canal de communication unique** : chaque agent lit ce dont il a besoin
dans le `BookState` et y écrit son résultat. Le superviseur lit `stage` /
`next_agent` pour router. Aucun agent n'appelle directement un autre agent —
toute la coordination passe par cet état, ce qui rend le système modulaire et
facile à faire évoluer.

LangGraph fusionne les mises à jour : un nœud renvoie un dict partiel, fusionné
dans l'état. Pour les champs « liste à accumuler » (messages, journal),
on utilise un réducteur `operator.add`.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, Literal, TypedDict

# --------------------------------------------------------------------------- #
# Énumérations de pilotage
# --------------------------------------------------------------------------- #

Stage = Literal[
    "market_research",
    "outline",
    "writing",
    "editing",
    "formatting",
    "marketing",
    "done",
]

Market = Literal["FR", "UK"]


# --------------------------------------------------------------------------- #
# Sous-structures métier
# --------------------------------------------------------------------------- #


class Keyword(TypedDict):
    """Mot-clé Amazon avec estimation qualitative."""

    term: str
    intent: str  # ex. "transactionnel", "informationnel"
    competition: str  # "faible" | "moyenne" | "forte"
    relevance: str  # justification courte


class Competitor(TypedDict):
    title: str
    angle: str  # positionnement du concurrent
    weakness: str  # faille à exploiter


class MarketResearch(TypedDict):
    """Sortie du Market Research Agent."""

    niche: str
    market: Market
    audience: str
    rationale: str
    keywords: list[Keyword]
    competitors: list[Competitor]
    suggested_categories: list[str]
    angle: str  # angle différenciant recommandé pour le livre


class ChapterPlan(TypedDict):
    """Un chapitre tel que défini par le plan (avant rédaction)."""

    index: int
    title: str
    summary: str  # ce que le chapitre doit couvrir
    key_points: list[str]
    target_words: int


class Outline(TypedDict):
    """Sortie de l'Outline & Structure Agent."""

    working_title: str
    promise: str  # promesse / transformation pour le lecteur
    chapters: list[ChapterPlan]
    front_matter: list[str]  # ex. ["Page de titre", "Avant-propos"]
    back_matter: list[str]  # ex. ["À propos de l'auteur", "Autres livres"]


class Chapter(TypedDict):
    """Un chapitre rédigé (rempli par le Writer, raffiné par l'Editor)."""

    index: int
    title: str
    content: str  # Markdown
    word_count: int
    status: Literal["pending", "drafted", "edited"]
    editor_notes: str  # remarques laissées par l'Editor


class Marketing(TypedDict):
    """Sortie du Marketing Amazon Agent."""

    title: str
    subtitle: str
    description_html: str  # description produit (HTML autorisé par KDP)
    keywords: list[str]  # 7 mots-clés backend
    categories: list[str]  # catégories BISAC / chemins Amazon
    author_bio: str
    a_plus_content: list[str]  # modules A+ Content suggérés


# --------------------------------------------------------------------------- #
# Entrée fournie par l'utilisateur
# --------------------------------------------------------------------------- #


class BookBrief(TypedDict, total=False):
    """Brief minimal pour lancer la production d'un livre."""

    topic: str  # sujet / idée de départ (obligatoire)
    market: Market  # "FR" ou "UK"
    language: str  # "fr" ou "en"
    style: str  # description du style d'écriture souhaité
    target_chapters: int  # nombre de chapitres visé (indicatif)
    constraints: str  # contraintes libres (ton, longueur, public...)


# --------------------------------------------------------------------------- #
# État global
# --------------------------------------------------------------------------- #


class LogEntry(TypedDict):
    agent: str
    message: str


class BookState(TypedDict, total=False):
    """État complet d'un livre en cours de production."""

    # --- Entrée -----------------------------------------------------------
    brief: BookBrief

    # --- Artefacts produits par le pipeline -------------------------------
    research: MarketResearch
    outline: Outline
    chapters: list[Chapter]
    manuscript_md: str  # manuscrit final formaté (Markdown structuré)
    export_instructions: str  # consignes d'export Kindle (KDP)
    marketing: Marketing

    # --- Pilotage / coordination ------------------------------------------
    stage: Stage  # étape courante (lue par le superviseur)
    next_agent: str  # destination décidée par le superviseur (routage)
    revision_count: int  # garde-fou anti-boucle pour l'édition
    rag_context: str  # contexte injecté par le RAG (style, livres passés)

    # --- Observabilité (champs accumulés via réducteur) -------------------
    log: Annotated[list[LogEntry], operator.add]
    errors: Annotated[list[str], operator.add]


def new_state(brief: BookBrief) -> BookState:
    """Construit un état initial propre à partir d'un brief utilisateur."""
    brief.setdefault("market", "FR")
    brief.setdefault("language", "fr" if brief.get("market", "FR") == "FR" else "en")
    return {
        "brief": brief,
        "chapters": [],
        "stage": "market_research",
        "revision_count": 0,
        "rag_context": "",
        "log": [],
        "errors": [],
    }


def log(agent: str, message: str) -> dict[str, Any]:
    """Helper pour qu'un agent ajoute une ligne au journal partagé."""
    return {"log": [{"agent": agent, "message": message}]}
