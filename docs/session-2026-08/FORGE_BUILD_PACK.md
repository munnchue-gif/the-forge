# THE FORGE — Layout + Prompt Pack

Everything you described, mapped to the formal architecture in your own
Concepts Guide, with a paste-ready prompt for each part.

---

## PART 1 — Your "missing" concepts were never missing

I searched every artifact for your spoken vocabulary. The words are absent, but
**the concepts are all there under formal names.** This is the Rosetta stone:

| Your word | Formal name in your docs | Status |
|---|---|---|
| **wardrobe** | **WrapStore** — *"the recycling yard"* | BUILT, 6/6 tests |
| **baptize** | **Wrap-conform** — *"Wrap-conform IS the baptism"* | BUILT |
| **flatten / recycle** | **Reclaim capability** + *"Recycle, don't delete — models stripped and re-poured"* | BUILT (capability), engine partial |
| **suit / fabric** | **The Substance** / Wrap | BUILT |
| **commander** | **Overseer = Watcher + Commander** (one organ, two halves) | BUILT, 7/7 tests |
| **conduit (hears, can't order)** | **VectorConduit** — *"observes and proposes, cannot execute without the Gate"* | BUILT, 8/8 tests |
| **splice** | **Splice capability** + *"Isolation = the substance splicing itself"* | BUILT |
| **spawn** | **Spawn capability** | BUILT |
| **keychain** | *(GPU/capsule metadata — only in kernel review as `~/Forge/keychain/*.gz`)* | **DESIGN ONLY** |
| **hopper** | *(not in this guide; note in `03_BRONZE/prompts/NEXT_ISOLATION_HOPPER.md`)* | **DESIGN ONLY** |

**Only two are genuinely unbuilt: Keychain and Hopper.** Everything else exists
and has passing tests. You have been rebuilding things you already finished.

Your verbal split — *"conduit hears but can't order, commander orders but can't
hear"* — is **exactly** the Overseer/VectorConduit design, stated in the guide
as: *"The brain (NPU) observes and proposes actions, but cannot execute them
without passing the Gate."* You did not lose that idea. You re-derived it
correctly a year later, which means it is load-bearing.

---

## PART 2 — A fourth path lineage (important before any rebuild)

Your artifacts now show **four** different roots for the same code:

| Lineage | Source | Era |
|---|---|---|
| `forge/<organ>/kernel.py` | App manual | oldest |
| `backend/kernel/bus.py` | Kernel review | parallel branch |
| **`forge_ng/fabric/gate.py`** | **This Concepts Guide** | **the "NG" rewrite** |
| `forge/fabric/gate.py` | your live spine today | current |

`forge_ng` appears 8 times in this guide. Your live spine uses `forge/fabric/`.
The recovered `gate.py` docstring says *"Forge-NG — FabricGate"* — **your live
gate IS the forge_ng gate, moved.** That is the migration that broke
`kernel.py`'s factory table.

Also note the test count: this guide says **119/119 green**. You are at
**134 tests, 11 failing**. The 15 new tests came after this guide; the 11
failures are the drift documented in `BASELINE_DRIFT.md`.

---

## PART 3 — The layout

### The stack (from your guide, annotated with today's reality)

```
L8  DJ Booth GUI ─────────────── PENDING   (the-forge-ui exists)
L7  Couplers A/B ─────────────── PENDING   ← build LAST, #1 hacker surface
L6  Real Models ──────────────── IN PROGRESS  ← NPU now works
L5  Harden + Specialize ──────── partial   ← burn op, attenuation
L4  The Tailor ───────────────── DONE      ← EmbeddedTailor live
L3  Proving Ground ───────────── DONE      ← Concoctinator
L2  The Being ────────────────── DONE      ← wrap + conduit + memory
L1  Trust Core ───────────────── DONE      ← gate + bus + overseer
L0  Bare Metal ───────────────── READY     ← Pop!_OS, 5080, NPU
```

### Target repo shape

```
~/the-forge/                        ← THE ONLY CODE REPO
├── FORGE_STATE.md                  ← read-first / write-last  ★ NEW
├── CONCEPT_MAP.md                  ← the vocabulary           ★ NEW
├── forge/
│   ├── fabric/                     ← the locked core (small)
│   │   ├── gate.py                 ← the one door
│   │   ├── bus.py                  ← deaf sections, bounded queues
│   │   ├── overseer.py             ← Watcher + Commander
│   │   ├── conduit.py              ← VectorConduit (NPU bond)
│   │   ├── wrap.py                 ← Wrap + WrapStore (the wardrobe)
│   │   ├── capabilities.py         ← Spawn/Mount/Egress/NpuEval/Conform/Splice/Reclaim
│   │   ├── ledger.py               ← hash-chained audit
│   │   ├── judge.py                ← BehavioralJudge
│   │   ├── sandbox.py              ← Concoctinator
│   │   ├── tailor.py               ← EmbeddedTailor
│   │   ├── kernel.py               ← boot + request_action
│   │   ├── capsule.py              ← ★ recovered today
│   │   ├── hub.py                  ← ★ recovered today
│   │   ├── keychain.py             ← ☐ TO BUILD
│   │   └── hopper.py               ← ☐ TO BUILD
│   └── bind/                       ← snap-on model seats
│       ├── openvino_seat.py        ← NPU brain
│       └── ollama_capsule.py       ← RTX workhorse
└── docs/
```

**Locked core = `fabric/`. Snap-on = `bind/` + capsules + hubs.** That is your
"bare metal, layered, snap on/off" plan, already the shape of the repo.

---

## PART 4 — THE PROMPTS

Rules for all of them:
- One prompt per session. Never two.
- Paste `FORGE_STATE.md` above the prompt every time.
- End every session by updating `FORGE_STATE.md`.
- New code goes on a branch: `git checkout -b feat/<name>`.

---

### PROMPT 0 — FORGE_STATE.md (do this first, always)

```text
Create ~/the-forge/FORGE_STATE.md. This file is the handoff contract: every
future session reads it first and updates it last. Keep it under 200 lines.

Sections, in this order:

1. LOCKED DECISIONS (date + one-line rationale each). Seed with:
   - 2026-08: FabricGate.authorize() is SYNC, never async. Reason: it must
     never stall the event loop. Supersedes the async design in the App manual.
   - 2026-08: Canonical path root is forge/fabric/. Supersedes forge/<organ>/,
     backend/kernel/, and forge_ng/fabric/.
   - 2026-08: Models are wrapped on entry (SHA-256). No raw model ever runs.
   - 2026-08: Deaf-by-default. No wildcard subscribe on SubstanceBus.
     Overseer holds the only read-only tap.
   - 2026-08: Couplers are built LAST. They are the #1 attack surface.
   - 2026-08: NPU path is OpenVINO GenAI only. ipex-llm is Windows-only;
     intel-npu-acceleration-library is deprecated.
   - 2026-08: Capsule became fabric — the spawning sandbox wrapper that
     oversees all, without holding kernel authority.

2. CANONICAL SHAPES — paste the real dataclass definitions for Finding,
   the Capability protocol, LedgerEntry, and Wrap. Read them from the live
   code, do not invent. Note that Finding.severity is a STRING enum, not int.

3. ORGAN STATUS — table of every organ: name, file, tests passing, status
   (LIVE / PARTIAL / DESIGN-ONLY / BROKEN).

4. KNOWN BROKEN — with file:line. Seed with:
   - forge/fabric/kernel.py:80-82 — capability factory table passes kwargs
     the dataclasses reject (EgressCapability(destination=...),
     NpuEvalCapability(input_sha=...)). request_action raises TypeError
     before reaching the gate.
   - forge/fabric/bind/test_bind.py — 5 tests pinned to a pre-refactor
     Finding shape. Stale tests, not broken code.
   - BASELINE: 11 failed, 123 passed. Any other number means you caused it.

5. DO NOT REBUILD — list what exists with its path, so no session
   re-derives it: WrapStore is the wardrobe. Wrap-conform is the baptism.
   Reclaim is the flatten. Overseer contains the Commander. VectorConduit
   is the hearing-but-not-ordering organ.

6. OPEN QUESTION — exactly one, for the next session.

Commit it as: docs(state): add handoff contract
```

---

### PROMPT 1 — Fix the kernel factory table (real bug, highest value)

```text
Fix the capability factory table in ~/the-forge/forge/fabric/kernel.py
(around lines 78-85).

The bug: the lambdas construct capabilities with keyword arguments the
dataclasses do not accept. request_action() therefore raises TypeError
before it ever reaches the gate. Egress and npu.eval are broken at runtime,
not merely untested.

Failing today:
  EgressCapability(destination=t, protocol="https", port=443)
  NpuEvalCapability(model_id=t, input_sha=_EMPTY_SHA)

Steps:
1. Read the ACTUAL current definitions in forge/fabric/capabilities.py for
   all seven capabilities: Spawn, Mount, Egress, NpuEval, Conform, Splice,
   Reclaim.
2. Correct every lambda in the factory table to match the real signatures.
   Do not change the dataclasses to match the lambdas — the dataclasses are
   canonical.
3. Keep request_action SYNCHRONOUS. Do not add async/await.
4. Make test_request_action_unknown_op raise ValueError for an unmapped op.

Constraint: baseline is 11 failed / 123 passed. When done, the four
test_bridge_accessors failures caused by this bug must be gone and NOTHING
else may newly fail.

Work on branch fix/kernel-factory. Show me the diff before committing.
```

---

### PROMPT 2 — Merge the recovered gate.py PathwayRegistry

```text
Port the PathwayRegistry subsystem from the cabinet copy of gate.py into the
live spine gate.py. DO NOT replace the file.

Live (authoritative): ~/the-forge/forge/fabric/gate.py            (250 lines)
Reference only:       ~/forge-spine/forge/fabric/gate.py          (305 lines)

The cabinet copy is a strict API superset: +25 symbols, 0 spine-only.

ADD to the live file:
  - Role(str, Enum): KERNEL/OVERSEER/MODEL/EXTERNAL with properties
    may_inspect_registry and may_modify_registry
  - Direction and ClearanceLevel enums
  - PathwayDescriptor (frozen dataclass, __post_init__ validation)
  - PathwayRegistry with a _Missing sentinel; register/deregister/_lookup/
    list_pathways/pathway_registered/__len__; mutation gated on Role
  - FabricGate: pathway_registry ctor param, _revocation_epochs dict,
    register_pathway/deregister_pathway/list_pathways/pathway_registered,
    revoke_vessel/clear_revocation
  - Decision: DENY_PATH_NOT_DECLARED, DENY_PATH_SUSPENDED, DENY_REVOKED
  - GateStats: matching counters + _bump(decision) match-dispatch
  - SignedCapability.vessel_id, bound into the HMAC body in sign() and
    verified in authorize()
  - authorize(): Axis-0 pathway check BEFORE any crypto; revocation check
    after replay. Keep the existing order: freshness -> signature -> replay.

PRESERVE VERBATIM from the live file — this is the whole point:
  - The DESIGN THESIS docstring block
  - The WHAT I FIXED FROM THE ORIGINAL block (exact replay ledger rationale)
  - The ReplayLedger class docstring
  - Every existing method docstring

The cabinet copy DELETED that rationale. Do not let that loss through.

THEN add a new docstring block, in the same voice, explaining why
forward-declared pathways exist: an undeclared kind is denied before any
crypto runs, so a new capability cannot silently create a new door.

Backwards compatibility: sign/authorize/enforce/stats/ledger_size must keep
working for callers passing no vessel_id and no registry.

Add tests: undeclared pathway denied; suspended pathway denied; revoked
vessel denied for tokens issued before the epoch, allowed after.

Branch: feat/gate-pathway-registry
```

---

### PROMPT 3 — Build the Keychain (genuinely new)

```text
Build ~/the-forge/forge/fabric/keychain.py — GPU capsule metadata store.

Purpose (from the architecture): models are flattened after use so the GPU is
freed and each model in turn gets maximum power draw. What persists is the
CAPSULE METADATA, never the knowledge base.

Requirements:
  - KeychainEntry (frozen dataclass): capsule_id, model_id, wrap_sha,
    created_at, flattened_at, vram_peak_mb, task_count, provenance dict
  - Keychain class: store to ~/.forge/keychain/<capsule_id>.json.gz
    (gzip, atomic write via temp file + os.replace)
  - mint(capsule) -> KeychainEntry           record a spawn
  - flatten(capsule_id, stats) -> KeychainEntry   record teardown + free VRAM
  - recall(capsule_id) -> KeychainEntry | None
  - list_keys(*, since=None) -> tuple[KeychainEntry, ...]
  - purge(capsule_id) -> bool
  - vram_ledger() -> dict: current claimed VRAM, peak, free estimate

Hard rules:
  - Store METADATA ONLY. Never persist weights, prompts, or model output.
    If a caller passes anything over 4KB in provenance, raise KeychainError.
  - Stdlib only (json, gzip, pathlib, dataclasses, time, os).
  - Sync API. No async.
  - The Keychain never takes KERNEL role and never calls the Gate — it is a
    record keeper, not an actor.

Add tests: mint/recall round-trip, flatten updates the entry, oversized
provenance rejected, atomic write survives an interrupted run, list_keys
filters by time.

Branch: feat/keychain
```

---

### PROMPT 4 — Build the Hopper (genuinely new)

```text
Build ~/the-forge/forge/fabric/hopper.py — non-blocking work distribution.

Design (stated by the architect):
  "Agents pull whenever they want and drop them in whenever they're done.
   If it's too difficult a task, they just drop it back in. If one agent is
   taking a long time, the next one can still pull."

That is a work-stealing queue with lease + refusal semantics. NOT push-based.

Requirements:
  - Task (frozen dataclass): id, kind, payload, difficulty, attempts,
    max_attempts, created_at
  - Lease (frozen dataclass): task_id, holder, expires_at
  - Hopper class:
      drop(task)                     -> add work
      pull(holder, *, kinds=None)    -> Task | None   (non-blocking, never waits)
      complete(task_id, result)      -> None
      refuse(task_id, reason)        -> None   requeue with attempts+1
      reap()                         -> int    reclaim expired leases
      stats()                        -> dict   pending/leased/done/refused counts

Hard rules:
  - pull() NEVER blocks. If nothing is available it returns None immediately.
    A slow holder must never create head-of-line blocking.
  - Leases expire (default 300s). reap() returns expired tasks to pending so
    a dead agent cannot strand work.
  - A task refused more than max_attempts goes to a dead-letter list, never
    an infinite loop.
  - Bounded: max_pending (default 4096). Over that, drop() raises HopperFull.
  - Stdlib only, sync, thread-safe with threading.Lock.
  - The Hopper does not execute anything and never calls the Gate. It sorts.

Add tests: pull returns None when empty; two holders never get the same task;
refuse requeues and increments attempts; max_attempts sends to dead-letter;
expired lease is reaped and re-pullable; a slow holder does not block a fast
one; drop past max_pending raises.

Branch: feat/hopper
```

---

### PROMPT 5 — Capsule resource ceiling (closes the sandbox gap)

```text
Add resource limits to capsule execution in ~/the-forge/forge/fabric/capsule.py.

Context: the architecture deliberately avoids Docker. Network isolation plus a
split watcher covers exfiltration and remote control. It does NOT cover
filesystem damage inside reach, or resource exhaustion. Close those two with
~20 lines, no daemon, no container.

Add to CapsuleStore (or a new CapsuleRunner):
  - run_contained(capsule, argv, *, mem_max="8G", cpu_quota="200%",
                  allow_paths: list[Path], timeout=300)
  - Wrap the child in:
      systemd-run --user --scope --collect
        -p MemoryMax=<mem_max> -p CPUQuota=<cpu_quota>
        -p PrivateNetwork=yes
  - Before exec, assert every path the capsule may write is under an
    allow_paths entry. Reuse the same resolve()-and-compare guard pattern
    used by the cabinet sorter's assert_writable(); refuse otherwise.
  - Capture stdout/stderr to a bounded buffer (1MB cap) so a runaway child
    cannot fill the disk with logs.
  - On timeout, kill the scope and record a CapsuleTimeout.

Fallback: if systemd-run is unavailable, use resource.setrlimit
(RLIMIT_AS, RLIMIT_CPU) in a preexec_fn and log that the weaker path is used.

Add tests (skip if systemd-run absent): memory ceiling kills a hog, timeout
fires, a write outside allow_paths is refused before exec, network is
unavailable inside the scope.

Branch: feat/capsule-limits
```

---

### PROMPT 6 — Re-sync the stale bind tests (do last)

```text
Re-sync ~/the-forge/forge/fabric/bind/test_bind.py to the current API.
These 5 tests are older than the code. They are not reporting bugs.

Three eras of Finding exist in the project history:
  era 1: Finding(section_id=, kind=, detail=, severity=1)      <- tests use this
  era 2: Finding(verdict=, reason=, meta={})
  era 3: Finding(id=, organ=, severity='critical', title=, detail=,
                 timestamp=, metadata={})                       <- CURRENT

Fix:
1. Import Finding from wherever it actually lives now; fix the NameError.
2. severity is a STRING enum in era 3. Update assertions: the clamp test
   must expect the top string value, not the int 3.
3. OpenVinoSeat.judge() now takes ONE positional arg. Drop the VectorMemory
   argument from all three call sites; memory is internal now.
4. Do not change openvino_seat.py to match the tests. The code is canonical.

The NPU driver stack now works (OpenVINO GenAI, devices report CPU/GPU/NPU),
so these tests can run for real rather than being permanently mocked.

Target: 11 failed -> 6 failed after this (the 5 bind failures resolved).

Branch: fix/bind-tests
```

---

## PART 5 — Order of operations

```
Session 1   PROMPT 0   FORGE_STATE.md            ← nothing else. Do it first.
Session 2   finish harvest: port forge.py, merge ledger.py, validate_ledger.py
Session 3   PROMPT 1   kernel factory fix        → 11 failed becomes 7
Session 4   PROMPT 2   gate PathwayRegistry      ← the big recovery
Session 5   PROMPT 6   bind test re-sync         → 7 failed becomes 2
Session 6   PROMPT 3   Keychain                  ← new
Session 7   PROMPT 4   Hopper                    ← new
Session 8   PROMPT 5   capsule limits
Session 9   sorter over the other 10 repos
Session 10  write it all into FORGE_STATE.md, offload, THEN wipe
```

Ten sessions to a clean, complete, documented system — with nothing lost.
Compare that to a rebuild, where session 1 starts by re-deriving the Overseer.

---

## PART 6 — The one thing to internalise

Your Concepts Guide says **119/119 tests green** and lists Gate, Capabilities,
SubstanceBus, Overseer, VectorConduit, Wrap, Concoctinator, Skeleton as
**BUILT AND TESTED**.

You did not fail to build this. **You built it, then lost the map to it four
times.** The wardrobe is `WrapStore`. The baptism is `wrap-conform`. The
commander is half of `Overseer`. All of it has passing tests somewhere on that
drive.

Do not rebuild. Reconnect.
