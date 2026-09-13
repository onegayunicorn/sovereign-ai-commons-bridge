# Claims and Evidence Boundaries — KYREXIS / PHOTONIC-Ω v4.7

This document prevents over-claiming. Software verification is not physical validation.

## Evidence levels

| Level | Meaning |
|-------|--------|
| L0 | Spec / design only |
| L1 | Software simulation or unit test |
| L2 | Integration test in controlled environment |
| L3 | Software verified on target runtime (e.g. Termux) |
| L4 | Hardware-backed (sensor, NFC UID, biometric TEE) |

## Current claims

| Claim | Evidence level | Notes |
|-------|----------------|-------|
| Merkle audit integrity | L1 | Unit-tested SHA3-256 tree; deterministic |
| 43-agent **registry** | L1 | Static registry surface — not 43 live processes |
| ML-DSA-65 interface | L1 | Dual backend (`simulation` / `real` / `auto`); sim is default; real requires liboqs + ML-DSA-65 |
| NFC physical anchoring | L0–L1 | Protocol implemented in software; no tag hardware proven here |
| Biometric auth | L0–L1 | Simulated; hardware KeyStore not proven in this repo |
| Photonic / AMOLED loop | L0 | Design / external to this verification core |
| Fold FE-OGUF-P1 | L1 | Logical anchor ID in software state |
| Coherence 0.99997 | L1 | Simulation metric, not physical QPU |

## Explicit non-claims

- `simulation_is_cryptographic_evidence: false` for ML-DSA simulation backend
- Real liboqs ML-DSA-65 (when available) is L1 software cryptographic evidence only — not L4 hardware
- `physical_validation: false` for NFC, biometric, photonic
- Registry entries are **not** asserted as concurrent autonomous runtimes
- GitHub remote may be absent until created under `onegayunicorn/sovereign-ai-commons-bridge`

## Promotion rules

To raise a claim’s evidence level, attach:

1. Reproducible test or measurement
2. Environment identity (device model, OS, library versions)
3. Artifact hash (Merkle leaf or release attestation)
