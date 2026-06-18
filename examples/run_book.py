"""Exemple : produire un livre par programmation (sans CLI).

    python examples/run_book.py

Nécessite ANTHROPIC_API_KEY dans l'environnement ou un fichier .env.
"""

from kdp_factory.main import run, save_outputs
from kdp_factory.state import BookBrief

brief: BookBrief = {
    "topic": "Apprendre à investir en bourse quand on débute",
    "market": "FR",
    "style": "pédagogique, rassurant, concret, avec des exemples chiffrés",
    "target_chapters": 8,
    "constraints": "Public débutant total, éviter le jargon, ton bienveillant.",
}

if __name__ == "__main__":
    state = run(brief)
    save_outputs(state, "./output/bourse-debutant")
