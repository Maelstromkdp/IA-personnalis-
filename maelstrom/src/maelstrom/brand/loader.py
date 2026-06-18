"""Chargeur du contexte de marque depuis des fichiers Markdown éditables.

Le contexte MAELSTRÖM vit dans `brand_context/*.md` (éditables sans toucher au
code Python). Ce module les localise et les lit UNE seule fois (lru_cache), de
sorte que le texte est stable d'un appel à l'autre — condition nécessaire pour
que le cache de prompt Anthropic fasse mouche.

Ordre de recherche du dossier `brand_context/` :
1. variable d'environnement `MAELSTROM_CONTEXT_DIR` ;
2. `./brand_context/` dans le répertoire courant ;
3. la racine du projet (cas d'une installation éditable `pip install -e .`).

Si aucun fichier n'est trouvé, l'appelant retombe sur le contenu intégré au code
(les modules `maelstrom.py` / `transcreation.py`) : le système fonctionne donc
même sans fichiers externes.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


def _candidate_dirs() -> list[Path]:
    dirs: list[Path] = []
    env = os.environ.get("MAELSTROM_CONTEXT_DIR")
    if env:
        dirs.append(Path(env))
    dirs.append(Path.cwd() / "brand_context")
    # .../<projet>/src/maelstrom/brand/loader.py → parents[3] = racine du projet
    dirs.append(Path(__file__).resolve().parents[3] / "brand_context")
    return dirs


@lru_cache(maxsize=None)
def context_path(filename: str) -> Path | None:
    """Renvoie le chemin du fichier de contexte trouvé, ou None."""
    for d in _candidate_dirs():
        p = d / filename
        if p.is_file():
            return p
    return None


@lru_cache(maxsize=None)
def load_context_file(filename: str) -> str | None:
    """Lit et renvoie le contenu (sans les commentaires HTML d'en-tête), ou None."""
    p = context_path(filename)
    if p is None:
        return None
    text = p.read_text(encoding="utf-8")
    return _strip_html_comments(text).strip()


def _strip_html_comments(text: str) -> str:
    """Retire les commentaires `<!-- ... -->` (instructions d'édition) du Markdown."""
    out: list[str] = []
    i = 0
    while True:
        start = text.find("<!--", i)
        if start == -1:
            out.append(text[i:])
            break
        out.append(text[i:start])
        end = text.find("-->", start)
        if end == -1:
            break
        i = end + 3
    return "".join(out)
