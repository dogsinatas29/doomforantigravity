import json
from dataclasses import asdict
from src.ecs.event_dispatcher import EventDispatcher
from src.ecs.ghost import WorldProxy
from src.utils.math_core import Vector3

class World:
    def __init__(self):
        self.next_entity_id = 0
        self.entities = {} # id -> set(Component Types)
        self.components = {} # Type -> {id -> Component}
        self.systems = [] # List[System] - Core execution order
        self.ghosts = [] # Experimental Systems (Observers only)
        self.dispatcher = EventDispatcher() # New: Centralized Zero-copy Dispatcher
        self.proxy = WorldProxy(self)
        self.texture_registry = ["EMPTY", "DEFAULT_WALL"]
        
        # Deterministic Time Base
        self.ticks = 0
        self.time = 0.0

    def create_entity(self):
        entity_id = self.next_entity_id
        self.entities[entity_id] = {}
        self.next_entity_id += 1
        return entity_id

    def add_component(self, entity_id, component):
        comp_type = type(component)
        self.entities[entity_id][comp_type] = component

    def get_component(self, entity_id, component_type):
        return self.entities[entity_id].get(component_type)

    def has_component(self, entity_id, component_type):
        return component_type in self.entities[entity_id]

    def remove_entity(self, entity_id):
        if entity_id in self.entities:
            del self.entities[entity_id]

    def add_system(self, system: 'System'):
        """Register a system and manage its execution order locally."""
        self.systems.append(system)

    def add_ghost(self, ghost_instance):
        self.ghosts.append(ghost_instance)

    def update(self, dt, engine):
        """
        [Standard Execution Order Contract]
        1. Collect: Capture all emitted events.
        2. Dispatch: Distribute events to Core systems.
        3. Ghosts: Let experimental systems observe and emit.
        4. Systems: Execute core polled logic in fixed sequence.
        """
        self.ticks += 1
        self.time += dt
        
        # 1. Collect Events from input/previous frame
        events = self.dispatcher.collect()
        
        # 2. Batch Dispatch to Core Systems
        self.dispatcher.dispatch(events, self)
        
        # 3. Update Ghosts (Experimental)
        # Ghosts are observers and emitters ONLY.
        # SKIP ghosts in PLAYING mode to ensure input stream integrity.
        is_playing = getattr(engine, 'replay_mode', "NONE") == "PLAYING"
        if not is_playing:
            for ghost in self.ghosts:
                ghost.update(self.proxy, self.emit)
        
        # 4. Final Core Logical Update
        for system in self.systems:
            system.update(self, engine, dt)

    def emit(self, event):
        """Standard path for all entities to communicate state changes."""
        self.dispatcher.emit(event)

    def get_entities_with(self, *component_types):
        """Yield entities that have all specified components."""
        for entity_id, components in self.entities.items():
            if all(ct in components for ct in component_types):
                yield entity_id

    def init_map(self, width, height, vertexes, linedefs, sidedefs):
        self.map_width = width
        self.map_height = height
        self.world_map = [[0 for _ in range(height)] for _ in range(width)]
        self.vertexes = vertexes
        self.linedefs = linedefs
        self.sidedefs = sidedefs
        self.map_bounds = None
        self.linedefs = linedefs if linedefs else []

    def capture_state(self) -> dict:
        """Serialize current ECS state to a serializable dictionary."""
        snapshot = {
            'next_id': self.next_entity_id,
            'entities': {},
            'ticks': self.ticks,
            'time': self.time
        }
        
        for eid, comps in self.entities.items():
            snapshot['entities'][eid] = {}
            for comp_type, comp in comps.items():
                if comp_type.__name__ == "InputState":
                    continue
                
                comp_data = asdict(comp)
                for key, val in comp_data.items():
                    if isinstance(val, Vector3):
                        comp_data[key] = [val.x, val.y, val.z]
                
                snapshot['entities'][eid][comp_type.__name__] = comp_data
        return snapshot

    def get_state_hash(self) -> str:
        """Generate a stable SHA-256 hash of the world state."""
        from src.utils.hash_utils import generate_state_hash
        return generate_state_hash(self.capture_state())

    def save_snapshot(self, filepath):
        """Save ECS state to a JSON file."""
        snapshot = self.capture_state()
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2)

    def restore_state(self, snapshot: dict):
        """Apply a recorded state dictionary to the world."""
        import src.ecs.components as comp_mod
        self.next_entity_id = snapshot['next_id']
        self.ticks = snapshot.get('ticks', 0)
        self.time = snapshot.get('time', 0.0)
        self.entities = {}
        
        for eid_str, comps_dict in snapshot['entities'].items():
            eid = int(eid_str)
            self.entities[eid] = {}
            for comp_name, comp_data in comps_dict.items():
                comp_cls = getattr(comp_mod, comp_name)
                for key, val in comp_data.items():
                    if isinstance(val, list) and len(val) == 3:
                        comp_data[key] = Vector3(*val)
                self.entities[eid][comp_cls] = comp_cls(**comp_data)

    def load_snapshot(self, filepath):
        """Restore from a JSON file."""
        with open(filepath, 'r') as f:
            snapshot = json.load(f)
        self.restore_state(snapshot)
