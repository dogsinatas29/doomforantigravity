import struct
import os

def generate_standard_test_wad(path):
    # vertices: 4
    vertices_data = b"".join(struct.pack('<hh', x, y) for x, y in [(0, 0), (512, 0), (512, 512), (0, 512)])
    
    # linedefs: 4 (14 bytes each)
    # v1, v2, flags, special, tag, r_side, l_side
    lines_data = b"".join([
        struct.pack('<HHHHHHH', 0, 1, 0, 0, 0, 0, 65535),
        struct.pack('<HHHHHHH', 1, 2, 0, 0, 0, 0, 65535),
        struct.pack('<HHHHHHH', 2, 3, 0, 0, 0, 0, 65535),
        struct.pack('<HHHHHHH', 3, 0, 0, 0, 0, 0, 65535)
    ])
    
    # THINGS data: 1 thing (10 bytes)
    # x, y, angle, type, flags
    things_data = struct.pack('<hhhhh', 128, 128, 0, 1, 7)
    
    # Dummy lumps
    dummy_data = b""
    
    # Lumps in order: E1M1, THINGS, LINEDEFS, SIDEDEFS, VERTEXES
    lump_configs = [
        ("E1M1", b""),
        ("THINGS", things_data),
        ("LINEDEFS", lines_data),
        ("SIDEDEFS", b""),
        ("VERTEXES", vertices_data)
    ]
    
    header_size = 12
    current_offset = header_size
    
    lump_blobs = []
    lump_info = []
    
    for name, data in lump_configs:
        lump_info.append((current_offset, len(data), name))
        lump_blobs.append(data)
        current_offset += len(data)
        
    dir_offset = current_offset
    directory = b"".join(struct.pack('<II8s', off, size, name.encode('ascii')) for off, size, name in lump_info)
    header = struct.pack('<4sII', b"IWAD", len(lump_info), dir_offset)
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(header)
        for blob in lump_blobs:
            f.write(blob)
        f.write(directory)
    print(f"Generated standard test WAD at {path}")

if __name__ == "__main__":
    generate_standard_test_wad("assets/DOOM1.WAD")
