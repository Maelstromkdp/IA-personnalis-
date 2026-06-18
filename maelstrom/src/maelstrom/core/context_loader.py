"""Chargeur de contexte de marque — API publique simple.

C'est l'API « façade » : elle expose des fonctions faciles à appeler, mais
s'appuie sur le chargeur robuste `brand/loader.py` (recherche du dossier
`brand_context/` via MAELSTROM_CONTEXT_DIR / cwd / racine projet, lecture mise en
cache, nettoyage des commentaires d'édition, repli sur le contenu intégré).

Deux niveaux d'usage :
- `get_system_prompt(agent, mode)` → une **chaîne** prête à l'emploi (simple).
- `get_system_blocks(agent, mode)` → des **blocs système avec point de cache**
  (`cache_control`) ; c'est ce que les agents utilisent en production pour
  bénéficier du cache de prompt Anthropic.

Le contexte marque est TOUJOURS injecté ; le protocole de transcréation ne l'est
qu'en `mode="transcreation"` (plus économe).
"""

from __future__ import annotations

from ..brand.maelstrom import brand_bible
from ..brand.transcreation import transcreation_protocol

_PRIORITY_RULES = """\
### RÈGLES PRIORITAIRES
- Règle absolue n°1 : ZÉRO SPOILER. Jamais.
- Respecte le ton, la voix et les contraintes de la marque MAELSTRÖM.
- Qualité > volume : mieux vaut refuser que produire du médiocre ou du non conforme.
- Sois excellent dans ton rôle spécifique.
"""


def load_maelstrom_context() -> str:
    """Contexte de marque (toujours injecté). Lu depuis brand_context, en cache."""
    return brand_bible()


def load_transcreation_protocol() -> str:
    """Protocole de transcréation (injecté seulement en mode transcréation)."""
    return transcreation_protocol()


def _brand_text(mode: str) -> str:
    """Texte de contexte complet selon le mode (marque [+ protocole])."""
    context = load_maelstrom_context()
    if mode == "transcreation":
        context += "\n\n" + load_transcreation_protocol()
    return context


def get_system_prompt(agent_name: str, mode: str = "creation", *, role_prompt: str = "") -> str:
    """Prompt système complet (chaîne) pour un agent.

    - `agent_name` : nom lisible de l'agent (ex. « Writer Agent »).
    - `mode` : "creation" (contexte marque seul) ou "transcreation" (+ protocole).
    - `role_prompt` : instructions spécifiques au rôle (optionnel).
    """
    parts = [
        f"Tu es l'agent {agent_name} du système MAELSTRÖM.",
        "### CONTEXTE MARQUE MAELSTRÖM (à respecter absolument)\n" + _brand_text(mode),
    ]
    if role_prompt:
        parts.append("### RÔLE DE L'AGENT\n" + role_prompt)
    parts.append(_PRIORITY_RULES)
    return "\n\n".join(parts)


def get_system_blocks(agent_name: str, mode: str = "creation", *, role_prompt: str = "") -> list[dict]:
    """Version cache-aware : blocs système avec `cache_control` sur le contexte.

    Le 1er bloc (contexte marque [+ protocole] + règles prioritaires) est stable
    pour un mode donné → mis en cache. Le 2e bloc (rôle de l'agent) varie.
    """
    stable = (
        f"Tu es l'agent {agent_name} du système MAELSTRÖM.\n\n"
        "### CONTEXTE MARQUE MAELSTRÖM (à respecter absolument)\n"
        + _brand_text(mode)
        + "\n\n"
        + _PRIORITY_RULES
    )
    blocks = [{"type": "text", "text": stable, "cache_control": {"type": "ephemeral"}}]
    if role_prompt:
        blocks.append({"type": "text", "text": "### RÔLE DE L'AGENT\n" + role_prompt})
    return blocks


def show_context_stats() -> None:
    """Affiche des infos de debug sur les fichiers de contexte réellement chargés.

    Utile pour vérifier d'un coup d'œil que tes documents (et non la version par
    défaut intégrée) sont bien pris en compte.
    """
    from ..brand.loader import context_path

    ctx = load_maelstrom_context()
    cpath = context_path("maelstrom_context.md")
    print(
        f"Contexte MAELSTRÖM : {len(ctx):,} caractères "
        f"— source : {cpath or 'version intégrée au code (fichier .md absent)'}"
    )

    ppath = context_path("transcreation_protocol.md")
    proto = load_transcreation_protocol()
    print(
        f"Protocole Transcréation : {len(proto):,} caractères "
        f"— source : {ppath or 'version intégrée au code (fichier .md absent)'}"
    )
