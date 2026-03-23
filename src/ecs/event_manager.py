from dataclasses import dataclass
from typing import Any, List, Dict, Callable

@dataclass
class Event:
    """Base class for all system events."""
    pass

@dataclass
class MoveEvent(Event):
    entity_id: int
    dx: float = 0.0
    dy: float = 0.0
    dz: float = 0.0

@dataclass
class RotateEvent(Event):
    entity_id: int
    da: float = 0.0 # Delta Angle (Yaw)
    dp: float = 0.0 # Delta Pitch

@dataclass
class FireEvent(Event):
    entity_id: int

@dataclass
class GhostInputEvent(Event):
    entity_id: int
    move_x: float = 0.0
    move_y: float = 0.0
    look_x: float = 0.0
    fire_pressed: bool = False

@dataclass
class DamageEvent(Event):
    target_id: int
    amount: int
    source_id: int = -1

class EventManager:
    def __init__(self):
        self.queue: List[Event] = []
        self.handlers: Dict[type, List[Callable]] = {}

    def emit(self, event: Event):
        """Add an event to the queue."""
        self.queue.append(event)

    def subscribe(self, event_type: type, handler: Callable):
        """Register a handler for a specific event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def process_events(self):
        """Dispatch all queued events to their handlers."""
        current_events = self.queue
        self.queue = []
        
        for event in current_events:
            event_type = type(event)
            if event_type in self.handlers:
                for handler in self.handlers[event_type]:
                    handler(event)
