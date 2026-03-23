from abc import ABC, abstractmethod
from typing import List, Type, Tuple, TYPE_CHECKING
from src.ecs.event_manager import Event

if TYPE_CHECKING:
    from src.ecs.world import World
    from src.engine import GameEngine

class System(ABC):
    """
    Standard interface for all ECS systems in DooM for AntigravitY.
    Each system acts as a complete unit of logic with a defined lifecycle.
    """
    
    # Static tuple of Event types this system handles in batches.
    # Using tuple for immutability and performance.
    EVENTS: Tuple[Type[Event], ...] = ()

    @abstractmethod
    def handle_events(self, events: List[Event], world: 'World'):
        """
        Process a batch of events of a specific type.
        Designed for zero-copy performance in hot paths.
        """
        pass

    @abstractmethod
    def update(self, world: 'World', engine: 'GameEngine', dt: float):
        """
        Continuous frame-based logic (e.g., gravity, animation).
        Executed in the order defined in World.systems.
        """
        pass
