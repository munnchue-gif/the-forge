# WHAT IS ON THE PC — 2026-08-17

Where everything lives, what state it is in, and what is safe to delete.

---

# 1 · THE THREE THINGS THAT MATTER

Everything else is copies, archaeology, or scratch.

```
~/the-forge/                 ← THE LIVE SPINE. Only living code.
                                189 files · 9 failed / 125 passed
                                origin/master = github.com/munnchue-gif/the-forge
                                Last commits: hub.py, capsule.py, kernel factory fix,
                                              FORGE_STATE.md

~/FORGE_CABINET/             ← THE HARVEST. Everything else, graded.
                                ~1,700 files in 06_ARCHIVE_RAW
                                This is what makes deleting safe.

~/newapps/arch/              ← THE NEW DESIGN. The clean-slate architecture app.
                                src/data/frontiers.ts (24KB) = the seven answers
                                6 corrections pending (handoff §7a)
```

---

# 2 · THE LIVE SPINE — `~/the-forge/`

```
~/the-forge/
├── FORGE_STATE.md              ← the contract. Read first, write last.
├── .venv/                      ← activate before ANY python command
├── forge/
│   ├── fabric/                 ← the locked core
│   │   ├── gate.py             🟢 10 tests · nonce + delimiter escape shipped
│   │   ├── capabilities.py     🟢 7 verbs · Spawn Mount Egress NpuEval
│   │   │                          Conform Splice Reclaim
│   │   ├── overseer.py         🟢 268L · Watcher + Commander + JudgeSeat
│   │   ├── wrap.py             🟢 6 tests · THIS IS THE WARDROBE
│   │   ├── sandbox.py          🟢 9 tests · THIS IS THE CONCOCTINATOR
│   │   ├── tailor.py           🟢 7 tests · built at M4 (the "missing organ")
│   │   ├── judge.py            🟢 8 tests · THIS DEFINES CLEAN
│   │   ├── ledger.py           🟡 8 tests · hash-chained · pruning undefined
│   │   ├── conduit.py          🟡 HeuristicSeat only · real NPU seat pending
│   │   ├── bus.py              🟡 95L · WEAK — two reviewers flagged it
│   │   ├── kernel.py           🟢 factory table fixed 2026-08-17
│   │   ├── capsule.py          🟢 merged 2026-08-15 from cabinet
│   │   ├── hub.py              🟢 merged 2026-08-15 from cabinet
│   │   └── bind/               🔴 5 stale tests (old Finding shape)
│   │       ├── openvino_seat.py    NPU · OpenVINO GenAI
│   │       └── ollama_capsule.py   RTX · Ollama
│   └── bridge/server.py        🟢 /mint /feed /ledger /health
└── docs/

MISSING (not built): hopper · keychain · toolchain · boneyard
                     copilot · surface · splice.py
```

**Git state:** clean, pushed. Merge commits for `hub`, `capsule`, the kernel
fix, and `FORGE_STATE.md` are all on `origin/master`.

---

# 3 · THE CABINET — `~/FORGE_CABINET/`

```
00_MANIFEST/     scan.jsonl · graded.jsonl · grades.csv
                 concepts.csv ← the concept ledger
01_GOLD/ 02_SILVER/ 03_BRONZE/ 04_DUPLICATE/ 05_QUARANTINE/
06_ARCHIVE_RAW/  ~1,700 verbatim copies  ← THE PERMISSION SLIP FOR DELETING
_WORK/sorter/    forgelib scan grade compare port tune grid xdoc
                 (8 tools import forgelib — never rewrite it)
```

**Harvest totals across all scans:** ~1,900 files, 25 GOLD, 14 SILVER,
491 DUP — **two thirds of everything scanned was a byte-identical copy.**

**Concept ledger:** Forge 50 · Fabric 33 · Gate 30 · Kernel 22 · Capability 21 ·
Bind 19 · Overseer 18 · Organ 10 — and thin at Finding 3, Drift 2, Spine 1.

---

# 4 · THE ELEVEN REPOS

| Path | Verdict |
|---|---|
| `~/the-forge` | ✅ **THE SPINE** |
| `~/forge-spine` | ✅ harvested — gave 7 GOLD, 4 merged. **deletable** |
| `~/forge-workspace/the-forge` | 🔁 GOLD:11 — one of five identical copies |
| `~/ALLFORGE/the-forge` | 🔁 same GOLD:11 |
| `~/ALLFORGE/the-forge-repo/the-forge` | 🔁 same GOLD:11 |
| `~/Videos/the-forge-repo/the-forge` | 🔁 same GOLD:11 |
| `~/forge-os/the-forge` | 🔁 same GOLD:11 |
| `~/forge-os-locked-pc` | 🔁 GOLD:10, DUP:159 |
| `~/Forge` | ⚠️ **the `backend/` lineage** — hopper, peer_review, Registry/Gold_C44 |
| `~/core_Forge-unziped` | 📄 mostly docs |
| `~/forge-workspace/the-forge-ui` | 🎨 React — belongs in `the-forge-ui` |
| `~/forge-workspace/git-concoctinating` | 🎨 Base44 command board |
| `~/forge-os/llama.cpp` | 🚫 third-party, not yours |

