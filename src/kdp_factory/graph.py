"""Construction du graphe LangGraph reliant superviseur et agents.

Topologie en étoile autour du superviseur :

    START → supervisor → (routage conditionnel) → agent → supervisor → ... → END

Chaque agent revient au superviseur, qui réévalue l'état et choisit la suite.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from .agents import (
    editor_agent,
    formatting_agent,
    market_research_agent,
    marketing_agent,
    outline_agent,
    writer_agent,
)
from .state import BookState
from .supervisor import (
    EDITOR,
    FORMATTING,
    MARKET_RESEARCH,
    MARKETING,
    OUTLINE,
    WRITER,
    route,
    supervisor,
)


def build_graph():
    """Compile et renvoie le graphe exécutable (LangGraph `CompiledGraph`)."""
    g = StateGraph(BookState)

    # Nœuds
    g.add_node("supervisor", supervisor)
    g.add_node(MARKET_RESEARCH, market_research_agent)
    g.add_node(OUTLINE, outline_agent)
    g.add_node(WRITER, writer_agent)
    g.add_node(EDITOR, editor_agent)
    g.add_node(FORMATTING, formatting_agent)
    g.add_node(MARKETING, marketing_agent)

    # Entrée
    g.add_edge(START, "supervisor")

    # Routage conditionnel depuis le superviseur
    g.add_conditional_edges(
        "supervisor",
        route,
        {
            MARKET_RESEARCH: MARKET_RESEARCH,
            OUTLINE: OUTLINE,
            WRITER: WRITER,
            EDITOR: EDITOR,
            FORMATTING: FORMATTING,
            MARKETING: MARKETING,
            END: END,
        },
    )

    # Chaque agent rend la main au superviseur
    for node in (MARKET_RESEARCH, OUTLINE, WRITER, EDITOR, FORMATTING, MARKETING):
        g.add_edge(node, "supervisor")

    return g.compile()
