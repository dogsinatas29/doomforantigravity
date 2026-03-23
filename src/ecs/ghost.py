from abc import ABC, abstractmethod
from typing import Callable

class Ghost(ABC):
    """
    Experimental system that operates on a read-only view of the world.
    Communication back to the core must be done via events.
    """
    
    @abstractmethod
    def update(self, world_proxy, emit: Callable):
        """
        world_proxy: Read-only access to entities and components.
        emit: Function to send events to the core.
        """
        pass

class WorldProxy:
    """Read-only wrapper for the ECS World."""
    def __init__(self, world):
        self._world = world
        
    def get_component(self, entity_id, component_type):
        return self._world.get_component(entity_id, component_type)
        
    def has_component(self, entity_id, component_type):
        return self._world.has_component(entity_id, component_type)
        
    def get_entities_with(self, *component_types):
        return self._world.get_entities_with(*component_types)
        
    @property
    def map_width(self): return getattr(self._world, 'map_width', 0)
    
    @property
    def map_height(self): return getattr(self._world, 'map_height', 0)
    
    @property
    def world_map(self): return getattr(self._world, 'world_map', [])
    
    @property
    def ticks(self): return getattr(self._world, 'ticks', 0)
    
    @property
    def time(self): return getattr(self._world, 'time', 0.0)
