# FORGE_STATE.md — handoff contract

Read this FIRST. Update it LAST. Generated 2026-08-17 from cabinet harvest.

## 1. LOCKED DECISIONS

| Date | Decision | Reason |
|---|---|---|
| 2026-08 | authorize() is SYNC, never async | Must not stall the event loop |
| 2026-08 | Canonical root is forge/fabric/ | Supersedes forge/<organ>/, backend/kernel/, forge_ng/fabric/ |
| 2026-08 | Models SHA-256 wrapped on entry | No raw model runs. The wrap IS the training |
| 2026-08 | Deaf-by-default, no wildcard subscribe | Overseer holds the only tap |
| 2026-08 | Couplers built LAST | #1 hacker surface |
| 2026-08 | NPU = OpenVINO GenAI only | ipex-llm Windows-only; npu-accel-lib deprecated |
| 2026-08 | Do NOT distro-hop | RTX 5080 issues are distro-agnostic (Kimi review) |
| 2026-08 | seL4 = future substrate, not a task | No Linux userland = no Ollama/CUDA/OpenVINO |
| 2026-08 | Capsule became fabric | Spawning sandbox wrapper, no kernel authority |

## 2. VOCABULARY (Rosetta stone - all BUILT, stop re-deriving)

| Spoken | Canonical | Evidence |
|---|---|---|
| wardrobe | WrapStore | "the recycling yard", 6 tests |
| baptism | wrap-conform | "Wrap-conform IS the baptism" |
| flatten | Reclaim capability | "Recycle, don't delete" |
| commander | acting half of Overseer | Commander class in overseer.py |
| conduit | VectorConduit | observes+proposes, cannot execute |
| suit | Wrap / the Substance | |
| missing organ | EmbeddedTailor | BUILT at M4, tailor.py, 7 tests |

Safety property (original wording): "the thing that watches cannot act, and
the thing that acts cannot watch on its own - it acts only on the watcher's
findings, and only through the gate."

## 3. ORGAN STATUS  (187 files, baseline 11 failed / 123 passed)

| Organ | File | Status | Note |
|---|---|---|---|
| Gate | forge/fabric/gate.py | GREEN | +25 symbols pending from cabinet |
| Overseer | forge/fabric/overseer.py | GREEN | 268L, 26 symbols |
| EmbeddedTailor | forge/fabric/tailor.py | GREEN | built M4; filename label stale |
| Capsule | forge/fabric/capsule.py | GREEN | merged 2026-08-15 |
| Hub | forge/fabric/hub.py | GREEN | merged 2026-08-15 |
| Kernel | forge/fabric/kernel.py | GREEN | factory table fixed 2026-08-17 |
| Ledger | forge/fabric/ledger.py | YELLOW | DIVERGED +20 cand / +6 spine |
| VectorConduit | forge/fabric/conduit.py | YELLOW | HeuristicSeat live |
| Bind | forge/fabric/bind/ | RED | 5 stale tests, see 5 |
| Couplers | - | YELLOW | LOCKED: build last |
| Keychain | - | NOT BUILT | design only |
| Hopper | - | NOT BUILT | note in 03_BRONZE/prompts/ |

## 4. CANONICAL SHAPES

Regenerate before trusting:
  grep -rn "class Finding\|class LedgerEntry\|class Wrap" forge/fabric/

From runtime: Finding(id, organ, severity, title, detail, timestamp, metadata)
severity is a STRING enum, never an int.
Capabilities: Spawn, Mount, Egress, NpuEval, Conform, Splice, Reclaim

## 5. KNOWN BROKEN

BASELINE: 9 failed, 125 passed. Any other number = you caused it.

1. forge/fabric/kernel.py:80-82 - factory table passes kwargs the dataclasses
   reject. EgressCapability(destination=...) and NpuEvalCapability(input_sha=...)
   raise TypeError BEFORE reaching the gate. Fix the lambdas against real
   signatures. Do NOT strip kwargs - that sends under-specified capabilities
   to the Gate.
2. forge/fabric/bind/test_bind.py - 5 tests pinned to old Finding shape.
   Stale tests, not broken code. judge() also lost an argument.
3. test_sequence.py - 1 test rolls back where it should complete.

## 6. DO NOT REBUILD

- Overseer/Watcher/Commander : forge/fabric/overseer.py (268L, complete)
- EmbeddedTailor : forge/fabric/tailor.py (M4, 7 tests)
- WrapStore (wardrobe) : forge/fabric/wrap.py (6 tests)
- BehavioralJudge : forge/fabric/judge.py (8 tests) = "define clean behaviorally"
- AuditLedger : forge/fabric/ledger.py (hash-chained, 8 tests)
- Cabinet sorter : ~/FORGE_CABINET/_WORK/sorter/ - 8 tools import forgelib.
  NEVER rewrite forgelib/scan/grade. They exist.
- Handoff system : you built it months ago (FORGE STATE SYNC swap file)

## 7. CABINET STATE 2026-08-17

235 files scanned, 44 Office docs extracted to .md sidecars.
Grades: 0 GOLD, 2 SILVER, 58 BRONZE, 175 QUARANTINE.
Concepts: Forge 50, Fabric 33, Gate 30, Kernel 22, Capability 21, Bind 19,
Overseer 18, Organ 10. THIN: Finding 3, Drift 2, Spine 1.
ZERO for: Codex, Hopper, Keychain, seL4.
board_core = React command board, belongs in the-forge-ui NOT the spine.

## 8. OPEN QUESTION (exactly one)

Should Capability.scope be validated against a per-organ schema at grant time,
or remain intentionally opaque to the fabric core?
If validated: fabric must know organ schemas (coupling).
If opaque: validation moves to organs, ledger unauditable without organ code.
Blocks: Ledger pruning pass.

## 9. NEXT THREE ACTIONS

1. Fix kernel.py factory table -> baseline 11 failed becomes 7
2. Port gate PathwayRegistry (+25 symbols, PRESERVE the DESIGN THESIS docstring)
3. Re-sync bind/test_bind.py to current Finding -> 7 becomes 2
