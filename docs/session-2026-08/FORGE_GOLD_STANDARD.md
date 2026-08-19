# THE FORGE — GOLD STANDARD LAYOUT

The canonical shape of the system, and a brief for every part that is not yet
at standard. This document supersedes every prior layout. When a repo disagrees
with this file, this file wins.

Companion to `~/the-forge/FORGE_STATE.md` (the live contract). This is the
target; that is the current position.

---

# PART I · THE STANDARD

## The five laws

Any piece that breaks one of these is wrong regardless of how well it is
written.

| # | Law | What it forbids |
|---|---|---|
| 1 | **One door** | No privileged action outside `FabricGate.authorize()`. New powers implement `Capability`; they never invent a new entry. |
| 2 | **Deaf by default** | No wildcard subscribe. No section hears another. The Overseer's tap is the single privileged exception. |
| 3 | **Watching ≠ acting** | The organ that observes cannot act. The organ that acts cannot observe on its own. It acts only on findings, only through the gate. |
| 4 | **Sync on the decision path** | `authorize()` never awaits. Async is permitted only off the hot path. |
| 5 | **Nothing thrown away** | Reclaim, don't delete. The wrap and its vectors outlive the model. |

## The house style

Established in `gate.py`, `capabilities.py`, `overseer.py`. Match it.

- **stdlib-first.** A third-party dependency needs a written justification.
- **`@dataclass(frozen=True, slots=True)`** for anything that gets signed.
- **`canonical()`** returns a delimiter-escaped string. Every field that
  matters to security is in it. `_esc()` is not optional — an unescaped `|`
  was a real signature-forgery vector found in this codebase.
- **Bounded everything.** Queues, ledgers, retries, caches. Unbounded is a
  denial-of-service waiting to be discovered.
- **Fail closed.** Unknown severity ranks as critical. Undeclared pathway
  denies before crypto runs. An unparseable input is a refusal, not a default.
- **Decisions are values, not exceptions.** Return a `GateDecision`; offer
  `.enforce()` for callers who want the raise.
- **A DESIGN THESIS docstring** at the top of every organ, explaining *why the
  shape is what it is* and what it replaced. This is a hard requirement — see
  Part III.

## Canonical tree

```
~/the-forge/
├── FORGE_STATE.md              contract · read first, write last
├── tools/hooks/pre-commit      enforces the above
├── forge/
│   ├── fabric/                 THE LOCKED CORE — small, sync, stdlib
│   │   ├── gate.py             the one door
│   │   ├── capabilities.py     the verbs (7)
│   │   ├── bus.py              SubstanceBus — deaf sections + tap
│   │   ├── overseer.py         Watcher + Commander
│   │   ├── conduit.py          VectorConduit — the NPU bond
│   │   ├── wrap.py             Wrap + WrapStore (the wardrobe)
│   │   ├── ledger.py           hash-chained audit
│   │   ├── judge.py            BehavioralJudge — defines CLEAN
│   │   ├── sandbox.py          Concoctinator — observe-mode proving ground
│   │   ├── tailor.py           EmbeddedTailor — strips + drafts
│   │   ├── kernel.py           boot + request_action
│   │   ├── capsule.py          CapsuleStore
│   │   ├── hub.py              external tool hubs
│   │   ├── hopper.py           ☐ work distribution
│   │   ├── keychain.py         ☐ capsule metadata + VRAM ledger
│   │   └── splice.py           ☐ intent-bound audit
│   ├── bind/                   SNAP-ON model seats
│   │   ├── openvino_seat.py    NPU brain
│   │   └── ollama_capsule.py   RTX workhorse
│   ├── bridge/server.py        the glass — /mint, /feed, /ledger
│   └── couplers/               ☐ LOCKED — built last
└── docs/
```

**Locked core is `fabric/`. Everything else snaps on.** That is the war-jeep
principle: the frame is small and fixed; capability arrives as modules.

## The grading rubric

Yours. It already caught two real security bugs. Do not replace it.

```
🟢 GREEN  solid, built, tested      🔴 RED     weak or missing
🟡 YELLOW needs a look              🟣 PURPLE  revolutionary
🟠 ORANGE needs custom work         ★1-5      priority
```

