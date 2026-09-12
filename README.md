# sovereign-ai-commons-bridge (SACB)

**KYREXIS SOVEREIGN / PHOTONIC-Ω v4.7 — verification core**

Samsung A17 target · Fold ID `FE-OGUF-P1` · Coherence metric `0.99997` (simulation)

## What this repo is

- Merkle audit (SHA3-256) with integrity checks
- ML-DSA-65 **interface** with explicit simulation fallback (`real_liboqs=false` until liboqs is present)
- **43-agent registry surface** (not a claim of 43 concurrent live processes)
- Integration and claims/evidence documentation

## What this repo is not (yet)

- Hardware-proven NFC / biometric / photonic validation
- Production ML-DSA-65 without liboqs
- A substitute for physical chain-of-custody

## Quick verify

```bash
python tests/test_core.py
python agents/full_43_agents.py
bash scripts/github_commit.sh
```

## Documentation

| Document | Purpose |
|----------|--------|
| [docs/PROJECT.md](docs/PROJECT.md) | Full project docs — layout, architecture, crypto, agents, CI, deployment |
| [docs/INTEGRATION.md](docs/INTEGRATION.md) | Install, module APIs, Merkle seal, liboqs path, troubleshooting |
| [docs/CLAIMS_AND_EVIDENCE.md](docs/CLAIMS_AND_EVIDENCE.md) | L0–L4 levels, claim table, explicit non-claims, promotion rules |

## GitHub

```bash
git remote add origin https://github.com/onegayunicorn/sovereign-ai-commons-bridge.git
git push -u origin main
```

Evidence boundaries remain explicit: Merkle/registry **L1**; ML-DSA **simulation** until liboqs; no claim of 43 live processes or hardware NFC/biometric proof in this core.
