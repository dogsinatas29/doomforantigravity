from src.ecs.ghost import Ghost
from src.ecs.components import Transform, Render, Stats
from src.ecs.event_manager import GhostInputEvent
import math
import random

class ReactiveGhost(Ghost):
    """
    1st Stage AI (Reactive). 
    Stateless, reacts purely based on immediate world proxy data.
    - If wall ahead: Rotate randomly.
    - If player at distance: Look toward player.
    - If player close: Back off.
    - Otherwise: Strafe periodically.
    """
    def update(self, world_proxy, emit):
        # 1. Self identification (assuming we control 'G' sprites)
        ghost_ids = []
        player_id = None
        
        for eid in world_proxy.get_entities_with(Transform, Render):
            render = world_proxy.get_component(eid, Render)
            if render.sprite_char == "G":
                ghost_ids.append(eid)
            elif render.sprite_char == "P" or render.sprite_char == "@":
                player_id = eid

        if not player_id:
            return # No prey found

        player_tr = world_proxy.get_component(player_id, Transform)
        
        for gid in ghost_ids:
            # 2. Local variables for decision making
            tr = world_proxy.get_component(gid, Transform)
            
            dx = player_tr.x - tr.x
            dy = player_tr.y - tr.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            # 3. Simple Stateless Reactive Logic
            move_x, move_y = 0.0, 0.0
            look_x = 0.0
            
            # Decision Tree
            if dist < 3.0: 
                # Too close: Back up
                move_y = -0.5
            elif dist > 10.0:
                # Too far: Move toward player
                move_y = 0.8
            else:
                # Mid distance: Strafe + look
                move_x = math.sin(world_proxy.time * 2.0) * 0.5
            
            # Simple Look-at-Player logic
            # (In raycasting doom, rotation is angle based)
            target_angle = math.atan2(dy, dx)
            angle_diff = target_angle - tr.angle
            
            # Normalize angle diff to [-pi, pi]
            while angle_diff > math.pi: angle_diff -= 2 * math.pi
            while angle_diff < -math.pi: angle_diff += 2 * math.pi
            
            # Proportional rotation (Reactive look)
            look_x = angle_diff * 0.1 # Limit turn speed
            
            # 4. Wall Detection (Reactive avoidance)
            # Rough check: if we move we might hit?
            # We'll check the map ahead
            look_ahead_dist = 1.0
            ax = tr.x + math.cos(tr.angle) * look_ahead_dist
            ay = tr.y + math.sin(tr.angle) * look_ahead_dist
            
            # Check map
            m_width = world_proxy.map_width
            m_height = world_proxy.map_height
            w_map = world_proxy.world_map
            
            if 0 <= int(ax) < m_width and 0 <= int(ay) < m_height:
                if w_map[int(ay)][int(ax)] != 0: # Hit wall
                    # Force turn!
                    look_x = 0.5 # Sharp turn
                    move_y = -0.2 # Back up slightly
            
            # 5. Emit intent
            emit(GhostInputEvent(
                entity_id=gid,
                move_x=move_x,
                move_y=move_y,
                look_x=look_x,
                fire_pressed=(dist < 8.0 and world_proxy.ticks % 20 == 0)
            ))
