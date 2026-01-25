from src.utils.visual_assets import ANSI_COLORS, ANSI_BG_COLORS

class SpriteRenderer:
    def __init__(self, wad_loader):
        self.loader = wad_loader
        self.sprite_cache = {}
        
        # ASCII ramp for sprite shading (Dark to Light)
        # Using a slightly detailed ramp for weapons
        self.ramp = " .:-=+*#%@"

    def get_ascii_char(self, luma):
        # Map 0-255 luma to ASCII char
        idx = int((luma / 255) * (len(self.ramp) - 1))
        return self.ramp[idx]

    def load_sprite(self, sprite_name):
        """
        Loads a sprite from WAD, converts to TrueColor ASCII grid, and caches it.
        Returns: List[List[str]] (2D Grid of Colored Characters)
        """
        if sprite_name in self.sprite_cache:
            return self.sprite_cache[sprite_name]

        patch = self.loader.load_patch_data(sprite_name)
        if not patch:
            return None

        # Convert to 2D Grid
        sprite_grid = []
        
        pixels = patch['pixels']
        width = patch['width']
        height = patch['height']

        for y in range(height):
            row_data = [] # List of strings (one per pixel)
            for x in range(width):
                color_idx = pixels[y][x]
                if color_idx is None:
                    row_data.append(" ") # Transparent
                else:
                    if color_idx < len(self.loader.palette):
                        r, g, b = self.loader.palette[color_idx]
                        
                        # Character selection based on luma
                        luma = int(0.299*r + 0.587*g + 0.114*b)
                        # [High Fidelity Mode] User requested "Source Mapping". 
                        # We use Solid Block to represent the raw pixel color.
                        char = "█" 
                        
                        # TrueColor ANSI (Foreground only)
                        # \033[38;2;R;G;Bm
                        colored_char = f"\033[38;2;{r};{g};{int(b)}m{char}\033[0m"
                        row_data.append(colored_char)
                    else:
                        row_data.append("?")
            sprite_grid.append(row_data)

        self.sprite_cache[sprite_name] = sprite_grid
        return sprite_grid

    def get_weapon_sprite(self, weapon_state):
        # Map weapon states to WAD sprite names
        # TODO: This mapping should ideally be config-driven or in a constants file
        mapping = {
            "SHOTGUN_IDLE": "SHTGA0",
            "SHOTGUN_FIRE_1": "SHTGA0", # Just for flash? Doom has SHTGA0 for idle/fire
            # Actually Doom Shotgun:
            # SHTG A0: Idle / Fire frame 1
            # SHTG B0: Recoil / Cocking?
            # SHTG C0, D0: Pump
            "SHOTGUN_FIRE": "SHTGA0", # Flash is usually a separate sprite or overlay
            "SHOTGUN_RECOIL": "SHTGB0",
            "SHOTGUN_PUMP1": "SHTGC0",
            "SHOTGUN_PUMP2": "SHTGD0",
            
            "PISTOL_IDLE": "PISGA0",
            "PISTOL_FIRE": "PISGB0",
            "PISTOL_RECOIL": "PISGC0",
        }
        
        sprite_name = mapping.get(weapon_state, "SHTGA0") # Default to shotgun
        return self.load_sprite(sprite_name)
