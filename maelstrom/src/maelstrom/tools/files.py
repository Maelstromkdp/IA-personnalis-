"""Outils fichiers : lecture/écriture sûres (entrée transcréation, manuscrits, exports)."""

from __future__ import annotations

from pathlib import Path


def read_text(path: str | Path) -> str:
    """Lit un fichier texte (UTF-8). Lève FileNotFoundError si absent."""
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str | Path, content: str) -> Path:
    """Écrit un fichier texte (UTF-8), en créant les dossiers parents si besoin."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
