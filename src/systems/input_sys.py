import sys
import select
from src.ecs.components import Transform, Motion
from src.utils.math_core import get_sin, get_cos

def input_system(world, engine, dt):
    """Non-blocking keyboard input processing."""
    # Check if stdin has data
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        key = sys.stdin.read(1)
        
        player_id = next(world.get_entities_with(Transform, Motion), None)
        if player_id is None:
            return
            
        transform = world.get_component(player_id, Transform)
        motion = world.get_component(player_id, Motion)
        
        # Movement speeds adjusted for grid-based scale (0.2 SCALE)
        # Boosted based on user feedback (Was 8.0)
        move_speed = 16.0 * dt 
        rot_speed = 6.0 * dt
        pitch_speed = 4.0 * dt
        
        # Escape Sequence Detection for Arrow Keys
        if key == '\x1b':
            # Check if there are more characters to read immediately
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                seq = sys.stdin.read(2)
                if seq == '[A': # UP Arrow
                    transform.pitch += pitch_speed
                elif seq == '[B': # DOWN Arrow
                    transform.pitch -= pitch_speed
                elif seq == '[C': # RIGHT Arrow
                    transform.angle += rot_speed
                elif seq == '[D': # LEFT Arrow
                    transform.angle -= rot_speed

        if key == 'w':
            motion.vel.x += move_speed * get_cos(transform.angle)
            motion.vel.y += move_speed * get_sin(transform.angle)
        elif key == 's':
            motion.vel.x -= move_speed * get_cos(transform.angle)
            motion.vel.y -= move_speed * get_sin(transform.angle)
        elif key == 'a':
            motion.vel.x += move_speed * get_cos(transform.angle - 1.5708) 
            motion.vel.y += move_speed * get_sin(transform.angle - 1.5708)
        elif key == 'd':
            motion.vel.x += move_speed * get_cos(transform.angle + 1.5708)
            motion.vel.y += move_speed * get_sin(transform.angle + 1.5708)
        elif key == 'q':
            transform.angle -= rot_speed
        elif key == 'e':
            transform.angle += rot_speed
        elif key == 'r': # Pitch Up
            transform.pitch += pitch_speed
        elif key == 'f': # Pitch Down
            transform.pitch -= pitch_speed
        elif key == '1':
            from src.ecs.components import PhysicsModeType, PhysicsMode
            phys_mode = world.get_component(player_id, PhysicsMode)
            if phys_mode: phys_mode.mode = PhysicsModeType.NORMAL
        elif key == '2':
            from src.ecs.components import PhysicsModeType, PhysicsMode
            phys_mode = world.get_component(player_id, PhysicsMode)
            if phys_mode: phys_mode.mode = PhysicsModeType.ZERO_G
        elif key == '3':
            from src.ecs.components import PhysicsModeType, PhysicsMode
            phys_mode = world.get_component(player_id, PhysicsMode)
            if phys_mode: phys_mode.mode = PhysicsModeType.INVERTED
        elif key == ' ':
            jump_speed = 1.2 # Scaled for grid height
            motion.vel.z += jump_speed
        elif key == '\t': # TAB key
            if engine.input_cooldown <= 0:
                engine.show_automap = not engine.show_automap
                engine.input_cooldown = 0.3 # 300ms debounce
        elif key == 'x' or key == '\x03' or key == '\x04':
            engine.running = False
        
        # Clamp Pitch (Prevent neck breaking)
        # Limit to +/- 1.0 (approx 45 degrees visual tilt)
        transform.pitch = max(-1.0, min(1.0, transform.pitch))
