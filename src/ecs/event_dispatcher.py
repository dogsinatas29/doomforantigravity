from typing import List, Dict, Type
from src.ecs.event_manager import Event

class EventDispatcher:
    """
    Zero-copy Batch Event Dispatcher for SYNAPSE.
    Optimized for high-performance terminal rendering.
    """
    
    # Hard cap for both ingestion and dispatch to ensure 33ms frame budget.
    MAX_EVENTS_PER_FRAME = 256
    EVENT_BUDGET = 256 

    def __init__(self):
        self.queue: List[Event] = []

    def emit(self, event: Event):
        """Add an event to the queue. Best-effort: drops if over capacity."""
        if len(self.queue) < self.MAX_EVENTS_PER_FRAME:
            self.queue.append(event)

    def collect(self) -> List[Event]:
        """Transfer current frame's events and reset. No allocation if empty."""
        if not self.queue:
            return []
        events = self.queue
        self.queue = []
        return events

    def dispatch(self, events: List[Event], world: 'World'):
        """Route batches of events to systems within the EVENT_BUDGET."""
        if not events:
            return

        # 1. Budgeting: Only process up to the defined budget
        # Remaining events are discarded (Best-effort delivery)
        to_process = events[:self.EVENT_BUDGET]
        
        # 2. Batch events by type (O(N))
        event_buffer: Dict[Type[Event], List[Event]] = {}
        for event in to_process:
            etype = type(event)
            if etype not in event_buffer:
                event_buffer[etype] = []
            event_buffer[etype].append(event)

        # 3. Dispatch zero-copy batches to core systems
        for system in world.systems:
            for etype in system.EVENTS:
                batch = event_buffer.get(etype)
                if batch:
                    system.handle_events(batch, world)
