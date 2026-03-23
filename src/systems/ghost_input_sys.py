from typing import List, TYPE_CHECKING
from src.ecs.system import System
from src.ecs.components import InputState
from src.ecs.event_manager import GhostInputEvent

if TYPE_CHECKING:
    from src.ecs.world import World
    from src.engine import GameEngine
    from src.ecs.event_manager import Event

class GhostInputSystem(System):
    """
    Core system that translates GhostInputEvents into InputState component updates.
    This maintains the 'Read-only + Emit-only' boundary for Ghosts.
    """
    
    EVENTS = (GhostInputEvent,)

    def handle_events(self, events: List['Event'], world: 'World'):
        """Apply ghost intent to entity InputState."""
        for event in events:
            if isinstance(event, GhostInputEvent):
                input_state = world.get_component(event.entity_id, InputState)
                if input_state:
                    # Ghost input is additive or overriding for that frame.
                    # Usually, Ghosts have their own entities, so this is clean.
                    input_state.move_x = event.move_x
                    input_state.move_y = event.move_y
                    input_state.look_x = event.look_x
                    input_state.fire_pressed = event.fire_pressed

    def update(self, world: 'World', engine: 'GameEngine', dt: float):
        """Logic execution is handled in handle_events for Ghost intents."""
        pass
