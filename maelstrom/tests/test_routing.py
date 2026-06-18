"""Tests du routage du superviseur (hors ligne, sans appel réseau)."""

from langgraph.graph import END

from maelstrom.book_state import new_state
from maelstrom.graph.supervisor import (
    EDITOR,
    FORMATTING,
    MARKETING,
    OUTLINE,
    RESEARCH,
    WRITER,
    decide_next,
)


def _chapters(*statuses):
    return [
        {"index": i, "title": f"C{i}", "content": "", "word_count": 0,
         "status": s, "editor_notes": "", "revisions": 0}
        for i, s in enumerate(statuses, start=1)
    ]


def test_creation_starts_with_research():
    state = new_state({"mode": "creation"})
    assert state["stage"] == "research"
    assert decide_next(state) == RESEARCH


def test_transcreation_skips_research():
    state = new_state({"mode": "transcreation", "source_text": "x"})
    assert state["stage"] == "outline"
    assert state["language"] == "EN"  # défaut transcréation
    assert decide_next(state) == OUTLINE


def test_outline_then_writing():
    state = new_state({"mode": "creation"})
    state["stage"] = "outline"
    assert decide_next(state) == OUTLINE


def test_writing_drafts_then_edits_then_formats():
    state = new_state({"mode": "creation"})
    state["stage"] = "writing"
    state["chapters"] = _chapters("pending", "pending")
    assert decide_next(state) == WRITER
    state["chapters"] = _chapters("drafted", "drafted")
    assert decide_next(state) == EDITOR
    state["chapters"] = _chapters("edited", "edited")
    assert decide_next(state) == FORMATTING


def test_rewrite_loop_routes_back_to_writer():
    # Un chapitre renvoyé en réécriture (pending) repasse par le writer.
    state = new_state({"mode": "creation"})
    state["stage"] = "editing"
    state["chapters"] = _chapters("edited", "pending")
    assert decide_next(state) == WRITER


def test_marketing_then_end():
    state = new_state({"mode": "creation"})
    state["stage"] = "marketing"
    assert decide_next(state) == MARKETING
    state["stage"] = "done"
    assert decide_next(state) == END
