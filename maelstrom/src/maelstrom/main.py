"""Point d'entrée CLI — création originale OU transcréation FR → EN."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from rich.console import Console

from .book_state import Brief, new_state
from .config import get_settings
from .graph import build_graph
from .tools import read_text, write_text

console = Console()


def run(brief: Brief) -> dict:
    """Exécute le pipeline complet (une passe) et renvoie l'état final."""
    graph = build_graph()
    initial = new_state(brief)

    final: dict = initial
    seen = 0
    # recursion_limit élevé : la boucle qualité (writer ⇄ editor) multiplie les tours.
    for state in graph.stream(initial, stream_mode="values", config={"recursion_limit": 400}):
        for entry in state.get("log", [])[seen:]:
            console.log(f"[bold magenta]{entry['agent']}[/]: {entry['message']}")
        seen = len(state.get("log", []))
        final = state
    for err in final.get("errors", []):
        console.print(f"[yellow]⚠ {err}[/]")
    return final


def save_outputs(state: dict, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if state.get("full_manuscript"):
        write_text(out / "manuscrit.md", state["full_manuscript"])
    if state.get("export_instructions"):
        write_text(out / "export_kindle.md", state["export_instructions"])
    if state.get("marketing_assets"):
        write_text(
            out / "marketing.json",
            json.dumps(state["marketing_assets"], ensure_ascii=False, indent=2),
        )
    serializable = {k: v for k, v in state.items() if k != "log"}
    write_text(out / "etat_final.json", json.dumps(serializable, ensure_ascii=False, indent=2))
    console.print(f"\n[bold green]Livrables écrits dans[/] {out.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MAELSTRÖM — produit ou transcrée un thriller psychologique court."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("create", help="Création originale d'une novella.")
    pc.add_argument("--seed", default="", help="Idée / contrainte de départ (optionnel).")
    pc.add_argument("--language", choices=["FR", "EN"], default="FR")
    pc.add_argument("--words", type=int, default=16000, help="Cible de mots (~13000–20000).")
    pc.add_argument("--out", default=None)

    pt = sub.add_parser("transcreate", help="Transcréation FR → EN d'un manuscrit existant.")
    pt.add_argument("source", help="Chemin du manuscrit source (français).")
    pt.add_argument("--language", choices=["EN", "FR"], default="EN")
    pt.add_argument("--out", default=None)

    args = parser.parse_args()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[bold red]ANTHROPIC_API_KEY non défini.[/] Voir .env.example.")
        raise SystemExit(1)

    if args.cmd == "create":
        brief: Brief = {
            "mode": "creation",
            "language": args.language,
            "seed": args.seed,
            "target_words": args.words,
        }
        default_out = "./output/creation"
    else:
        brief = {
            "mode": "transcreation",
            "language": args.language,
            "source_text": read_text(args.source),
        }
        default_out = "./output/transcreation"

    console.rule("[bold]MAELSTRÖM")
    state = run(brief)
    save_outputs(state, args.out or default_out)
    console.rule("[bold green]Terminé")


if __name__ == "__main__":
    main()
