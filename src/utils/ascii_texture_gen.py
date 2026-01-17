from src.utils.visual_assets import ANSI_COLORS

# Pattern Constants
# Optimized for 16-char width to allow seamless tiling logic
PAT_BRICK  = "##==##==++..++.."
PAT_TECH   = "1010101001001011"
PAT_DOOR   = "[][]..[][]..==== "
PAT_STONE  = ".,.,.,.,`'`'.,.,"
PAT_METAL  = "||//||//||--||--"
PAT_FLESH  = "%%$$%%$$@@&&@@&&"
PAT_SOLID  = "################" # Fallback

def generate_ascii_texture(texture_name):
    """
    Parses Doom WAD texture names and returns an ASCII pattern string.
    Returns: (pattern_string, color_code)
    """
    if not texture_name:
        return PAT_SOLID, ANSI_COLORS["WHITE"]
    
    name = texture_name.upper()
    
    # 1. Tech / Computer / Lights
    if any(k in name for k in ["TEK", "COMP", "LITE", "SHAWN", "SILVER", "SUPPORT", "PLAT"]):
        color = ANSI_COLORS["GREY_WALL"]
        if "LITE" in name: color = ANSI_COLORS["WHITE"]
        return PAT_TECH, color
        
    # 2. Door / Gate
    if any(k in name for k in ["DOOR", "GATE", "BIGDOOR"]):
        return PAT_DOOR, ANSI_COLORS["SILVER"]
        
    # 3. Brick / Tan / Brown / Wood
    if any(k in name for k in ["BRICK", "TAN", "BROWN", "WOOD", "PANEL", "STARTAN"]):
        color = ANSI_COLORS["BROWN_WALL"]
        if "WOOD" in name: color = ANSI_COLORS["DIM_BROWN"]
        return PAT_BRICK, color
        
    # 4. Stone / Rock / Ash
    if any(k in name for k in ["STONE", "ROCK", "ASH", "MARB"]):
        color = ANSI_COLORS["GREY_WALL"]
        if "MARB" in name: color = ANSI_COLORS["SLIME_GREEN"]
        return PAT_STONE, color
        
    # 5. Flesh / Skin / Blood
    if any(k in name for k in ["SKIN", "FLESH", "SLIME", "BLOOD"]):
        return PAT_FLESH, ANSI_COLORS["BLOOD_RED"]
        
    # 6. Metal / Pipes
    if any(k in name for k in ["METAL", "PIPE", "STEEL", "IRON"]):
        return PAT_METAL, ANSI_COLORS["SILVER"]

    # Fallback
    return PAT_BRICK, ANSI_COLORS["GREY_WALL"]
