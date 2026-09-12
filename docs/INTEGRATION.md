# KYREXIS Integration Guide — SACB v4.7

## Install / run

```bash
# Clone
git clone https://github.com/onegayunicorn/sovereign-ai-commons-bridge.git
cd sovereign-ai-commons-bridge

# No external Python deps required for the verification core
python tests/test_core.py
python agents/full_43_agents.py
bash scripts/github_commit.sh
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

```python
from crypto.ml_dsa65 import MLDSA65

m = MLDSA65()
print(m.status())           # runtime=simulation, ready=True
sig = m.sign_merkle_root("abc123", fold="FE-OGUF-P1")
# algorithm=ML-DSA-65-sim, real_liboqs=False, verified=True
```

Until real liboqs is linked, treat signatures as **simulation only**. Do not promote to cryptographic evidence.

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

## liboqs path (future)

1. Install/build liboqs with ML-DSA-65 support.
2. Replace simulation body in `crypto/ml_dsa65.py` (or add a real backend behind a flag).
3. Ensure `status()` and `sign_merkle_root()` report `real_liboqs=True`.
4. Add integration tests and promote claim level per `docs/CLAIMS_AND_EVIDENCE.md`.

---

## Capacitor / NFC / Android notes

- `android/` directory is scaffolding only.
- No Capacitator config, no NFC plugin, no KeyStore integration is present in this verification core.
- Future work may add Termux or Capacitor hooks for Samsung A17; any such claim must be promoted with L3/L4 evidence.

---

## Troubleshooting

| Symptom | Check |
|---------|-------|
| `ModuleNotFoundError: crypto` | Run from repo root or ensure `sys.path` includes parent |
| Tests fail on merkle | Confirm pure Python 3; no external hash libs needed |
| `real_liboqs` unexpectedly true | Inspect `ml_dsa65.py` — simulation is the default |
| Manifest missing | Run `bash scripts/github_commit.sh` |
| CI red | Actions → re-run; confirm Python 3.12 and test path |

---

## Related docs

- `docs/PROJECT.md` — full architecture and layout
- `docs/CLAIMS_AND_EVIDENCE.md` — evidence levels and non-claims
- `README.md` — quick start
