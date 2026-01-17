
import sys
import math
from src.utils.wad_loader import WADLoader
from src.utils.math_core import PI

# --- Configuration (Must match engine.py) ---
SCALE = 0.20
PADDING = 20

def rasterize_line(world_map, width, height, x0, y0, x1, y1, val):
    """Bresenham's algo copy-pasted from engine.py for fidelity."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        gx, gy = int(x0), int(y0)
        if 0 <= gx < width and 0 <= gy < height:
            world_map[gx][gy] = val
        
        if x0 == x1 and y0 == y1:
            break
            
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def dump_map(map_name="E1M1"):
    print(f"[*] Loading {map_name} from assets/Doom1.WAD...")
    try:
        loader = WADLoader("assets/Doom1.WAD")
        verts, lines, things = loader.load_map_data(map_name)
    except Exception as e:
        print(f"[!] Failed to load WAD: {e}")
        return

    # 1. Bounds Logic
    min_x = min(v[0] for v in verts)
    min_y = min(v[1] for v in verts)
    max_x = max(v[0] for v in verts)
    max_y = max(v[1] for v in verts)
    
    print(f"[*] Original Bounds: ({min_x}, {min_y}) to ({max_x}, {max_y})")
    print(f"[*] WIDTH: {max_x - min_x}, HEIGHT: {max_y - min_y}")

    # 2. Setup Grid
    map_w = int((max_x - min_x) * SCALE) + PADDING
    map_h = int((max_y - min_y) * SCALE) + PADDING
    
    print(f"[*] Scaled MAP Size: {map_w}x{map_h} (Scale: {SCALE})")
    
    # 2D Array [x][y]
    world_map = [[0 for _ in range(map_h)] for _ in range(map_w)]

    # 3. Rasterize
    print("[*] Rasterizing Linedefs...")
    for line in lines:
        v1 = verts[line[0]]
        v2 = verts[line[1]]
        
        # Transform to grid space
        x1 = (v1[0] - min_x) * SCALE + (PADDING // 2)
        y1 = (v1[1] - min_y) * SCALE + (PADDING // 2)
        x2 = (v2[0] - min_x) * SCALE + (PADDING // 2)
        y2 = (v2[1] - min_y) * SCALE + (PADDING // 2)
        
        tex_id = (line[2] % 3) + 1 # Texture ID logic from engine
        
        rasterize_line(world_map, map_w, map_h, int(x1), int(y1), int(x2), int(y2), tex_id)

    # 4. Find Player
    player_start = next((t for t in things if t['type'] == 1), None)
    px_grid, py_grid = -1, -1
    if player_start:
        px_grid = int((player_start['x'] - min_x) * SCALE + (PADDING // 2))
        py_grid = int((player_start['y'] - min_y) * SCALE + (PADDING // 2))
        print(f"[*] Player Start Grid: {px_grid}, {py_grid}")

    # 5. Output to File
    out_path = "debug_map.txt"
    print(f"[*] Writing to {out_path}...")
    with open(out_path, "w", encoding="utf-8") as f:
        # Note: Printing Y row by row means iterating Y descending or ascending.
        # Engine usually renders Y=0 at bottom if it's world coords, but text file reads top-down.
        # Let's print Y descending to match standard coordinate visualization (Y up).
        for y in range(map_h - 1, -1, -1):
            row_str = []
            for x in range(map_w):
                if x == px_grid and y == py_grid:
                    row_str.append("@") # Player
                elif world_map[x][y] > 0:
                    val = world_map[x][y]
                    char = "#" if val == 1 else ("%" if val == 2 else "+")
                    row_str.append(char)
                else:
                    row_str.append(".")
            f.write(f"{y:03d} " + "".join(row_str) + "\n")
            
    print("[*] Done.")

if __name__ == "__main__":
    dump_map()
