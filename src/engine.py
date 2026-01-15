import sys
import time
import termios
import tty
from src.ecs.world import World
from src.ecs.components import Transform, Motion, PhysicsMode, Render, Wall
from src.utils.math_core import Vector3, PI
from src.systems.input_sys import input_system
from src.systems.physics_sys import physics_system
from src.systems.render_sys import render_system
from src.utils.wad_loader import WADLoader

class GameEngine:
    def __init__(self):
        self.world = World()
        self.running = False
        self.width = 100
        self.height = 40
        self.frame_buffer = [[" " for _ in range(self.width)] for _ in range(self.height)]
        
        # Terminal state
        self.original_termios = None
        self.loader = None
        self.player_id = None

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
            self.loader = WADLoader("assets/DOOM1.WAD")
            verts, lines, things = self.loader.load_map_data(map_name)

            # 1. Scaling (Doom 100 -> Engine 20)
            SCALE = 0.20
            
            min_x = min(v[0] for v in verts)
            min_y = min(v[1] for v in verts)
            max_x = max(v[0] for v in verts)
            max_y = max(v[1] for v in verts)
            
            map_w = int((max_x - min_x) * SCALE) + 20
            map_h = int((max_y - min_y) * SCALE) + 20
            self.world.init_map(map_w, map_h)
            self.log(f"[*] Map Scaled: {map_w}x{map_h} (Original Bounds: {min_x},{min_y} to {max_x},{max_y})")

            # 2. Rasterize LINEDEFS
            for line in lines:
                v1, v2 = verts[line[0]], verts[line[1]]
                x1 = (v1[0] - min_x) * SCALE + 5
                y1 = (v1[1] - min_y) * SCALE + 5
                x2 = (v2[0] - min_x) * SCALE + 5
                y2 = (v2[1] - min_y) * SCALE + 5
                
                # Use flags or sequence to vary textures for debug
                tex_id = (line[2] % 3) + 1
                self.rasterize_line(int(x1), int(y1), int(x2), int(y2), tex_id)

            # 3. Player Spawn
            player_start = next((t for t in things if t['type'] == 1), None)
            if player_start and self.player_id is not None:
                px = (player_start['x'] - min_x) * SCALE + 5
                py = (player_start['y'] - min_y) * SCALE + 5
                p_trans = self.world.get_component(self.player_id, Transform)
                p_trans.pos.x = px
                p_trans.pos.y = py
                p_trans.pos.z = 8.2 # Scaled eye height (41 * 0.2)
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
        
        # Load the level map
        self.load_level("E1M1")
        
        # Add systems
        self.world.add_system(input_system)
        self.world.add_system(physics_system)

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
                self.world.update(dt, self)
                
                # Render
                self.clear_buffer()
                render_system(self.world, self, dt)
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