## Current position

Baseline **9 failed / 125 passed**. Any other number after a change means you
caused it.

| Organ | State | Gap to standard |
|---|---|---|
| Gate | 🟢 | +25 recovered symbols pending (Brief 3) |
| Capabilities | 🟢 | escaping shipped; verbs complete |
| Overseer | 🟢 | 268L, Watcher+Commander split correct |
| EmbeddedTailor | 🟢 | built M4; label was stale |
| Capsule / Hub | 🟢 | merged 2026-08-15 |
| Kernel | 🟢 | factory table fixed 2026-08-17 |
| Judge | 🟢 | +6 test symbols available (Brief 8) |
| Ledger | 🟡 | DIVERGED; pruning undefined (Brief 5) |
| Bus | 🟡 | 95L vs 383L recovered (Brief 2) |
| VectorConduit | 🟡 | HeuristicSeat only (Brief 6) |
| Bind tests | 🔴 | 5 stale (Brief 7) |
| Hopper | ⬜ | Brief 1 |
| Keychain | ⬜ | Brief 4 |
| Splice | ⬜ | Brief 9 |
| Couplers | 🔒 | Brief 10 — review only |

---

# PART II · THE BRIEFS

Each gives stakes, invariants, and what is deliberately left open. None
dictates implementation.

---

## BRIEF 1 · HOPPER ★★★★★ — `fabric/hopper.py`

**Stakes.** `SpawnCapability` is a signed door onto an empty room. Nothing
decides which agent does what work. Without this the multi-model architecture —
the whole reason the box has both an NPU and a 5080 — has no scheduler.

Four `hopper.py` files exist on disk. **None match the spec.** All four built an
*output throttle* (rate-limited drain with WAL). Useful, but a different organ.
Read them for the WAL durability idea; ignore their shape.

**What it must be**, in the architect's words:

> *"If one agent is taking a long time to finish something, the next one can
> still pull. They can pull whenever they want and they drop them in whenever
> they're done. And if it's too difficult of a task, they just drop it back in."*

Pull-based with refusal — not push dispatch. A dispatcher must model who is
free and is therefore wrong the instant an agent stalls. A puller cannot be
wrong, because only a free agent pulls.

**Invariants**
- `pull()` never blocks. Empty returns immediately. No head-of-line blocking, ever.
- Work is **leased, not given**. Leases expire; a dead holder strands nothing.
- **Refusal is an outcome, not an error.** Return with reason, increment attempts.
- Bounded: queue ceiling, attempt ceiling, dead-letter for exhausted tasks.
- Sorts work. **Never executes. Never calls the Gate.** No authority (Law 3).
- Two holders never receive the same task.

**Open** — lease mechanism (time, heartbeat, both). Whether difficulty drives
routing; NPU-sized vs GPU-sized is a real distinction here, exploit it if
clean. Priority, or none. Whether WAL durability belongs in this organ.
Sync or async, justified against Law 4.

**Done** — two holders hammering it never double-execute; a killed holder loses
nothing; a refused task returns; a slow holder provably does not block a fast
one. Write that last test.

---

## BRIEF 2 · BUS HARDENING ★★★★★ — `fabric/bus.py`

**Stakes.** Live bus is **95 lines**. Recovered variants are **383L (+21
symbols)** and 290L. Your own Graded Master List names the weakness:
*"drops silently under load; not thread-safe."* A stalled consumer can
currently degrade the whole fabric.

What the recovered lineage has:
- Per-subscriber queues with **dead-letter overflow** — *"a stalled consumer
  never affects peers"*
- **Two-phase teardown**: inject `SWARM_EOF` into every live queue, *then*
  cancel and join. No leaked coroutine frames.
- **`SubKernelBus`** — one isolated bus per swarm; the outer bus is unreachable
  from inside. Law 2 made structural instead of conventional.
- Threadsafe publish from non-async callers.

**The task.** Bring those properties into the live bus **without** importing
that lineage's Event model, async-everywhere assumption, or naming. Existing
`SubstanceBus` callers keep working.

