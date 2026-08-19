# CODER BRIEFS — the remaining organs

Written for a capable model with room to design. Each brief gives the
**stakes**, the **invariants that cannot bend**, and what the piece is **for**.
It does not dictate implementation. Where a design choice is genuinely open,
it says so — take it.

Read `~/the-forge/FORGE_STATE.md` before any of these. It is the contract.

---

## THE FRAME (applies to every brief)

THE FORGE is a local-first, security-hardened AI-native OS on one Pop!_OS
workstation (RTX 5080 16GB, Intel Arrow Lake NPU 13 TOPS, 93GB RAM). It treats
raw AI models as **hostile untrusted binaries** that must be sealed, shaped and
gated before they act.

**The five laws.** Break one and the piece is wrong no matter how elegant:

1. **One door.** Every privileged action passes `FabricGate.authorize()`.
   Nothing bypasses it. New capabilities implement the `Capability` protocol;
   they never invent a new way in.
2. **Deaf by default.** Sections cannot hear each other. No wildcard subscribe.
   The Overseer holds the only tap.
3. **Watching and acting are separate organs.** *"The thing that watches
   cannot act, and the thing that acts cannot watch on its own — it acts only
   on the watcher's findings, and only through the gate."*
4. **Sync on the decision path.** `authorize()` never awaits. It cannot be
   allowed to stall the event loop. Async is fine off the hot path.
5. **Nothing is thrown away.** Reclaim, don't delete. The wrap and its vectors
   survive the model.

**Style that is already established** — match it, don't reinvent:
stdlib-first, frozen dataclasses with `slots=True`, `canonical()` returning an
escaped delimited string for signing, bounded queues everywhere, and a
docstring at the top of each organ explaining *why the design is what it is*.
That last one is load-bearing. Reasoning that isn't written down gets rebuilt
wrong six months later — it has already happened four times on this project.

---

## BRIEF 1 — THE HOPPER (highest value, genuinely missing)

### Stakes
`SpawnCapability` already exists and is signed by the Gate, but there is
**nothing on the other side of it**. The Hopper is the organ that decides which
agent does what work and when. Without it there is no way to run more than one
capsule usefully, which means the whole multi-model architecture — the reason
the machine has both an NPU and a 5080 — has no scheduler.

Four implementations exist on disk and **none match the spec**:
- `~/Forge/backend/hopper.py` (114L) — output rate-limiter with WAL
- `.../ForgeOS-Arch-Rev/backend/services/hopper.py` (278L) — richer, same idea
- plus two more variants

They all built an **output throttle**. That is a real and useful thing, and its
WAL journalling ("no approved task is ever silently dropped") is worth keeping.
But it is not the organ described below. Read them for parts, not shape.

### What it must be
The architect's words, verbatim:

> *"The hopper is special design so it doesn't — if one agent or something is
> taking a long time to finish something, the next one can still pull. They can
> pull whenever they want and they drop them in whenever they're done. And if
> it's too difficult of a task, they just drop it back in."*

That is **pull-based work distribution with refusal**, not push-based dispatch.
The distinction is the whole point: a dispatcher must model who is free, and is
therefore wrong the moment an agent stalls. A pull model cannot be wrong,
because only a free agent pulls.

### Invariants
- `pull()` **never blocks**. Empty means empty; return immediately. A slow
  holder must never create head-of-line blocking for a fast one.
- A task handed out is **leased, not given**. Leases expire. A dead agent
  cannot strand work — expired leases return to the pool.
- **Refusal is a first-class outcome**, not an error. An agent that finds a
  task too hard returns it with a reason and an incremented attempt count.
- Bounded. A task refused past its limit goes to a dead-letter list, never an
  infinite loop. The queue itself has a ceiling and rejects beyond it.
- The Hopper **sorts work; it never executes and never calls the Gate.** It
  holds no authority. (Law 3 — this is a watcher-side organ.)
- Two holders must never receive the same task. Concurrency safety is not
  optional.

### Open to you
Whether leases are time-based, heartbeat-based, or both. How difficulty is
expressed and whether the Hopper uses it for routing (an NPU-sized task vs a
5080-sized one is a real distinction on this machine — exploit it if you see a
clean way). Whether priority exists at all. Whether the WAL from the existing
implementations belongs here for durability across restart. Sync or async —
justify whichever you pick against Law 4.

