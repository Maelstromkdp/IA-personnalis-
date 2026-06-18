"""Tests de l'API publique core.context_loader."""

from maelstrom.core.context_loader import (
    get_system_blocks,
    get_system_prompt,
    load_maelstrom_context,
    load_transcreation_protocol,
)


def test_load_maelstrom_context():
    ctx = load_maelstrom_context()
    assert "MAELSTRÖM" in ctx and "ZÉRO SPOILER" in ctx


def test_load_transcreation_protocol():
    assert "TEST DU NATIF" in load_transcreation_protocol().upper()


def test_creation_prompt_excludes_protocol():
    prompt = get_system_prompt("Writer Agent", mode="creation")
    assert "CONTEXTE MARQUE" in prompt
    assert "ZÉRO SPOILER" in prompt
    assert "TEST DU NATIF" not in prompt.upper()  # protocole non injecté en création


def test_transcreation_prompt_includes_protocol():
    prompt = get_system_prompt("Writer Agent", mode="transcreation")
    assert "TEST DU NATIF" in prompt.upper()  # protocole injecté


def test_system_blocks_are_cache_aware():
    blocks = get_system_blocks("Writer Agent", mode="creation", role_prompt="Écris.")
    assert blocks[0]["cache_control"] == {"type": "ephemeral"}
    assert "ZÉRO SPOILER" in blocks[0]["text"]
    # Le rôle (variable) est dans un bloc séparé, hors du préfixe mis en cache.
    assert any("Écris." in b["text"] for b in blocks[1:])
