# THE FORGE

A local-first, security-hardened, **AI-native operating system** built on a zero-trust
model where raw AI models are treated as hostile, untrusted binaries. Runs on one
workstation (Intel NPU + NVIDIA RTX + CPU). The "alien substance" — one material,
reclaimed and re-formed on demand; nothing runs bare, everything passes the one door.

> Full vision + rules: [`docs/FABLE5_HANDOVER.md`](docs/FABLE5_HANDOVER.md).
> One-page status: [`docs/FORGE_MASTER_WHITESHEET.md`](docs/FORGE_MASTER_WHITESHEET.md).

---

## Repo layout

```
the-forge/
├── forge/          ← THE FORGE  (runs on the PC — the local AI fabric)
│   ├── fabric/         14 organs (gate, overseer, tailor, kernel, …) + tests
│   ├── bind/           PC-side model-binding scripts (NPU/OpenVINO, RTX/Ollama)
│   ├── concept_map/    the idea-tree (Obsidian-ready)
│   └── _sync/          the swap file + state exports (Fable5 ↔ Solene)
├── app/            ← THE APP    (built by Fable 5 — the window into the Forge)
│                       thin GUI: live feed + capability controls. NO logic, NO secrets.
├── contract/       ← THE CONTRACT  (how app ↔ forge talk — build against this)
│   └── FORGE_APP_CONTRACT.md
└── docs/           ← handover brief, whitesheet, prompt
```

## Who works where
- **Fable 5** → builds `app/` (the GUI) and may extend `forge/` (with creative license).
- **Solene** → reviews commits, keeps `forge/` tests green, maintains the contract + sync.
- **Eugene** → owns the concept/IP; approves trust-boundary changes.

## Run the Forge (PC)
```bash
cd forge
python -m pytest -q      # expect 119 passing
python __main__.py       # boots the fabric, runs a heartbeat, verifies audit chain
```

## Hard rules
The gate is the ONE door · models never run bare · brain observes, Commander acts ·
keep tests green · append to `LEDGER.md` · **nothing thrown away** (archive, don't delete) ·
silicon: NPU = 1–3B watcher/Whisper/judge (INT4 only), RTX = 7–13B reasoning, iGPU = display.

## Branch flow
`main` always passes tests. Work on branches; open a PR; the diff is the review surface.
