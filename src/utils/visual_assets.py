
# src/utils/visual_assets.py

# --- 1. ANSI Color Configuration ---
ANSI_COLORS = {
    "RESET": "\033[0m",
    "BROWN_WALL": "\033[38;5;94m",   # ANSI 94: Brown/Orange
    "GREY_WALL": "\033[38;5;248m",   # ANSI 248: Concrete Grey
    "SLIME_GREEN": "\033[38;5;118m", # ANSI 118: Bright Slime
    "BLOOD_RED": "\033[38;5;196m",   # ANSI 196: Blood Red
    "DARK_RED": "\033[38;5;52m",     # ANSI 52: Dark Red (Fog)
    "FOG_RED": "\033[38;5;88m",      # ANSI 88: Medium Red
    "SILVER": "\033[38;5;250m",      # Silver
    "WHITE": "\033[38;5;255m",       # White
    "BLACK": "\033[38;5;232m",       # Deep Black
    "DARK_BROWN": "\033[38;5;94m",   # Actually same as BROWN? Let's use darker.
    "DIM_BROWN": "\033[38;5;58m",    # Much Darker Brown
    "DIM_GREY": "\033[38;5;240m",    # Darker Grey
    "DIM_SILVER": "\033[38;5;245m",  # Darker Silver
}

# --- 2. Texture Styles (Doom Gritty Mix v2: Expanded Depth) ---
# Key: Texture ID (Arbitrary mapping from WAD)
# Value: Dictionary of character sets for distances
TEXTURE_STYLES = {
    1: { # BRICK (Brown)
        # Simplified: Single char per band to remove "Static/Noise"
        "chars_close":      ["█"],  
        "chars_near_mid":   ["▓"],  
        "chars_mid":        ["▒"],  
        "chars_far":        ["░"],  
        "chars_very_far":   ["."],  
        "color": ANSI_COLORS["BROWN_WALL"],
        "dim_color": ANSI_COLORS["DIM_BROWN"] 
    },
    2: { # METAL (Grey)
        "chars_close":      ["█"],  
        "chars_near_mid":   ["▓"],  
        "chars_mid":        ["▒"],  
        "chars_far":        ["░"],  
        "chars_very_far":   ["."],  
        "color": ANSI_COLORS["GREY_WALL"],
        "dim_color": ANSI_COLORS["DIM_GREY"]
    },
    3: { # DOOR / SPECIAL (Silver)
        "chars_close":      ["█"],  
        "chars_near_mid":   ["▓"],  
        "chars_mid":        ["▒"],  
        "chars_far":        ["░"],  
        "chars_very_far":   ["."],  
        "color": ANSI_COLORS["SILVER"],
        "dim_color": ANSI_COLORS["DIM_SILVER"]
    }
}

# --- 3. Fog & Floor Assets ---
FOG_CHARS = [".", ",", "~", "`", "'", "^", "-"] # Expanded for variety
ASCII_RAMP = " .:-=+*#%@" # Standard lighting ramp (backup)

# --- 4. HUD Assets (Big Face) ---
# --- [HUD ASSETS] ---
# High-Fidelity Doomguy Faces (Approx 6x4)
FACE_ASSETS = {
    "HEALTHY": [
        " .--. ",
        "| \/ |",
        " \__/",
    ],
    "LOOK_R": [
        " .--. ",
        "| ..>|",
        " \__/",
    ],
    "LOOK_L": [
        " .--. ",
        "|<.. |",
        " \__/",
    ],
    "ANGRY": [
        " .--. ",
        "|`--'|", # Gritted teeth
        " \__/",
    ],
    "BLEEDING": [
        f"  /  ~   ~  \\   ",
        f"  |  > | <  |   ",
        f"  \\  ,###,  /   "
    ],
    "MESSY": [
        "   .-------.    ",
        f"  /  x   ~  \\   ",
        f"  |  o | <  |   ",
        f"  \\ \" ### \" /   "
    ],
    "CRITICAL": [
        "   .-------.    ",
        f"  / # \\ / # \\   ",
        f"  | # | ; # |   ",
        f"  \\ ; ### ; /   "
    ],
    "EVIL": [
        "   .-------.    ",
        "  /  `   `  \\   ",
        "  |  * | *  |   ",
        "  \\  [wWw]  /   "
    ]
}

# --- 5. Weapon Assets ---

# --- [WEAPON ASSETS] ---
# Imitating Doom Sprite Frames (SHTGA0, SHTGB0...)
WEAPON_ASSETS = {
    "SHOTGUN_IDLE": [
        "      _  ",
        "     / \ ",
        "====|   |",
        "    |   |",
    ],
    "SHOTGUN_FIRE": [
        "   * BOOM * ",
        "  \  | |  / ",
        " ==\ \ / /==",
        "    |   |   ",
    ],
    "SHOTGUN_PUMP1": [
        "      // ",
        "   __//  ",
        "==|  |   ", # Pump back
        "  |  |   ",
    ],
    "SHOTGUN_PUMP2": [
        "     _   ",
        "    / \  ",
        "===|==|  ", # Pump forward
        "   |  |  ",
    ],
    "PISTOL_IDLE": [
        "    =--  ",
        "   [_]   ",
        "   /     ",
    ],
    "PISTOL_FIRE": [
        "   *BAT* ",
        "   _=--  ",
        "  /[_]   ",
        "  /      ",
    ]
}

def get_texture_id_from_name(tex_name):
    """Maps Doom texture names to our 3 styles."""
    if not tex_name: return 2
    tex_name = tex_name.upper()
    
    # Style 1: BROWN / EARTHY
    if any(x in tex_name for x in ["BROWN", "BRICK", "TAN", "DIRT", "WOOD", "PANEL", "STARTAN"]):
        return 1
        
    # Style 3: TECH / SILVER / DOOR
    if any(x in tex_name for x in ["DOOR", "SILVER", "PLAT", "SUPPORT", "LITE", "COMP", "TEK"]):
        return 3
        
    # Style 2: GREY / STONE / DEFAULT
    return 2
