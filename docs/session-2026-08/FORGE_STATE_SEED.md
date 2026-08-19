# FORGE_STATE.md — seed, built from evidence

Generated 2026-08-17 from the cabinet harvest. Every line below is backed by a
file on disk or a command output, not memory. Paste into `~/the-forge/FORGE_STATE.md`,
correct anything you know to be wrong, commit.

---

## § 1 · LOCKED DECISIONS

| Date | Decision | Reason |
|---|---|---|
| 2026-08 | `authorize()` is **SYNC**, never async | Must not stall the event loop. Supersedes the async design in the App manual. |
| 2026-08 | Canonical root is `forge/fabric/` | Supersedes `forge/<organ>/`, `backend/kernel/`, `forge_ng/fabric/` — four lineages confirmed in artifacts. |
| 2026-08 | Models are SHA-256 wrapped on entry | No raw model ever runs. The wrap IS the training. |
| 2026-08 | Deaf-by-default; no wildcard subscribe | Overseer holds the only tap. |
| 2026-08 | Couplers built **LAST** | #1 hacker surface (your own Graded Master List). |
| 2026-08 | NPU path is **OpenVINO GenAI only** | ipex-llm is Windows-only; intel-npu-acceleration-library deprecated. NPU now working. |
| 2026-08 | **Do NOT distro-hop** | Kimi review: RTX 5080 issues are distro-agnostic. Stay Pop!_OS. |
| 2026-08 | **seL4 is a future substrate, not a task** | No Linux userland → no Ollama/CUDA/OpenVINO. Design toward it; build nothing. |
| 2026-08 | Capsule became fabric | The spawning sandbox wrapper that oversees all without holding kernel authority. |

---

## § 2 · VOCABULARY — the Rosetta Stone

Stop re-deriving these. Every one is BUILT.

