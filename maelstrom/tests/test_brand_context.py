"""Tests du chargement du contexte de marque depuis les fichiers Markdown."""

from maelstrom.brand.loader import _strip_html_comments, load_context_file
from maelstrom.brand.maelstrom import brand_bible
from maelstrom.brand.transcreation import transcreation_protocol


def test_strip_html_comments():
    txt = "<!-- instructions à éditer -->\n# Titre\nContenu."
    out = _strip_html_comments(txt).strip()
    assert out.startswith("# Titre")
    assert "instructions" not in out


def test_brand_bible_loads_markdown_file():
    # Les fichiers brand_context/*.md du projet sont chargés en priorité.
    bible = brand_bible()
    assert "MAELSTRÖM" in bible
    assert "ZÉRO SPOILER" in bible
    assert "<!--" not in bible  # commentaires d'édition retirés


def test_transcreation_protocol_loads_markdown_file():
    proto = transcreation_protocol()
    assert "TRANSCRÉ" in proto.upper()
    assert "TEST DU NATIF" in proto.upper()


def test_missing_file_returns_none():
    assert load_context_file("fichier_inexistant_xyz.md") is None
