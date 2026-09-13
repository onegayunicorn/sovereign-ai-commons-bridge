#!/usr/bin/env python3
"""ML-DSA-65 interface with explicit simulation and liboqs backends.

The simulation backend is retained for portable interface tests. It is never
reported as real cryptographic evidence. The real backend requires the
liboqs-python ``oqs`` module and an enabled ``ML-DSA-65`` mechanism.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, Optional

ALGORITHM = "ML-DSA-65"
SIMULATION_ALGORITHM = "ML-DSA-65-sim"
SUPPORTED_BACKENDS = ("simulation", "real", "auto")


class MLDSA65:
    """Sign and verify messages using simulation or real liboqs ML-DSA-65.

    ``backend="simulation"`` preserves the repository's portable test mode.
    ``backend="real"`` requires liboqs-python and fails closed if ML-DSA-65
    is unavailable. ``backend="auto"`` selects liboqs when available and
    otherwise uses simulation; callers that require cryptographic evidence
    should use ``backend="real"`` instead.

    In real mode, generated key material remains in the underlying oqs
    Signature object. A restored secret key must be accompanied by its public
    key because liboqs does not derive the public key through this wrapper.
    """

    def __init__(
        self,
        backend: str = "simulation",
        secret_key: Optional[bytes] = None,
        public_key: Optional[bytes] = None,
    ) -> None:
        if backend not in SUPPORTED_BACKENDS:
            raise ValueError(
                f"backend must be one of {SUPPORTED_BACKENDS}, got {backend!r}"
            )

        self._oqs = None
        self._signer = None
        self._secret_key = secret_key
        self._public_key = public_key

        if backend in ("real", "auto"):
            try:
                import oqs  # type: ignore

                mechanisms = oqs.get_enabled_sig_mechanisms()
                if ALGORITHM not in mechanisms:
                    raise RuntimeError(
                        f"{ALGORITHM} is not enabled by the installed liboqs "
                        f"build; enabled signature mechanisms do not include it"
                    )
                self._oqs = oqs
            except Exception:
                if backend == "real":
                    raise
                # auto mode is deliberately the only mode permitted to fall
                # back; status() continues to identify this as simulation.
                self._oqs = None

        if self._oqs is not None:
            self.backend = "real"
            self.mech = ALGORITHM
            self._signer = self._oqs.Signature(ALGORITHM, secret_key)
            if secret_key is None:
                self._public_key = self._signer.generate_keypair()
            elif public_key is None:
                raise ValueError(
                    "public_key is required when restoring a real ML-DSA-65 "
                    "secret key"
                )
        else:
            self.backend = "simulation"
            self.mech = SIMULATION_ALGORITHM
            seed = os.urandom(32)
            self._sk = hashlib.sha3_512(seed + b"sk").digest()
            self._pk = hashlib.sha3_512(seed + b"pk").digest()
            self._public_key = self._pk

    @property
    def public_key(self) -> Optional[bytes]:
        """Return the public key for verification or persistence."""
        return self._public_key

    def sign(self, message: bytes) -> bytes:
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        if self.backend == "real":
            return self._signer.sign(message)

        h = hashlib.sha3_512(self._sk + message).digest()
        sig = h
        while len(sig) < 256:
            sig += hashlib.sha3_256(sig).digest()
        return sig[:256]

    def verify(
        self,
        message: bytes,
        signature: bytes,
        public_key: Optional[bytes] = None,
    ) -> bool:
        if not isinstance(message, bytes) or not isinstance(signature, bytes):
            raise TypeError("message and signature must be bytes")
        key = public_key or self._public_key
        if self.backend == "real":
            if key is None:
                raise ValueError("a public key is required for real verification")
            with self._oqs.Signature(ALGORITHM) as verifier:
                return bool(verifier.verify(message, signature, key))

        # The simulator is intentionally marked as non-cryptographic. Its
        # behavior is retained only for interface compatibility tests.
        return hashlib.sha3_256(signature).digest() == hashlib.sha3_256(
            self.sign(message)
        ).digest()

    def sign_merkle_root(
        self, merkle_root: str, fold: str = "FE-OGUF-P1"
    ) -> Dict[str, Any]:
        if not isinstance(merkle_root, str) or not merkle_root:
            raise ValueError("merkle_root must be a non-empty string")
        message = (
            f"SACB-MLDSA65-v1\n"
            f"algorithm={ALGORITHM}\n"
            f"merkle_root={merkle_root}\n"
            f"fold={fold}\n"
        ).encode("utf-8")
        signature = self.sign(message)
        result: Dict[str, Any] = {
            "algorithm": self.mech,
            "backend": self.backend,
            "real_liboqs": self.backend == "real",
            "verified": self.verify(message, signature),
            "fold": fold,
            "public_key_sha3_256": hashlib.sha3_256(self._public_key).hexdigest()
            if self._public_key is not None
            else None,
            "signature_sha3_256": hashlib.sha3_256(signature).hexdigest(),
        }
        if self.backend == "real":
            result["oqs_version"] = self._oqs.oqs_version()
            result["oqs_python_version"] = self._oqs.oqs_python_version()
        return result

    def status(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "runtime": "liboqs" if self.backend == "real" else "simulation",
            "mechanism": self.mech,
            "backend": self.backend,
            "real_liboqs": self.backend == "real",
            "ready": True,
        }
        if self.backend == "real":
            result["oqs_version"] = self._oqs.oqs_version()
            result["oqs_python_version"] = self._oqs.oqs_python_version()
        return result

    def close(self) -> None:
        """Release the native signer when the binding exposes close()."""
        if self._signer is not None:
            close = getattr(self._signer, "close", None)
            if close is not None:
                close()
            self._signer = None

    def __enter__(self) -> "MLDSA65":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Check ML-DSA-65 backend")
    parser.add_argument(
        "--backend", choices=SUPPORTED_BACKENDS, default="simulation"
    )
    args = parser.parse_args()
    with MLDSA65(backend=args.backend) as m:
        print(json.dumps(m.status(), sort_keys=True))
        print(json.dumps(m.sign_merkle_root("testroot"), sort_keys=True))
