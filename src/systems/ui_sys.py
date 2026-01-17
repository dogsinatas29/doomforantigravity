
from src.ecs.components import Transform, Stats
from src.utils.visual_assets import FACE_ASSETS, WEAPON_ASSETS, ANSI_COLORS

def ui_system(world, engine, dt):
    """
    Renders the HUD and Weapon Overlay.
    Modifies engine.frame_buffer directly.
    """
    # 0. Crosshair (Horizon Aligned)
    cx = engine.width // 2
    
    # Calculate Horizon exactly as render_sys does
    # This ensures Crosshair points to the geometric center of 3D view
    player_id = next(world.get_entities_with(Transform), None)
    pitch_offset = 0
    if player_id:
        trans = world.get_component(player_id, Transform)
        pitch_offset = int(trans.pitch * engine.height)
        
    # Horizon Shift REMOVED (Synced with render_sys)
    horizon_shift = 0 
    cy = (engine.height // 2) + pitch_offset
    
    # Clamp to viewport
    hud_height = 6
    if 0 <= cx < engine.width and 0 <= cy < (engine.height - hud_height):
        # Use Bright White for max contrast
        engine.frame_buffer[cy][cx] = ANSI_COLORS["WHITE"] + "+" + ANSI_COLORS["RESET"]

    # 1. Weapon Overlay (Render BEFORE HUD)
    # -------------------------------------
    # Draw weapon CENTERED at bottom
    
    weapon_key = "SHOTGUN_IDLE"
    weapon_sprite = WEAPON_ASSETS.get(weapon_key, [])
    
    if weapon_sprite:
        sprite_h = len(weapon_sprite)
        sprite_w = len(weapon_sprite[0]) if sprite_h > 0 else 0
        
        # Position: Center align
        # Y: Bottom of Viewport (Height - HUD - SpriteHeight)
        start_y = engine.height - hud_height - sprite_h
        # X: Center
        start_x = (engine.width // 2) - (sprite_w // 2)
        
        for r, row_str in enumerate(weapon_sprite):
            draw_y = start_y + r
            if 0 <= draw_y < (engine.height - hud_height):
                for c, char in enumerate(row_str):
                    draw_x = start_x + c
                    if 0 <= draw_x < engine.width:
                        # WAD Converter uses " " for transparent?
                        # Check wad_loader: it returns " " for None.
                        if char != " ": 
                            engine.frame_buffer[draw_y][draw_x] = char

    # 2. HUD Logic (Bottom Area)
    # --------------------------
    player_id = next(world.get_entities_with(Stats), None)
    hp = 0
    max_hp = 100
    ammo = 0
    armor = 0
    
    if player_id is not None:
        stats = world.get_component(player_id, Stats)
        hp = stats.hp
        ammo = stats.ammo
        armor = stats.armor
        # Assuming max_hp is 100 for now
    
    # Calculate Face State
    hp_pct = (hp / max_hp) * 100
    face_key = "HEALTHY"
    if hp_pct < 20: face_key = "CRITICAL"
    elif hp_pct < 40: face_key = "MESSY"
    elif hp_pct < 60: face_key = "BLEEDING"
    elif hp_pct < 80: face_key = "ANGRY"
    
    face_sprite = FACE_ASSETS.get(face_key, FACE_ASSETS["HEALTHY"])
    
    # Draw HUD Frame
    hud_start_y = engine.height - hud_height
    
    # Fill HUD background
    for y in range(hud_start_y, engine.height):
        # Draw border
        if y == hud_start_y:
            line_str = "+" + "-" * (engine.width - 2) + "+"
        else:
             line_str = "|" + " " * (engine.width - 2) + "|"
             
        for x, char in enumerate(line_str):
            if x < engine.width:
                engine.frame_buffer[y][x] = char

    # Draw Data
    # Helper to write string at pos
    def draw_text(x, y, text, color=None):
        if y >= engine.height or y < 0: return
        for i, char in enumerate(text):
            if x + i < engine.width - 1:
                # Apply color if given, but remember frame_buffer stores strings
                # Assuming raw terminal output handle ANSI
                 val = (color + char + ANSI_COLORS["RESET"]) if color else char
                 engine.frame_buffer[y][x + i] = val

    # AMMO
    draw_text(3, hud_start_y + 1, "AMMO")
    draw_text(3, hud_start_y + 2, f"{ammo:03d}")
    
    # HEALTH
    draw_text(15, hud_start_y + 1, "HEALTH")
    draw_text(15, hud_start_y + 2, f"{int(hp_pct)}%")
    
    # ARMOR
    draw_text(engine.width - 25, hud_start_y + 1, "ARMOR")
    draw_text(engine.width - 25, hud_start_y + 2, f"{armor}%")

    # FACE (Center)
    face_x = engine.width // 2 - 8
    face_y = hud_start_y + 1
    
    for r, row_str in enumerate(face_sprite):
        draw_text(face_x, face_y + r, row_str)

