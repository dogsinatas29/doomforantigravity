import sys
import time
import termios
import tty
from src.ecs.world import World
from src.ecs.components import Transform, Motion, PhysicsMode, Render, Wall, Stats
from src.utils.math_core import Vector3, PI
from src.systems.input_sys import input_system
from src.systems.physics_sys import physics_system
from src.systems.render_sys import render_system
from src.systems.ui_sys import ui_system
from src.utils.wad_loader import WADLoader

class GameEngine:
    def __init__(self):
        self.world = World()
        self.running = False
        self.width = 200
        self.height = 40
        self.frame_buffer = [[" " for _ in range(self.width)] for _ in range(self.height)]
        
        # Terminal state
        self.original_termios = None
        self.loader = None
        self.player_id = None
        self.player_id = None
        self.show_automap = False # Toggle via TAB
        self.input_cooldown = 0.0 # Debounce timer

    def setup_terminal(self):
        """Set terminal to raw mode for non-blocking input."""
        self.original_termios = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
        # Hide cursor
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

    def restore_terminal(self):
        """Restore terminal to original state."""
        if self.original_termios:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.original_termios)
        # Show cursor
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def clear_buffer(self):
        for y in range(self.height):
            for x in range(self.width):
                self.frame_buffer[y][x] = " "

    def render_to_terminal(self):
        """Optimized rendering using string join."""
        # Move cursor to top-left
        sys.stdout.write("\033[H")
        
        lines = []
        for row in self.frame_buffer:
            lines.append("".join(row))
        
        full_frame = "\r\n".join(lines)
        sys.stdout.write(full_frame)
        sys.stdout.flush()

    def log(self, msg):
        """Helper to print correctly in raw mode."""
        sys.stdout.write(msg + "\r\n")
        sys.stdout.flush()

    def render_debug_map(self):
        """
        맵 전체를 출력하는 'God Mode' 뷰입니다.
        """
        self.log("\n--- [DEBUG: FULL MAP VIEW] ---")
        
        # 플레이어 위치 가져오기
        p_transform = self.world.get_component(self.player_id, Transform)
        px, py = int(p_transform.pos.x), int(p_transform.pos.y)
        
        for y in range(self.world.map_height - 1, -1, -1):
            line = []
            for x in range(self.world.map_width):
                if x == px and y == py:
                    line.append("P")
                elif self.world.world_map[x][y] > 0:
                    val = self.world.world_map[x][y]
                    # 텍스처 ID에 따른 문자 구분
                    char = "#" if val == 1 else ("%" if val == 2 else "+")
                    line.append(char)
                else:
                    line.append(" ")
            
            line_str = "".join(line)
            if line_str.strip():
                self.log(f"{y:03d} {line_str}")
        
        self.log(f"Player Pos: ({px}, {py}) | Map Size: {self.world.map_width}x{self.world.map_height}")
        self.log("---------------------------------")

    def rasterize_line(self, x0, y0, x1, y1, texture_id):
        """Bresenham's algorithm to fill world_map grid."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            gx, gy = int(x0), int(y0)
            if 0 <= gx < self.world.map_width and 0 <= gy < self.world.map_height:
                self.world.world_map[gx][gy] = texture_id
            
            if x0 == x1 and y0 == y1:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def load_level(self, map_name="E1M1"):
        """WAD 데이터를 읽어 그리드 맵으로 래스터화"""
        try:
            self.log(f"[*] Loading {map_name}...")
            self.loader = WADLoader("assets/Doom1.WAD")
            verts, lines, things, sides = self.loader.load_map_data(map_name)

            # 1. Scaling (Doom 100 -> Engine 20)
            SCALE = 0.20
            
            min_x = min(v[0] for v in verts)
            min_y = min(v[1] for v in verts)
            max_x = max(v[0] for v in verts)
            max_y = max(v[1] for v in verts)
            
            map_w = int((max_x - min_x) * SCALE) + 20
            map_h = int((max_y - min_y) * SCALE) + 20
            
            # Pass vector data to World for debug/automap/vector-render
            self.world.init_map(map_w, map_h, verts, lines, sides)
            self.world.map_bounds = (min_x, min_y, SCALE) # Store scaling info
            
            self.log(f"[*] Map Scaled: {map_w}x{map_h} (Original Bounds: {min_x},{min_y} to {max_x},{max_y})")

            # 2. Rasterize LINEDEFS
            # Import mapping helper
            from src.utils.visual_assets import get_texture_id_from_name
            
            for line in lines:
                v1, v2 = verts[line[0]], verts[line[1]]
                x1 = (v1[0] - min_x) * SCALE + 5
                y1 = (v1[1] - min_y) * SCALE + 5
                x2 = (v2[0] - min_x) * SCALE + 5
                y2 = (v2[1] - min_y) * SCALE + 5
                
                # Get Texture from Sidedef
                # line format: (start, end, flags, right_side)
                tex_idx = 1 # Default Wall
                right_side_idx = line[3]
                if right_side_idx != -1 and right_side_idx < len(sides):
                    tex_name = sides[right_side_idx]['mid']
                    # Register texture if new
                    if tex_name not in self.world.texture_registry:
                        self.world.texture_registry.append(tex_name)
                    tex_idx = self.world.texture_registry.index(tex_name)

                self.rasterize_line(int(x1), int(y1), int(x2), int(y2), tex_idx)

            # 3. Player Spawn
            player_start = next((t for t in things if t['type'] == 1), None)
            if player_start and self.player_id is not None:
                px = (player_start['x'] - min_x) * SCALE + 5
                py = (player_start['y'] - min_y) * SCALE + 5
                p_trans = self.world.get_component(self.player_id, Transform)
                p_trans.pos.x = px
                p_trans.pos.y = py
                
                # Safe Spawn Logic (Spiral Search)
                # If spawn point is inside a wall (val > 0), search outward
                if self.world.world_map[int(px)][int(py)] > 0:
                    self.log(f"[!] Spawn ({int(px)},{int(py)}) is SOLID! Searching nearby...")
                    found = False
                    radius = 1
                    while not found and radius < 10:
                        for dx in range(-radius, radius + 1):
                            for dy in range(-radius, radius + 1):
                                nx, ny = int(px) + dx, int(py) + dy
                                if 0 <= nx < self.world.map_width and 0 <= ny < self.world.map_height:
                                    if self.world.world_map[nx][ny] == 0:
                                        p_trans.pos.x = float(nx) + 0.5 # Center in cell
                                        p_trans.pos.y = float(ny) + 0.5
                                        px, py = p_trans.pos.x, p_trans.pos.y
                                        found = True
                                        self.log(f"[*] Safe Spawn Found at ({px}, {py})")
                                        break
                            if found: break
                        radius += 1
                
                # Fix Eye Height (Was 20.0 -> Too High).
                # Doom Guy Height ~56 units. Scale 0.2 -> 11.2
                # Setting to 12.0 for standard eye level.
                p_trans.pos.z = 12.0 
                
                p_trans.angle = (float(player_start['angle']) * PI) / 180.0
                self.log(f"[*] Player at Grid ({px:.2f}, {py:.2f})")
            
            self.log(f"[*] Level Loaded successfully.")

        except Exception as e:
            self.log(f"[!] Level Load Failed: {e}")
            import traceback
            # Can't easily use traceback.print_exc() in raw mode without our log()
            # but we'll try to log the error string.

    def init_game(self):
        """Initialize world, systems, and load level."""
        # Create Player first to ensure consistent ID (usually 0)
        self.player_id = self.world.create_entity()
        self.world.add_component(self.player_id, Transform(Vector3(0, 0, 41), 0.0))
        self.world.add_component(self.player_id, Motion(Vector3(), Vector3()))
        self.world.add_component(self.player_id, PhysicsMode())
        self.world.add_component(self.player_id, Render("@"))
        # Phase 4: Init Stats for HUD
        self.world.add_component(self.player_id, Stats(hp=100, armor=0, ammo=50, fuel=100.0))
        
        # Load the level map
        self.loader = WADLoader("assets/Doom1.WAD")
        self.load_wad_assets()
        self.load_level("E1M1")
        
        # Add systems
        self.world.add_system(input_system)
        self.world.add_system(physics_system)

    def load_wad_assets(self):
        """Load Sprites (Weapons) from WAD and convert to ASCII."""
        try:
            from src.utils.visual_assets import WEAPON_ASSETS
            
            # 1. Shotgun Sprites (SHTG)
            # SHTGA0 (Idle), SHTGB0 (Fire), SHTGC0/D0 (Reload)
            sprites = {
                "SHOTGUN_IDLE": "SHTGA0",
                "SHOTGUN_FIRE": "SHTGB0", 
                "SHOTGUN_PUMP1": "SHTGC0",
                "SHOTGUN_PUMP2": "SHTGD0"
            }
            
            self.log("[*] Loading Weapon Sprites from WAD...")
            
            for key, lump_name in sprites.items():
                data = self.loader.read_lump(lump_name)
                if data:
                    grid = self.loader.parse_patch(data)
                    # Scale down: Doom 320x200 -> Terminal ~80x40
                    # Weapon sprite ~100px width -> want ~30 chars? -> 0.3
                    ascii_art = self.loader.patch_to_ascii(grid, scale_x=0.4, scale_y=0.2)
                    if ascii_art:
                        WEAPON_ASSETS[key] = ascii_art
                        self.log(f"    - Loaded {lump_name} -> {len(ascii_art)} lines.")
                    else:
                         self.log(f"    - Failed to convert {lump_name}.")
                else:
                    self.log(f"    - Lump {lump_name} not found.")
                    
        except Exception as e:
            self.log(f"[!] Asset Load Error: {e}")

    def run(self):
        try:
            self.init_game()
            
            # self.render_debug_map() # 진단 완료 후 비활성
            
            self.setup_terminal()
            # Clear screen and move cursor to top-left
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()
            
            self.running = True
            
            last_time = time.time()
            
            while self.running:
                current_time = time.time()
                dt = current_time - last_time
                if dt < 0.01:
                    time.sleep(0.01)
                    continue
                last_time = current_time
                
                # Update logic
                if self.input_cooldown > 0:
                    self.input_cooldown -= dt
                self.world.update(dt, self)
                
                # Render
                self.clear_buffer()
                if self.show_automap:
                     from src.systems.render_sys import render_automap
                     render_automap(self.world, self)
                else:
                     render_system(self.world, self, dt)
                     ui_system(self.world, self, dt) # Phase 4: UI Overlay
                
                self.render_to_terminal()
                
                # Cap FPS (approx 30 FPS)
                sleep_time = 0.033 - (time.time() - current_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.running = False
        except Exception as e:
            self.restore_terminal()
            print(f"\nEngine error: {e}")
            raise e
        finally:
            self.restore_terminal()

if __name__ == "__main__":
    game = GameEngine()
    game.run()
