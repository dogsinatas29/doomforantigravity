import math
from src.ecs.components import Transform, Render, PhysicsMode, PhysicsModeType
from src.utils.math_core import get_sin, get_cos, PI

ASCII_RAMP = " .:-=+*#%@"

def render_system(world, engine, dt):
    """Raycasting Render System using World Grid Map."""
    player_id = next(world.get_entities_with(Transform), None)
    if player_id is None:
        return
    
    transform = world.get_component(player_id, Transform)
    phys_mode = world.get_component(player_id, PhysicsMode)
    
    pos = transform.pos
    player_angle = transform.angle
    
    # Grid Map access
    world_map = getattr(world, 'world_map', None)
    if not world_map:
        return
        
    map_w = world.map_width
    map_h = world.map_height
    
    FOV = PI / 3
    STEP_ANGLE = FOV / engine.width
    
    for x in range(engine.width):
        ray_angle = player_angle - (FOV / 2.0) + (x * STEP_ANGLE)
        
        # Ray direction
        ray_dir_x = get_cos(ray_angle)
        ray_dir_y = get_sin(ray_angle)
        
        # Current grid position
        map_x = int(pos.x)
        map_y = int(pos.y)
        
        # Length of ray from one x or y-side to next x or y-side
        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else 1e30
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else 1e30
        
        # Direction to step in x or y-direction (either +1 or -1)
        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (pos.x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - pos.x) * delta_dist_x
            
        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (pos.y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - pos.y) * delta_dist_y
            
        # DDA
        max_ray_steps = 256
        hit = False
        side = 0 # 0 for X, 1 for Y
        
        for _ in range(max_ray_steps):
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
                
            if 0 <= map_x < map_w and 0 <= map_y < map_h:
                if world_map[map_x][map_y] > 0:
                    hit = True
                    break
            else:
                break
        
        if hit:
            # Calculate perpendicular distance (standard DDA)
            if side == 0:
                perp_wall_dist = (map_x - pos.x + (1 - step_x) / 2) / ray_dir_x
            else:
                perp_wall_dist = (map_y - pos.y + (1 - step_y) / 2) / ray_dir_y
            
            # Distance must be at least 0.1
            perp_wall_dist = max(0.1, perp_wall_dist)
            
            # Proportional scaling for terminal height
            # Doom wall height 128 -> Scale 0.20 -> 25.6 units
            wall_h_scaled = 25.6
            fov_multiplier = engine.height * 0.9
            
            # Horizon line (center + pitch)
            horizon = engine.height // 2 + int(transform.pitch * engine.height)
            
            # Projection: Y = horizon +/- (Z_diff / dist) * fov_multiplier
            # Floor (Z=0)
            floor_y = horizon + int((pos.z / perp_wall_dist) * fov_multiplier)
            # Ceiling (Z=25.6)
            ceil_y = horizon - int(((wall_h_scaled - pos.z) / perp_wall_dist) * fov_multiplier)
            
            # Shading
            SHADE_DIST = 80.0
            color_idx = max(0, min(len(ASCII_RAMP) - 1, int((1.0 - perp_wall_dist / SHADE_DIST) * (len(ASCII_RAMP) - 1))))
            wall_char = ASCII_RAMP[color_idx]
            
            for y in range(max(0, ceil_y), min(engine.height, floor_y)):
                engine.frame_buffer[y][x] = wall_char

    if phys_mode and phys_mode.mode == PhysicsModeType.INVERTED:
        engine.frame_buffer.reverse()
