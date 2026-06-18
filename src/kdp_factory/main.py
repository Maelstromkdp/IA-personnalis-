"""Point d'entrée CLI — lance la production d'un livre de bout en bout."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from rich.console import Console

from .config import get_settings
from .graph import build_graph
from .state import BookBrief, new_state

console = Console()


def run(brief: BookBrief) -> dict:
    """Exécute le pipeline complet (une seule passe) et renvoie l'état final.

    `stream_mode="values"` renvoie l'état COMPLET accumulé après chaque étape :
    on suit l'avancement en direct et le dernier état reçu est l'état final.
    recursion_limit élevé : chaque chapitre = plusieurs allers-retours superviseur↔agent.
    """
    graph = build_graph()
    initial = new_state(brief)

    final: dict = initial
    seen = 0
    for state in graph.stream(initial, stream_mode="values", config={"recursion_limit": 300}):
        # N'affiche que les nouvelles lignes de journal depuis la dernière étape.
        entries = state.get("log", [])
        for entry in entries[seen:]:
            console.log(f"[bold cyan]{entry['agent']}[/]: {entry['message']}")
        seen = len(entries)
        final = state
    return final


def save_outputs(state: dict, out_dir: str) -> None:
    """Écrit les livrables sur disque : manuscrit, marketing, état complet."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    if state.get("manuscript_md"):
        (out / "manuscrit.md").write_text(state["manuscript_md"], encoding="utf-8")
    if state.get("export_instructions"):
        (out / "consignes_export_kindle.md").write_text(
            state["export_instructions"], encoding="utf-8"
        )
    if state.get("marketing"):
        (out / "marketing.json").write_text(
            json.dumps(state["marketing"], ensure_ascii=False, indent=2), encoding="utf-8"
        )
    # État complet (utile pour reprise / débogage).
    serializable = {k: v for k, v in state.items() if k != "log"}
    (out / "etat_final.json").write_text(
        json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    console.print(f"\n[bold green]Livrables écrits dans[/] {out.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="KDP Factory — produit un livre Amazon KDP via un système multi-agents."
    )
    parser.add_argument("topic", help="Sujet / idée de départ du livre.")
    parser.add_argument("--market", choices=["FR", "UK"], default="FR")
    parser.add_argument("--language", default=None, help="fr | en (déduit du marché par défaut).")
    parser.add_argument("--style", default="clair, professionnel, accessible et engageant")
    parser.add_argument("--chapters", type=int, default=None, help="Nombre de chapitres visé.")
    parser.add_argument("--constraints", default="")
    parser.add_argument("--out", default=None, help="Dossier de sortie.")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[bold red]ANTHROPIC_API_KEY non défini.[/] Voir .env.example.")
        raise SystemExit(1)

    brief: BookBrief = {"topic": args.topic, "market": args.market, "style": args.style}
    if args.language:
        brief["language"] = args.language
    if args.chapters:
        brief["target_chapters"] = args.chapters
    if args.constraints:
        brief["constraints"] = args.constraints

    console.rule("[bold]KDP Factory")
    state = run(brief)
    save_outputs(state, args.out or get_settings().output_dir)
    console.rule("[bold green]Terminé")


if __name__ == "__main__":
    main()
