"""Tests unitaires du routage du superviseur (sans appel réseau).

La logique de routage est une fonction pure : on peut la vérifier entièrement
hors ligne, ce qui garantit que le pipeline progresse comme prévu.
"""

from langgraph.graph import END

from kdp_factory.state import new_state
from kdp_factory.supervisor import (
    EDITOR,
    FORMATTING,
    MARKET_RESEARCH,
    MARKETING,
    OUTLINE,
    WRITER,
    decide_next,
)


def _chapters(*statuses):
    return [
        {"index": i, "title": f"C{i}", "content": "", "word_count": 0,
         "status": s, "editor_notes": ""}
        for i, s in enumerate(statuses, start=1)
    ]


def test_starts_with_market_research():
    state = new_state({"topic": "x"})
    assert decide_next(state) == MARKET_RESEARCH


def test_outline_stage():
    state = new_state({"topic": "x"})
    state["stage"] = "outline"
    assert decide_next(state) == OUTLINE


def test_writing_drafts_pending_first():
    state = new_state({"topic": "x"})
    state["stage"] = "writing"
    state["chapters"] = _chapters("drafted", "pending")
    assert decide_next(state) == WRITER


def test_writing_then_edits_drafted():
    state = new_state({"topic": "x"})
    state["stage"] = "writing"
    state["chapters"] = _chapters("drafted", "drafted")
    assert decide_next(state) == EDITOR


def test_all_edited_goes_to_formatting():
    state = new_state({"topic": "x"})
    state["stage"] = "writing"
    state["chapters"] = _chapters("edited", "edited")
    assert decide_next(state) == FORMATTING


def test_marketing_then_end():
    state = new_state({"topic": "x"})
    state["stage"] = "marketing"
    assert decide_next(state) == MARKETING
    state["stage"] = "done"
    assert decide_next(state) == END
