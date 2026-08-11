# THE FORGE — Start Here

**One place. One truth. No drift.**

This is a local-first, zero-trust AI fabric. Raw models are treated as untrusted binaries. Everything passes through the Gate. The Overseer watches. The Commander only acts through the one door.

If you are a human or a model entering this repository, read this file completely before touching anything else.

---

## What this is

An AI-native operating fabric that runs on one workstation (Intel NPU + NVIDIA RTX + high RAM). Models never run bare. They are wrapped, sealed, gated, and overseen. The system can splice, recycle, and re-form model substance under strict local control.

## Canonical layout

```
the-forge/
├── START_HERE.md          ← you are here
├── README.md              ← short overview
├── forge/                 ← THE LIVING FABRIC (code that runs on the PC)
│   ├── fabric/            ← organs (gate, overseer, kernel, tailor, …)
│   ├── bridge/            ← thin FastAPI surface the App talks to
│   ├── bind/              ← model-binding scripts (NPU / Ollama)
│   └── concept_map/       ← idea tree
├── contract/              ← how the App talks to the Forge
├── docs/                  ← status, whitesheet, handover
└── app/                   ← thin glass UI (no logic, no secrets)
```

Supporting repos (do not treat as spine):
- `forge-copilot` — model protocol, handoff, node-logs
- `forge-os-core` — lock / status snapshots

## Rules that never change

1. **The Gate is the one door.** Nothing acts without it.
2. **Models never run bare.** Wrap → seal → gate.
3. **Watcher observes. Commander acts.** They stay separate.
4. **Nothing is thrown away.** Archive, do not delete.
5. **Secrets stay client-side / env.** Never the source of truth in a DB.
6. **Base44 is glass only.** It is not the spine.

## How any model must enter

1. Read this file.
2. Read `docs/FORGE_MASTER_WHITESHEET.md` and the current STATUS (in `forge-os-core` or local).
3. Absorb the protocol in `forge-copilot/protocol/` (PRE_PROMPT + MASTER_PROMPT).
4. Every substantive output uses the **AI NODE COMMIT LOG** format.
5. Prefer small, verifiable patches over rewrites.
6. After code changes: run the baseline tests and append a node-log entry.

## Boot the fabric (PC)

```bash
cd forge
python -m pytest forge/fabric -q   # keep the baseline green
python -m bridge.server            # http://127.0.0.1:8787/health must show booted: true
```

Bridge now boots via `boot_forge()` (secret is supplied). Do not call `ForgeKernel()` bare.

## Current next bricks (ordered)

1. Prove `/health` → `booted: true` on the live machine.
2. Unify any remaining old Finding constructors to the live `types.Finding` shape.
3. Bind real models (NPU brain + RTX capsules).
4. Keep the glass App thin.

---

This repository is the source of truth for the fabric. Treat it that way.
