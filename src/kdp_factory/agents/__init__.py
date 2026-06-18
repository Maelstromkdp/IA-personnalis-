"""Les 6 agents du système, chacun exposé comme un nœud LangGraph.

Chaque agent est une fonction `(state) -> dict` : il lit le `BookState`, appelle
le LLM, et renvoie une mise à jour partielle de l'état. Aucune dépendance directe
entre agents — toute la communication passe par l'état.
"""

from .market_research import market_research_agent
from .outline import outline_agent
from .writer import writer_agent
from .editor import editor_agent
from .formatting import formatting_agent
from .marketing import marketing_agent

__all__ = [
    "market_research_agent",
    "outline_agent",
    "writer_agent",
    "editor_agent",
    "formatting_agent",
    "marketing_agent",
]
