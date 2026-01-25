from src.utils.wad_loader import WADLoader
import sys

try:
    loader = WADLoader("assets/DOOM1.WAD")
    print(f"Loaded WAD. Lumps: {len(loader.lumps)}")
    print(f"PNAMES: {len(loader.pnames)}")
    print(f"TEXTURES: {len(loader.texture_defs)}")
    
    print("\n--- Texture Sample ---")
    keys = list(loader.texture_defs.keys())
    print(keys[:20])
    
    check_list = ["STARTAN3", "TEKWALL4", "BIGDOOR2", "COMPBLUE", "BROWN96"]
    for name in check_list:
        if name in loader.texture_defs:
            print(f"[OK] {name} found.")
            # Try decoding
            tex = loader.get_decoded_texture(name)
            if tex:
                print(f"    - Decoded size: {len(tex[0])}x{len(tex)}")
            else:
                print(f"    - Failed to decode!")
        else:
            print(f"[FAIL] {name} NOT found in WAD.")

except Exception as e:
    print(f"Error: {e}")
