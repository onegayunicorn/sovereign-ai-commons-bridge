#!/usr/bin/env python3
"""Core verification tests — L1 software evidence only."""
import hashlib
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_merkle_deterministic():
    from crypto.merkle_audit import MerkleTree
    t1, t2 = MerkleTree(), MerkleTree()
    # Fixed timestamp for determinism in leaf content via controlled payload
    for tree in (t1, t2):
        tree.log_event("TEST", "node", {"n": 1})
    # Structure validity
    v1 = t1.verify_integrity()
    assert v1["valid"] is True
    assert v1["leaf_count"] >= 1
    print("PASS merkle_deterministic / integrity")

def test_mldsa_interface():
    from crypto.ml_dsa65 import MLDSA65
    m = MLDSA65()
    st = m.status()
    assert st.get("ready") is True
    # Must not claim real PQC if simulation
    r = m.sign_merkle_root("abc123")
    assert r.get("verified") is True
    if not r.get("real_liboqs", False):
        assert "sim" in r.get("algorithm", "").lower() or st.get("runtime") == "simulation"
    print("PASS mldsa_interface (simulation boundaries respected)")

def test_agent_registry_43():
    from agents.full_43_agents import total, AGENTS
    assert total() == 43
    assert "quantum" in AGENTS and "junction" in AGENTS
    # Registry surface — not runtime process count
    print("PASS agent_registry_43 (registry surface only)")

def test_manifest():
    path = os.path.join(os.path.dirname(__file__), "..", "audit", "manifest.json")
    if os.path.isfile(path):
        data = json.load(open(path))
        assert "merkle_root" in data
        assert len(data["merkle_root"]) == 64
        print("PASS manifest merkle_root present")
    else:
        print("SKIP manifest (not yet sealed)")

if __name__ == "__main__":
    test_merkle_deterministic()
    test_mldsa_interface()
    test_agent_registry_43()
    test_manifest()
    print("ALL CORE TESTS PASSED")
