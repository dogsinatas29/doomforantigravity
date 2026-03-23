import math
from typing import List, TYPE_CHECKING
from src.ecs.system import System
from src.ecs.components import Transform, Motion, PhysicsMode, PhysicsModeType, InputState
from src.ecs.event_manager import Event, MoveEvent, RotateEvent

if TYPE_CHECKING:
    from src.ecs.world import World
    from src.engine import GameEngine

class PhysicsSystem(System):
    """
    Stabilized Physics System for SYNAPSE.
    Uses Fixed Timestep Accumulator and Axis-Separated Collision Projection.
    """
    
    EVENTS = () # Driven by InputState, no event interests for move/rotate.

    def __init__(self):
        # 1. Fixed Timestep Configuration
        self.FIXED_DT = 1.0 / 60.0
        self.accumulator = 0.0
        
        # 2. Physics Constants
        self.base_gravity = 25.0
        self.friction_normal = 0.5
        self.friction_zero_g = 0.95
        self.radius = 0.45
        self.EPSILON = 1e-4

    def handle_events(self, events: List[Event], world: 'World'):
        """Still handle jumps via events but movement via InputState."""
        for event in events:
            if isinstance(event, MoveEvent):
                # We still handle Z-boost (jump) as an impulse event.
                if event.dz != 0:
                    motion = world.get_component(event.entity_id, Motion)
                    if motion: motion.vel.z += event.dz

    def update(self, world: 'World', engine: 'GameEngine', dt: float):
        """Orchestrate Fixed Timestep loop."""
        dt = min(dt, 0.1)
        self.accumulator += dt
        
        while self.accumulator >= self.FIXED_DT:
            self._physics_step(world, engine, self.FIXED_DT)
            self.accumulator -= self.FIXED_DT

    def _physics_step(self, world, engine, dt):
        """Deterministic physics sub-step using InputState."""
        world_map = getattr(world, 'world_map', None)
        if not world_map: return
            
        for entity_id in world.get_entities_with(Transform, Motion, InputState):
            transform = world.get_component(entity_id, Transform)
            motion = world.get_component(entity_id, Motion)
            phys_mode = world.get_component(entity_id, PhysicsMode)
            input_state = world.get_component(entity_id, InputState)
            
            # --- 1. Apply Intent-based Forces ---
            if input_state.move_x != 0:
                motion.vel.x += input_state.move_x * math.cos(transform.angle)
                motion.vel.y += input_state.move_x * math.sin(transform.angle)
            if input_state.move_y != 0:
                motion.vel.x += input_state.move_y * math.cos(transform.angle + 1.5708)
                motion.vel.y += input_state.move_y * math.sin(transform.angle + 1.5708)
            
            # Rotation (Yaw)
            transform.angle += input_state.look_x
            
            # --- 2. Environment Forces & Friction ---
            gravity = 0.0
            friction = self.friction_normal
            if phys_mode:
                if phys_mode.mode == PhysicsModeType.NORMAL:
                    gravity = -self.base_gravity * dt
                    friction = self.friction_normal
                elif phys_mode.mode == PhysicsModeType.INVERTED:
                    gravity = self.base_gravity * dt
                    friction = self.friction_normal
                elif phys_mode.mode == PhysicsModeType.ZERO_G:
                    gravity = 0.0
                    friction = self.friction_zero_g
            
            motion.vel.z += gravity
            motion.vel.x *= friction
            motion.vel.y *= friction
            motion.vel.z *= friction

            # Micro-movement suppression (Epsilon)
            if abs(motion.vel.x) < self.EPSILON: motion.vel.x = 0
            if abs(motion.vel.y) < self.EPSILON: motion.vel.y = 0
            if abs(motion.vel.z) < self.EPSILON: motion.vel.z = 0

            # --- 3. Axis-Separated Collision Resolution ---
            radius = self.radius
            margin = 0.1 
            
            def is_occupied(x, y):
                gx, gy = int(x), int(y)
                if not (0 <= gx < world.map_width and 0 <= gy < world.map_height):
                    return True 
                return world.world_map[gx][gy] > 0

            # [Resolve X Axis]
            transform.pos.x += motion.vel.x
            check_x = transform.pos.x + (radius if motion.vel.x > 0 else -radius)
            if is_occupied(check_x, transform.pos.y - radius + margin) or \
               is_occupied(check_x, transform.pos.y + radius - margin):
                if motion.vel.x > 0:
                    transform.pos.x = math.floor(check_x) - radius - self.EPSILON
                else:
                    transform.pos.x = math.ceil(check_x) + radius + self.EPSILON
                motion.vel.x = 0

            # [Resolve Y Axis]
            transform.pos.y += motion.vel.y
            check_y = transform.pos.y + (radius if motion.vel.y > 0 else -radius)
            if is_occupied(transform.pos.x - radius + margin, check_y) or \
               is_occupied(transform.pos.x + radius - margin, check_y):
                if motion.vel.y > 0:
                    transform.pos.y = math.floor(check_y) - radius - self.EPSILON
                else:
                    transform.pos.y = math.ceil(check_y) + radius + self.EPSILON
                motion.vel.y = 0

            # [Resolve Z Axis]
            transform.pos.z += motion.vel.z
            if transform.pos.z < 0:
                transform.pos.z = 0
                motion.vel.z = 0
            elif transform.pos.z > 30.0:
                transform.pos.z = 30.0
                motion.vel.z = 0
