import math
from src.ecs.components import Transform
from src.utils.math_core import get_sin, get_cos, PI
from src.utils.visual_assets import ANSI_COLORS
from src.utils.ascii_texture_gen import generate_ascii_texture

def render_system(world, engine, dt):
    """
    Textured Raycasting + Scanline Floor.
    """
    player_id = next(world.get_entities_with(Transform), None)
    if player_id is None: return

    transform = world.get_component(player_id, Transform)
    px, py = transform.pos.x, transform.pos.y
    pa = transform.angle
    
    # DEBUG: Print Player Pos and Map Check ONCE
    if not hasattr(engine, "_debug_render_once"):
        world_map = getattr(world, 'world_map', None)
        mw = world.map_width if world_map else 0
        mh = world.map_height if world_map else 0
        grid_val = world_map[int(px)][int(py)] if world_map and 0 <= int(px) < mw and 0 <= int(py) < mh else "OOB"
        print(f"[DEBUG] Render: Pos({px:.1f},{py:.1f}) MapW:{mw} MapH:{mh} GridAtPos:{grid_val}")
        
        # Check a few neighbors
        neighbors = []
        for dx in range(-2, 3):
            nx = int(px) + dx
            if 0 <= nx < mw:
                 neighbors.append(str(world_map[nx][int(py)]))
        print(f"[DEBUG] Neighbors X: {neighbors}")
        engine._debug_render_once = True
    
    # 1. Horizon Calculation (Center + Pitch)
    # Reset horizon to TRUE CENTER to fix perspective
    # User felt walls were "too low" (Horizon too low)
    pitch_offset = int(transform.pitch * engine.height)
    # horizon_shift = 0 (Removed)
    horizon = (engine.height // 2) + pitch_offset
    
    # 2. DEBUG: Ensure Crosshair matches this logic in UI_SYS!

    # World Map is essential for Raycasting
    world_map = getattr(world, 'world_map', None)
    if not world_map: return
    map_w, map_h = world.map_width, world.map_height

    # Texture Patterns (The Converter Logic)
    # Map Texture ID -> ASCII String Pattern
    TEXTURE_ASSET = {
         1: "##==##==++..++..", # Brick / Brown
         2: "||//||//||--||--", # Metal / Grey
         3: "[]..[]..##  ##  ", # Door / Silver
         "DEFAULT": "10101010010010111001010100101010##+==+##"
    }

    # 1. Scanline Floor/Ceiling
    for y in range(engine.height):
        # Floor (Scanline)
        if y > horizon and y % 2 == 0:
             # Scanline Floor
             fill = ANSI_COLORS["DIM_GREY"] + "-" + ANSI_COLORS["RESET"]
             engine.frame_buffer[y] = [fill] * engine.width
        # Ceiling (Empty)
        else:
             engine.frame_buffer[y] = [" "] * engine.width

    # 2. Raycasting
    FOV = PI / 2.0
    half_fov = FOV / 2.0
    step_angle = FOV / engine.width
    start_angle = pa - half_fov

    last_side = 0
    last_wall_dist = 0

    for x in range(engine.width):
        debug_ray = (x == engine.width // 2) and not hasattr(engine, "_debug_ray_done")
        
        ray_angle = start_angle + x * step_angle
        ray_dir_x = get_cos(ray_angle)
        ray_dir_y = get_sin(ray_angle)
        
        # DDA Init
        map_x, map_y = int(px), int(py)
        
        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else 1e30
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else 1e30
        
        step_x = -1 if ray_dir_x < 0 else 1
        side_dist_x = (px - map_x) * delta_dist_x if ray_dir_x < 0 else (map_x + 1.0 - px) * delta_dist_x
        
        step_y = -1 if ray_dir_y < 0 else 1
        side_dist_y = (py - map_y) * delta_dist_y if ray_dir_y < 0 else (map_y + 1.0 - py) * delta_dist_y
        
        hit = False
        side = 0 # 0: NS, 1: EW
        tex_id = 1
        
        # Determine max depth to avoid infinite loop
        # Map is ~1000 wide. 60 was too short!
        max_depth = 2000
        for _ in range(max_depth):
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
                
            if 0 <= map_x < map_w and 0 <= map_y < map_h:
                val = world_map[map_x][map_y]
                if val > 0:
                    hit = True
                    tex_id = val
                    break
            else:
                break
        
        if debug_ray:
             print(f"[DEBUG] Center Ray: Hit={hit} Map({map_x},{map_y}) Side={side} Depth={_}")
             engine._debug_ray_done = True

        if hit:
            # Calc perp dist
            if side == 0:
                perp_wall_dist = (map_x - px + (1 - step_x) / 2) / ray_dir_x
            else:
                perp_wall_dist = (map_y - py + (1 - step_y) / 2) / ray_dir_y
            
            # Correction for fisheye
            # perp_wall_dist *= math.cos(pa - ray_angle) 
            # Note: Math core cos/sin might already be doing something? 
            # Or standard DDA perp_wall_dist IS the corrected distance if using camera plane.
            # But here we used rayDir directly.
            # Correction:
            perp_wall_dist *= math.cos(pa - ray_angle)

            if perp_wall_dist < 0.1: perp_wall_dist = 0.1
            
            # Wall Height (Vertical Scaling applied)
            # Doom Rule: Wall Height ~20x Grid Unit (128/5)
            # Adjusted for ASCII Aspect Ratio (2x height for characters) -> ~10-15
            WALL_SCALE = 15.0
            line_height = int((engine.height / perp_wall_dist) * WALL_SCALE)
            
            draw_start = -line_height // 2 + horizon
            draw_end = line_height // 2 + horizon
            
            draw_start_clamped = max(0, draw_start)
            draw_end_clamped = min(engine.height, draw_end)
            
            # Wall X (Texture Mapping)
            if side == 0:
                wall_x = py + perp_wall_dist * ray_dir_y
            else:
                wall_x = px + perp_wall_dist * ray_dir_x
            
            wall_x -= math.floor(wall_x)
            
            # Select Texture Pattern (Procedural)
            pattern = "##++"
            wall_color = ANSI_COLORS["WHITE"]
            
            # Lookup texture name from registry
            texture_registry = getattr(world, 'texture_registry', [])
            if 0 < tex_id < len(texture_registry):
                tex_name = texture_registry[tex_id]
                pattern, wall_color = generate_ascii_texture(tex_name)
            
            tex_width = len(pattern)
            
            # Texture X
            tex_x = int(wall_x * tex_width)
            if side == 0 and ray_dir_x > 0: tex_x = tex_width - tex_x - 1
            if side == 1 and ray_dir_y < 0: tex_x = tex_width - tex_x - 1
            
            # Draw Vertical Strip
            for y in range(draw_start_clamped, draw_end_clamped):
                # Matrix Style: Vertical texture mapping
                # Slow down Y repitition to prevent barcode noise
                # Use (tex_x) primarily, with slight Y offset for diagonal feel?
                # Let's simple use column mapping for now for clean 'Texture' look
                char_idx = tex_x % tex_width
                
                # Optional: Diagonal rain effect
                # char_idx = (tex_x + (y // 2)) % tex_width
                
                char = pattern[char_idx]
                
                # Shading
                # Distance based dimming
                dim_char = char
                if perp_wall_dist > 15.0:
                    dim_char = "."
                elif perp_wall_dist > 8.0:
                    if y % 2 == 0: dim_char = ":"
                    
                # Edge highlight
                if x > 0 and abs(perp_wall_dist - last_wall_dist) > 1.0:
                    dim_char = "|"
                
                # Side Shading (Darken Color)
                final_color = wall_color
                if side == 1:
                     # Simple logic: If white, make grey. If color, keep color but maybe dim char?
                     # Let's just keep color constant but change char for side?
                     # No, let's use ANSI DIM if available or just rely on char difference.
                     # Actually we can't easily darken ANSI codes without a lookup table.
                     pass 
                
                # Apply Texture Pattern
                engine.frame_buffer[y][x] = final_color + dim_char + ANSI_COLORS["RESET"]
            
            last_wall_dist = perp_wall_dist
            last_side = side

def render_automap(world, engine):
    """2D Top-down Mini-map Overlay."""
    player_id = next(world.get_entities_with(Transform), None)
    if not player_id: return

    transform = world.get_component(player_id, Transform)
    px, py = int(transform.pos.x), int(transform.pos.y)
    p_angle = transform.angle % (2 * PI)
    
    if p_angle < PI/4 or p_angle > 7*PI/4: arrow = ">"
    elif p_angle < 3*PI/4: arrow = "^" 
    elif p_angle < 5*PI/4: arrow = "<"
    else: arrow = "v"

    # Screen Center
    cx, cy = engine.width // 2, engine.height // 2
    
    # -------------------------------------------------------------
    # DIAGNOSTIC BACKGROUND & BORDER
    # -------------------------------------------------------------
    for y in range(engine.height):
        for x in range(engine.width):
            # Background pattern to verify buffer coverage
            if x % 2 == 0 and y % 2 == 0:
                engine.frame_buffer[y][x] = ANSI_COLORS["DIM_GREY"] + "·" + ANSI_COLORS["RESET"]
            
            # Border
            if x == 0 or x == engine.width - 1 or y == 0 or y == engine.height - 1:
                engine.frame_buffer[y][x] = ANSI_COLORS["WHITE"] + "#" + ANSI_COLORS["RESET"]
            
            # Center Crosshair (Player fixed position)
            if x == cx or y == cy:
                engine.frame_buffer[y][x] = ANSI_COLORS["DARK_RED"] + "+" + ANSI_COLORS["RESET"]

    # -------------------------------------------------------------
    # VECTOR RENDERING
    # -------------------------------------------------------------
    vertexes = getattr(world, 'vertexes', [])
    linedefs = getattr(world, 'linedefs', [])
    bounds = getattr(world, 'map_bounds', None)
    
    if vertexes and linedefs and bounds:
        min_x, min_y, SCALE = bounds
        # Safe Zoom
        ZOOM = 4.0
        vis_range_x = engine.width * ZOOM
        vis_range_y = engine.height * ZOOM
        
        def to_screen(gx, gy):
            sx = cx + int((gx - px) / ZOOM)
            sy = cy - int((gy - py) / ZOOM)
            return sx, sy

        for line in linedefs:
            v1 = vertexes[line[0]]
            v2 = vertexes[line[1]]
            
            gx1 = (v1[0] - min_x) * SCALE + 5
            gy1 = (v1[1] - min_y) * SCALE + 5
            gx2 = (v2[0] - min_x) * SCALE + 5
            gy2 = (v2[1] - min_y) * SCALE + 5
            
            if (abs(gx1 - px) > vis_range_x and abs(gx2 - px) > vis_range_x) or \
               (abs(gy1 - py) > vis_range_y and abs(gy2 - py) > vis_range_y):
                continue
                
            sx1, sy1 = to_screen(gx1, gy1)
            sx2, sy2 = to_screen(gx2, gy2)
            draw_line(engine, sx1, sy1, sx2, sy2, ANSI_COLORS["WHITE"] + "*" + ANSI_COLORS["RESET"])

    # Draw Stats at CENTER (to avoid scrolling off-screen)
    v_count = len(vertexes)
    l_count = len(linedefs)
    txt = f"[ AUTOMAP : V:{v_count} L:{l_count} ]"
    start_x = cx - (len(txt) // 2)
    for i, c in enumerate(txt):
        engine.frame_buffer[cy - 2][start_x + i] = ANSI_COLORS["WHITE"] + c + ANSI_COLORS["RESET"]
    
    # Player Arrow
    engine.frame_buffer[cy][cx] = ANSI_COLORS["BLOOD_RED"] + arrow + ANSI_COLORS["RESET"]

def draw_line(engine, x0, y0, x1, y1, char):
    """Bresenham's Line Algo for Terminal Buffer."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    while True:
        if 0 <= x0 < engine.width and 0 <= y0 < engine.height:
            engine.frame_buffer[y0][x0] = char
            
        if x0 == x1 and y0 == y1:
            break
            
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
