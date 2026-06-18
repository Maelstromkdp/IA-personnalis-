"""Assemble le graphe LangGraph : superviseur en étoile + 6 agents."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from ..agents import (
    editor_agent,
    formatting_agent,
    market_research_agent,
    marketing_agent,
    outline_agent,
    writer_agent,
)
from ..book_state import BookState
from .supervisor import (
    EDITOR,
    FORMATTING,
    MARKETING,
    OUTLINE,
    RESEARCH,
    WRITER,
    route,
    supervisor,
)


def build_graph():
    """Compile et renvoie le graphe exécutable."""
    g = StateGraph(BookState)

    g.add_node("supervisor", supervisor)
    g.add_node(RESEARCH, market_research_agent)
    g.add_node(OUTLINE, outline_agent)
    g.add_node(WRITER, writer_agent)
    g.add_node(EDITOR, editor_agent)
    g.add_node(FORMATTING, formatting_agent)
    g.add_node(MARKETING, marketing_agent)

    g.add_edge(START, "supervisor")
    g.add_conditional_edges(
        "supervisor",
        route,
        {
            RESEARCH: RESEARCH,
            OUTLINE: OUTLINE,
            WRITER: WRITER,
            EDITOR: EDITOR,
            FORMATTING: FORMATTING,
            MARKETING: MARKETING,
            END: END,
        },
    )
    for node in (RESEARCH, OUTLINE, WRITER, EDITOR, FORMATTING, MARKETING):
        g.add_edge(node, "supervisor")

    return g.compile()
