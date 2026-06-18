"""Connaissance de marque MAELSTRÖM.

Ces modules encodent le positionnement, les règles d'or, la voix de marque, le
Protocole de Transcréation et les contrôles qualité. Ils sont injectés dans le
prompt système de CHAQUE agent via `brand.context.full_brand_context()`.

Points d'extension :
- `maelstrom.py`   → colle ici l'intégralité de tes consignes projet MAELSTRÖM.
- `transcreation.py` → colle ici l'intégralité du Protocole de Transcréation v2.
- `guardrails.py`  → logique anti-spoiler + définition des 8 contrôles qualité.
"""

from .context import full_brand_context, transcreation_context
from .guardrails import SpoilerGuard, QUALITY_TESTS, QualityVerdict

__all__ = [
    "full_brand_context",
    "transcreation_context",
    "SpoilerGuard",
    "QUALITY_TESTS",
    "QualityVerdict",
]
