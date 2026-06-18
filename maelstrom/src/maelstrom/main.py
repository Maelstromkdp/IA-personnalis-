"""Point d'entrée — assistant interactif + CLI (création / transcréation).

Usage le plus simple : lance `maelstrom` sans rien → un assistant te guide.
CLI : `maelstrom create ...`, `maelstrom transcreate <fichier>`, `maelstrom doctor`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from .book_state import Brief
from .config import get_settings
from .graph import build_graph
from .tools import read_text, write_text

console = Console()


# --------------------------------------------------------------------------- #
# Exécution du pipeline
# --------------------------------------------------------------------------- #
def run(brief: Brief) -> dict:
    """Exécute le pipeline complet (une passe) et renvoie l'état final."""
    graph = build_graph()
    from .book_state import new_state

    initial = new_state(brief)
    final: dict = initial
    seen = 0
    with console.status("[bold magenta]Production en cours…", spinner="dots"):
        for state in graph.stream(initial, stream_mode="values", config={"recursion_limit": 400}):
            for entry in state.get("log", [])[seen:]:
                console.log(f"[bold magenta]{entry['agent']}[/]: {entry['message']}")
            seen = len(state.get("log", []))
            final = state
    return final


# --------------------------------------------------------------------------- #
# Sorties + récapitulatif
# --------------------------------------------------------------------------- #
def _slugify(text: str, fallback: str = "livre") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return slug[:50] or fallback


def save_outputs(state: dict, out_dir: str) -> Path:
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
    return out


def print_summary(state: dict, out: Path) -> None:
    """Récapitulatif lisible en fin de production."""
    chapters = state.get("chapters", [])
    words = sum(c.get("word_count", 0) for c in chapters)
    qc = state.get("quality_checks", [])
    qc_ok = sum(1 for q in qc if q.get("passed"))
    assets = state.get("marketing_assets", {})
    audit = assets.get("spoiler_audit", {})

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("Mode", state.get("mode", "?"))
    table.add_row("Langue", state.get("language", "?"))
    table.add_row("Titre (travail)", assets.get("title") or state.get("book_concept", {}).get("working_title", "—"))
    table.add_row("Chapitres", str(len(chapters)))
    table.add_row("Mots (récit)", f"{words:,}".replace(",", " "))
    if qc:
        table.add_row("Contrôles qualité", f"{qc_ok}/{len(qc)} chapitres validés sans réserve")
    if assets:
        clean = audit.get("clean", True)
        table.add_row("Audit anti-spoiler", "[green]propre[/]" if clean else
                      f"[yellow]corrigé : {', '.join(audit.get('flagged_fields', []))}[/]")
    table.add_row("Dossier", str(out.resolve()))

    console.print(Panel(table, title="[bold]Récapitulatif MAELSTRÖM", border_style="magenta"))

    errors = state.get("errors", [])
    if errors:
        console.print("[yellow]Points à revoir (revue humaine conseillée) :[/]")
        for e in errors:
            console.print(f"  [yellow]• {e}[/]")

    console.print("\n[bold]Fichiers produits :[/]")
    for f in ("manuscrit.md", "export_kindle.md", "marketing.json", "etat_final.json"):
        if (out / f).exists():
            console.print(f"  • {out / f}")


