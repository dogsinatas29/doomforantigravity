
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

# Background Colors (Solid Walls)
ANSI_BG_COLORS = {
    "RESET": "\033[49m",
    "BROWN": "\033[48;5;94m",     # Brown Background
    "DARK_BROWN": "\033[48;5;58m", # Dark Brown Background
    "GREY": "\033[48;5;240m",      # Grey Background
    "DARK_GREY": "\033[48;5;236m", # Dark Grey Background
    "SILVER": "\033[48;5;250m",    # Silver BG
    "DARK_SILVER": "\033[48;5;245m",
    "BLACK": "\033[48;5;232m",     # Black BG
}

# Composite Styles (High Contrast: FG ONLY)
WALL_STYLES = {
    # 1. BRICK (Brown)
    "BROWN_LIGHT":  ANSI_COLORS["WHITE"],      # Lit Face (Bright)
    "BROWN_SHADOW": ANSI_COLORS["BROWN_WALL"], # Side/Shadow Face (Dim)
    
    # 2. METAL (Grey)
    "GREY_LIGHT":   ANSI_COLORS["WHITE"],
    "GREY_SHADOW":  ANSI_COLORS["GREY_WALL"],
    
    # 3. TECH (Silver)
    "SILVER_LIGHT": ANSI_COLORS["WHITE"],      # Bright Silver
    "SILVER_SHADOW":ANSI_COLORS["DIM_GREY"],   # Dim Silver
}

# --- 2. Texture Styles (Doom High Contrast Characters) ---
# Key: Texture ID
TEXTURE_STYLES = {
    # 1: BRICK Patterns (No Numbers)
    1: {
        "chars_close": "##H==", # Heavy
        "chars_mid": "#|:.",   # Mid
        "chars_far": ":.",     # Far
        "chars_very_far": " "
    },
    # 2: METAL Patterns
    2: {
        "chars_close": "//#==", 
        "chars_mid": "/|:.",
        "chars_far": ":.",
        "chars_very_far": " "
    },
    # 3: TECH Patterns
    3: {
        "chars_close": "[]##=",
        "chars_mid": "[|:.",
        "chars_far": ":.",
        "chars_very_far": " "
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
ASCII_WEAPONS = {
    "SHOTGUN_IDLE": [
        "  _ ",
        " / \\",
        "=| |",
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