### Done means
Two holders hammering the same Hopper never double-execute. A holder that
dies mid-task loses nothing. A refused task comes back. A slow holder provably
does not block a fast one — write the test that proves it.

---

## BRIEF 2 — THE KEYCHAIN (missing, and the GPU depends on it)

### Stakes
16 GB of VRAM is the binding constraint on this entire machine. The design
answer is that models do not co-reside — each is spawned, used, then
**flattened** so the next gets full power. That only works if something
remembers what happened *after* the model is gone.

The architect's rule, which is the crux:

> *"Save the capsule metadata, not the knowledge base."*

The Keychain is that memory. It is what makes models disposable and the fabric
permanent.

### What it must be
A durable record of capsule lifecycles — minted, run, flattened — holding
**metadata only**: which wrap, which model, when, peak VRAM, task counts,
provenance. Never weights. Never prompts. Never model output.

It is a record keeper, not an actor. It takes no KERNEL role and calls no Gate.

### Invariants
- **Metadata only, enforced in code.** A caller that tries to stash bulk
  content should be refused loudly, not silently truncated. Pick a ceiling and
  raise past it.
- Writes must be **atomic**. An interrupted flatten cannot leave a corrupt
  entry — temp file plus rename, or equivalent.
- Must survive restart and be readable by a human without the Forge running.
  (When something goes wrong at 2am, this is the file you read.)
- Must be able to answer: *what is claiming VRAM right now, and what was the
  peak?* That is the question the GPU keychain exists to answer.

### Open to you
Storage format — one file per capsule, an append-only log, SQLite. Each has a
real trade-off; state which you chose and why. Whether entries are immutable
with a separate flatten record, or mutated in place. Whether it tracks vectors
by reference into the WrapStore (it must not copy them). Whether it can
reconstruct a timeline, and whether that is worth the cost.

### Done means
Mint → flatten → recall round-trips. An oversized payload is rejected. Killing
the process mid-write leaves the store readable. The VRAM ledger matches
reality on a machine that has actually cycled three models.

---

## BRIEF 3 — THE BUS MERGE (the biggest quality gap on disk)

### Stakes
Your live `forge/fabric/bus.py` is **95 lines**. Recovered variants are
**383 lines with +21 symbols you don't have**, and a second at 290. These came
from a different lineage (`backend/kernel/`, fully async) and cannot be dropped
in — but they solve problems your 95-line version does not.

What they have that you don't:
- **Per-subscriber queues with dead-letter overflow.** The comment in the
  source states the principle exactly: *"a stalled consumer never affects
  peers."* Your current bus drops silently under load and is not thread-safe —
  both flagged in your own Graded Master List as the weak spot.
- **Two-phase teardown.** A `SWARM_EOF` sentinel is injected into every live
  queue *before* tasks are cancelled, so worker coroutines blocked on
  `queue.get()` wake, exit, and get collected. No leaked coroutine frames.
- **`SubKernelBus`** — one isolated bus per swarm, where the outer bus is
  unreachable from inside the boundary. This is Law 2 made structural rather
  than conventional.
- Threadsafe publish from non-async callers.

### The task
Bring those properties into the live bus **without** importing the other
lineage's Event model, its async-everywhere assumption, or its naming. The
live `SubstanceBus` API and its callers stay working.

### Invariants
- Deaf-by-default survives. **No wildcard subscribe** — the recovered code has
  one; the live design forbids it. The Overseer's tap is the single exception
  and must remain privileged, not a general feature.
- Bounded queues. Backpressure must be visible (counted, logged, inspectable),
  never silent.
- Drops become observable events, not nothing.
- Whatever you do about async, `authorize()` stays sync (Law 4).

### Open to you
Whether `SubKernelBus` arrives now or is left as a seam for later. Whether the
DLQ is per-subscriber or global. Whether teardown uses a sentinel, cancellation
scopes, or something better. Whether thread safety comes from a lock, a queue
discipline, or single-threaded confinement with an explicit boundary.

### Done means
A deliberately stalled subscriber cannot slow or drop events for any other.
Shutdown leaves no live tasks. Every drop is counted. The existing bus tests
still pass unchanged.

---

## BRIEF 4 — SECURITY GUARDIAN + SOCKET COUPLER (recovered, unreviewed)

