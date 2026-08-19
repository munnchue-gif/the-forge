# The Forge — Concept Map (v1, dictated 2026-08-16)

Your architecture in your own vocabulary, written down before another session
loses it. **This is the seed for `FORGE_STATE.md`.**

---

## Term survival check — why this file had to exist

I searched all three artifacts you uploaded for your core vocabulary:

| Term | App manual | Kernel review | Mistral feed |
|---|---|---|---|
| `capsule` | 0 | 184 | 45 |
| `keychain` | 0 | 23 | 0 |
| `wrap` | 39 | 10 | 8 |
| `tailor` | 1 | 0 | 9 |
| `concoctinator` | 3 | 0 | 0 |
| `spawn` | 0 | 4 | 3 |
| **`wardrobe`** | **0** | **0** | **0** |
| **`flatten`** | **0** | **0** | **0** |
| **`baptized`** | **0** | **0** | **0** |

The three concepts you just described as *central* — the wardrobe, flattening,
baptism — **appear nowhere in any artifact you have.** They exist only in your
head and in this conversation. That is the whole problem in one table.

Note also: `capsule` scores 184 in one artifact and 0 in another; `keychain`
lives only in the kernel review, pointing at `~/Forge/keychain/*.gz`. Each
session kept a different subset of the vocabulary.

---

## The design, as you described it

### Core principle
**The fabric holds the system. The AI does not.**
Models are interchangeable tools. Nothing durable lives inside them.

> *"It keeps it all in the fabric not the AI, since they are always making a
> new one. Who wants to build this again?"*

### The lifecycle

```
    spawn ──► suit up ──► animate ──► baptize ──► work ──► flatten ──► recycle
      ▲                  (fabric)   (compartment)          (concoctinator)  │
      └──────────────────────── keychain / capsule metadata ◄───────────────┘
```

| Stage | What happens |
|---|---|
| **Spawn** | A model instance is created for a task |
| **Suit / Fabric** | It is wrapped in the fabric — given identity, cached memory, its task set |
| **Animate** | The suit is live; the model acts only through it |
| **Baptize** | Fully compartmentalised — it cannot reach outside its wrap |
| **Flatten** | Work done: the model is collapsed, knowledge extracted |
| **Concoctinator** | Flattened material is recycled into something new |
| **Keychain** | Capsule *metadata* persists (`.gz` in `~/Forge/keychain/`), **not** the knowledge base |
| **Wardrobe** | The applied knowledge — in-house, pinned by "magic scripts" once proven |

### The critical distinction (write this down everywhere)

> **Save the capsule metadata, not the knowledge base.**
> The wardrobe is the knowledge that gets *applied*; it lives in-house, wrapped
> and pinned by scripts. The model never owns it.

That single rule is what makes models disposable and the fabric permanent.

### Isolation without Docker

Your claim: heavy sandboxing is unnecessary because
- the coder capsule **has no network**, and
- a **split watcher** observes it, and
- **multiple versions of each model** cross-check and task each other, and
- the **Gate** is the only door.

Offsets between the redundant models keep the system from failing as a whole.

### GPU keychain
Models are flattened after use so the GPU is freed — **max power draw
available to each model in turn**, rather than several resident at once.
On a 16 GB 5080 this is not an optimisation, it is a requirement.

### The fabric as designer
> *"The fabric will make custom designs to any part — create the creative piece
> to fit this into a unique design."*

The fabric is not just a container; it tailors the wrap per task. That is what
`tailor` is (already a live organ in your 14).

---

## Where each concept stands in code today

| Concept | Code status | Evidence |
|---|---|---|
| **Gate** | LIVE | `forge/fabric/gate.py`, 250L; +25 symbols pending recovery |
| **Capsule** | **MERGED TODAY** | `forge/fabric/capsule.py` — `Capsule`, `CapsuleStore`, `CapsuleError` |
| **Hub** | **MERGED TODAY** | `forge/fabric/hub.py` — routes tools → Capsules |
| **Tailor** | LIVE | `fabric.tailor.EmbeddedTailor` (seen in pytest output) |
| **Concoctinator** | LIVE, partial | `Concoctinator()` + `SequenceRunner` in `test_sequence.py` (1 failing) |
| **Keychain** | design only | `~/Forge/keychain/*.gz` in kernel review; not in `the-forge` |
| **Overseer** | pattern only | `HealthCheckMonitor` in kernel review (counters + sweep) |
| **Hopper** | design note | `03_BRONZE/prompts/NEXT_ISOLATION_HOPPER.md` |
| **Conduit** | named only | listed in README's 14 organs |
| **Commander** | **not in code** | described verbally only |
| **Wardrobe** | **not in code, not in any doc** | this conversation only |
| **Flatten** | **not in code, not in any doc** | this conversation only |
| **Baptize** | **not in code, not in any doc** | this conversation only |

**Six of your concepts have no written home.** That is what to fix first —
before any wipe, before any rebuild.

---

## Your "bare metal, snap-on" plan — this is correct

> *"small, only what's needed, bare metal forge on PC, locked in, then layered
> on top modular snap on/off so upgrades or new models don't matter."*

This is the right architecture, and it is *already* what the cabinet is
producing. Note what the recoveries look like:

- `hub.py` — 67L, registers external tool hubs, **explicitly never takes
  KERNEL role**
- `capsule.py` — 108L, `CapsuleStore` register → expand → run under Gate
- Together: snap-on tools that route through one door

The locked core is small. Everything else is a capsule. You are already
building the thing you described — you just could not see it because it was
scattered across 11 repos.

---

## What to pin before wiping (the honest list)

Ventoy offload + clean PC is fine **after** these exist in git:

1. **`FORGE_STATE.md`** in `~/the-forge` — LOCKED decisions, canonical
   dataclass shapes, organ status, what not to rebuild
2. **This concept map** — the vocabulary, committed
3. **The lifecycle spec** — spawn→suit→baptize→flatten→recycle, with the
   metadata-not-knowledge rule stated explicitly
4. **Finish the harvest** — `forge.py`, `ledger.py`, `validate_ledger.py`, then
   the other 10 repos
5. **`grades.csv` + `concepts.csv` + `06_ARCHIVE_RAW`** committed or offloaded

Then wipe. You will be restoring one repo and one vault.

---

## One honest caution on the isolation model

"Nothing can happen if the coder can't get online" is **necessary but not
sufficient**. No network blocks exfiltration and remote control — genuinely the
biggest risks. It does not block:

- filesystem damage inside whatever the capsule can reach
- resource exhaustion (a runaway loop eating the GPU/RAM)
- a poisoned artifact written into the wardrobe that a later capsule trusts

Your multi-model cross-check helps with the third. For the first two, the cheap
answer is not Docker — it is the same discipline you already use: the capsule
gets a **path allowlist** (exactly what the sorter's `assert_writable()` does)
and a **resource ceiling** (`systemd-run --scope -p MemoryMax= -p CPUQuota=`).
Both are ~10 lines, no daemon, no container.

That keeps your "no heavy sandbox" rule intact while closing the two holes the
network cut leaves open.
