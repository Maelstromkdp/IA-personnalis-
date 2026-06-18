# MAELSTRÖM 🌀 — Fabrique de thrillers psychologiques courts

Système **multi-agents** (LangGraph + Claude `claude-opus-4-8`) pour **produire** des novellas psychologiques courtes dans l'univers MAELSTRÖM et les **transcréer** (FR → EN US), en volume, sans jamais sacrifier la qualité éditoriale ni la règle **Zéro Spoiler**.

> **Le danger vient des gens qu'on croit connaître.**
> Format court, ton calme et froid, on suggère sans expliquer. Marque sans visage.

---

## Principes garantis par l'architecture

| Exigence | Comment elle est appliquée |
|---|---|
| **Connaissance marque par tous les agents** | `brand/` est injecté en tête du prompt système de chaque agent (`compose_system`). |
| **Zéro Spoiler prioritaire** | `SpoilerGuard` (indépendant) vérifie et **réécrit** chaque texte public du Marketing ; les contrôles `zero_spoiler` / `twist_preserved` de l'Editor sont **bloquants**. |
| **Qualité > Volume** | L'Editor applique **8 contrôles qualité** ; un échec bloquant renvoie le chapitre au Writer (quota de réécritures par chapitre, puis escalade signalée). |
| **Création ET transcréation** | `mode` dans le State ; le superviseur route différemment et le Protocole de Transcréation v2 est injecté en mode `transcreation`. |
| **Communication via State** | Aucun appel direct entre agents : tout passe par `BookState`. |
| **Performance / coût** | Le contexte de marque (injecté à chaque appel) est **mis en cache** (`cache_control`) → coût et latence fortement réduits, surtout une fois tes documents complets collés dans `brand/`. |

---

## Les 6 agents

1. **Market Research & Niche** — recherche web (native Claude / Tavily), tropes, mots-clés, concepts MAELSTRÖM.
2. **Outline & Structure** — outline 3–5 actes (création) **ou** segmentation du manuscrit source (transcréation).
3. **Writer** — rédige (création) ou transcrée (FR→EN) chapitre par chapitre ; intègre les consignes de réécriture.
4. **Editor & Quality** — applique les 8 contrôles qualité, renvoie au Writer si échec bloquant.
5. **Formatting & Kindle** — manuscrit Markdown propre + consignes d'export KDP.
6. **Marketing & Amazon** — titre, description, mots-clés, catégories, hameçons TikTok/Insta/Threads — **passés au SpoilerGuard**.

---

## Architecture

```
                ┌───────────────── supervisor (route selon mode + état) ─────────────────┐
                │                                                                          │
CRÉATION :  research → outline → ┌ writer ⇄ editor ┐ → formatting → marketing → END        │
TRANSCRÉ. :            outline → └ (boucle qualité) ┘ → formatting → marketing → END        │
                └──────────────────────── chaque agent revient au supervisor ──────────────┘
```

- `book_state.py` — `BookState` (TypedDict) : `book_concept`, `outline`, `current_chapter`, `full_manuscript`, `research_data`, `marketing_assets`, `quality_checks`, `language`, `mode` + pilotage.
- `graph/` — `supervisor.py` (routage, fonction pure `decide_next`) + `build.py` (graphe LangGraph).
- `agents/` — les 6 agents (`base.py` injecte la marque dans chaque prompt).
- `prompts/` — prompts système détaillés par agent (partie rôle).
- `brand/` — **bible MAELSTRÖM**, **Protocole de Transcréation v2**, **garde-fous** (SpoilerGuard + 8 contrôles).
- `tools/` — recherche web + lecture/écriture de fichiers.
- `llm.py` — wrapper Claude (pensée adaptative, effort, streaming, JSON contraint, web search).

---

## Installation

```bash
cd maelstrom
pip install -e ".[dev]"        # + ".[tavily]" ou ".[rag]" si besoin
cp .env.example .env           # renseigner ANTHROPIC_API_KEY
```

## Le plus simple : l'assistant

```bash
maelstrom            # assistant interactif : il te pose 2-3 questions et produit le livre
maelstrom doctor     # vérifie que tout est bien configuré (clé API, modèle, etc.)
```

L'assistant gère création ET transcréation, choisit un dossier de sortie, lance la
production, puis affiche un récapitulatif clair (titre, mots, contrôles qualité,
audit anti-spoiler, fichiers produits).

## En ligne de commande (si tu préfères les options)

```bash
# Création originale
maelstrom create \
  --seed "Une femme découvre que son mari rentre chaque soir avec 10 minutes de retard inexpliquées" \
  --language FR --words 16000 --out ./output/mon-livre

# Transcréation FR → EN
maelstrom transcreate ./mon_manuscrit_fr.md --language EN --out ./output/transcrea
```

### En Python
```python
from maelstrom.book_state import Brief
from maelstrom.main import run, save_outputs

state = run({"mode": "creation", "language": "FR",
             "seed": "Le voisin a une clé de chez nous."})
save_outputs(state, "./output/demo")
```

**Livrables** : `manuscrit.md`, `export_kindle.md`, `marketing.json`, `etat_final.json` (avec `quality_checks` et `spoiler_audit`).

---

## Recherche web

Par défaut : **web search natif de Claude** (aucune clé supplémentaire). Pour Tavily : `MAELSTROM_WEB_SEARCH=tavily` + `TAVILY_API_KEY` (`pip install -e ".[tavily]"`).

## Tests

```bash
pytest        # routage (2 modes) + garde-fous (8 contrôles, SpoilerGuard) — hors ligne
```

---

## Personnaliser la marque (le plus important)

Tout le contexte de marque vit dans **deux fichiers Markdown éditables** — aucun
code à toucher :

```
brand_context/
├── maelstrom_context.md         ← colle ici tes CONSIGNES PROJET MAELSTRÖM
└── transcreation_protocol.md    ← colle ici ton PROTOCOLE DE TRANSCRÉATION v2
```

- Ces fichiers sont **injectés automatiquement** dans chaque agent et **mis en cache**.
- `maelstrom_context.md` est toujours injecté ; `transcreation_protocol.md` ne l'est
  qu'en mode transcréation (plus économe).
- Vérifie qu'ils sont bien pris en compte avec `maelstrom doctor` (il affiche le
  chemin du fichier chargé).
- Tu peux pointer ailleurs via `MAELSTROM_CONTEXT_DIR=/chemin/vers/brand_context`.
- Si les fichiers sont absents, le système retombe sur une version par défaut
  intégrée au code (il fonctionne quand même).

## Faire évoluer le système

- **Brancher tes vrais documents** : remplace le contenu de `brand_context/maelstrom_context.md`
  et `brand_context/transcreation_protocol.md` par tes documents complets. Rien d'autre à changer.
- **Ajuster les 8 contrôles** : édite `QUALITY_TESTS` dans `brand/guardrails.py` (id, libellé, bloquant ou non).
- **RAG (hameçons + livres précédents)** : implémenter un retriever et l'injecter dans Writer/Editor (`MAELSTROM_RAG_ENABLED=true`).
- **Ajouter un agent / une étape** : nouveau nœud + prompt, enregistrement dans `graph/build.py`, transition dans `decide_next`.
- **Persistance / reprise** : brancher un checkpointer LangGraph dans `build_graph()`.

> ⚠️ Les contenus des deux documents de référence sont **encodés d'après le brief** dans `brand/`. Vérifie et complète ces fichiers avec tes documents exacts avant production.
