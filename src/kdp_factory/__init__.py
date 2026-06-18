"""KDP Factory — système multi-agents pour la production de livres Amazon KDP.

Orchestration LangGraph + Claude (Anthropic). Voir `graph.build_graph` pour
le point d'entrée principal et `state.BookState` pour l'état partagé.
"""

from .state import BookState
from .graph import build_graph

__all__ = ["BookState", "build_graph"]
__version__ = "0.1.0"
