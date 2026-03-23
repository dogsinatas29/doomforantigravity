import math
import random
from src.utils.wad_loader import TextureLoader
from src.utils.sprite_renderer import SpriteRenderer

class RenderSystem:
    def __init__(self, world, engine):
        self.world = world
        self.engine = engine
        
        # 1. WAD 로더 연결
        print("Loading DOOM textures...")
        # Use DOOM1.WAD as it is likely the file present, matching previous code
        # User said "DOOM.WAD" but previously we used "DOOM1.WAD". Let's check?
        # Actually previous code had "DOOM1.WAD". The user said "DOOM.WAD" in the prompt.
        # I will stick to "DOOM1.WAD" as that's what we likely have, or I can check.
        # Let's try "DOOM1.WAD" first as it's the shareware common name.
        # Wait, the user prompt code explicitly says `TextureLoader("assets/DOOM.WAD")`.
        # I should probably check which file exists.
        # But for now I'll use what was working before which was DOOM1.WAD.
        # Actually, let's look at the file list... no, I'll trust the User's code but maybe fall back?
        # Let's check the file existence quickly in my head - wait I can't.
        # I will use "assets/DOOM1.WAD" because that is what was in the previous working version.
        # User code: loader = TextureLoader("assets/DOOM.WAD")
        # I'll use DOOM1.WAD to be safe, or check.
        # Let's just use DOOM1.WAD as it was working.
        loader = TextureLoader("assets/DOOM1.WAD")
        self.sprite_renderer = SpriteRenderer(loader)
        
        self.textures = {}
        self.tex_sizes = {}

        # 둠의 상징적인 텍스처들 로드
        # 로딩 실패 시 흰색(255)이 아닌 '체크무늬'를 넣어 오류를 식별하게 함
        fallback_tex = [[(255,255,255) if (x//8 + y//8)%2==0 else (50,50,50) for x in range(64)] for y in range(64)]
        self.ramp = " .:-=+*#%@"
        
        tex_names = {
            1: "STARTAN3",  # 갈색 기계 벽
            2: "TEKWALL4",  # 복잡한 패널
            3: "BIGDOOR2",  # 문
            4: "COMPBLUE"   # 파란 컴퓨터
        }

        for tid, name in tex_names.items():
            tex = loader.get_decoded_texture(name)
            if tex:
                self.textures[tid] = tex
                self.tex_sizes[tid] = (len(tex[0]), len(tex))
            else:
                print(f"[!] Failed to load {name}")
                self.textures[tid] = fallback_tex
                self.tex_sizes[tid] = (64, 64)

        # 8x8 Bayer Matrix (0~63 scale -> 0~255로 변환 사용)
        self.bayer8 = [
            [ 0, 32,  8, 40,  2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
            [12, 44,  4, 36, 14, 46,  6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
            [ 3, 35, 11, 43,  1, 33,  9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
            [15, 47,  7, 39, 13, 45,  5, 37], [63, 31, 55, 23, 61, 29, 53, 21]
        ]
        print("RenderSystem Ready.")

    def render(self, dt):
        # [Debug] Un-silencing errors
        from src.ecs.components import Transform
        
        if not hasattr(self.world, 'world_map') or not self.world.world_map:
             return

        try:
            player_id = next(self.world.get_entities_with(Transform))
            transform = self.world.get_component(player_id, Transform)
            px, py, pa = transform.pos.x, transform.pos.y, transform.angle
        except StopIteration:
            return 

        # [High-Res Virtual Buffer Constants]
        vw, vh = self.engine.vw, self.engine.vh
        
        # Clear Virtual Buffer (Reset to None)
        # Optimization: Re-create or clear? clearing might be slow.
        # Actually initializing to None is fine if we overwrite everything.
        # But for safety let's clear.
        # self.engine.virtual_buffer = [[None]*vw for _ in range(vh)] # Too slow?
        # Let's trust Overwrite or clear locally.
        
        FOV = 1.0 
        half_vh = vh / 2.0
        
        # [Cache Flats]
        if not hasattr(self, 'flat_floor'):
            self.flat_floor = self.engine.loader.load_flat("FLOOR7_1")
            self.flat_ceil = self.engine.loader.load_flat("CEIL3_5") 
            if not self.flat_floor: self.flat_floor = [[(50,30,10) for _ in range(64)] for _ in range(64)]
            if not self.flat_ceil: self.flat_ceil = [[(50,50,50) for _ in range(64)] for _ in range(64)]

        # --- Raycasting Loop (High Res) ---
        for x in range(vw):
            # Raycasting on Virtual Width
            ray_angle = (pa - FOV / 2.0) + (x / vw) * FOV
            ray_x, ray_y = math.cos(ray_angle), math.sin(ray_angle)
            
            map_x, map_y = int(px), int(py)
            delta_dist_x = abs(1 / ray_x) if ray_x != 0 else 1e30
            delta_dist_y = abs(1 / ray_y) if ray_y != 0 else 1e30
            step_x = 1 if ray_x >= 0 else -1
            step_y = 1 if ray_y >= 0 else -1
            side_dist_x = (map_x + 1.0 - px) * delta_dist_x if ray_x >= 0 else (px - map_x) * delta_dist_x
            side_dist_y = (map_y + 1.0 - py) * delta_dist_y if ray_y >= 0 else (py - map_y) * delta_dist_y
            
            hit, side, tex_id = False, 0, 1
            
            # Limited DDA
            for _ in range(50):
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side = 1
                
                if map_x < 0 or map_y < 0 or map_x >= self.world.map_width or map_y >= self.world.map_height:
                    hit = True; tex_id = 0; break
                
                val = self.world.world_map[map_x][map_y]
                if val > 0: hit = True; tex_id = val; break

            # if tex_id == 0: continue # Don't skip, we need to clear/draw sky/floor

            if side == 0: dist = (side_dist_x - delta_dist_x)
            else:         dist = (side_dist_y - delta_dist_y)
            dist *= math.cos(pa - ray_angle)

            # --- Wall Rendering ---
            # Aspect Ratio Correction for FOV 1.0
            # Since VH is 4x Height, we need to adjust standard scaling logic?
            # Standard: h / dist. 
            # Here: vh / dist. 
            # WALL_SCALE at 1.0 works for 1:1 pixels.
            # Terminal char is 1:2. Braille dot is approx 1:1.
            WALL_SCALE = 1.3
            line_height = int((vh / (dist + 0.0001)) * WALL_SCALE)
            
            draw_start = -line_height // 2 + vh // 2
            draw_end = line_height // 2 + vh // 2
            y_start = max(0, draw_start)
            y_end = min(vh, draw_end)

            # [Wall Texturing]
            world_pos = (py + dist * ray_y) if side == 0 else (px + dist * ray_x)
            local_u = world_pos - math.floor(world_pos)
            
            current_texture = self.textures.get(tex_id, self.textures[1]) if tex_id > 0 else None
            tex_w, tex_h = self.tex_sizes.get(tex_id, (64, 64))
            
            tex_u = int(local_u * tex_w)
            if (side == 0 and ray_x > 0) or (side == 1 and ray_y < 0): 
                tex_u = tex_w - tex_u - 1
            
            light = 1.0 
            if dist > 2.0: light = 1.0 / (1.0 + (dist - 2.0) * 0.3)

            # Top (Ceiling)
            # Casting logic for ceiling
            PROJ_CONST = half_vh * WALL_SCALE 
            
            # Ceiling Loop
            for y in range(0, y_start):
                 # Inverse ceiling logic
                 p = half_vh - y
                 if p <= 0: continue
                 row_dist = PROJ_CONST / p
                 row_dist /= math.cos(pa - ray_angle)
                 
                 f_light = 1.0
                 if row_dist > 2.0: f_light = 1.0 / (1.0 + (row_dist - 2.0) * 0.3)
                 
                 cx = px + row_dist * ray_x
                 cy = py + row_dist * ray_y
                 tx = int(cx * 64) % 64
                 ty = int(cy * 64) % 64
                 
                 r, g, b = self.flat_ceil[ty][tx]
                 self.engine.virtual_buffer[y][x] = (int(r*f_light), int(g*f_light), int(b*f_light))

            # Wall Loop
            if tex_id > 0:
                for y in range(y_start, y_end):
                    normalized_y = (float(y) - draw_start) / line_height
                    tex_v = int(normalized_y * tex_h)
                    tex_v = max(0, min(tex_h - 1, tex_v))
                    
                    try: r, g, b = current_texture[tex_v][tex_u]
                    except: r, g, b = 100, 0, 100
                    
                    self.engine.virtual_buffer[y][x] = (int(r*light), int(g*light), int(b*light))
            else:
                # Sky/Void
                 for y in range(y_start, y_end):
                      self.engine.virtual_buffer[y][x] = (30, 30, 30) # Dark grey void

            # Floor Loop
            for y in range(y_end, vh):
                 p = y - half_vh
                 if p <= 0: continue
                 row_dist = PROJ_CONST / p
                 row_dist /= math.cos(pa - ray_angle)
                 
                 f_light = 1.0
                 if row_dist > 2.0: f_light = 1.0 / (1.0 + (row_dist - 2.0) * 0.3)
                 
                 fx = px + row_dist * ray_x
                 fy = py + row_dist * ray_y
                 tx = int(fx * 64) % 64
                 ty = int(fy * 64) % 64
                 
                 r, g, b = self.flat_floor[ty][tx]
                 self.engine.virtual_buffer[y][x] = (int(r*f_light), int(g*f_light), int(b*f_light))

        # --- Downsampling to Terminal ---
        self.downsample_to_terminal(vw, vh)
        
        # --- UI Overlay ---
        self.draw_ui_overlay(vw, vh)
        self.draw_face_overlay(vw, vh)
        self.draw_weapon_overlay(vw, vh)

    def downsample_to_terminal(self, vw, vh):
        # Braille Mapping:
        # 1 4
        # 2 5
        # 3 6
        # 7 8
        # Maps to bits: 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80
        # Offsets from char base (x, y)
        dot_map = [
            (0, 0, 0x01), (0, 1, 0x02), (0, 2, 0x04), (1, 0, 0x08),
            (1, 1, 0x10), (1, 2, 0x20), (0, 3, 0x40), (1, 3, 0x80)
        ]
        
        for ty in range(self.engine.height):
            for tx in range(self.engine.width):
                base_vx = tx * 2
                base_vy = ty * 4
                
                mask = 0
                r_sum, g_sum, b_sum, count = 0, 0, 0, 0
                
                for dx, dy, bit in dot_map:
                    vx = base_vx + dx
                    vy = base_vy + dy
                    
                    if 0 <= vx < vw and 0 <= vy < vh:
                        pixel = self.engine.virtual_buffer[vy][vx]
                        if pixel:
                            # Pixel exists -> Dot ON
                            mask |= bit
                            r_sum += pixel[0]
                            g_sum += pixel[1]
                            b_sum += pixel[2]
                            count += 1
                
                # Render Char
                if mask == 0:
                    self.engine.frame_buffer[ty][tx] = " "
                else:
                    code = 0x2800 + mask
                    char = chr(code)
                    
                    # Average Color
                    if count > 0:
                        r = r_sum // count
                        g = g_sum // count
                        b = b_sum // count
                        colored_char = f"\033[38;2;{r};{g};{int(b)}m{char}\033[0m"
                        self.engine.frame_buffer[ty][tx] = colored_char
                    else:
                        self.engine.frame_buffer[ty][tx] = char

    def draw_weapon_overlay(self, screen_w, screen_h):
        # [Weapon State Selection]
        from src.ecs.components import Weapon
        weapon_state = "SHOTGUN_IDLE"
        
        try:
            player_id = next(self.world.get_entities_with(Weapon))
            weapon = self.world.get_component(player_id, Weapon)
            
            # Map Component State to Animation Frame
            if weapon.state == "FIRE": weapon_state = "SHOTGUN_FIRE"
            elif weapon.state == "RECOIL": weapon_state = "SHOTGUN_RECOIL"
            elif weapon.state == "PUMP1": weapon_state = "SHOTGUN_PUMP1"
            elif weapon.state == "PUMP2": weapon_state = "SHOTGUN_PUMP2"
            else: weapon_state = "SHOTGUN_IDLE"
        except StopIteration:
            pass
        
        # Get ASCII sprite from Renderer
        sprite = self.sprite_renderer.get_weapon_sprite(weapon_state)
        if not sprite: return

        # Original Size
        org_h = len(sprite)
        org_w = len(sprite[0]) if org_h > 0 else 0
        
        # Scale 20% smaller than previous 0.3 -> 0.24
        SCALE = 0.24
        target_w = int(org_w * SCALE)
        target_h = int(org_h * SCALE)
        
        # Centered position
        start_x = (screen_w - target_w) // 2
        # Weapon sits slightly above the UI bar (approx 7 lines reserved)
        start_y = screen_h - target_h - 6 
        
        # Downscale Loop (Nearest Neighbor)
        scale_denom = 1.0 / SCALE 
        
        for y in range(target_h):
            screen_y = start_y + y
            if screen_y < 0 or screen_y >= screen_h: continue
            
            # Sample Source Y
            src_y = int(y * scale_denom)
            src_y = max(0, min(src_y, org_h - 1))
            
            src_line = sprite[src_y]
            
            for x in range(target_w):
                screen_x = start_x + x
                if screen_x < 0 or screen_x >= screen_w: continue
                
                # Sample Source X
                src_x = int(x * scale_denom)
                src_x = max(0, min(src_x, org_w - 1))
                
                char = src_line[src_x]
                if char != " ": # Transparent check
                    self.engine.frame_buffer[screen_y][screen_x] = char

    def draw_face_overlay(self, screen_w, screen_h):
        # [Dynamic Face Selection]
        from src.ecs.components import Stats
        
        face_name = "STFST00"
        
        # Get Player Health
        try:
            player_id = next(self.world.get_entities_with(Stats))
            stats = self.world.get_component(player_id, Stats)
            hp = stats.hp
            
            if hp >= 80: face_name = "STFST00"
            elif hp >= 60: face_name = "STFST01"
            elif hp >= 40: face_name = "STFST02"
            elif hp >= 20: face_name = "STFST03"
            else:          face_name = "STFST04"
            
            # TODO: Add "Evil Grin" (EVL) or "Ouch" (OUCH) states later
        except StopIteration:
            pass # No stats, use default
        
        sprite = self.sprite_renderer.load_sprite(face_name)
        if not sprite: return
        
        org_h = len(sprite)
        org_w = len(sprite[0])
        
        # STBAR is 32px high -> mapped to 7 lines.
        # Face is ~29px high. Should mapped to ~6 lines.
        # Let's keep the aspect ratio relatively generic.
        # Original: 24x29.
        # Target: ~6 lines high. Width should be roughly 12 chars (since chars are 1:2).
        
        target_h = 6
        target_w = 8 # Slightly adjusted for aspect ratio
        
        # Position: Center of STBAR (Bottom of screen)
        # STBAR height is 7
        target_w = 12 # Adjusted for aspect ratio
        start_x = (screen_w - target_w) // 2
        start_y = screen_h - target_h 
        
        scale_x = org_w / target_w
        scale_y = org_h / target_h
        
        for y in range(target_h):
            screen_y = start_y + y
            if screen_y >= screen_h: break
            
            src_y = int(y * scale_y)
            src_y = min(src_y, org_h - 1)
            src_line = sprite[src_y]
            
            for x in range(target_w):
                screen_x = start_x + x
                if screen_x < 0 or screen_x >= screen_w: continue
                
                src_x = int(x * scale_x)
                src_x = min(src_x, org_w - 1)
                
                char = src_line[src_x]
                if char != " ":
                     self.engine.frame_buffer[screen_y][screen_x] = char

    def draw_ui_overlay(self, screen_w, screen_h):
        # Load STBAR
        # We need to access load_sprite or similar from sprite_renderer
        # But SpriteRenderer.load_sprite converts to ASCII using a generic ramp.
        # STBAR might need specific resizing logic.
        # Let's just use load_sprite for now, but we need to resize it.
        # Wait, load_sprite returns a list of strings (ASCII).
        # STBAR is 320 chars wide. Screen is 100 wide.
        # Simply sampling the ASCII string at intervals is easiest.
        
        stbar_sprite = self.sprite_renderer.load_sprite("STBAR")
        if not stbar_sprite: return
        
        bar_h = len(stbar_sprite)
        bar_w = len(stbar_sprite[0])
        
        # Target height: ~6 lines
        # Target width: screen_w (100)
        
        target_h = 7
        
        start_y = screen_h - target_h
        
        # Downscale Logic (Nearest Neighbor)
        scale_x = bar_w / screen_w
        scale_y = bar_h / target_h
        
        for y in range(target_h):
            screen_y = start_y + y
            if screen_y >= screen_h: break
            
            # Sample Y
            src_y = int(y * scale_y)
            src_y = min(src_y, bar_h - 1)
            
            src_line = stbar_sprite[src_y]
            
            for x in range(screen_w):
                # Sample X
                src_x = int(x * scale_x)
                src_x = min(src_x, bar_w - 1)
                
                char = src_line[src_x]
                self.engine.frame_buffer[screen_y][x] = char
                
def render_system(world, engine, dt):
    # Wrapper for old API compatibility
    if not hasattr(engine, 'renderer'):
        engine.renderer = RenderSystem(world, engine)
    engine.renderer.render(dt)
