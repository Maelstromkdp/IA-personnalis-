"""Exemple — transcréation FR → EN d'un manuscrit MAELSTRÖM existant.

    python examples/transcreate_book.py chemin/vers/manuscrit_fr.md
"""

import sys

from maelstrom.book_state import Brief
from maelstrom.main import run, save_outputs
from maelstrom.tools import read_text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python examples/transcreate_book.py <manuscrit_fr.md>")

    brief: Brief = {
        "mode": "transcreation",
        "language": "EN",
        "source_text": read_text(sys.argv[1]),
    }
    state = run(brief)
    save_outputs(state, "./output/exemple-transcreation")