# --------------------------------------------------------------------------- #
# Assistant interactif
# --------------------------------------------------------------------------- #
def wizard() -> None:
    console.print(Panel(
        "[bold]Assistant MAELSTRÖM[/]\nJe te pose quelques questions, puis je produis le livre.",
        border_style="magenta",
    ))
    mode = Prompt.ask(
        "Que veux-tu faire",
        choices=["creation", "transcreation"],
        default="creation",
    )

    if mode == "creation":
        seed = Prompt.ask("Idée / situation de départ (laisse vide pour me laisser proposer)", default="")
        language = Prompt.ask("Langue de sortie", choices=["FR", "EN"], default="FR")
        words = IntPrompt.ask("Nombre de mots visé", default=16000)
        brief: Brief = {"mode": "creation", "language": language, "seed": seed, "target_words": words}
        default_slug = _slugify(seed, "creation")
    else:
        source = Prompt.ask("Chemin du manuscrit source (français)")
        while not Path(source).exists():
            console.print("[red]Fichier introuvable.[/]")
            source = Prompt.ask("Chemin du manuscrit source (français)")
        language = Prompt.ask("Langue de sortie", choices=["EN", "FR"], default="EN")
        brief = {"mode": "transcreation", "language": language, "source_text": read_text(source)}
        default_slug = _slugify(Path(source).stem, "transcreation")

    out = Prompt.ask("Dossier de sortie", default=f"./output/{default_slug}")
    if not Confirm.ask("Je lance la production", default=True):
        console.print("Annulé.")
        return

    _execute(brief, out)


# --------------------------------------------------------------------------- #
# Diagnostic
# --------------------------------------------------------------------------- #
def doctor() -> None:
    s = get_settings()
    table = Table(title="Diagnostic MAELSTRÖM", show_header=True, header_style="bold")
    table.add_column("Paramètre")
    table.add_column("Valeur")
    key = os.environ.get("ANTHROPIC_API_KEY")
    table.add_row("ANTHROPIC_API_KEY", "[green]défini[/]" if key else "[red]MANQUANT[/]")
    table.add_row("Modèle principal", s.model_main)
    table.add_row("Effort", s.effort_default)
    table.add_row("Recherche web", s.web_search + ("  (TAVILY_API_KEY manquant)"
                  if s.web_search == "tavily" and not os.environ.get("TAVILY_API_KEY") else ""))
    table.add_row("Réécritures max/chapitre", str(s.max_revisions))
    table.add_row("RAG", "activé" if s.rag_enabled else "désactivé")
    console.print(table)
    if not key:
        console.print("[red]→ Définis ANTHROPIC_API_KEY (voir .env.example) avant de lancer une production.[/]")


# --------------------------------------------------------------------------- #
# Orchestration commune
# --------------------------------------------------------------------------- #
def _execute(brief: Brief, out_dir: str) -> dict:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[bold red]ANTHROPIC_API_KEY non défini.[/] Lance `maelstrom doctor`.")
        raise SystemExit(1)
    console.rule("[bold]MAELSTRÖM")
    state = run(brief)
    out = save_outputs(state, out_dir)
    print_summary(state, out)
    console.rule("[bold green]Terminé")
    return state


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MAELSTRÖM — production & transcréation de thrillers psychologiques courts."
    )
    sub = parser.add_subparsers(dest="cmd")

    pc = sub.add_parser("create", help="Création originale d'une novella.")
    pc.add_argument("--seed", default="")
    pc.add_argument("--language", choices=["FR", "EN"], default="FR")
    pc.add_argument("--words", type=int, default=16000)
    pc.add_argument("--out", default=None)

    pt = sub.add_parser("transcreate", help="Transcréation FR → EN d'un manuscrit.")
    pt.add_argument("source")
    pt.add_argument("--language", choices=["EN", "FR"], default="EN")
    pt.add_argument("--out", default=None)

    sub.add_parser("doctor", help="Vérifie la configuration.")
    sub.add_parser("wizard", help="Assistant interactif (par défaut si aucune commande).")

    args = parser.parse_args()

    if args.cmd in (None, "wizard"):
        wizard()
    elif args.cmd == "doctor":
        doctor()
    elif args.cmd == "create":
        brief: Brief = {
            "mode": "creation",
            "language": args.language,
            "seed": args.seed,
            "target_words": args.words,
        }
        _execute(brief, args.out or f"./output/{_slugify(args.seed, 'creation')}")
    elif args.cmd == "transcreate":
        brief = {
            "mode": "transcreation",
            "language": args.language,
            "source_text": read_text(args.source),
        }
        _execute(brief, args.out or f"./output/{_slugify(Path(args.source).stem, 'transcreation')}")


if __name__ == "__main__":
    main()
