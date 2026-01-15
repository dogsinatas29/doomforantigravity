from src.ecs.components import Transform, Motion, PhysicsMode, PhysicsModeType

def physics_system(world, engine, dt):
    """Grid-based movement and collision."""
    world_map = getattr(world, 'world_map', None)
    if not world_map:
        return
        
    for entity_id in world.get_entities_with(Transform, Motion):
        transform = world.get_component(entity_id, Transform)
        motion = world.get_component(entity_id, Motion)
        phys_mode = world.get_component(entity_id, PhysicsMode)
        
        # Apply Gravity (adjusted for smaller grid scale)
        gravity = 0.0
        if phys_mode:
            if phys_mode.mode == PhysicsModeType.NORMAL:
                gravity = -15.0 * dt
                motion.friction = 0.8
            elif phys_mode.mode == PhysicsModeType.INVERTED:
                gravity = 15.0 * dt
                motion.friction = 0.8
            elif phys_mode.mode == PhysicsModeType.ZERO_G:
                gravity = 0.0
                motion.friction = 0.99
        
        motion.vel.z += gravity
        motion.vel.x *= motion.friction
        motion.vel.y *= motion.friction
        motion.vel.z *= motion.friction
        
        # Proposed new position
        new_x = transform.pos.x + motion.vel.x
        new_y = transform.pos.y + motion.vel.y
        new_z = transform.pos.z + motion.vel.z
        
        # Collision Check (Simple Grid)
        # Check X
        if 0 <= int(new_x) < world.map_width and 0 <= int(transform.pos.y) < world.map_height:
            if world_map[int(new_x)][int(transform.pos.y)] == 0:
                transform.pos.x = new_x
            else:
                if phys_mode and phys_mode.mode == PhysicsModeType.ZERO_G:
                    motion.vel.x *= -0.8
                else:
                    motion.vel.x = 0
                
        # Check Y
        if 0 <= int(transform.pos.x) < world.map_width and 0 <= int(new_y) < world.map_height:
            if world_map[int(transform.pos.x)][int(new_y)] == 0:
                transform.pos.y = new_y
            else:
                if phys_mode and phys_mode.mode == PhysicsModeType.ZERO_G:
                    motion.vel.y *= -0.8
                else:
                    motion.vel.y = 0

        # Update Z with floor/ceiling limits (scaled)
        if new_z < 0:
            transform.pos.z = 0
            motion.vel.z = 0
        elif new_z > 30.0: # Ceiling for SCALE=0.2
            transform.pos.z = 30.0
            motion.vel.z = 0
        else:
            transform.pos.z = new_z
