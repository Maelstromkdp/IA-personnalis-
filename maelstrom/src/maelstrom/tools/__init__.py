"""Outils utilisables par les agents : recherche web et lecture/écriture de fichiers."""

from .files import read_text, write_text, ensure_dir
from .web_search import web_search

__all__ = ["read_text", "write_text", "ensure_dir", "web_search"]
