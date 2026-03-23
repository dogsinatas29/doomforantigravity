from src.ecs.ghost import Ghost
from src.ecs.components import Transform, Render
from src.ecs.event_manager import GhostInputEvent
import math
import time

class DebugGhost(Ghost):
    """
    Experimental Ghost AI.
    Generates circular movement intent for any entity tagged as 'G' (Ghost).
    """
    def update(self, world_proxy, emit):
        # 1. Logic: Calculate circular movement pattern using deterministic time
        elapsed = world_proxy.time
        mx = math.cos(elapsed * 2.0) * 0.4
        my = math.sin(elapsed * 2.0) * 0.4
        
        # 2. Intent: Emit to any entity we control (Self-discovery)
        # For this experiment, we target entities with a specific Render char.
        for eid in world_proxy.get_entities_with(Transform, Render):
            render = world_proxy.get_component(eid, Render)
            if render.sprite_char == "G": # Ghost tag
                emit(GhostInputEvent(
                    entity_id=eid,
                    move_x=mx,
                    move_y=my,
                    look_x=0.05,
                    fire_pressed=(int(elapsed) % 3 == 0) # Fire every 3s
                ))