**Invariants** — no wildcard subscribe (the recovered code has one; the live
design forbids it). Bounded queues. Backpressure **visible** — counted, logged,
inspectable. Drops become events, never silence. `authorize()` stays sync.

**Open** — whether `SubKernelBus` lands now or is left as a seam. DLQ per
subscriber or global. Teardown by sentinel, cancel scope, or better. Thread
safety via lock, queue discipline, or single-threaded confinement with an
explicit boundary.

**Done** — a deliberately stalled subscriber cannot slow or drop events for any
other. Shutdown leaves no live tasks. Every drop counted. Existing tests pass
unchanged.

---

## BRIEF 3 · GATE PATHWAY REGISTRY ★★★★☆ — `fabric/gate.py`

**Stakes.** A recovered `gate.py` is a strict superset: **+25 symbols, 0
spine-only**. It adds a coherent subsystem the live gate lacks — forward-declared
pathways, role-gated registry mutation, and O(1) vessel revocation.

- `PathwayRegistry` + `PathwayDescriptor` — an **undeclared `kind` is denied
  before any crypto runs** (`DENY_PATH_NOT_DECLARED`). A new capability cannot
  silently create a new door.
- `Role` (KERNEL/OVERSEER/MODEL/EXTERNAL) with `may_inspect_registry` /
  `may_modify_registry`
- `revoke_vessel` / `clear_revocation` with epoch comparison against `issued_at`
- `vessel_id` bound into the HMAC body, not carried alongside it
- `GateStats._bump()` match-dispatch; three new `Decision` members

**The trap.** The recovered file **deleted ~40 lines of design rationale** — the
DESIGN THESIS and "WHAT I FIXED FROM THE ORIGINAL" blocks explaining why the
replay ledger is exact rather than probabilistic, why nothing reaches into
`asyncio.Semaphore._value`, why decisions are values. AST comparison scores that
loss as zero. It is not zero.

**Port the symbols into the live file. Keep the live prose. Do not copy the
file over.** Then write a new thesis block, in the same voice, explaining why
forward-declared pathways exist.

**Invariants** — `sign/authorize/enforce/stats/ledger_size` keep working for
callers passing no `vessel_id` and no registry. Pathway check is **Axis 0**,
before crypto. Existing order preserved: freshness → signature → replay.

**Done** — undeclared pathway denied; suspended pathway denied; revoked vessel
denied for tokens issued before the epoch and allowed after; every existing
gate test green.

---

## BRIEF 4 · KEYCHAIN ★★★★☆ — `fabric/keychain.py`

**Stakes.** 16 GB VRAM is the binding constraint on this machine. The design
answer is that models do not co-reside — spawn, use, **flatten**, so the next
gets full power. That only works if something remembers after the model is gone.

The rule, which is the crux:

> *"Save the capsule metadata, not the knowledge base."*

This organ is what makes models disposable and the fabric permanent.

**What it must be.** A durable record of capsule lifecycles — minted, run,
flattened — holding **metadata only**: wrap reference, model id, timestamps,
peak VRAM, task counts, provenance. Never weights, prompts, or output. A record
keeper: no KERNEL role, no Gate calls.

**Invariants** — metadata-only **enforced in code**; oversized payloads refused
loudly, never silently truncated. Atomic writes; an interrupted flatten cannot
corrupt an entry. Readable by a human without the Forge running — this is the
file you open at 2am. Must answer: *what claims VRAM now, and what was peak?*

**Open** — storage format (file-per-capsule, append-only log, SQLite); state the
trade-off you chose. Immutable entries plus a flatten record, or in-place
mutation. Whether vectors are referenced into the WrapStore (never copied).
Whether timeline reconstruction is worth its cost.

**Done** — mint → flatten → recall round-trips; oversized payload rejected;
process killed mid-write leaves a readable store; VRAM ledger matches a machine
that has actually cycled three models.

---

## BRIEF 5 · LEDGER RECONCILE ★★★☆☆ — `fabric/ledger.py`

