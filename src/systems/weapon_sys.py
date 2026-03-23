from typing import List, TYPE_CHECKING
from src.ecs.system import System
from src.ecs.components import Weapon, Stats, InputState

if TYPE_CHECKING:
    from src.ecs.world import World
    from src.engine import GameEngine
    from src.ecs.event_manager import Event

class WeaponSystem(System):
    """
    Stabilized Weapon System.
    Logic is driven by InputState component (transient intent).
    """
    
    # Driven by InputState, so no event interests needed for basic firing.
    EVENTS = ()

    def __init__(self):
        self.FIXED_DT = 1.0 / 60.0
        self.accumulator = 0.0
        self.fire_delay = 0.6 

    def handle_events(self, events: List['Event'], world: 'World'):
        """No-op: firing is now intent-driven via InputState."""
        pass

    def update(self, world: 'World', engine: 'GameEngine', dt: float):
        """Fixed-rate logic for weapon gating."""
        dt = min(dt, 0.1)
        self.accumulator += dt
        
        while self.accumulator >= self.FIXED_DT:
            self._weapon_step(world, engine, self.FIXED_DT)
            self.accumulator -= self.FIXED_DT

    def _weapon_step(self, world: 'World', engine: 'GameEngine', dt: float):
        """Logic loop iterating over entities with Weapon and InputState components."""
        for entity_id in world.get_entities_with(Weapon, InputState):
            weapon = world.get_component(entity_id, Weapon)
            input_state = world.get_component(entity_id, InputState)
            
            if weapon.state == "IDLE":
                if input_state.fire_pressed and not input_state.prev_fire_pressed:
                    weapon.state = "FIRING"
            
            # Edge sync
            input_state.prev_fire_pressed = input_state.fire_pressed

            if weapon.state == "FIRING":
                self._fire(entity_id, world)
                weapon.state = "COOLDOWN"
                weapon.cooldown = self.fire_delay

            elif weapon.state == "COOLDOWN":
                weapon.cooldown -= dt
                if weapon.cooldown <= 0:
                    weapon.state = "IDLE"

    def _fire(self, entity_id: int, world: 'World'):
        """Executed exactly once when state hits FIRING."""
        # TODO: Implement hitscan/projectile
        pass
