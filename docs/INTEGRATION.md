# KYREXIS Integration Guide — SACB v4.7

## Install / run

```bash
# Clone
git clone https://github.com/onegayunicorn/sovereign-ai-commons-bridge.git
cd sovereign-ai-commons-bridge

# No external Python deps required for the verification core (simulation path)
python tests/test_core.py
python agents/full_43_agents.py
bash scripts/github_commit.sh
python scripts/check_mldsa_backend.py
```

Python ≥ 3.10 recommended (CI uses 3.12).

---

## Module APIs

### Merkle audit (`crypto.merkle_audit`)

```python
from crypto.merkle_audit import MerkleTree

t = MerkleTree()
t.log_event("TEST", "a17", {"ok": True})
result = t.verify_integrity()
# {"valid": True, "leaf_count": N, "root": "...", "errors": []}
```

- `append(leaf)` / `log_event(event_type, actor, payload)`
- `verify_integrity()` — chain + root check
- Root is SHA3-256 of the binary tree over leaf hashes

### ML-DSA-65 interface (`crypto.ml_dsa65`)

Dual backend: **simulation** (default, portable) and **real** (liboqs).

```python
from crypto.ml_dsa65 import MLDSA65

# Default: simulation
with MLDSA65(backend="simulation") as m:
    print(m.status())
    # runtime=simulation, mechanism=ML-DSA-65-sim, real_liboqs=False
    sig = m.sign_merkle_root("abc123", fold="FE-OGUF-P1")
```

| Backend | Behavior |
|---------|----------|
| `simulation` | SHA3-based simulator; always available; `real_liboqs=false` |
| `real` | Requires `liboqs` + enabled `ML-DSA-65`; **fails closed** otherwise |
| `auto` | Uses liboqs when available, otherwise simulation (reports mode accurately) |

```bash
# Capability probe
python scripts/check_mldsa_backend.py
python scripts/check_mldsa_backend.py --json
python scripts/check_mldsa_backend.py --require-real   # exit 1 if real unavailable
```

Until a real liboqs build with ML-DSA-65 is present, treat signatures as **simulation only**. Do not promote simulation results to cryptographic evidence.

### Agent registry (`agents.full_43_agents`)

```python
from agents.full_43_agents import total, AGENTS
assert total() == 43
# AGENTS keys: quantum, orchestration, execution, security, monitoring, specialized, junction
```

Running the module writes/updates `registry/agents_43.json`.

### Merkle seal (`scripts/github_commit.sh`)

Walks tracked source extensions (`.py`, `.md`, `.json`, …), sorts SHA3-256 of file contents, derives root, writes:

```json
{
  "merkle_root": "<64-hex>",
  "fold_entry": "FE-OGUF-P1",
  "coherence": 0.99997,
  "agents": 43,
  "files": N,
  "ts": <unix>
}
```

to `audit/manifest.json`.

---

## Real liboqs path

1. Install native prerequisites and `liboqs-python` (see pinned `requirements-real.txt` when present).
2. Confirm capability:
   ```bash
   python scripts/check_mldsa_backend.py --require-real
   ```
3. Use `MLDSA65(backend="real")`. `status()` and `sign_merkle_root()` report `real_liboqs=True` and OQS versions.
4. Add real round-trip / tamper tests and promote only the ML-DSA software claim per `docs/CLAIMS_AND_EVIDENCE.md`.

Real liboqs execution is **L1 software cryptographic evidence**. It does not establish hardware-backed signing, NFC, biometric TEE, or photonic validation.

---

## Capacitor / NFC / Android notes

- `android/` directory is scaffolding only.
- No Capacitor config, no NFC plugin, no KeyStore integration is present in this verification core.
- Future work may add Termux or Capacitor hooks for Samsung A17; any such claim must be promoted with L3/L4 evidence.

---

## Troubleshooting

| Symptom | Check |
|---------|-------|
| `ModuleNotFoundError: crypto` | Run from repo root or ensure `sys.path` includes parent |
| Tests fail on merkle | Confirm pure Python 3; no external hash libs needed |
| `real_liboqs` unexpectedly true | Inspect `ml_dsa65.py` — simulation is the default |
| `backend="real"` raises | `oqs` missing or ML-DSA-65 not enabled — expected fail-closed |
| Manifest missing | Run `bash scripts/github_commit.sh` |
| CI red | Actions → re-run; confirm Python 3.12 and test path |

---

## Related docs

- `docs/PROJECT.md` — full architecture and layout
- `docs/CLAIMS_AND_EVIDENCE.md` — evidence levels and non-claims
- `README.md` — quick start
