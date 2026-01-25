import sys
import math
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
        self.width = 100  # Terminal Width (Standard 100x40)
        self.height = 40  # Terminal Height
        self.frame_buffer = [[" " for _ in range(self.width)] for _ in range(self.height)]
        
        # [High-Res Internal Buffer]
        # Braille is 2x4 dots per character.
        self.vw = self.width * 2
        self.vh = self.height * 4
        self.virtual_buffer = [[None for _ in range(self.vw)] for _ in range(self.vh)]
        
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
        # 브레전험 알고리즘으로 world_map 채우기
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            if 0 <= x0 < self.world.map_width and 0 <= y0 < self.world.map_height:
                self.world.world_map[x0][y0] = texture_id
            if x0 == x1 and y0 == y1: break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def find_safe_spawn(self, transform, map_w, map_h):
        """Find non-solid spawn point nearby."""
        px, py = int(transform.pos.x), int(transform.pos.y)
        self.log(f"[!] Spawn ({px},{py}) is SOLID! Searching nearby...")
        found = False
        radius = 1
        while not found and radius < 15:
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < map_w and 0 <= ny < map_h:
                        if self.world.world_map[nx][ny] == 0:
                            transform.pos.x = float(nx) + 0.5
                            transform.pos.y = float(ny) + 0.5
                            self.log(f"[*] Safe Spawn Found at ({transform.pos.x}, {transform.pos.y})")
                            found = True
                            return
            radius += 1

    def load_level(self, map_name="E1M1"):
        print(f"Loading {map_name} with PRECISION SPAWN...")
        
        # 1. WAD 로드
        self.wad_loader = WADLoader("assets/DOOM1.WAD")
        vertices, linedefs, things, sidedefs = self.wad_loader.load_map_data(map_name)
        
        # 2. 맵 범위 계산
        min_x = min(v[0] for v in vertices)
        max_x = max(v[0] for v in vertices)
        min_y = min(v[1] for v in vertices)
        max_y = max(v[1] for v in vertices)
        
        SCALE = 0.15
        PADDING = 20 # 맵 테두리 여유 공간
        
        map_width = int((max_x - min_x) * SCALE) + (PADDING * 2)
        map_height = int((max_y - min_y) * SCALE) + (PADDING * 2)
        
        self.world.map_width = map_width
        self.world.map_height = map_height
        self.world.world_map = [[0] * map_height for _ in range(map_width)]
        
        # 3. 벽 그리기
        for line in linedefs:
            v1 = vertices[line[0]]
            v2 = vertices[line[1]]
            
            x1 = int((v1[0] - min_x) * SCALE) + PADDING
            y1 = int((v1[1] - min_y) * SCALE) + PADDING
            x2 = int((v2[0] - min_x) * SCALE) + PADDING
            y2 = int((v2[1] - min_y) * SCALE) + PADDING
            
            # Texture Lookup (Simple for now)
            val = 1
            right_side_idx = line[3] 
            if right_side_idx != -1 and right_side_idx < len(sidedefs):
                tex_name = sidedefs[right_side_idx]['mid']
                if tex_name and tex_name != "-":
                     val = sum(ord(c) for c in tex_name) % 8 + 1
            
            self.rasterize_line(x1, y1, x2, y2, val)

        # ---------------------------------------------------------
        # [핵심] E1M1 정밀 스폰 로직
        # ---------------------------------------------------------
        # 둠 E1M1 실제 시작 좌표
        target_raw_x = 1056
        target_raw_y = -3616
        target_angle = 90 # 북쪽(North)
        
        # 우리 맵 좌표계로 변환
        target_px = (target_raw_x - min_x) * SCALE + PADDING
        target_py = (target_raw_y - min_y) * SCALE + PADDING
        
        spawn_x, spawn_y = target_px, target_py
        
        # 정수로 변환해서 벽인지 확인
        ix, iy = int(spawn_x), int(spawn_y)
        
        # 만약 목표 지점이 벽(>0)이라면, 주변을 살짝 뒤져서 빈 곳(0)으로 이동
        # Safety check for bounds
        if 0 <= ix < map_width and 0 <= iy < map_height and self.world.world_map[ix][iy] != 0:
            print(f"[!] Target spawn ({ix}, {iy}) is blocked. Nudging player...")
            found = False
            # 중심에서 나선형으로 퍼지며 탐색 (최대 10칸 범위)
            for r in range(1, 10):
                if found: break
                for dx in range(-r, r+1):
                    for dy in range(-r, r+1):
                        nx, ny = ix + dx, iy + dy
                        if 0 <= nx < map_width and 0 <= ny < map_height:
                            if self.world.world_map[nx][ny] == 0:
                                # 찾았다! 빈 공간의 중심으로 이동
                                spawn_x, spawn_y = float(nx) + 0.5, float(ny) + 0.5
                                print(f"[*] Adjusted Spawn to ({spawn_x:.2f}, {spawn_y:.2f})")
                                found = True
                                break
            if not found:
                print("[!] CRITICAL: Could not find empty space near start point!")
        else:
            print(f"[*] Spawn clean at ({spawn_x:.2f}, {spawn_y:.2f})")

        # ---------------------------------------------------------
        # ECS 플레이어 생성
        # ---------------------------------------------------------
        from src.ecs.components import Transform
        
        if self.player_id is not None:
             player_ent = self.player_id
        else:
             player_ent = self.world.create_entity()
             self.player_id = player_ent
             
        # [Fix] Transform requires Vector3(x, y, z)
        # Z=41.0 (Standard Player Height)
        from src.utils.math_core import Vector3
        self.world.add_component(player_ent, Transform(Vector3(spawn_x, spawn_y, 41.0), math.radians(target_angle)))
        
        # [Debug: Map Validation]
        wall_count = sum(row.count(0) for row in self.world.world_map)
        total_cells = map_width * map_height
        filled_cells = total_cells - wall_count
        self.log(f"[*] Map Stats: {filled_cells} filled cells out of {total_cells} ({filled_cells/total_cells*100:.2f}%)")
        
        if filled_cells == 0:
            self.log("[!] WARNING: Map is completely empty! Rasterization failed.")
        
        self.log(f"[*] Level Loaded successfully.")

    def rasterize_line(self, x0, y0, x1, y1, val):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            if 0 <= x0 < self.world.map_width and 0 <= y0 < self.world.map_height:
                self.world.world_map[x0][y0] = val
            if x0 == x1 and y0 == y1: break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

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
        
        # [Phase 7] Texture Loading
        self.load_wad_textures()
        
        self.load_level("E1M1")
        
        # Add systems
        self.world.add_system(input_system)
        self.world.add_system(physics_system)

    def load_wad_textures(self):
        """Parse WAD textures and preload common ones."""
        try:
            self.log("[*] Loading WAD Texture Definitions...")
            # We need a loader instance for texture lumps, even if not loading level yet.
            if not getattr(self, 'loader', None):
                self.loader = WADLoader("assets/DOOM1.WAD")
            
            # WADLoader already loads pnames and texture_defs in __init__
            if hasattr(self.loader, 'texture_defs'):
                self.world.texture_defs = self.loader.texture_defs
                self.log(f"[*] Use {len(self.world.texture_defs)} Texture Definitions from Loader.")
            else:
                self.world.texture_defs = {}
                self.log("[!] Loader has no texture defs.")

            # 3. Prebuild Common Textures (Cache)
            # Essential Doom Textures
            preload_list = ["STARTAN3", "BROWN96", "BIGDOOR2", "STONE2", "FLOOR7_1", "STEP1"]
            self.world.texture_cache = {}
            
            for tex_name in preload_list:
                if tex_name in self.world.texture_defs:
                     # Build the grid (Note: wad_loader.py doesn't have build_texture method visible in previous view, 
                     # but it has get_decoded_texture. Let's assume build_texture was intended to be get_decoded_texture
                     # or we just skip this cache for now if method missing. 
                     # Wait, get_decoded_texture returns 2D grid. So we can use that.)
                     grid = self.loader.get_decoded_texture(tex_name)
                     if grid:
                         self.world.texture_cache[tex_name] = grid
                         self.log(f"    - Cached {tex_name} ({len(grid[0])}x{len(grid)})")
                     else:
                         self.log(f"    - Failed to build {tex_name}")
            
        except Exception as e:
            self.log(f"[!] Texture Load Error: {e}")
            import traceback

    def load_wad_assets(self):
        """
        [DEPRECATED] WAD Sprite Loading.
        Disabled to prevent '8888' artifact. Using visual_assets.ASCII_WEAPONS instead.
        """
        pass

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
