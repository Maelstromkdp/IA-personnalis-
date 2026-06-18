"""État partagé du pipeline MAELSTRÖM — le « livre en cours ».

Unique canal de communication entre agents : chaque agent lit ce dont il a besoin
et écrit son résultat. Le superviseur lit `stage` / `mode` / `next_agent` pour
router. Aucun agent n'appelle directement un autre.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, Literal, TypedDict

# --------------------------------------------------------------------------- #
# Pilotage
# --------------------------------------------------------------------------- #
Language = Literal["FR", "EN"]
Mode = Literal["creation", "transcreation"]

Stage = Literal[
    "research",     # recherche marché/niche (création uniquement)
    "outline",      # structuration (création) ou segmentation (transcréation)
    "writing",      # rédaction / transcréation chapitre par chapitre
    "editing",      # contrôle qualité chapitre par chapitre
    "formatting",   # assemblage Kindle
    "marketing",    # actifs commerciaux sans spoiler
    "done",
]


# --------------------------------------------------------------------------- #
# Sous-structures métier
# --------------------------------------------------------------------------- #
class BookConcept(TypedDict, total=False):
    """Concept du livre (sortie du Research Agent, ou fourni en entrée)."""

    premise: str           # prémisse « serrure » (sans spoiler)
    hook: str              # accroche centrale
    threat: str            # qui est le proche menaçant (interne, peut spoiler — NON public)
    setting: str
    tropes: list[str]      # tropes thriller exploités
    target_keywords: list[str]
    working_title: str


class ResearchData(TypedDict, total=False):
    """Données de marché brutes + concepts proposés."""

    summary: str                       # synthèse de la recherche web
    market_keywords: list[str]
    competitors: list[str]
    winning_tropes: list[str]
    concepts: list[BookConcept]        # plusieurs concepts proposés


class Beat(TypedDict):
    """Un battement / scène du plan."""

    act: int
    title: str
    summary: str          # ce qui se passe (peut contenir le twist — interne, NON public)
    tension_goal: str     # rôle dans la montée de tension


class ChapterOutline(TypedDict, total=False):
    index: int
    title: str
    beats: list[str]
    source_text: str      # texte original FR (mode transcréation uniquement)


class Outline(TypedDict, total=False):
    structure: str                    # ex. "3 actes" / "5 actes"
    logline: str
    beats: list[Beat]
    chapters: list[ChapterOutline]


class Chapter(TypedDict):
    index: int
    title: str
    content: str
    word_count: int
    status: Literal["pending", "drafted", "edited"]
    editor_notes: str
    revisions: int  # nombre de réécritures déjà demandées pour CE chapitre


class QualityCheck(TypedDict):
    """Résultat des 8 contrôles qualité pour un chapitre."""

    chapter_index: int
    passed: bool                      # tous les tests bloquants OK ?
    verdicts: list[dict[str, Any]]    # [{test_id, passed, notes}, ...]


class MarketingAssets(TypedDict, total=False):
    title: str
    subtitle: str
    amazon_description: str           # HTML simple autorisé par KDP
    backend_keywords: list[str]       # 7 mots-clés backend
    frontend_keywords: list[str]
    categories: list[str]
    social_hooks: dict[str, list[str]]  # {"tiktok": [...], "instagram": [...], "threads": [...]}
    spoiler_audit: dict[str, Any]     # verdict final du SpoilerGuard


# --------------------------------------------------------------------------- #
# Entrée
# --------------------------------------------------------------------------- #
class Brief(TypedDict, total=False):
    """Brief d'entrée."""

    mode: Mode
    language: Language                # langue de SORTIE
    # Mode création :
    seed: str                         # idée / contrainte de départ (optionnel)
    target_words: int                 # cible (~13000–20000)
    # Mode transcréation :
    source_path: str                  # chemin du manuscrit FR à transcréer
    source_text: str                  # ou texte fourni directement


# --------------------------------------------------------------------------- #
# État global
# --------------------------------------------------------------------------- #
class LogEntry(TypedDict):
    agent: str
    message: str


class BookState(TypedDict, total=False):
    # Entrée
    brief: Brief
    mode: Mode
    language: Language

    # Artefacts (noms demandés dans le cahier des charges)
    research_data: ResearchData
    book_concept: BookConcept
    outline: Outline
    chapters: list[Chapter]
    current_chapter: int              # index du chapitre en cours de traitement
    full_manuscript: str              # manuscrit final formaté (Markdown)
    export_instructions: str
    marketing_assets: MarketingAssets
    quality_checks: list[QualityCheck]

    # Pilotage
    stage: Stage
    next_agent: str
    revision_count: int               # réécritures cumulées (garde-fou)

    # Observabilité
    log: Annotated[list[LogEntry], operator.add]
    errors: Annotated[list[str], operator.add]


def new_state(brief: Brief) -> BookState:
    """Construit un état initial propre à partir d'un brief."""
    mode: Mode = brief.get("mode", "creation")
    language: Language = brief.get("language", "FR")
    # En transcréation, la sortie est par défaut l'anglais.
    if mode == "transcreation":
        language = brief.get("language", "EN")

    first_stage: Stage = "research" if mode == "creation" else "outline"
    return {
        "brief": brief,
        "mode": mode,
        "language": language,
        "chapters": [],
        "current_chapter": 0,
        "quality_checks": [],
        "stage": first_stage,
        "revision_count": 0,
        "log": [],
        "errors": [],
    }


def log(agent: str, message: str) -> dict[str, Any]:
    """Helper : ajoute une ligne au journal partagé."""
    return {"log": [{"agent": agent, "message": message}]}
