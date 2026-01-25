from src.utils.wad_loader import WADLoader
import sys

try:
    loader = WADLoader("assets/DOOM1.WAD")
    name = "STARTAN3"
    
    if name in loader.texture_defs:
        defn = loader.texture_defs[name]
        print(f"Def: w={defn['width']}, h={defn['height']}, patches={len(defn['patches'])}")
        
        for i, patch in enumerate(defn['patches']):
            idx = patch['patch_idx']
            pname = loader.pnames[idx]
            print(f"  Patch {i}: idx={idx}, name={pname}")
            
            # Check if patch lump exists
            lump = loader.find_lump(pname)
            if lump:
                print(f"    -> Lump found: size={lump['size']}")
            else:
                print(f"    -> Lump NOT FOUND")
                
        tex = loader.get_decoded_texture(name)
        print(f"Result: {type(tex)}")
        if tex:
            print(f"Len: {len(tex)}")
        else:
            print("Tex is Falsy/None")
    else:
        print("STARTAN3 not in defs")

except Exception as e:
    print(f"Error: {e}")
