from src.utils.wad_loader import WADLoader
from src.utils.sprite_renderer import SpriteRenderer
import sys

def print_sprite(renderer, name):
    print(f"\n--- Sprite: {name} ---")
    sprite = renderer.load_sprite(name)
    if not sprite:
        print("Not found.")
        return
        
    h = len(sprite)
    w = len(sprite[0])
    print(f"Size: {w}x{h}")
    
    for row in sprite:
        print("".join(row))

try:
    loader = WADLoader("assets/DOOM1.WAD")
    renderer = SpriteRenderer(loader)
    
    # 1. Weapon (Shotgun)
    print_sprite(renderer, "SHTGA0")
    
    # 2. Face (Player)
    print_sprite(renderer, "STFST01")
    
    # 3. Status Bar
    # STBAR is usually a patch, but let's check if load_sprite can handle it
    # If it's in TEXTURE1, it might be a texture, but usually STBAR is a graphic lump.
    # load_sprite uses load_patch_data, which searches lumps. So it should work.
    print_sprite(renderer, "STBAR")

except Exception as e:
    print(f"Error: {e}")
