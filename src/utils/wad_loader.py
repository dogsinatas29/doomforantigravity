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

    def read_linedefs(self, offset, size):
        """
        LINEDEFS 럼프 파싱
        포맷: start_v(H), end_v(H), flags(H), type(H), tag(H), right(H), left(H) -> 14 bytes
        우리는 벽을 그리기 위해 start_v, end_v, flags만 우선적으로 필요합니다.
        """
        linedefs = []
        with open(self.wad_path, "rb") as f:
            f.seek(offset)
            num_linedefs = size // 14
            for _ in range(num_linedefs):
                # <7H: Little Endian, unsigned short (2 bytes) * 7
                data = struct.unpack("<7H", f.read(14))
                start_v_id = data[0]
                end_v_id = data[1]
                flags = data[2]
                # (Start Index, End Index, Flags)
                linedefs.append((start_v_id, end_v_id, flags))
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
        
        # 실제 데이터 파싱
        print(f"[*] Parsing Data for {map_name}...")
        vertexes = self.read_vertexes(v_lump['offset'], v_lump['size'])
        linedefs = self.read_linedefs(l_lump['offset'], l_lump['size'])
        things = self.read_things(t_lump['offset'], t_lump['size'])
        
        return vertexes, linedefs, things

if __name__ == "__main__":
    try:
        loader = WADLoader("assets/DOOM1.WAD")
        verts, lines, things = loader.load_map_data("E1M1")
        
        print(f"\n[Result] {len(verts)} Verts, {len(lines)} Lines, {len(things)} Things.")
        
        # Player 1 Start (Type 1) 찾기
        player_start = next((t for t in things if t['type'] == 1), None)
        
        if player_start:
            print(f"Found Player Start: Pos({player_start['x']}, {player_start['y']}), Angle {player_start['angle']}")
        else:
            print("Error: Player 1 Start point not found!")

    except Exception as e:
        print(f"\n[Error] {e}")
