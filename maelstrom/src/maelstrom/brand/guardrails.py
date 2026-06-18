"""Garde-fous qualité MAELSTRÖM : anti-spoiler + 8 contrôles qualité.

- `QUALITY_TESTS` : les 8 contrôles que l'Editor applique (données → utilisées à
  la fois pour le prompt et pour le schéma de sortie structurée).
- `SpoilerGuard` : détecteur/correcteur de spoiler indépendant, prioritaire sur
  tout. Utilisé sur les chapitres ET sur le matériel marketing.

La règle « Zéro Spoiler » est traitée comme un bloqueur : tant qu'elle n'est pas
satisfaite, le contenu ne peut pas être validé.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:  # évite l'import circulaire à l'exécution
    from ..llm import LLM


# --------------------------------------------------------------------------- #
# Les 8 contrôles qualité (encodés d'après le brief — ajuste selon ton protocole)
# --------------------------------------------------------------------------- #
class QualityTest(TypedDict):
    id: str
    label: str
    description: str
    blocking: bool  # un échec bloque la validation si True


QUALITY_TESTS: list[QualityTest] = [
    {
        "id": "zero_spoiler",
        "label": "Zéro spoiler",
        "description": "Le texte ne révèle aucun twist/coupable/fin de façon prématurée "
        "ni ne gâche un retournement à venir.",
        "blocking": True,
    },
    {
        "id": "twist_preserved",
        "label": "Préservation des twists",
        "description": "Les retournements et le foreshadowing restent intacts, discrets, "
        "ni annoncés trop tôt ni affaiblis.",
        "blocking": True,
    },
    {
        "id": "tension",
        "label": "Tension maintenue",
        "description": "La montée d'angoisse est continue ; aucun temps mort, aucun "
        "relâchement non voulu.",
        "blocking": True,
    },
    {
        "id": "non_dit",
        "label": "Non-dit préservé",
        "description": "On suggère sans expliquer ; les émotions et menaces ne sont pas "
        "sur-explicitées.",
        "blocking": True,
    },
    {
        "id": "coherence",
        "label": "Cohérence narrative",
        "description": "Continuité des faits, des personnages, de la chronologie et des "
        "motifs récurrents.",
        "blocking": True,
    },
    {
        "id": "native_test",
        "label": "Test du natif",
        "description": "La langue sonne native (en transcréation EN US : aucune tournure "
        "traduite, aucune maladresse).",
        "blocking": True,
    },
    {
        "id": "brand_voice",
        "label": "Ton / voix de marque",
        "description": "Le passage respecte le ton MAELSTRÖM : calme, froid, suggestif, "
        "rugueux quand il le faut.",
        "blocking": True,
    },
    {
        "id": "fidelity_grit",
        "label": "Fidélité & rugosité (transcréation)",
        "description": "En transcréation : le sens, les twists et les aspérités voulues du "
        "style original sont préservés (non lissés).",
        "blocking": False,
    },
]


class QualityVerdict(TypedDict):
    test_id: str
    passed: bool
    notes: str


# --------------------------------------------------------------------------- #
# SpoilerGuard — bloqueur prioritaire
# --------------------------------------------------------------------------- #
_SPOILER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "spoils": {"type": "boolean"},
        "severity": {"type": "string", "enum": ["none", "minor", "major"]},
        "reasons": {"type": "array", "items": {"type": "string"}},
        "safe_rewrite": {
            "type": "string",
            "description": "Réécriture sans spoiler, conservant la voix de marque. "
            "Vide si rien à corriger.",
        },
    },
    "required": ["spoils", "severity", "reasons", "safe_rewrite"],
}

_SPOILER_SYSTEM = """\
Tu es le gardien anti-spoiler de la marque MAELSTRÖM. Ta seule mission : déterminer
si un texte PUBLIC (titre, description, hameçon, post, synopsis commercial) révèle
quoi que ce soit qui devrait rester caché.

Constitue un spoiler TOUT élément qui :
- révèle ou laisse deviner le twist / le retournement final ;
- dévoile l'identité du coupable ou la nature réelle d'un personnage ;
- annonce le sort final d'un personnage (mort, trahison, survie) ;
- explique le « pourquoi » que le livre garde pour la fin.

Ne constitue PAS un spoiler : la situation de départ, le malaise, la promesse de
tension, la « serrure » (la question troublante) tant que la « pièce derrière la
porte » (la réponse) reste cachée.

Si le texte spoile, fournis une réécriture sûre qui garde la voix de marque
(calme, brève, un peu sèche, tutoiement, sans emphase commerciale) et crée le
manque sans livrer la réponse. Sinon, renvoie un `safe_rewrite` vide.

Réponds uniquement via le schéma structuré.
"""


class SpoilerGuard:
    """Détecte et corrige les spoilers. Indépendant des autres agents."""

    def __init__(self, llm: "LLM") -> None:
        self._llm = llm

    def check(self, text: str, *, context: str = "") -> dict[str, Any]:
        """Renvoie {spoils, severity, reasons[], safe_rewrite}."""
        user = (
            (f"Contexte (intrigue connue, peut contenir le twist) :\n{context}\n\n" if context else "")
            + f"Texte public à vérifier :\n---\n{text}\n---"
        )
        return self._llm.structured(
            system=_SPOILER_SYSTEM,
            user=user,
            schema=_SPOILER_SCHEMA,
            effort="medium",
        )

    def enforce(self, text: str, *, context: str = "") -> tuple[str, dict[str, Any]]:
        """Garantit un texte sans spoiler.

        Retourne (texte_sûr, verdict). Si le texte spoile et qu'une réécriture est
        proposée, applique-la puis re-vérifie une fois.
        """
        verdict = self.check(text, context=context)
        if not verdict["spoils"]:
            return text, verdict
        rewrite = verdict.get("safe_rewrite", "").strip()
        if not rewrite:
            return text, verdict  # signalé mais non corrigeable automatiquement
        second = self.check(rewrite, context=context)
        return rewrite, second
