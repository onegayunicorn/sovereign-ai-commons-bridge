#!/usr/bin/env python3
"""Report whether the real liboqs ML-DSA-65 backend is available.

Exit status:
  0  ML-DSA-65 is available, or a non-strict probe completed.
  1  --require-real was supplied and the real backend is unavailable.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from typing import Any, Dict

ALGORITHM = "ML-DSA-65"


def inspect_backend() -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "algorithm": ALGORITHM,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "available": False,
        "real_liboqs": False,
    }
    try:
        import oqs  # type: ignore
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result

    result["oqs_version"] = oqs.oqs_version()
    result["oqs_python_version"] = oqs.oqs_python_version()
    result["enabled_signature_mechanisms"] = sorted(
        oqs.get_enabled_sig_mechanisms()
    )
    result["available"] = ALGORITHM in result["enabled_signature_mechanisms"]
    result["real_liboqs"] = result["available"]
    if not result["available"]:
        result["error"] = (
            f"{ALGORITHM} is not enabled by the installed liboqs build"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check for a real liboqs ML-DSA-65 backend"
    )
    parser.add_argument(
        "--require-real",
        action="store_true",
        help="exit 1 unless liboqs and ML-DSA-65 are available",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit one machine-readable JSON object",
    )
    args = parser.parse_args()

    result = inspect_backend()
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"algorithm: {result['algorithm']}")
        print(f"available: {result['available']}")
        print(f"real_liboqs: {result['real_liboqs']}")
        for key in (
            "oqs_version",
            "oqs_python_version",
            "enabled_signature_mechanisms",
            "error",
        ):
            if key in result:
                print(f"{key}: {result[key]}")

    if args.require_real and not result["available"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