**Five of these reported identical `GOLD: 11`.** They are five copies of one
repo. That is the sprawl, quantified.

---

# 5 · THE UNMERGED GOLD

Graded, archived, waiting.

| Piece | Where | Verdict |
|---|---|---|
| `gate.py` PathwayRegistry | forge-spine | **+25 symbols, 0 spine-only** — port it, keep the prose |
| `bus.py` variant | `~/Forge/backend/kernel/` | 383L vs your 95L, +21 symbols — DLQ, two-phase teardown, SubKernelBus |
| `FabricSandbox` | `ForgeOS-Arch-Rev` | bwrap `--unshare-all` + systemd-run — **real isolation, no Docker** |
| `splicing_engine.py` | `ForgeOS-Arch-Rev` | 261L · intent-recorded-then-audited · strong idea, flawed code |
| `socket_coupler.py` | `ForgeOS-Arch-Rev` | 483L · unreviewed · #1 attack surface |
| `security_guardian.py` | `ForgeOS-Arch-Rev` | 485L, 7 classes · unreviewed |
| `subkernel.py` | `~/Forge/backend/kernel/` | 385L · SWARM_EOF sentinel teardown |
| `test_judge.py` | forge-spine | 74L vs your 24L, +6 symbols |

---

# 6 · NOT YET SCANNED

```
~/Downloads/ForgeOS-Arch-Rev/     ← 959 files, 24 GOLD, 44 SILVER
                                     the single biggest find
~/Music/optimizing-local-llm-development-workflow/
~/clean_up-arena_files/Forge_socket_arena/     ← "Arena" — possibly the voting layer
~/Music/clean_up-arena_files/Forge_socket_arena/
~/newapps/arch/  and  ~/newapps/layout/        ← the new design apps
```

`Forge_socket_arena` appears in **four** locations and has never been examined.
Given you described an Arena for model voting, worth a look.

---

# 7 · THE RUNTIME

```
Ollama      gpt-oss:20b · 12 GB · 100% GPU · CONTEXT 16384 ✅
            systemd override at /etc/systemd/system/ollama.service.d/
NPU         OpenVINO GenAI · CPU/GPU/NPU all enumerate ✅
Editor      VS Code + Remote-SSH  (use Continue.dev, NOT Cursor —
            Cursor routes through its cloud, needs a public tunnel)
Venv        ~/the-forge/.venv — activate before any python command
```

---

# 8 · THE DOCS FROM THIS SESSION

In `~/forge_sorter/` on the workspace — **not yet on your PC:**

```
FORGE_HANDOFF.md          ★ paste into any new chat — self-contained
THE_FORGE_MASTER_LAYOUT.md  the full system, locked vocabulary
FRONTIERS_REVIEW.md         the 6 corrections
THESIS_EVOLUTION_AND_PROMPTS.md   seven shifts + prompts
CLEAN_BUILD_PROMPT.md       the from-scratch prompt
LAYOUT_REVIEW.md            why the SubKernelBus cut was wrong
M4_SCORECARD.md             7 of 10 M4 findings closed
THE_ACTUAL_DESIGN.md · LAYERS_AND_PORTABILITY.md · HOPPER_AND_TWINS.md
FORGE_CONCEPT_MAP.md · CODER_BRIEFS.md · GOLD_HUNT_PROMPT.md
PC_MAP.md                   this file
```

**Get them onto the PC and into git** — that is the one gap that matters:

```bash
mkdir -p ~/the-forge/docs/session-2026-08
# paste each from the viewer, then:
cd ~/the-forge && git add docs/ && git commit -m "docs: session artifacts" && git push
```

---

# 9 · WHERE YOU ACTUALLY ARE

**Done this session:**
- ✅ 4 modules recovered, 2 merged and pushed (`hub.py`, `capsule.py`)
- ✅ kernel factory table fixed — **`/mint` was broken for 5 of 7 verbs in production**
- ✅ sandbox severity fix recovered from a forgotten stash
- ✅ baseline **11 → 9 failed**
- ✅ 44 unreadable Office docs extracted and graded
- ✅ ~1,900 files harvested, 1,700 archived
- ✅ `FORGE_STATE.md` written, committed, pushed
- ✅ vocabulary locked · 4 hoppers resolved into distinct organs
- ✅ 7 of 10 M4 findings confirmed closed
- ✅ clean-slate design produced with all 7 frontier answers

**Next, in order:**
1. Apply the 6 corrections to `frontiers.ts` (mechanical, ~10 min, no model needed)
2. Get session docs into `~/the-forge/docs/` and push
3. Scan `~/Downloads/ForgeOS-Arch-Rev/` properly — 959 files, biggest unharvested find
4. Then build #1 (capsule spec) or #2 (hopper)

**Do not delete anything yet.** After the merges land, the five duplicate repos
collapse to zero loss — `06_ARCHIVE_RAW` already holds them.
