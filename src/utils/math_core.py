import math

# Constants
PI = math.pi
TWO_PI = 2 * math.pi

# Lookup Table configuration
LUT_SIZE = 3600  # 0.1 degree resolution
_sin_lut = [math.sin(i * TWO_PI / LUT_SIZE) for i in range(LUT_SIZE)]
_cos_lut = [math.cos(i * TWO_PI / LUT_SIZE) for i in range(LUT_SIZE)]

def get_sin(angle_rad):
    """Get sine from LUT using radians."""
    idx = int((angle_rad % TWO_PI) * (LUT_SIZE / TWO_PI)) % LUT_SIZE
    return _sin_lut[idx]

def get_cos(angle_rad):
    """Get cosine from LUT using radians."""
    idx = int((angle_rad % TWO_PI) * (LUT_SIZE / TWO_PI)) % LUT_SIZE
    return _cos_lut[idx]

def normalize_angle(angle):
    """Keep angle within [0, 2PI]."""
    return angle % TWO_PI

class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
