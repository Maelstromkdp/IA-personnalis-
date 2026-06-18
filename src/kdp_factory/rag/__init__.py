"""Couche RAG (Retrieval-Augmented Generation).

Aujourd'hui désactivée par défaut. L'objectif est de pouvoir, plus tard, injecter
dans les agents (surtout Writer et Editor) :
- des extraits de **vos livres précédents** (cohérence, réutilisation d'idées) ;
- des échantillons de **votre style d'écriture** (ton, vocabulaire, rythme).

L'interface `Retriever` est volontairement minimale pour que l'on puisse brancher
n'importe quel backend (Chroma, pgvector, etc.) sans toucher aux agents.
"""

from .retriever import Retriever, NullRetriever, get_retriever

__all__ = ["Retriever", "NullRetriever", "get_retriever"]
