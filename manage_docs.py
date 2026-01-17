from gdrive_mcp import get_gdrive_service
from googleapiclient.http import MediaIoBaseUpload
import io

# --- Content Generators ---

def get_content_01_overview():
    return """# 🚀 01. Project Overview

## 1. Project Identity
*   **Title**: DooM for AntigravitY
*   **Concept**: Classic Doom Resources + Quake Physics + Zero-G Mechanics.
*   **Platform**: Linux / WSL (Windows Subsystem for Linux).
*   **Constraint**: Zero-Dependency (Python 3.8+ Standard Library Only), Console Only (No GUI libraries).

## 2. Project File Structure
```
DooM-AntigravitY/
├── assets/             # External Resources
│   ├── DOOM.WAD        # Original Doom WAD
│   └── config.json     # User Settings
├── saves/              # Save Data
├── src/                # Source Code
│   ├── engine.py       # Main Loop & Entry Point
│   ├── ecs/            # ECS Core
│   ├── systems/        # Game Logic (Input, Physics, Render)
│   └── utils/          # Utilities (WAD Loader, Math)
├── docs/               # Documentation
└── main.py             # Execution Script
```
"""

def get_content_02_design():
    return """# 🎮 02. Game Design

## 1. Physics Modes (The Core)
*   **Normal Mode**: `g = -9.8`. Standard FPS movement. Space to boost.
*   **Zero-G Mode**: `g = 0`. High conservation of momentum. Bounce off walls. 360-degree movement.
*   **Inverted Mode**: `g = +9.8`. Gravity is reversed. Ceiling becomes floor. Rendering is flipped upside down.

## 2. Movement Tech
*   **Inertia**: Smooth acceleration/deceleration.
*   **Hovering**: Tap boost to maintain altitude.
*   **Wall Kick**: In Zero-G, kick off walls for rapid direction changes.

## 3. Rendering Pipeline
*   **Raycasting**: Classic DDA algorithm.
*   **Z-Shearing**: Simulates vertical look (pitch) by shearing the 2D projection, rather than true 3D rotation, for performance.
*   **ASCII output**: 100x40 text grid resolution using standard characters.
"""

def get_content_03_architecture():
    return """# 🏗️ 03. Architecture

## 1. ECS (Entity Component System)
The project rigorously follows ECS pattern to decouple data from logic.

### Components (`src/ecs/components.py`)
*   **Transform**: Position (x, y, z), Angle (yaw), Pitch.
*   **Motion**: Velocity (vx, vy, vz), Acceleration, Friction.
*   **PhysicsMode**: Stores current gravity state (NORMAL, ZERO_G, INVERTED).
*   **Body**: Physical dimensions (radius, height) for collision.
*   **Wall**: Defines static map geometry.

### Systems (`src/systems/`)
*   **`physics_system`**: 
    1. Apply gravity based on `PhysicsMode`.
    2. Update position (`pos += vel`).
    3. Check grid-based wall collisions.
    4. Constrain Z-height (Floor/Ceiling).
*   **`render_system`**: 
    1. Cast rays for horizontal FOV.
    2. Calculate wall heights.
    3. Apply Z-shearing for pitch.
    4. Render to ASCII buffer.

## 2. Main Loop (`src/engine.py`)
*   Initializes `World`.
*   Loads WAD data.
*   Loops: `Input` -> `Physics` -> `Combat` -> `Render` -> `Sleep`.
"""

def get_content_04_data():
    return """# 💾 04. Data Specifications

## 1. WAD File Integration (`src/utils/wad_loader.py`)
We directly parse the binary `DOOM.WAD` format using Python's `struct` module.

### Core Lumps Parsed
*   **THINGS**: Entity spawn points. We look for Type 1 (Player Start).
    *   Format: `x(short)`, `y(short)`, `angle(short)`, `type(short)`, `flags(short)`.
*   **LINEDEFS**: Wall definitions.
    *   Format: `start_v`, `end_v`, `flags`...
*   **VERTEXES**: 2D Coordinates of wall endpoints.

### Scaling
*   **Vertical Scale**: All ceiling heights are multiplied by **2.5** during loading.
    *   *Reasoning*: Original Doom maps are vertically short; scaling is needed to accommodate the "Jetpack/Zero-G" gameplay without cramping the player.

## 2. Missing Data / Planned
*   **`items.csv`**: Currently not present. Planned for defining weapon stats, drop rates, and enemy attributes in a data-driven way.
"""

# --- Main Upload Logic ---

def update_index():
    service = get_gdrive_service()
    
    # 1. 'GOOGLE AI Studio' Root 찾기
    root_name = 'GOOGLE AI Studio'
    query = f"name = '{root_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    roots = results.get('files', [])
    root_id = roots[0].get('id')

    # 2. index.md 찾기
    index_filename = "index.md"
    query = f"name = '{index_filename}' and '{root_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])

    new_content = """# 📂 AI Studio Project Index

## 🛡️ Enhanced Roguelike Analysis (Detailed)
*Based on Source Code Analysis of `Roguelike` Folder*

### 📘 Documentation
1.  **[01_GAME_DESIGN.md](./Roguelike/01_GAME_DESIGN.md)** - 기획서 (Reverse Engineered)
    *   Classes, Items, Skills, Bestiary
2.  **[02_DEV_ARCH.md](./Roguelike/02_DEV_ARCH.md)** - 개발 문서 (Architecture)
    *   ECS Core, Event System, Data Factory
3.  **[03_BALANCE_GUIDE.md](./Roguelike/03_BALANCE_GUIDE.md)** - 밸런싱 가이드 (CSV)
    *   Items, Monsters, Skills Data Manipulation
"""
    media = MediaIoBaseUpload(io.BytesIO(new_content.encode('utf-8')), mimetype='text/markdown', resumable=True)
    
    if files:
        service.files().update(fileId=files[0]['id'], media_body=media).execute()
        print("Updated index.md")
    else:
        print("index.md not found to update.")

if __name__ == "__main__":
    update_index()
