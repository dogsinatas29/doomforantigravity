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
                gravity = -25.0 * dt # Stronger gravity for snappy jumps
                motion.friction = 0.5 # Less slippery (was 0.8)
            elif phys_mode.mode == PhysicsModeType.INVERTED:
                gravity = 25.0 * dt
                motion.friction = 0.5
            elif phys_mode.mode == PhysicsModeType.ZERO_G:
                gravity = 0.0
                motion.friction = 0.95 # Drift in Zero-G
        
        motion.vel.z += gravity
        motion.vel.x *= motion.friction
        motion.vel.y *= motion.friction
        motion.vel.z *= motion.friction

        # Head Bobbing Logic
        # Calculate horizontal speed
        h_speed = (motion.vel.x**2 + motion.vel.y**2)**0.5
        if h_speed > 0.01 and phys_mode.mode == PhysicsModeType.NORMAL:
             # Frequency: 10.0, Speed scalar
             motion.bob_timer += 10.0 * dt
        else:
             # Reset to neutral phase slowly? Or just stop.
             # Let's align to pi/2 (neutral) or 0. For now just pause.
             pass
        
        # Proposed new position
        new_x = transform.pos.x + motion.vel.x
        new_y = transform.pos.y + motion.vel.y
        new_z = transform.pos.z + motion.vel.z
        
        # Collision Check (Box-based)
        # We must check the range of the player's body against grid cells.
        radius = 0.4 # Slightly smaller than 0.5 to allow fitting in 1.0 holes
        
        # Helper to check if a range of Y intersects any walls at X
        def is_wall_in_range_x(grid_x, min_y, max_y):
            if not (0 <= grid_x < world.map_width): return True
            start_y = int(min_y)
            end_y = int(max_y)
            for y in range(start_y, end_y + 1):
                if 0 <= y < world.map_height:
                    if world.world_map[grid_x][y] > 0: return True
            return False

        # Helper for X range at Y
        def is_wall_in_range_y(grid_y, min_x, max_x):
            if not (0 <= grid_y < world.map_height): return True
            start_x = int(min_x)
            end_x = int(max_x)
            for x in range(start_x, end_x + 1):
                if 0 <= x < world.map_width:
                    if world.world_map[x][grid_y] > 0: return True
            return False

        # Check X
        check_x_edge = new_x + (radius if motion.vel.x > 0 else -radius)
        grid_x = int(check_x_edge)
        # Check vertical range (shoulders)
        if not is_wall_in_range_x(grid_x, transform.pos.y - radius + 0.1, transform.pos.y + radius - 0.1):
             transform.pos.x = new_x
        else:
             if phys_mode and phys_mode.mode == PhysicsModeType.ZERO_G:
                motion.vel.x *= -0.5
             else:
                motion.vel.x = 0
                
        # Check Y
        check_y_edge = new_y + (radius if motion.vel.y > 0 else -radius)
        grid_y = int(check_y_edge)
        # Check horizontal range (shoulders)
        if not is_wall_in_range_y(grid_y, transform.pos.x - radius + 0.1, transform.pos.x + radius - 0.1):
             transform.pos.y = new_y
        else:
             if phys_mode and phys_mode.mode == PhysicsModeType.ZERO_G:
                motion.vel.y *= -0.5
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
