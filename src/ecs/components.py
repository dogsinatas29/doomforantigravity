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
