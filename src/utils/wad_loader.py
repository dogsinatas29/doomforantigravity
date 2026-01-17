import struct
import os

class WADLoader:
    def __init__(self, wad_path):
        self.wad_path = wad_path
        self.lumps = [] # (name, offset, size)
        if os.path.exists(self.wad_path):
            self.load_directory()
        else:
            print(f"[!] WAD file not found: {self.wad_path}")

    def load_directory(self):
        with open(self.wad_path, "rb") as f:
            # 1. Read Header
            # <: Little Endian, 4s: char[4], I: uint32
            header_data = f.read(12)
            if len(header_data) < 12:
                print("[!] Header too short.")
                return
                
            signature, num_lumps, dir_offset = struct.unpack("<4sII", header_data)
            
            print(f"[*] WAD Type: {signature.decode(errors='ignore')}")
            print(f"[*] Lumps: {num_lumps}")
            print(f"[*] Dir Offset: {dir_offset}")

            # 2. Seek to Directory
            f.seek(dir_offset)

            # 3. Read All Lumps
            for _ in range(num_lumps):
                # 16 bytes: offset(I), size(I), name(8s)
                lump_data = f.read(16)
                if len(lump_data) < 16: break
                offset, size, name_bytes = struct.unpack("<II8s", lump_data)
                
                # Clean up name (remove null bytes)
                name = name_bytes.decode(errors='ignore').strip('\x00').upper()
                self.lumps.append({'name': name, 'offset': offset, 'size': size})
    
    def find_lump(self, name):
        for lump in self.lumps:
            if lump['name'] == name:
                return lump
        return None

    def read_vertexes(self, offset, size):
        """
        VERTEXES 럼프 파싱
        포맷: x(short), y(short) -> 4 bytes per vertex
        """
        vertexes = []
        with open(self.wad_path, "rb") as f:
            f.seek(offset)
            num_vertexes = size // 4
            for _ in range(num_vertexes):
                # <hh: Little Endian, signed short (2 bytes) * 2
                x, y = struct.unpack("<hh", f.read(4))
                vertexes.append((x, y))
        return vertexes

    def read_sidedefs(self, offset, size):
        """
        SIDEDEFS 럼프 파싱
        Format: x_offset(h), y_offset(h), upper_tex(8s), lower_tex(8s), mid_tex(8s), sector(h) -> 30 bytes
        """
        sidedefs = []
        with open(self.wad_path, "rb") as f:
            f.seek(offset)
            num_sidedefs = size // 30
            for _ in range(num_sidedefs):
                data = struct.unpack("<hh8s8s8sh", f.read(30))
                # We mainly care about Middle Texture for walls
                mid_tex = data[4].decode(errors='ignore').strip('\x00').upper()
                sidedefs.append({
                    'mid': mid_tex
                })
        return sidedefs

    def read_linedefs(self, offset, size):
        """
        LINEDEFS 럼프 파싱
        Format: ..., right_side(H), left_side(H) ...
        """
        linedefs = []
        with open(self.wad_path, "rb") as f:
            f.seek(offset)
            num_linedefs = size // 14
            for _ in range(num_linedefs):
                # <7H: start, end, flags, type, tag, right, left
                data = struct.unpack("<7H", f.read(14))
                start_v_id = data[0]
                end_v_id = data[1]
                flags = data[2]
                right_side = data[5] # Index into SIDEDEFS
                left_side = data[6]
                
                # (Start, End, Flags, RightSide)
                linedefs.append((start_v_id, end_v_id, flags, right_side))
        return linedefs

    def read_things(self, offset, size):
        """
        THINGS 럼프 파싱 (플레이어 시작 위치 찾기용)
        Format: x(h), y(h), angle(h), type(h), flags(h) -> 10 bytes
        """
        things = []
        with open(self.wad_path, "rb") as f:
            f.seek(offset)
            num_things = size // 10
            for _ in range(num_things):
                data = struct.unpack("<5h", f.read(10))
                thing = {
                    'x': data[0],
                    'y': data[1],
                    'angle': data[2],
                    'type': data[3],
                    'flags': data[4]
                }
                things.append(thing)
        return things

    def read_lump(self, name):
        """Finds lump by name and returns raw bytes."""
        lump = self.find_lump(name)
        if not lump: return None
        with open(self.wad_path, "rb") as f:
            f.seek(lump['offset'])
            return f.read(lump['size'])

    def parse_patch(self, patch_data):
        """
        Parses Doom Patch format (Picture).
        Returns: 2D Grid of Pixel Indices (or None for transparent)
        """
        if not patch_data or len(patch_data) < 8: return None
        
        # Header: Width(H), Height(H), Left(h), Top(h)
        width, height, left, top = struct.unpack("<HHhh", patch_data[:8])
        
        # Initialize Grid (None = Transparent)
        grid = [[None for _ in range(width)] for _ in range(height)]
        
        # Column Offsets (Width * 4 bytes)
        col_offsets = []
        for i in range(width):
            offset = struct.unpack("<I", patch_data[8 + i*4 : 8 + (i+1)*4])[0]
            col_offsets.append(offset)
            
        # Parse Columns
        for x, col_offset in enumerate(col_offsets):
            # Seek to column start in data
            cursor = col_offset
            while cursor < len(patch_data):
                row_start = patch_data[cursor]
                if row_start == 255: break # End of Column
                
                pixel_count = patch_data[cursor + 1]
                # Dummy byte at cursor + 2
                
                # Pixels start at cursor + 3
                for i in range(pixel_count):
                    pixel = patch_data[cursor + 3 + i]
                    y = row_start + i
                    if 0 <= y < height:
                        grid[y][x] = pixel
                        
                # Dummy byte at end of post
                cursor += 3 + pixel_count + 1
                
        return grid

    def patch_to_ascii(self, grid, scale_x=1.0, scale_y=0.6):
        """
        Converts pixel grid to ASCII strings.
        scale_y 0.6 compensates for terminal character aspect ratio.
        """
        if not grid: return []
        
        height = len(grid)
        width = len(grid[0])
        
        # Simple ASCII Density Map (Dark to Light)
        # In Doom, colors are indices. Without palette, we map Index>0 to Visible.
        # Let's map somewhat arbitrarily or just use Solid.
        CHARS = " .:-=+*#%@"
        
        lines = []
        # Downsampling loop
        # We want to compress the 320x200 sprite to a smaller ASCII size
        # Step size
        step_x = 1 / scale_x
        step_y = 1 / scale_y
        
        # Target Dimensions
        target_w = int(width * scale_x)
        target_h = int(height * scale_y)
        
        for y in range(target_h):
            line_chars = []
            src_y = int(y * step_y)
            if src_y >= height: break
            
            for x in range(target_w):
                src_x = int(x * step_x)
                if src_x >= width: break
                
                pixel = grid[src_y][src_x]
                
                if pixel is None:
                    char = " "
                else:
                    # Without Palette, we can try to guess brightness or just use shape
                    # Doom indices: 0-255. 
                    # Often gradients are grouped.
                    # Simple: Just return a solid character for now to see the Shape.
                    char = "8" 
                    
                line_chars.append(char)
            lines.append("".join(line_chars))
            
        return lines

    def load_map_data(self, map_name):
        """
        맵 이름(E1M1 등)을 찾아 그 뒤에 따르는 VERTEXES와 LINEDEFS를 로드
        순서: Header -> THINGS -> LINEDEFS(2) -> ... -> VERTEXES(4)
        """
        map_index = -1
        for i, lump in enumerate(self.lumps):
            if lump['name'] == map_name:
                map_index = i
                break
        
        if map_index == -1:
            raise ValueError(f"Map {map_name} not found in WAD.")

        # Doom 맵 데이터 순서는 고정되어 있습니다.
        # E1M1 (Header)
        # +1: THINGS
        # +2: LINEDEFS
        # +3: SIDEDEFS
        # +4: VERTEXES
        
        # THINGS 로드 (+1)
        t_lump = self.lumps[map_index + 1]
        if t_lump['name'] != "THINGS":
            print(f"[Warn] Expected THINGS but got {t_lump['name']}.")

        # LINEDEFS 로드 (Index + 2)
        l_lump = self.lumps[map_index + 2]
        if l_lump['name'] != "LINEDEFS":
            print(f"[Warn] Expected LINEDEFS but got {l_lump['name']}. Checking standard order...")
        
        # VERTEXES 로드 (Index + 4)
        v_lump = self.lumps[map_index + 4]
        if v_lump['name'] != "VERTEXES":
             print(f"[Warn] Expected VERTEXES but got {v_lump['name']}.")
        
        # SIDEDEFS 로드 (+3)
        s_lump = self.lumps[map_index + 3]
        if s_lump['name'] != "SIDEDEFS":
             print(f"[Warn] Expected SIDEDEFS but got {s_lump['name']}.")
        
        # 실제 데이터 파싱
        print(f"[*] Parsing Data for {map_name}...")
        vertexes = self.read_vertexes(v_lump['offset'], v_lump['size'])
        sidedefs = self.read_sidedefs(s_lump['offset'], s_lump['size'])
        linedefs = self.read_linedefs(l_lump['offset'], l_lump['size'])
        things = self.read_things(t_lump['offset'], t_lump['size'])
        
        return vertexes, linedefs, things, sidedefs

if __name__ == "__main__":
    try:
        loader = WADLoader("assets/DOOM1.WAD")
        loader = WADLoader("assets/Doom1.WAD")
        verts, lines, things, sides = loader.load_map_data("E1M1")
        
        print(f"\n[Result] {len(verts)} Verts, {len(lines)} Lines, {len(things)} Things, {len(sides)} Sides.")
        
        # Player 1 Start (Type 1) 찾기
        player_start = next((t for t in things if t['type'] == 1), None)
        
        if player_start:
            print(f"Found Player Start: Pos({player_start['x']}, {player_start['y']}), Angle {player_start['angle']}")
        else:
            print("Error: Player 1 Start point not found!")

    except Exception as e:
        print(f"\n[Error] {e}")
