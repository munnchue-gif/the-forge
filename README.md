# THE FORGE

Local-first, zero-trust AI fabric. Raw models are treated as hostile. Everything passes the Gate.

> **Start here:** [`START_HERE.md`](START_HERE.md)

## What it does

Runs on one workstation (NPU + RTX + high RAM). Models are wrapped, sealed, and gated. An Overseer watches. A Commander only acts through the single door. The fabric can splice, recycle, and re-form model substance under strict local control.

## Quick map

| Path | Role |
|------|------|
| `forge/fabric/` | Living organs (gate, overseer, kernel, tailor, conduit, sandbox, …) |
| `forge/bridge/` | Thin FastAPI surface — the only thing the App talks to |
| `forge/bind/` | Model binding scripts (OpenVINO NPU, Ollama RTX) |
| `contract/` | App ↔ Forge contract |
| `docs/` | Whitesheet, status, handover |

## Run

```bash
cd forge
python -m pytest forge/fabric -q
python -m bridge.server          # http://127.0.0.1:8787
```

`/health` must return `booted: true`.

## Hard rules

- Gate is the one door
- Models never run bare
- Watcher observes · Commander acts
- Nothing thrown away (archive)
- Secrets stay client-side / env
- Base44 is glass only — not the spine

## Model protocol

Any model working on this codebase must follow the protocol in the companion repo `forge-copilot` (PRE_PROMPT + MASTER_PROMPT + AI NODE COMMIT LOG). Read `START_HERE.md` first.

## Status

Canonical status lives with the lock docs. Keep the baseline tests green. Prefer small verifiable patches.
