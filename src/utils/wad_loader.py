import struct
import os

class WADLoader:
    def __init__(self, wad_path):
        self.wad_path = wad_path
        self.wad_file = None
        self.lumps = [] # (name, offset, size)
        self.texture_defs = {} # Safe default
        self.pnames = [] # Safe default
        self.palette = []
        self.directory_map = {}
        
        try:
            if os.path.exists(self.wad_path):
                self.wad_file = open(self.wad_path, "rb")
                print(f"[*] Opening WAD: {self.wad_path}")
                self.load_directory()
                
                # Load Global Data
                print("[*] Loading PNAMES...")
                self.pnames = self.load_pnames()
                
                self.directory_map = {l['name']:l for l in self.lumps}
                
                print("[*] Loading TEXTURE1...")
                self.texture_defs = self.load_texture1()
                
                print("[*] Loading PLAYPAL...")
                self.palette = self.load_playpal()
            else:
                print(f"[!] WAD file not found: {self.wad_path}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[!] WAD Init Error: {e}")

    def __del__(self):
        if self.wad_file:
            self.wad_file.close()

    def load_directory(self):
        self.wad_file.seek(0)
        # Read Header
        header_data = self.wad_file.read(12)
        if len(header_data) < 12: return
        signature, num_lumps, dir_offset = struct.unpack("<4sII", header_data)
        
        print(f"[*] WAD Type: {signature.decode(errors='ignore')}")
        print(f"[*] Lumps: {num_lumps}")

        # Seek to Directory
        self.wad_file.seek(dir_offset)

        # Read All Lumps
        for _ in range(num_lumps):
            lump_data = self.wad_file.read(16)
            if len(lump_data) < 16: break
            offset, size, name_bytes = struct.unpack("<II8s", lump_data)
            name = name_bytes.decode(errors='ignore').strip('\x00').upper()
            self.lumps.append({'name': name, 'offset': offset, 'size': size})
    
    def find_lump(self, name):
        for lump in self.lumps:
            if lump['name'] == name:
                return lump
        return None

    def load_playpal(self):
        # 색상 팔레트 (PLAYPAL) 로드
        lump = self.find_lump("PLAYPAL")
        if not lump: return []
        
        self.wad_file.seek(lump['offset'])
        # 첫 번째 팔레트(256컬러 * 3바이트)만 읽음
        raw_pal = self.wad_file.read(768) 
        palette = []
        for i in range(256):
            r = raw_pal[i*3]
            g = raw_pal[i*3+1]
            b = raw_pal[i*3+2]
            palette.append((r, g, b))
        return palette

    def load_pnames(self):
        # 패치 이름 목록 (PNAMES)
        lump = self.find_lump("PNAMES")
        if not lump: return []
        
        self.wad_file.seek(lump['offset'])
        num_patches = struct.unpack("<I", self.wad_file.read(4))[0]
        pnames = []
        for _ in range(num_patches):
            name = self.wad_file.read(8).decode('ascii').strip('\x00').upper()
            pnames.append(name)
        return pnames

    def load_texture1(self):
        # 텍스처 정의 (TEXTURE1)
        lump = self.find_lump("TEXTURE1")
        if not lump: return {}
        
        base_pos = lump['offset']
        self.wad_file.seek(base_pos)
        
        num_textures = struct.unpack("<I", self.wad_file.read(4))[0]
        offsets = struct.unpack(f"<{num_textures}I", self.wad_file.read(4 * num_textures))
        
        textures = {}
        for offset in offsets:
            self.wad_file.seek(base_pos + offset)
            name = self.wad_file.read(8).decode('ascii').strip('\x00').upper()
            # [Fix] Width/Height are Short(2), not Int(4). ColDir is Int(4), not Short(2).
            # Format: < I(Masked) H(W) H(H) I(ColDir) H(Count)
            masked, width, height, col_dir, num_patches = struct.unpack("<IHHIH", self.wad_file.read(14))
            
            patches = []
            for _ in range(num_patches):
                ox, oy, p_idx, step, colmap = struct.unpack("<hhHHH", self.wad_file.read(10))
                patches.append({'origin_x': ox, 'origin_y': oy, 'patch_idx': p_idx})
            
            textures[name] = {'width': width, 'height': height, 'patches': patches}
        return textures

    def load_patch_data(self, patch_name):
        # 실제 픽셀 데이터(Patch) 읽기 (컬럼 포맷 디코딩)
        lump = self.find_lump(patch_name)
        if not lump: return None
        
        self.wad_file.seek(lump['offset'])
        
        width, height, left, top = struct.unpack("<HHhh", self.wad_file.read(8))
        col_offsets = struct.unpack(f"<{width}I", self.wad_file.read(4 * width))
        
        # 픽셀 버퍼 생성 (2D 배열)
        pixels = [[None] * width for _ in range(height)]
        
        start_pos = lump['offset']
        for x, col_off in enumerate(col_offsets):
            self.wad_file.seek(start_pos + col_off)
            while True:
                row = struct.unpack("B", self.wad_file.read(1))[0]
                if row == 255: break # 컬럼 끝
                
                n_pixels = struct.unpack("B", self.wad_file.read(1))[0]
                self.wad_file.read(1) # Dummy
                
                for i in range(n_pixels):
                    color_idx = struct.unpack("B", self.wad_file.read(1))[0]
                    if 0 <= row + i < height:
                        pixels[row + i][x] = color_idx
                self.wad_file.read(1) # Dummy
                
        return {'width': width, 'height': height, 'pixels': pixels}

    # --------------------------------------------------------
    # [Ordered Dithering] 4x4 Bayer Matrix
    # --------------------------------------------------------
    BAYER_MATRIX = [
        [  0, 128,  32, 160 ],
        [ 192,  64, 224,  96 ],
        [  48, 176,  16, 144 ],
        [ 240, 112, 208,  80 ]
    ]

    def get_decoded_texture(self, tex_name):
        # 텍스처 이름으로 Grayscale (0~255) 맵 반환
        if tex_name not in self.texture_defs:
            # print(f"[!] Texture not found: {tex_name}")
            return None
        
        tex_def = self.texture_defs[tex_name]
        w, h = tex_def['width'], tex_def['height']
        
        # 0이 아니라 None으로 초기화 (투명도 처리를 위해) -> (0,0,0) (Black)
        canvas = [[(0, 0, 0)] * w for _ in range(h)]
        
        for patch_def in tex_def['patches']:
            if patch_def['patch_idx'] >= len(self.pnames): continue
            p_name = self.pnames[patch_def['patch_idx']]
            
            patch = self.load_patch_data(p_name)
            if not patch: continue
            
            ox, oy = patch_def['origin_x'], patch_def['origin_y']
            
            for Py in range(patch['height']):
                for Px in range(patch['width']):
                    Tx, Ty = Px + ox, Py + oy
                    if 0 <= Tx < w and 0 <= Ty < h:
                        color_idx = patch['pixels'][Py][Px]
                        if color_idx is not None:
                            if color_idx < len(self.palette):
                                # Store RGB Tuple directly
                                canvas[Ty][Tx] = self.palette[color_idx]
                            else:
                                canvas[Ty][Tx] = (255, 0, 255) # Magenta Error
        return canvas

        return canvas

    def load_flat(self, flat_name):
        """
        Loads a Flat (Floor/Ceiling Texture).
        Flats are raw 64x64 bytes (4096 bytes total), each byte is a palette index.
        """
        lump = self.find_lump(flat_name)
        if not lump: return None
        
        self.wad_file.seek(lump['offset'])
        
        # Flats are always 64x64 in Doom engine
        width, height = 64, 64
        size = width * height
        
        if lump['size'] != size:
            # print(f"[!] Warning: Flat {flat_name} has invalid size {lump['size']}")
            return None
            
        data = self.wad_file.read(size)
        
        # Init canvas
        canvas = [[(0,0,0) for _ in range(width)] for _ in range(height)]
        
        for y in range(height):
            for x in range(width):
                 # idx = y * 64 + x
                 color_index = data[y * width + x]
                 if color_index < len(self.palette):
                     canvas[y][x] = self.palette[color_index]
                 else:
                     canvas[y][x] = (255, 0, 255)
        return canvas

    def read_vertexes(self, offset, size):
        """VERTEXES 럼프 파싱"""
        vertexes = []
        self.wad_file.seek(offset)
        num_vertexes = size // 4
        for _ in range(num_vertexes):
            x, y = struct.unpack("<hh", self.wad_file.read(4))
            vertexes.append((x, y))
        return vertexes

    def read_sidedefs(self, offset, size):
        """SIDEDEFS 럼프 파싱"""
        sidedefs = []
        self.wad_file.seek(offset)
        num_sidedefs = size // 30
        for _ in range(num_sidedefs):
            data = struct.unpack("<hh8s8s8sh", self.wad_file.read(30))
            mid_tex = data[4].decode(errors='ignore').strip('\x00').upper()
            sidedefs.append({'mid': mid_tex})
        return sidedefs

    def read_linedefs(self, offset, size):
        """LINEDEFS 럼프 파싱"""
        linedefs = []
        self.wad_file.seek(offset)
        num_linedefs = size // 14
        for _ in range(num_linedefs):
            data = struct.unpack("<7H", self.wad_file.read(14))
            start_v_id = data[0]
            end_v_id = data[1]
            flags = data[2]
            right_side = data[5]
            left_side = data[6]
            linedefs.append((start_v_id, end_v_id, flags, right_side))
        return linedefs

    def read_things(self, offset, size):
        """THINGS 럼프 파싱"""
        things = []
        self.wad_file.seek(offset)
        num_things = size // 10
        for _ in range(num_things):
            data = struct.unpack("<5h", self.wad_file.read(10))
            thing = {
                'x': data[0], 'y': data[1], 'angle': data[2],
                'type': data[3], 'flags': data[4]
            }
            things.append(thing)
        return things

    def load_map_data(self, map_name):
        lump_idx = -1
        for i, l in enumerate(self.lumps):
            if l['name'] == map_name:
                lump_idx = i
                break
        
        if lump_idx == -1: raise ValueError(f"Map {map_name} not found")
        
        t_lump = self.lumps[lump_idx + 1]
        l_lump = self.lumps[lump_idx + 2]
        s_lump = self.lumps[lump_idx + 3]
        v_lump = self.lumps[lump_idx + 4]
        
        verts = self.read_vertexes(v_lump['offset'], v_lump['size'])
        sides = self.read_sidedefs(s_lump['offset'], s_lump['size'])
        lines = self.read_linedefs(l_lump['offset'], l_lump['size'])
        things = self.read_things(t_lump['offset'], t_lump['size'])
        
        return verts, lines, things, sides

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

# Alias for compatibility
TextureLoader = WADLoader
