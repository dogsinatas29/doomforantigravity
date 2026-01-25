from src.utils.wad_loader import WADLoader
import sys

def print_texture(loader, tex_name):
    print(f"--- Printing {tex_name} ---")
    tex = loader.get_decoded_texture(tex_name)
    if not tex:
        print("Texture not found or failed to decode.")
        return

    h = len(tex)
    w = len(tex[0])
    print(f"Size: {w}x{h}")
    
    # Print scaled down version or top-left corner if too big
    # Let's print the top-left 40x20
    
    display_w = min(w, 80)
    display_h = min(h, 40)
    
    for y in range(display_h):
        line = ""
        for x in range(display_w):
            r, g, b = tex[y][x]
            # ANSI TrueColor
            line += f"\033[38;2;{r};{g};{b}m█\033[0m"
        print(line)

try:
    loader = WADLoader("assets/DOOM1.WAD")
    print_texture(loader, "STARTAN3")
    print_texture(loader, "BROWN96")
    print_texture(loader, "FLOOR7_1")

except Exception as e:
    print(f"Error: {e}")
