import hashlib
import json

def generate_state_hash(state_dict: dict) -> str:
    """Creates a stable SHA-256 hash of a dictionary."""
    state_str = json.dumps(state_dict, sort_keys=True)
    return hashlib.sha256(state_str.encode('utf-8')).hexdigest()

def compare_states(s1: dict, s2: dict) -> list:
    """Returns a list of human-readable differences between two world states."""
    diffs = []
    
    e1 = s1.get('entities', {})
    e2 = s2.get('entities', {})
    
    all_eids = set(e1.keys()) | set(e2.keys())
    for eid in all_eids:
        if eid not in e1:
            diffs.append(f"Entity {eid}: Missing in state 1")
            continue
        if eid not in e2:
            diffs.append(f"Entity {eid}: Missing in state 2")
            continue
            
        c1 = e1[eid]
        c2 = e2[eid]
        all_comps = set(c1.keys()) | set(c2.keys())
        for comp in all_comps:
            if comp not in c1:
                diffs.append(f"Entity {eid}: Component {comp} missing in state 1")
                continue
            if comp not in c2:
                diffs.append(f"Entity {eid}: Component {comp} missing in state 2")
                continue
            
            if c1[comp] != c2[comp]:
                diffs.append(f"Entity {eid}: Component {comp} data mismatch")
                diffs.append(f"  Exp: {c1[comp]}")
                diffs.append(f"  Act: {c2[comp]}")
                
    return diffs
