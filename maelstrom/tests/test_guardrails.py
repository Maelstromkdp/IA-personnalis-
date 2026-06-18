"""Tests des garde-fous qualité (hors ligne, LLM simulé)."""

from maelstrom.brand.guardrails import QUALITY_TESTS, SpoilerGuard


def test_eight_quality_tests_defined():
    assert len(QUALITY_TESTS) == 8
    ids = {t["id"] for t in QUALITY_TESTS}
    # Les contrôles prioritaires du brief sont présents et bloquants.
    assert {"zero_spoiler", "twist_preserved", "tension", "non_dit",
            "coherence", "native_test", "brand_voice"} <= ids
    blocking = {t["id"] for t in QUALITY_TESTS if t["blocking"]}
    assert "zero_spoiler" in blocking and "twist_preserved" in blocking


class _FakeLLM:
    """LLM simulé : renvoie des verdicts scriptés sans réseau."""

    def __init__(self, verdicts):
        self._verdicts = list(verdicts)

    def structured(self, **kwargs):
        return self._verdicts.pop(0)


def test_spoiler_guard_passes_clean_text():
    fake = _FakeLLM([{"spoils": False, "severity": "none", "reasons": [], "safe_rewrite": ""}])
    guard = SpoilerGuard(fake)
    text, verdict = guard.enforce("Elle entend la porte. Il rentre. Encore en retard.")
    assert verdict["spoils"] is False
    assert text.startswith("Elle entend")


def test_spoiler_guard_rewrites_when_spoiling():
    fake = _FakeLLM([
        {"spoils": True, "severity": "major", "reasons": ["révèle le coupable"],
         "safe_rewrite": "Quelqu'un, tout près, sait déjà comment cela finit."},
        {"spoils": False, "severity": "none", "reasons": [], "safe_rewrite": ""},
    ])
    guard = SpoilerGuard(fake)
    text, verdict = guard.enforce("C'est le mari qui l'a tuée à la fin.")
    assert verdict["spoils"] is False  # re-vérifié après réécriture
    assert "sait déjà" in text
