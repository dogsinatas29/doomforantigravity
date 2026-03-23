from dataclasses import dataclass
from src.utils.math_core import Vector3

@dataclass
class Transform:
    pos: Vector3
    angle: float  # Horizontal angle (Yaw)
    pitch: float = 0.0  # Vertical tilt (for Z-Shearing)

@dataclass
class Motion:
    vel: Vector3
    acc: Vector3
    friction: float = 0.9
    bob_timer: float = 0.0

@dataclass
class Body:
    radius: float
    height: float

@dataclass
class Stats:
    hp: int
    armor: int
    ammo: int
    fuel: float

class PhysicsModeType:
    NORMAL = 0
    ZERO_G = 1
    INVERTED = 2

@dataclass
class PhysicsMode:
    mode: int = PhysicsModeType.NORMAL

@dataclass
class Render:
    sprite_char: str = "@"
    texture_id: str = "DEFAULT"

@dataclass
class Wall:
    x1: float
    y1: float
    x2: float
    y2: float
    texture_id: int = 1

@dataclass
class InputState:
    """Transient user intent. Not for persistence."""
    move_x: float = 0.0
    move_y: float = 0.0
    look_x: float = 0.0
    look_y: float = 0.0
    fire_pressed: bool = False
    fire_trigger: bool = False # Edge pulse (Logic can use this or prev_fire)
    prev_fire_pressed: bool = False # For edge detection in systems

@dataclass
class Weapon:
    name: str = "SHOTGUN"
    state: str = "IDLE"
    cooldown: float = 0.0
