#!/usr/bin/env python3
import hashlib, json, time
from dataclasses import dataclass
from typing import List, Dict, Tuple, Any
@dataclass
class AuditLeaf:
    event_id: str; timestamp: float; event_type: str; actor: str; payload: dict
    prev_leaf_hash: str = ""; leaf_hash: str = ""
    def compute_hash(self) -> str:
        raw = json.dumps({"event_id": self.event_id, "timestamp": self.timestamp, "event_type": self.event_type,
            "actor": self.actor, "payload": self.payload, "prev_leaf_hash": self.prev_leaf_hash}, sort_keys=True, default=str)
        self.leaf_hash = hashlib.sha3_256(raw.encode()).hexdigest(); return self.leaf_hash
class MerkleTree:
    def __init__(self):
        self.leaves: List[AuditLeaf] = []; self.tree_levels: List[List[str]] = []; self.root = "GENESIS_" + "0"*56
    def _hash_pair(self, left, right): return hashlib.sha3_256((left+right).encode()).hexdigest()
    def append(self, leaf: AuditLeaf) -> str:
        if self.leaves: leaf.prev_leaf_hash = self.leaves[-1].leaf_hash
        leaf.compute_hash(); self.leaves.append(leaf); self._rebuild(); return leaf.leaf_hash
    def _rebuild(self):
        if not self.leaves: self.tree_levels=[]; self.root="GENESIS_"+"0"*56; return
        current = [l.leaf_hash for l in self.leaves]; self.tree_levels=[current]
        while len(current)>1:
            nxt=[]
            for i in range(0,len(current),2):
                left=current[i]; right=current[i+1] if i+1<len(current) else left
                nxt.append(self._hash_pair(left,right))
            self.tree_levels.append(nxt); current=nxt
        self.root=current[0]
    def verify_integrity(self) -> Dict:
        errors=[]
        for i,leaf in enumerate(self.leaves):
            exp = self.leaves[i-1].leaf_hash if i>0 else ""
            if leaf.prev_leaf_hash != exp: errors.append(f"Leaf {i}: broken chain")
            leaf.compute_hash()
        expected=self.root; self._rebuild()
        if self.root != expected: errors.append("Root mismatch")
        return {"valid": len(errors)==0, "leaf_count": len(self.leaves), "root": self.root, "errors": errors[:5]}
    def log_event(self, event_type, actor, payload):
        eid = f"evt_{hashlib.sha3_256(f'{time.time()}{event_type}'.encode()).hexdigest()[:12]}"
        leaf = AuditLeaf(eid, time.time(), event_type, actor, payload)
        h = self.append(leaf)
        return {"event_id": eid, "leaf_hash": h[:16]+"...", "root": self.root[:16]+"...", "leaf_count": len(self.leaves)}
if __name__ == "__main__":
    t=MerkleTree()
    print(t.log_event("TEST","a17",{"ok":True}))
    print(t.verify_integrity())