### Stakes
Two substantial recovered files with no upstream twin:
- `security_guardian.py` — 485 lines, 7 classes
- `socket_coupler.py` — 483 lines, 4 classes, plus
  `test_capsule_slicing.py` at 568 lines

Your Whitesheet lists "Socket Coupler (hot-plug protocol)" as 🟢 GREEN, and
Couplers as **"#1 HACKER SURFACE — build LAST."** Both statements are true at
once: the design was approved, and it is the most dangerous thing in the
system. That is exactly why it is worth reading carefully and merging slowly.

### The task
This is a **review before a merge**. For each file: what does it actually do,
does it respect the five laws, and what is the smallest safe subset worth
bringing into the spine?

Specific things to check, because they are where this class of code goes wrong:
- Does anything here reach around the Gate, or add a second authorization path?
- Does the coupler hold secrets? (The Glass Rule: the remote limb is *"a tiny
  DUMB remote limb"* — brainless, holds nothing.)
- Does the guardian make security decisions by pattern-matching model output?
  One recovered splicing engine does exactly this — `if "APPROVED" in decision`
  — which is trivially spoofable. If this file does the same, say so plainly.
- Is isolation enforced structurally, or only by convention?

### Open to you
The recommendation. If your honest read is "this is good, port it whole," say
that. If it is "the ideas are right but the implementation trusts the model too
much," say that instead and describe what a correct version does differently.
An accurate refusal is worth more than an enthusiastic merge.

---

## BRIEF 5 — THE SPLICING ENGINE (strongest recovered idea)

### Stakes
`splicing_engine.py` — 261 lines. It implements something none of your live
organs do: **intent recorded before execution, then verified after.**

- **Splice A (Postmaster)** — authorizes an inbound intent, writes it to a
  memory sink, returns a transaction id
- **Splice B (Auditor)** — cross-references the *output* against the
  *originally recorded intent*, and drops it if dirty
- **Splice C (Concocter)** — background daemon extracting high-value state,
  triggering VRAM reclaim

Splice B is the valuable part. It is a genuine exfiltration control: it does
not ask "is this output allowed," it asks "does this output match what was
actually authorized?" That is a different and stronger question, and it is the
same shape as the Gate's sign→verify applied to data flow rather than
capability grants.

It also multiplexes **one pinned model across three channels from a single VRAM
allocation** — which on a 16 GB card is not an optimisation, it is the only way
three checkers can run at once.

### Known flaws — do not carry these forward
- Inference is mocked (`MockSharedWeightEngine`, `asyncio.sleep`)
- Security decisions are string matches on model text (`if "APPROVED" in ...`).
  A model that emits the word "APPROVED" in an explanation passes the gate.
  **This must not survive into the spine.**
- Fully async, including on decision paths

### Open to you
How intent gets bound to output such that the check is meaningful — hashes,
structured claims, capability references, something else. Whether Splice C's
recycling belongs here or in the Keychain. Whether three channels is the right
number or an artifact. Whether the shared-weight trick is worth the coupling it
introduces.

The concept is strong enough to be worth a real implementation. Design it
properly rather than porting it.

---

## PRIORITY, AND WHY

| # | Piece | Why now |
|---|---|---|
| 1 | **Hopper** | Nothing else can schedule work. `SpawnCapability` is a door onto an empty room. |
| 2 | **Bus merge** | Your own audit calls it the weak spot; a stalled consumer can currently take out the fabric. |
| 3 | **Keychain** | 16 GB VRAM makes flatten-and-recycle mandatory, and it needs a memory. |
| 4 | **Splicing engine** | Best idea recovered. Needs real design, not a port. |
| 5 | **Guardian / Coupler** | Review only. Couplers are LOCKED to last for good reason. |

One at a time. One branch each. The baseline is **9 failed, 125 passed** — any
other number after your change means you caused it.

---

## ONE LAST THING FOR THE CODER

This project has been rebuilt from scratch four times, not because the code was
bad — it was good — but because the **reasoning** was never written down, so
each new session re-derived it slightly differently and forked the tree.

So: whatever you build, the docstring explaining *why it is shaped that way* is
not decoration. It is the deliverable that survives you. The existing `gate.py`
does this properly — read its DESIGN THESIS block before you write yours.

Match that bar.
