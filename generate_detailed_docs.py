from gdrive_mcp import get_gdrive_service
from googleapiclient.http import MediaIoBaseUpload
import io

# --- Content Generators ---

def get_design_doc():
    return """# 🎮 01. Game Design Document
*Reverse-engineered from Source Code & Data*

## 1. Character Classes
Based on `classes.csv`, the game features 4 distinct classes:
*   **WARRIOR**: Tank. High Strength/Vitality. Starts with Dagger, Buckler. Skill: `REPAIR`.
*   **ROGUE**: DPS/Utility. High Dexterity. Starts with Short Bow. Skill: `DISARM` (Trap removal).
*   **SORCERER**: Mage. High Magic. Starts with Staff. Skill: `RECHARGE` (MP Gen).
*   **BARBARIAN**: Berserker. Highest HP/Str, Low Def (No Shield). Skill: `RAGE`.

## 2. Core Stats
*   **HP/MP**: Health and Mana.
*   **STR**: Melee Damage.
*   **MAG**: Spell Damage & Max MP.
*   **DEX**: Ranged Damage & Trap disarm chance.
*   **VIT**: Max HP & Defense.

## 3. Skill System (`skills.csv`)
Skills utilize an elemental system and `flags` for mechanics:
*   **Elements**: Fire, Ice, Lightning, Holy, Physical.
*   **Mechanics**:
    *   `PROJECTILE`: Fires a remote entity.
    *   `SPLIT`: Projectiles split on impact (e.g., Charged Bolt).
    *   `SCALABLE`: Damage scales with user stats.
    *   `UNDEAD_BONUS`: Bonus damage vs Wraiths/Skeletons (e.g., Holy Bolt).

## 4. Itemization (`items.csv`)
*   **Weapons**: Daggers, Sabers, Bows. Defined damage ranges (e.g., "1-4").
*   **Consumables**: Potions, Scrolls.
*   **Affix System**: Items can have Prefixes/Suffixes (`prefixes.json`, `suffixes.json`) modifying stats.

## 5. Bestiary (`monsters.csv`)
*   **AI Types**:
    *   `COWARD`: Flees when low HP (Goblin).
    *   `AGGRESSIVE`: Chases player (Orc, Wraith).
    *   `STATIONARY`: Does not move (Slime).
*   **Special Abilities**:
    *   `STUN_ON_HIT`: Orcs can stun.
    *   `SPLIT_ON_DEATH`: Slimes multiply.
    *   `UNDEAD`: Vulnerable to Holy.
"""

def get_dev_doc():
    return """# 🏗️ 02. Developer Architecture Guide
*Analysis of ECS and Core Systems*

## 1. ECS Architecture (`ecs.py`)
The game uses a strict Entity-Component-System pattern.
*   **World**: Container for all Entities and Systems. Manages `entity_id` allocation.
*   **Entity**: A simple ID with a dictionary of Components.
*   **Component**: Data containers (dataclasses recommended).
*   **System**: Logic processors. Must implement `process()`.

## 2. Event System
Centralized `EventManager` in `World`.
*   **Pattern**: Pub/Sub.
*   **Registration**: Systems register methods like `handle_collision_event`.
*   **Dispatch**: Events are pushed to a queue and processed sequentially in `process_events()`.

## 3. Data Loading (`items.py`)
*   **Factory Pattern**: `Item.from_definition` creates instances based on data.
*   **Polymorphism**:
    *   `Equipment`: Has `slot`, `value`, `req_level`.
    *   `Consumable`: Has `effect_type`.
    *   `SkillBook`: Grants skills.

## 4. Key Systems
*   **InventorySystem**: Manages item slots, weight, and equipment bonuses.
*   **BalanceTuner**: Tool for automated simulation of combat to test CSV values.
"""

def get_balance_doc():
    return """# ⚖️ 03. Balancer's Guide: Data Manipulation
*How to adjust game balance via CSV*

## 1. General Rules
*   **Format**: Standard CSV. Header row required.
*   **Reload**: Restart the game to apply changes.

## 2. Items (`items.csv`)
*   **`attack`**: Damage range. Format "Min-Max" (e.g., `3-8`).
*   **`required_level`**: Minimum level to equip.
*   **`hand_type`**: `1` (One-handed), `2` (Two-handed).
*   **`flags`**: Special properties (comma-separated).

## 3. Monsters (`monsters.csv`)
*   **`Action_Delay`**: Attack speed. Lower is faster (1.0 = standard).
*   **`Crit_Chance`**: 0.0 to 1.0 (Decimal).
*   **`Resistances`**: 0-100. Percentage damage reduction against elements (`res_fire`, `res_ice`).
*   **`flags`**:
    *   `STUN_ON_HIT`: Adds stun effect to attacks.
    *   `SPLIT_ON_DEATH`: Spawns smaller versions on kill.

## 4. Skills (`skills.csv`)
*   **`damage`**: Base damage range. Scaled by stats if `SCALABLE` flag is present.
*   **`type`**: `ATTACK` (Damage), `RECOVERY` (Heal), `BUFF` (Stat up).
*   **`flags`**:
    *   `PROJECTILE`: Needs line of sight.
    *   `SPLIT`: Multishot.
"""

def manage_docs():
    service = get_gdrive_service()
    
    # 1. 'GOOGLE AI Studio' Root 찾기
    root_name = 'GOOGLE AI Studio'
    query = f"name = '{root_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    roots = results.get('files', [])
    
    if not roots:
        print(f"Error: '{root_name}' not found.")
        return
    root_id = roots[0].get('id')

    # 2. 'Roguelike' Project Folder 찾기
    project_name = "Roguelike"
    query = f"name = '{project_name}' and '{root_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    projects = results.get('files', [])
    
    if not projects:
        print(f"Error: '{project_name}' folder not found.")
        return
    else:
        project_id = projects[0].get('id')
    
    print(f"Target Project Folder: '{project_name}' (ID: {project_id})")

    # 3. 문서 목록 정의
    docs = [
        ("01_GAME_DESIGN.md", get_design_doc()),
        ("02_DEV_ARCH.md", get_dev_doc()),
        ("03_BALANCE_GUIDE.md", get_balance_doc())
    ]

    # 4. 업로드 루프
    for filename, content in docs:
        query = f"name = '{filename}' and '{project_id}' in parents and trashed = false"
        results = service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])
        
        media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='text/markdown', resumable=True)
        
        if files:
            # Update
            service.files().update(fileId=files[0]['id'], media_body=media).execute()
            print(f"Updated: {filename}")
        else:
            # Create
            metadata = { 'name': filename, 'parents': [project_id] }
            service.files().create(body=metadata, media_body=media, fields='id').execute()
            print(f"Created: {filename}")

if __name__ == "__main__":
    manage_docs()
