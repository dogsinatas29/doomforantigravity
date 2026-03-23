import sys
import termios
from src.ecs.system import System
from src.ecs.event_manager import MoveEvent, RotateEvent
from src.ecs.components import InputState

class InputSystem(System):
    """
    Direct input capture system for GNOME/Terminal.
    Converts raw keyboard input into Engine Events.
    """
    
    # Input system is a pure emitter, no event interests.
    EVENTS = ()

    def __init__(self):
        self.move_speed = 0.5
        self.rot_speed = 0.1

    def update(self, world: 'World', engine: 'GameEngine', dt: float):
        """Standard input capture. Updates InputState for the player entity."""
        if getattr(engine, 'replay_mode', "NONE") == "PLAYING":
            return
            
        player_id = getattr(engine, 'player_id', None)
        if player_id is None: return
        
        input_state = world.get_component(player_id, InputState)
        if not input_state: return

        # 1. Reset transient input state per frame
        input_state.fire_pressed = False
        input_state.move_x = 0
        input_state.move_y = 0
        input_state.look_x = 0
        
        char = getattr(engine, 'last_char', None)
        if not char: return

        if char == 'q':
            engine.running = False
            
        # 2. Map direct keys to InputState
        speed = self.move_speed
        rot = self.rot_speed

        if char == 'w': input_state.move_x = speed
        elif char == 's': input_state.move_x = -speed
        elif char == 'a': input_state.move_y = -speed
        elif char == 'd': input_state.move_y = speed
        elif char == 'j': input_state.look_x = -rot
        elif char == 'l': input_state.look_x = rot
        elif char == 'k': input_state.fire_pressed = True
        elif char == ' ': world.emit(MoveEvent(player_id, dz=speed*2)) # Jump stays event?
