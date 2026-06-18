# KDP Factory 📚🤖

Système **multi-agents** pour produire des livres Amazon **KDP** (France 🇫🇷 + UK 🇬🇧) en série, orchestré avec **LangGraph** et propulsé par **Claude** (Anthropic, `claude-opus-4-8`).

Six agents spécialisés se coordonnent **uniquement via un état partagé** (`BookState`), sous le contrôle d'un superviseur. Architecture modulaire, prête pour le RAG (votre style + vos livres passés).

---

## Les 6 agents

| # | Agent | Rôle | Sortie dans le State |
|---|-------|------|----------------------|
| 1 | **Market Research** | Niche rentable, concurrence, mots-clés Amazon | `research` |
| 2 | **Outline & Structure** | Plan détaillé et structuré | `outline` + `chapters` (pending) |
| 3 | **Writer** | Rédaction chapitre par chapitre | `chapters` (drafted) |
| 4 | **Editor & Style** | Révision, fluidité, engagement | `chapters` (edited) |
| 5 | **Formatting & Kindle** | Manuscrit Markdown + consignes d'export | `manuscript_md`, `export_instructions` |
| 6 | **Marketing Amazon** | Titre, description, mots-clés, catégories, A+ Content | `marketing` |

---

## Architecture

```
START → supervisor → ┌─ market_research ─┐
                     ├─ outline          │
                     ├─ writer  ◀─┐      │   (boucle chapitres,
                     ├─ editor  ◀─┘      │    pilotée par l'état)
                     ├─ formatting       │
                     └─ marketing        │
                            ▲            ▼
                            └──────── supervisor ──→ END
```

- **`state.py`** — `BookState` (TypedDict). Le « livre en cours » : brief, recherche, plan, chapitres, manuscrit, marketing + champs de pilotage. **Seul canal de communication** entre agents.
- **`supervisor.py`** — décide qui agit ensuite en lisant l'état (aucun agent n'en appelle un autre). Toute la logique de flux est ici → facile à réordonner/étendre.
- **`graph.py`** — assemble le graphe LangGraph (étoile autour du superviseur).
- **`agents/`** — les 6 agents, chacun = une fonction `(state) -> mise à jour partielle`.
- **`prompts/`** — prompts système détaillés, séparés du code (versionnables, A/B testables).
- **`llm.py`** — wrapper Anthropic : pensée adaptative, `effort`, streaming, sorties JSON contraintes.
- **`rag/`** — interface `Retriever` prête à brancher (désactivée par défaut).

---

## Installation

```bash
pip install -e .            # ou: pip install -e ".[dev]"
cp .env.example .env        # puis renseigner ANTHROPIC_API_KEY
```

## Utilisation

### En ligne de commande
```bash
kdp "Apprendre à investir en bourse quand on débute" \
    --market FR --chapters 8 \
    --style "pédagogique, rassurant, concret" \
    --out ./output/bourse
```

### Par programmation
```python
from kdp_factory.main import run, save_outputs
from kdp_factory.state import BookBrief

brief: BookBrief = {"topic": "Productivité pour freelances", "market": "UK"}
state = run(brief)
save_outputs(state, "./output/productivity")
```

Livrables produits dans le dossier de sortie : `manuscrit.md`, `consignes_export_kindle.md`, `marketing.json`, `etat_final.json`.

---

## Activer le RAG plus tard

Le système fonctionne à l'identique RAG activé ou non. Pour brancher vos livres / votre style :

1. `pip install -e ".[rag]"`
2. Implémenter `ChromaRetriever` dans `src/kdp_factory/rag/store.py` (ingestion + recherche).
3. `KDP_RAG_ENABLED=true` dans `.env`.

Les agents `writer` et `editor` injectent automatiquement le contexte récupéré (`rag_block`) dès qu'un retriever réel est disponible — aucun autre changement nécessaire.

---

## Tests

```bash
pytest            # teste la logique de routage (hors ligne, sans appel API)
```

## Faire évoluer le système

- **Ajouter un agent** (ex. « Traduction FR↔UK ») : créer le nœud + prompt, l'enregistrer dans `graph.py`, ajouter une transition dans `supervisor.decide_next`.
- **Ajouter une boucle de relecture** : utiliser `revision_count` comme garde-fou et router `editor → writer` selon les notes éditoriales.
- **Persistance / reprise** : LangGraph supporte les checkpointers (SQLite/Postgres) — à brancher dans `build_graph()`.
