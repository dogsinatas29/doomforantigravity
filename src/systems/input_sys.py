import sys
import select
from src.ecs.components import Transform, Motion
from src.utils.math_core import get_sin, get_cos

def input_system(world, engine, dt):
    """Non-blocking keyboard input processing. Consumes all pending input."""
    
    player_id = next(world.get_entities_with(Transform, Motion), None)
    if player_id is None: return
    
    transform = world.get_component(player_id, Transform)
    motion = world.get_component(player_id, Motion)
    
    move_speed = 25.0 * dt 
    rot_speed = 6.0 * dt
    pitch_speed = 4.0 * dt
    
    # Read all pending input (Limit to avoiding freezing if flooded)
    chars = []
    import sys, select
    
    # Read up to 100 chars to clear buffer
    for _ in range(100):
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            try:
                chars.append(sys.stdin.read(1))
            except: break
        else:
            break
            
    # Process Chars
    i = 0
    while i < len(chars):
        key = chars[i]
        i += 1
        
        # Escape Sequence Detection
        if key == '\x1b':
            # Peek next 2 chars if available in our buffer
            if i + 1 < len(chars) and chars[i] == '[':
                seq = chars[i+1] # A, B, C, D
                i += 2
                
                if seq == 'A': # UP Arrow
                    transform.pitch += pitch_speed
                elif seq == 'B': # DOWN Arrow
                    transform.pitch -= pitch_speed
                elif seq == 'C': # RIGHT Arrow
                    transform.angle += rot_speed
                elif seq == 'D': # LEFT Arrow
                    transform.angle -= rot_speed
                continue
        
        # Standard Keys
        if key == 'w':
            motion.vel.x += move_speed * get_cos(transform.angle)
            motion.vel.y += move_speed * get_sin(transform.angle)
        elif key == 's':
            motion.vel.x -= move_speed * get_cos(transform.angle)
            motion.vel.y -= move_speed * get_sin(transform.angle)
        elif key == 'a':
            # Strafe Left: Angle - 90 deg (Correct for Y-Down)
            motion.vel.x += move_speed * get_cos(transform.angle - 1.5708) 
            motion.vel.y += move_speed * get_sin(transform.angle - 1.5708)
        elif key == 'd':
            # Strafe Right: Angle + 90 deg
            motion.vel.x += move_speed * get_cos(transform.angle + 1.5708)
            motion.vel.y += move_speed * get_sin(transform.angle + 1.5708)
        elif key == 'q':
            transform.angle -= rot_speed # Rotate Left
        elif key == 'e':
            transform.angle += rot_speed # Rotate Right
        elif key == 'r': 
            transform.pitch += pitch_speed
        elif key == 'f': 
            transform.pitch -= pitch_speed
        elif key == ' ':
            motion.vel.z += 1.2
        elif key == 'x' or key == '\x03':
            engine.running = False
        
    # Clamp Pitch
    transform.pitch = max(-1.0, min(1.0, transform.pitch))
