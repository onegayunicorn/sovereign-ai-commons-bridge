#!/usr/bin/env python3
"""Generate Boundary Seal v1 for SACB cryptographic claims.

Produces audit/boundary_seal.json documenting evidence levels and non-claims.
Does not claim hardware or independent third-party validation.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto.ml_dsa65 import MLDSA65


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    with MLDSA65(backend="auto") as m:
        status = m.status()

    # Probe capability without requiring real
    try:
        from scripts.check_mldsa_backend import inspect_backend
        probe = inspect_backend()
    except Exception:
        probe = {"available": False, "real_liboqs": False, "error": "probe_failed"}

    seal = {
        "boundary_seal_version": "v1",
        "project": "sovereign-ai-commons-bridge",
        "fold_entry": "FE-OGUF-P1",
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "backends": {
            "simulation": {
                "available": True,
                "evidence_level": "L1",
                "cryptographic_evidence": False,
            },
            "real_liboqs": {
                "available": bool(probe.get("available")),
                "evidence_level": "L1" if probe.get("available") else None,
                "cryptographic_evidence": bool(probe.get("available")),
                "note": "L1 software only when available; never L4 hardware",
            },
        },
        "active_status": status,
        "claims": {
            "merkle_audit": {"level": "L1", "notes": "SHA3-256 tree integrity"},
            "agent_registry_43": {"level": "L1", "notes": "static surface only"},
            "mldsa65_interface": {
                "level": "L1",
                "backend": status.get("backend"),
                "real_liboqs": status.get("real_liboqs"),
            },
        },
        "non_claims": [
            "simulation_is_cryptographic_evidence: false",
            "hardware_backed_signing: false",
            "nfc_physical_anchoring: false",
            "biometric_tee: false",
            "photonic_amoled_loop: false",
            "independent_third_party_reproduction: false",
            "43_concurrent_live_processes: false",
        ],
        "promotion_requires": [
            "reproducible_test_or_measurement",
            "environment_identity",
            "artifact_hash",
        ],
    }

    # Content hash of seal body (excluding this field)
    body = json.dumps(seal, sort_keys=True, separators=(",", ":")).encode()
    seal["seal_sha3_256"] = hashlib.sha3_256(body).hexdigest()

    out = os.path.join("audit", "boundary_seal.json")
    os.makedirs("audit", exist_ok=True)
    with open(out, "w") as f:
        json.dump(seal, f, indent=2, sort_keys=True)

    print("BOUNDARY_SEAL", out)
    print("seal_sha3_256", seal["seal_sha3_256"])
    print("real_liboqs_available", seal["backends"]["real_liboqs"]["available"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
