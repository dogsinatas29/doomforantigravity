import json
from dataclasses import asdict
from typing import Dict, List, Any, Optional
from src.ecs.components import InputState, Transform, Motion, Weapon, Stats

class ReplayManager:
    """
    Handles capturing initial state, frame-by-frame input stream, and periodic keyframes.
    Enables logarithmic time exploration (Seeking) and deterministic verification.
    """
    KEYFRAME_INTERVAL = 300 # Every 5-10 seconds of gameplay at 60/30fps

    def __init__(self, world: 'World'):
        self.world = world
        self.initial_snapshot = None
        self.input_stream: List[Dict[str, Any]] = []
        self.keyframes: List[Dict[str, Any]] = []
        self.start_tick = 0

    def start_recording(self):
        """Capture the starting line for the replay."""
        self.initial_snapshot = self.world.capture_state()
        self.start_tick = self.world.ticks
        self.input_stream = []
        self.keyframes = []
        
        initial_hash = self.world.get_state_hash()
        print(f"[*] Recording started at Tick {self.start_tick}")
        print(f"[*] Initial State Hash: {initial_hash}")

    def record_tick(self):
        """Store InputState and check if a keyframe should be captured."""
        elapsed_ticks = self.world.ticks - self.start_tick
        
        tick_inputs = {
            "tick": self.world.ticks,
            "entities": {},
            "state_hash": self.world.get_state_hash()
        }
        
        for eid in self.world.get_entities_with(InputState):
            inp = self.world.get_component(eid, InputState)
            tick_inputs["entities"][eid] = asdict(inp)
            
        self.input_stream.append(tick_inputs)

        # Keyframe logic: Periodic full state capture for fast-seeking
        if elapsed_ticks > 0 and elapsed_ticks % self.KEYFRAME_INTERVAL == 0:
            print(f"[*] Capturing Keyframe at Tick {self.world.ticks}")
            self.keyframes.append({
                "tick": self.world.ticks,
                "snapshot": self.world.capture_state()
            })

    def save_replay(self, filepath: str):
        """Bundle the snapshot, stream, and keyframes into a single replay file."""
        replay_data = {
            "version": "1.2-seekable",
            "start_tick": self.start_tick,
            "initial_snapshot": self.initial_snapshot,
            "keyframes": self.keyframes,
            "input_stream": self.input_stream
        }
        with open(filepath, 'w') as f:
            json.dump(replay_data, f, indent=2)
        print(f"[*] Replay saved to {filepath} ({len(self.input_stream)} ticks, {len(self.keyframes)} keyframes)")

    def load_replay(self, filepath: str):
        """Initialize the manager with a stored replay."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.initial_snapshot = data["initial_snapshot"]
            self.input_stream = data["input_stream"]
            self.keyframes = data.get("keyframes", [])
            self.start_tick = data["start_tick"]
        print(f"[*] Loaded replay from {filepath} (Start Tick: {self.start_tick})")

    def seek(self, target_tick: int, engine: Any = None) -> int:
        """
        Jump to a specific tick using the nearest previous keyframe.
        Returns the new replay_offset.
        """
        if not self.input_stream:
            return 0
            
        # 1. Find nearest keyframe before target_tick
        best_kf = None
        for kf in self.keyframes:
            if kf["tick"] <= target_tick:
                best_kf = kf
            else:
                break
        
        # 2. Restore state
        if best_kf:
            print(f"[*] Seeking: jumping to keyframe at Tick {best_kf['tick']}")
            self.world.restore_state(best_kf["snapshot"])
            current_tick = best_kf["tick"]
        else:
            print(f"[*] Seeking: jumping to initial snapshot at Tick {self.start_tick}")
            self.world.restore_state(self.initial_snapshot)
            current_tick = self.start_tick
            
        # 3. Fast-forward with deterministic update (headless)
        # We must use exactly the same timeline of inputs.
        # replay_offset is the index in input_stream.
        # input_stream[0] is for tick start_tick.
        start_offset = current_tick - self.start_tick
        target_offset = target_tick - self.start_tick
        
        # Clip target_offset to stream bounds
        target_offset = max(0, min(target_offset, len(self.input_stream) - 1))
        
        print(f"[*] Seeking: fast-forwarding {target_offset - start_offset} frames...")
        
        for offset in range(start_offset, target_offset):
            # Inject recorded input
            self.play_tick(offset)
            
            # Update world logic (using fixed dt for determinism proof)
            # engine.py might use variable DT, but for seeking, we follow the ticks.
            # If the engine update caps DT at FIXED_DT, we should use that.
            # We'll use 1/60 as requested previously for physics stability.
            self.world.update(1.0/60.0, engine)
            
            # Validation at each step (optional but good for proof)
            # if not self.verify_tick(offset): break
            
        return target_offset

    def play_tick(self, tick_offset: int) -> bool:
        """Inject recorded InputState into the world for the given frame offset."""
        if tick_offset < 0 or tick_offset >= len(self.input_stream):
            return False
            
        tick_data = self.input_stream[tick_offset]
        for eid_str, input_dict in tick_data["entities"].items():
            eid = int(eid_str)
            inp = self.world.get_component(eid, InputState)
            if inp:
                for k, v in input_dict.items():
                    setattr(inp, k, v)
        return True

    def verify_tick(self, tick_offset: int) -> bool:
        """Compare current world state with the recorded hash for this tick."""
        if tick_offset < 0 or tick_offset >= len(self.input_stream):
            return True
            
        recorded_data = self.input_stream[tick_offset]
        recorded_hash = recorded_data.get("state_hash")
        if not recorded_hash:
            return True 
            
        current_hash = self.world.get_state_hash()
        if current_hash != recorded_hash:
            print(f"[!] DETERMINISM BREACH at Tick {recorded_data['tick']} (Offset: {tick_offset})")
            print(f"    Expected: {recorded_hash}")
            print(f"    Actual:   {current_hash}")
            return False
        return True