**Stakes.** DIVERGED against recovered variants: **+4 candidate / +5 spine** in
one, **+4 / +6** in another. Both sides hold unique symbols, so neither wins
outright. Meanwhile pruning is undefined and the chain grows without bound —
which collides with "bounded everything."

The ledger is the audit spine: `H_i = Hash(seq || ts || payload || H_{i-1})`,
periodically signed. If it is not trustworthy, nothing downstream is.

**The task.** A genuine two-way merge. Identify what each side has, keep the
union where it is coherent, and define the pruning policy.

**The hard question, and it is blocked on §8 of FORGE_STATE.md:** pruning a
hash chain breaks verification from genesis. Either you keep signed checkpoints
so a pruned prefix can still be attested, or pruning silently destroys
tamper-evidence. Decide explicitly and write down which.

**Invariants** — tamper-evidence survives pruning, or pruning does not ship.
`verify()` must still catch a modified entry. Append path stays fast and sync.

**Open** — checkpoint frequency and format. Whether pruned entries are archived
to the Keychain or discarded. Whether rotation is by count, age, or size.

---

## BRIEF 6 · VECTOR CONDUIT / NPU SEAT ★★★☆☆ — `fabric/conduit.py`

**Stakes.** The conduit is the spinal cord bonding body to NPU brain **without
fusing them** — one `tick()` is FEED UP → JUDGE → COMMAND. It currently runs a
`HeuristicSeat`; the real Arrow Lake seat has never been bound. **Your NPU
driver stack now works** (OpenVINO GenAI enumerating CPU/GPU/NPU), so the
blocker is gone.

`TailorSeat` and `NpuSeat` protocols are already defined. This is binding, not
inventing.

**Invariants** — Law 3 in its purest form: the brain **observes and proposes,
and cannot execute**. Every action it wants goes through the Gate as a
capability. A hung or crashed seat returns empty findings — never fabricates,
never stalls the heartbeat. Model output is data, never a decision.

**Open** — model choice and quantization (1.5–3B INT4 is the sizing already
reasoned out; the NPU drafts, the GPU does heavy work). How findings are
structured. Whether the seat is hot-swappable at runtime. Failure semantics
beyond "return empty".

**Watch for** — recovered code that decides security by string-matching model
output (`if "APPROVED" in decision`). That pattern must not enter this organ.

---

## BRIEF 7 · BIND TEST RE-SYNC ★★★☆☆ — `fabric/bind/test_bind.py`

**Stakes.** 5 of your 9 remaining failures. These tests are **older than the
code** — they are not reporting bugs.

Three eras of `Finding` exist in this project's history:

| Era | Shape |
|---|---|
| 1 | `Finding(section_id=, kind=, detail=, severity=1)` ← tests use this |
| 2 | `Finding(verdict=, reason=, meta={})` |
| 3 | `Finding(id=, organ=, severity='critical', title=, detail=, timestamp=, metadata={})` ← current |

**The task.** Re-sync to era 3. `severity` is a **string enum** — the clamp test
must expect the top string, not `3`. `judge()` now takes one positional
argument; drop the `VectorMemory` parameter from all three call sites. Fix the
`Finding` import.

**Do not change `openvino_seat.py` to match the tests.** The code is canonical.

Since the NPU stack now works, these can run for real rather than staying
permanently mocked.

**Done** — 9 failed becomes 4.

---

## BRIEF 8 · JUDGE TEST UPLIFT ★★☆☆☆ — `fabric/test_judge.py`

**Stakes.** Recovered variant is **CANDIDATE_SUPERSET: +6 symbols, 74L vs your
24L**. Three times the test coverage.

This matters more than a test file usually would. `BehavioralJudge` is what
answers the EmbeddedTailor's one open question — *"define CLEAN behaviorally,
not just structurally"* — and it is the gate on promotion out of the
Concoctinator. Weak tests there mean an unproven definition of clean.

**Open** — whether all 6 recovered symbols are worth keeping, and what a
behavioral definition of clean should actually assert: dangerous tool
combinations, output distribution bounds, canary prompts, gate-would-deny
simulation. Your own M5 research folder covers this ground; read it.

---

## BRIEF 9 · SPLICE ★★★★☆ — `fabric/splice.py`

