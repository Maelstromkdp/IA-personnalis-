"""Exemple — création originale d'une novella MAELSTRÖM.

    python examples/create_book.py
"""

from maelstrom.book_state import Brief
from maelstrom.main import run, save_outputs

brief: Brief = {
    "mode": "creation",
    "language": "FR",
    "seed": "Une femme découvre que son mari rentre chaque soir avec dix minutes de retard inexpliquées.",
    "target_words": 16000,
}

if __name__ == "__main__":
    state = run(brief)
    save_outputs(state, "./output/exemple-creation")
