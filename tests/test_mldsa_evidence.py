#!/usr/bin/env python3
"""ML-DSA-65 Evidence Harness — deterministic L1 validation (Ω-style).

Produces structured evidence for the simulation backend and documents
real-backend requirements. Simulation results are never promoted to
cryptographic evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto.ml_dsa65 import MLDSA65, ALGORITHM, SIMULATION_ALGORITHM

# Fixed test vectors (deterministic inputs for evidence)
MERKLE_ROOT = "1742066dfc8bc898b461ce38baac17d3f349047c40afb8f96be320b2fd7f0d1d"
FOLD = "FE-OGUF-P1"
MESSAGE_PREFIX = "SACB-MLDSA65-v1"


def _canonical_message(merkle_root: str, fold: str) -> bytes:
    return (
        f"{MESSAGE_PREFIX}\n"
        f"algorithm={ALGORITHM}\n"
        f"merkle_root={merkle_root}\n"
        f"fold={fold}\n"
    ).encode("utf-8")


def test_simulation_status_boundaries():
    with MLDSA65(backend="simulation") as m:
        st = m.status()
        assert st["ready"] is True
        assert st["backend"] == "simulation"
        assert st["real_liboqs"] is False
        assert st["runtime"] == "simulation"
        assert "sim" in st["mechanism"].lower()
    print("PASS simulation_status_boundaries")


def test_simulation_sign_verify_roundtrip():
    with MLDSA65(backend="simulation") as m:
        result = m.sign_merkle_root(MERKLE_ROOT, fold=FOLD)
        assert result["verified"] is True
        assert result["real_liboqs"] is False
        assert result["backend"] == "simulation"
        assert result["algorithm"] == SIMULATION_ALGORITHM
        assert result["fold"] == FOLD
        assert result["public_key_sha3_256"] and len(result["public_key_sha3_256"]) == 64
        assert result["signature_sha3_256"] and len(result["signature_sha3_256"]) == 64
    print("PASS simulation_sign_verify_roundtrip")


def test_versioned_message_format():
    msg = _canonical_message(MERKLE_ROOT, FOLD)
    assert msg.startswith(MESSAGE_PREFIX.encode())
    assert b"algorithm=ML-DSA-65" in msg
    assert MERKLE_ROOT.encode() in msg
    assert FOLD.encode() in msg
    with MLDSA65(backend="simulation") as m:
        sig = m.sign(msg)
        assert m.verify(msg, sig) is True
        # Tamper detection (simulation verifies via recompute; still useful)
        assert m.verify(msg + b"x", sig) is False
    print("PASS versioned_message_format")


def test_real_backend_fails_closed_when_unavailable():
    try:
        MLDSA65(backend="real")
        # If we got here, real backend is present — note it but do not fail harness
        print("NOTE real backend available in this environment")
    except Exception as e:
        assert "oqs" in str(e).lower() or "ML-DSA" in str(e) or "enabled" in str(e).lower()
        print("PASS real_backend_fails_closed_when_unavailable")


def test_auto_backend_reports_accurately():
    with MLDSA65(backend="auto") as m:
        st = m.status()
        assert st["ready"] is True
        assert st["backend"] in ("simulation", "real")
        assert st["real_liboqs"] is (st["backend"] == "real")
    print("PASS auto_backend_reports_accurately")


def generate_evidence_record() -> dict:
    """Produce a structured evidence record for the simulation path."""
    with MLDSA65(backend="simulation") as m:
        status = m.status()
        signed = m.sign_merkle_root(MERKLE_ROOT, fold=FOLD)

    record = {
        "evidence_plane": "ML-DSA-65",
        "evidence_level": "L1",
        "evidence_kind": "software_interface_validation",
        "backend": status["backend"],
        "real_liboqs": status["real_liboqs"],
        "mechanism": status["mechanism"],
        "fold": FOLD,
        "merkle_root_under_test": MERKLE_ROOT,
        "message_version": MESSAGE_PREFIX,
        "verified": signed["verified"],
        "public_key_sha3_256": signed["public_key_sha3_256"],
        "signature_sha3_256": signed["signature_sha3_256"],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "non_claims": [
            "simulation_is_cryptographic_evidence: false",
            "hardware_backed_signing: false",
            "nfc_biometric_photonic: false",
        ],
        "ts_utc": datetime.now(timezone.utc).isoformat(),
    }
    return record


def main() -> int:
    test_simulation_status_boundaries()
    test_simulation_sign_verify_roundtrip()
    test_versioned_message_format()
    test_real_backend_fails_closed_when_unavailable()
    test_auto_backend_reports_accurately()

    record = generate_evidence_record()
    out_dir = os.path.join(os.path.dirname(__file__), "..", "audit")
    os.makedirs(out_dir, exist_ok=True)
    evidence_path = os.path.join(out_dir, "mldsa_evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(record, f, indent=2, sort_keys=True)
    print(f"EVIDENCE_WRITTEN {evidence_path}")
    print(json.dumps({k: record[k] for k in ("evidence_level", "backend", "real_liboqs", "verified")}, sort_keys=True))
    print("ALL ML-DSA EVIDENCE HARNESS TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