**Stakes.** The strongest idea recovered. `splicing_engine.py` (261L)
implements something no live organ does: **intent recorded before execution,
verified after.**

- **Splice A · Postmaster** — authorizes inbound intent, writes it to a sink,
  returns a transaction id
- **Splice B · Auditor** — checks the *output* against the *originally recorded
  intent*, drops if dirty
- **Splice C · Concocter** — background extraction, triggers VRAM reclaim

Splice B is the prize. It does not ask "is this output allowed" — it asks
"**does this output match what was actually authorized?**" A stronger question,
and the same shape as the Gate's sign→verify applied to data flow rather than
capability grants.

It also multiplexes **one pinned model across three channels from a single VRAM
allocation** — on a 16 GB card that is not an optimisation, it is the only way
three checkers run at once.

**Do not carry these forward** — mocked inference (`MockSharedWeightEngine`);
security by string match (`if "APPROVED" in decision`, trivially spoofable);
async on decision paths.

Note there is already a `SpliceCapability` verb (`region_id`, `mode`,
`sections`, `deaf`) for isolation boundaries. Decide whether this organ extends
that concept or is a distinct one, and name it so the two are never confused.

**Open** — how intent binds to output such that the check is meaningful
(hashes, structured claims, capability references). Whether Splice C's
recycling belongs here or in the Keychain. Whether three channels is principled
or an artifact. Whether shared-weight multiplexing justifies its coupling.

Design it properly. Do not port it.

---

## BRIEF 10 · GUARDIAN + COUPLER ★☆☆☆☆ — review only

**Stakes.** Two large recovered files, no upstream twin:
`security_guardian.py` (485L, 7 classes), `socket_coupler.py` (483L, 4 classes),
plus `test_capsule_slicing.py` (568L).

Your Whitesheet calls Socket Coupler 🟢 GREEN **and** calls couplers the
**"#1 HACKER SURFACE — build LAST."** Both are true: the design was approved,
and it is the most dangerous surface in the system.

**This is a review, not a merge.** For each file: what does it do, does it
respect the five laws, and what is the smallest safe subset worth taking?

Check specifically:
- Does anything reach around the Gate or add a second authorization path?
- Does the coupler hold secrets? The remote limb is *"a tiny DUMB remote limb"* —
  brainless, holds nothing.
- Does the guardian decide security by pattern-matching model output?
- Is isolation structural, or only conventional?

**Open** — the recommendation itself. "Port it whole" is a valid answer. So is
"the ideas are right, the implementation trusts the model too much, here is
what a correct version does instead." **An accurate refusal is worth more than
an enthusiastic merge.**

---

# PART III · THE RULE THAT MATTERS MOST

This system has been rebuilt from scratch four times. Not because the code was
bad — it was good, and most of it still exists on this disk. It was rebuilt
because the **reasoning was never written down**, so each new session
re-derived it slightly differently and forked the tree.

The evidence is measurable. Searching every artifact for the project's own
vocabulary:

```
capsule    184 hits in one document, 0 in another
keychain    23 in one, 0 everywhere else
wardrobe     0 anywhere — a central concept, unwritten
flatten      0 anywhere
baptize      0 anywhere
```

Three central concepts existed only in the architect's head. Meanwhile the
things they named were already built — the wardrobe is `WrapStore`, the baptism
is `wrap-conform`, the commander is half of `Overseer`, and the "missing organ"
shipped at M4.

So, the standard:

**Every organ carries a DESIGN THESIS docstring** stating what it replaces,
what problem it solves, what was tried before and rejected, and which of the
five laws constrain it. Read `gate.py`'s block before writing yours — it is the
bar. Its "WHAT I FIXED FROM THE ORIGINAL" section is why nobody has
reintroduced a probabilistic replay guard.

**Every merged decision lands in `FORGE_STATE.md` §1** with a date and a
one-line reason, in the same commit as the code. The pre-commit hook enforces
this. Instructions get skipped; hooks do not.

**Every new term goes in the vocabulary table** the first time it is used.

Code is regenerable. Reasoning is not. The docstring is the deliverable that
survives the session.