| Spoken term | Canonical name | Evidence |
|---|---|---|
| wardrobe | **WrapStore** | "the recycling yard", 6/6 tests |
| baptism | **wrap-conform** | "Wrap-conform IS the baptism" |
| flatten / recycle | **Reclaim** capability | "Recycle, don't delete — stripped and re-poured" |
| commander | **acting half of Overseer** | `Commander` class in live `overseer.py` |
| conduit (hears, can't order) | **VectorConduit** | "observes and proposes, cannot execute without the Gate" |
| suit / fabric | **Wrap / the Substance** | |
| splice | **Splice** capability | |
| the missing organ | **EmbeddedTailor** | **BUILT at M4** — `tailor.py`, 7 tests |

**The safety property, in the original words** (`Forge-NG` overseer docstring):
> *"the thing that watches cannot act, and the thing that acts cannot watch on
> its own — it acts only on the watcher's findings, and only through the gate."*

---

## § 3 · ORGAN STATUS

Live tree: **187 files**, baseline **11 failed / 123 passed** (134 tests).

| Organ | File | Status | Note |
|---|---|---|---|
| Gate | `forge/fabric/gate.py` | 🟢 GREEN | 250L. **+25 symbols pending** from cabinet (CANDIDATE_SUPERSET) |
| Overseer | `forge/fabric/overseer.py` | 🟢 GREEN | 268L, 26 symbols: Watcher, Commander, JudgeSeat, SeatManager |
| EmbeddedTailor | `forge/fabric/tailor.py` | 🟢 GREEN | Built M4. Filename still says 🔴 — stale label |
| Capsule | `forge/fabric/capsule.py` | 🟢 GREEN | **merged 2026-08-15** from cabinet |
| Hub | `forge/fabric/hub.py` | 🟢 GREEN | **merged 2026-08-15** from cabinet |
| Kernel | `forge/fabric/kernel.py` | 🟡 YELLOW | **factory table broken** — see §5 |
| Ledger | `forge/fabric/ledger.py` | 🟡 YELLOW | DIVERGED vs cabinet: +20 cand / +6 spine |
| VectorConduit | `forge/fabric/conduit.py` | 🟡 YELLOW | HeuristicSeat live; real NPU seat pending |
| Bind | `forge/fabric/bind/` | 🔴 RED | 5 stale tests — see §5 |
| Couplers | — | 🟡 YELLOW | LOCKED: build last |
| Keychain | — | ⬜ NOT BUILT | design only |
| Hopper | — | ⬜ NOT BUILT | note in `03_BRONZE/prompts/NEXT_ISOLATION_HOPPER.md` |

---

## § 4 · CANONICAL SHAPES

**Do not paraphrase — regenerate from live code before trusting this section:**

```bash
cd ~/the-forge
grep -rn "class Finding\|class Severity\|class LedgerEntry\|class Wrap" forge/fabric/ | head
```

Known from runtime output (pytest):
```python
Finding(id='s', organ='k', severity='critical', title='k', detail='d',
        timestamp=1786857977.78, metadata={})
```
`severity` is a **STRING**, not an int. Three historical shapes exist —
era 1 `section_id/kind/severity=int`, era 2 `verdict/reason/meta`,
era 3 (current) above.

Capabilities: `Spawn, Mount, Egress, NpuEval, Conform, Splice, Reclaim`

---

## § 5 · KNOWN BROKEN

**BASELINE: 11 failed, 123 passed. Any other number = you caused it.**

1. **`forge/fabric/kernel.py:80-82`** — capability factory table passes kwargs
   the dataclasses reject:
   ```python
   EgressCapability(destination=t, ...)   # TypeError
   NpuEvalCapability(model_id=t, input_sha=...)  # TypeError
   ```
   `request_action()` raises **before reaching the gate**. Egress and npu.eval
   are broken at runtime. **Fix the lambdas against the real signatures — do
   NOT strip kwargs**, that would send under-specified capabilities to the Gate.

2. **`forge/fabric/bind/test_bind.py`** — 5 tests pinned to era-1 `Finding`.
   Stale tests, not broken code. `judge()` also lost an argument.

3. **`test_sequence.py`** — 1 test: sequence rolls back where it should complete.

---

## § 6 · DO NOT REBUILD

| Thing | Where | Note |
|---|---|---|
| Overseer / Watcher / Commander | `forge/fabric/overseer.py` | 268L, complete |
| EmbeddedTailor | `forge/fabric/tailor.py` | built M4, 7 tests |
| WrapStore (the wardrobe) | `forge/fabric/wrap.py` | 6 tests |
| BehavioralJudge | `forge/fabric/judge.py` | 8 tests — this IS "define clean behaviorally" |
| AuditLedger | `forge/fabric/ledger.py` | hash-chained, 8 tests |
| Cabinet sorter | `~/FORGE_CABINET/_WORK/sorter/` | forgelib/scan/grade/compare/port/tune/grid — **8 tools import forgelib; never rewrite it** |
| Handoff system | `🔄 FORGE STATE SYNC (swap file).docx` | you built this months ago |

---

## § 7 · CABINET STATE (2026-08-17)

- **235 files** scanned from `~/harvest_zips`
- **44 Office docs extracted** to readable `.md` sidecars via `xdoc.py`
- Grades: 0 GOLD · 2 SILVER · 58 BRONZE · 175 QUARANTINE
- Concept ledger: Forge 50, Fabric 33, Gate 30, Kernel 22, Capability 21,
  Bind 19, Overseer 18, Organ 10
- **Thin concepts** (documented least, discussed most): Finding 3, Drift 2,
  Spine 1, and **zero** for Codex / Hopper / Keychain / seL4
- `board_core` = the React command board → belongs in **`the-forge-ui`**, not the spine

---

## § 8 · OPEN QUESTION

Exactly one.

> **Should `Capability.scope` be validated against a per-organ schema at grant
> time, or remain intentionally opaque to the fabric core?**
>
> If validated: the fabric must know organ schemas (coupling).
> If opaque: validation moves entirely to organs, and the ledger becomes
> unauditable without organ code.
>
> Blocks: Ledger pruning pass.

---

## § 9 · NEXT THREE ACTIONS

1. Fix `kernel.py` factory table → baseline should go 11 failed → 7
2. Port the gate `PathwayRegistry` (+25 symbols, preserve the DESIGN THESIS docstring)
3. Re-sync `bind/test_bind.py` to era-3 `Finding` → 7 failed → 2
