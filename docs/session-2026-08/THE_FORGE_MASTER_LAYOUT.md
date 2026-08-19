# THE FORGE — MASTER LAYOUT

**Locked 2026-08-17.** Every term below is fixed. When any document, repo, or
model disagrees with this file, this file wins. New words go in §2 or they do
not exist.

This is the whole system on one page: what it is, what it is made of, what
exists, what is missing, and who builds what next.

---

# 1 · THE THESIS

> **Do not buy the tool. Do not depend on the tool. Forge the tool, use it,
> keep what it taught you, and throw the tool away.**

The Forge is a workshop that builds capsules. A capsule is a portable,
self-contained artifact that can run **with** the Forge, with **fewer organs**,
or with **no Forge at all**. The workshop is not the product.

Everything else follows from four commitments:

| # | Commitment | Consequence |
|---|---|---|
| 1 | **Models are disposable tools** | Never build around one. Pull the best current model, keep what it produced, eject it. |
| 2 | **The system is empty by default** | Nothing runs between tasks. Capability is rendered up on demand and flattened after. |
| 3 | **Knowledge outlives the thing that made it** | Snips, vectors, wraps and metadata persist. Weights do not. |
| 4 | **Nothing acts without a pre-declared pathway** | The gate does not negotiate. It verifies a declaration. |

---

# 2 · THE LOCKED VOCABULARY

Every word here is final. This table is the anti-drift mechanism — five
different meanings of "hopper" happened because it did not exist.

## The substance

| Term | Meaning |
|---|---|
| **Fabric** | The living substance. It can capsulise, sandbox, liquefy, or build a specialised tool on demand. It wraps the model so the model never holds control. |
| **Wrap** | The mold that IS the training. A SHA-256 fingerprint of a conformation manifest. Identity, not behaviour. |
| **Baptism** | Wrap-conform. The moment a raw model becomes a wrapped occupant. No bypass. |
| **Capsule** | A sealed, portable artifact: wrap + vectors + cache + metadata + sockets + provenance. The Forge's output. |
| **Snip** | A spliced extract — the delta, fact, or vector that carries history without bulk. Formerly "Confetti Snip." |
| **Wardrobe** | `WrapStore`. The recycling yard. Knowledge-suits a later model can wear and pick up as if it had been there. |

## The organs

| Term | Meaning | Zone |
|---|---|---|
| **Skeleton** | Layer −0. Bare metal, locked, pinned, always on. | resident |
| **Copilot** | Small embedded model on GPU. Decides what to render up. Answers questions. Never does the heavy work. | resident |
| **Being** | The NPU intelligence. Vectors, meta, cache, persistent memory. Outlives every capsule. Independent checker. | resident |
| **Gate** | The one door. One-way: verifies a declaration, never negotiates. | resident |
| **Overseer** | Watcher half. Sees everything, cannot act. | resident |
| **Commander** | Acting half. Same model, spliced, walled. Acts only on findings, only through the Gate. | resident |
| **Ledger** | Hash-chained audit. Every decision inscribed. | resident |
| **Splice** | Splits one thing into deaf sections. Powers twins, the Watcher/Commander wall, and snip extraction. | resident |
| **Hopper** | Pull-with-refusal work queue. Eligibility-hashed tasks. Never blocks. | on demand |
| **Tailor** | Strips old wraps, drafts new shapes, fits them in the Concoctinator. | on demand |
| **Concoctinator** | Sandbox **and** recycler. Tests drafts; turns snips into wearable suits. | on demand |
| **Keychain** | The resume point. What to pull, in what shrunk form, to put a capsule back exactly where it left off. | on demand |
| **Sockets** | Remembered outside connections. Reconnect cheaply; re-authorize every time. | on demand |
| **Boneyard** | Where built tools rest between uses. The tool library. | storage |
| **Toolchain** | Finds, evaluates, converts, and rebuilds external repos into usable organs. | on demand |

## The operations

| Term | Meaning |
|---|---|
| **Render up** | Pull from keychain/boneyard, embed shrunk, spawn. |
| **Flatten** | Splice out snips → keep vectors/meta → revoke tokens → inscribe ledger → clear GPU → return slot. |
| **Encapsulate** | Seal a capsule for portability or shelving. The keep-it path, versus flatten's discard path. |
| **Flatline** | Emergency kill of a misbehaving agent. Overseer detects, Commander executes. |
| **Twin** | One wrap, spliced into N deaf agents. Deliberately heterogeneous. |

## Words that are now retired

`OutputDrain` (was hopper #1) · `SlotGovernor` (was hopper #2) ·
`VectorConduit` stays the NPU bond; the human interface is `Surface`, not
conduit.

---

# 3 · THE LAYER STACK

```
╔═══════════════════════════════════════════════════════════════════╗
║  PRODUCTS — portable, run anywhere, Forge optional                ║
║    content-bot.capsule · kali-lab.capsule · scraper.capsule       ║
╚═══════════════════════════════════════════════════════════════════╝
╔═══════════════════════════════════════════════════════════════════╗
║  ORGANS — snap on / snap off, only what this task needs           ║
║    hopper · tailor · concoctinator · keychain · sockets · toolchain║
╚═══════════════════════════════════════════════════════════════════╝
╔═══════════════════════════════════════════════════════════════════╗
║  THE FORGE — itself removable                                     ║
║    gate · overseer+commander · splice · ledger · bus              ║
╚═══════════════════════════════════════════════════════════════════╝
╔═══════════════════════════════════════════════════════════════════╗
║  LAYER −0 · SKELETON — locked, pinned, always on                  ║
║    GPU: copilot (1-3B)     NPU: the Being (vectors, meta, memory) ║
╚═══════════════════════════════════════════════════════════════════╝
                          BARE METAL PC
```

**The system stays capable by staying empty.** Because almost nothing is
resident, there is always headroom to spawn an organ that did not exist five
minutes ago.

---

# 4 · THE TASK LIFECYCLE

```
  intent
    │
    ▼
  SURFACE ─────────── shapes intent inbound, sanitises output outbound
    │
    ▼
  COPILOT ─────────── which organs does this need? what do we not have?
    │
    ├──► TOOLCHAIN ── missing capability? scrape / evaluate / convert / build
    │                 └─► new organ → BONEYARD
    ▼
  RENDER UP ───────── pull from keychain + boneyard, embed shrunk, spawn
    │
    ▼
  HOPPER ──────────── tasks posted with eligibility hash + release condition
    │                 twins PULL (never assigned, never blocked)
    ▼
  WORK ───────────── capsule forges · every privileged act through the GATE
    │                 OVERSEER watches all · COMMANDER acts on findings
    │                 misbehaviour → FLATLINE
    ▼
  SPLICE ─────────── extract snips: the history without the bulk
    │
    ├──► keep? ──► ENCAPSULATE ──► capsule (portable, resumable)
    │
    ▼
  FLATTEN ────────── revoke tokens · inscribe ledger · clear GPU · slot returned
    │
    ▼
  LAYER −0 ───────── empty again. copilot and Being still resident.
```

---

# 5 · THE TWO TRUST ZONES

| | Outside | Inside |
|---|---|---|
| **Where** | sockets, adapters, web, remote couplers | hopper routing, twin eligibility, organ signalling |
| **Threat** | an attacker who can forge a request | no attacker — only mistakes |
| **Mechanism** | **HMAC.** Full crypto. This is the Gate. | **Cheap tag.** Routing only. |
| **Why safe** | pre-declared pathways; undeclared kind denied before crypto runs | **routing is not authority** — a mis-routed task still cannot act without the Gate |

Socket memory holds *where and how*, **never a bearer token**. Reconnection is
a fresh authorization, not a resumption.

---

# 6 · WHAT EXISTS — the honest inventory

Baseline: **9 failed / 125 passed**, 189 files in the live spine.

## Built and tested — do not rebuild

| Organ | File | Evidence |
|---|---|---|
| Gate | `fabric/gate.py` | 10 tests. Nonce + delimiter escape shipped. |
| Capabilities | `fabric/capabilities.py` | 7 verbs, 6 tests. `_esc()` escaping. |
| Overseer + Commander | `fabric/overseer.py` | 268L, 26 symbols, 7 tests |
| Wrap / WrapStore | `fabric/wrap.py` | 6 tests. **This is the wardrobe.** |
| Concoctinator | `fabric/sandbox.py` | 9 tests. OBSERVE mode. |
| EmbeddedTailor | `fabric/tailor.py` | 7 tests. Built M4 — label was stale. |
| BehavioralJudge | `fabric/judge.py` | 8 tests. **This defines CLEAN.** |
| AuditLedger | `fabric/ledger.py` | 8 tests. Hash-chained. |
| VectorMemory.burn() | | 3 tests. Tainted-vector purge. |
| Caveat / attenuation | | 9 tests. Macaroon chain. |
| SubstanceBus | `fabric/bus.py` | 95L — **weak, see §7** |
| Capsule / Hub | `fabric/capsule.py`, `hub.py` | merged 2026-08-15 |
| Kernel | `fabric/kernel.py` | factory table fixed 2026-08-17 |
| Property tests | `test_properties.py` | Hypothesis, 5 tests |

## Recovered, unmerged — on disk, graded, waiting

| Piece | Size | Verdict |
|---|---|---|
| `gate.py` PathwayRegistry | +25 symbols | CANDIDATE_SUPERSET — **port, preserve the prose** |
| `bus.py` variant | 383L vs 95L | DIVERGED, +21 symbols — DLQ, two-phase teardown, SubKernelBus |
| `FabricSandbox` | bwrap + systemd-run | **the isolation mechanism** — real namespaces, no Docker |
| `splicing_engine.py` | 261L | intent-recorded-then-audited. Strong idea, flawed code. |
| `socket_coupler.py` | 483L | unreviewed. #1 attack surface. |
| `security_guardian.py` | 485L | unreviewed. |
| `test_judge.py` | 74L vs 24L | CANDIDATE_SUPERSET, +6 symbols |
| Four `hopper.py` files | 114–278L | none match spec — all throttles |

## Not built

Hopper (as specced) · Keychain · Toolchain · Boneyard · Copilot ·
Capsule format · Surface · Sockets-with-memory

---

# 7 · THE GAPS — where you need to invent

These are the places where nothing on disk answers the question, and where a
creative mechanism is genuinely required. **This is the list you asked for.**

### GAP 1 · How does a snip carry history without the bulk?
Splicing is the load-bearing mechanism of the entire design — it is what makes
flatten-and-recycle possible. But *what a snip actually is* has never been
defined. A diff? An embedding? A structured claim? A weight delta?

**Why it needs you:** the answer determines whether a later model can genuinely
"pick up as if it had been there," or only gets a summary. That is a design
judgement about what knowledge *is*, not an implementation detail.

### GAP 2 · How does a capsule resume?
> *"it's not the model that I need, it's plugging the model back in so it knows
> where it's at."*

A capsule holds vectors, cache, metadata. But resumption means restoring
*state mid-task* — what it was doing, what it had decided, what it was about
to do next. No existing artifact defines this.

**Why it needs you:** this is the difference between "reload the model" and
"continue the thought."

### GAP 3 · What makes a scraped repo trustworthy enough to become an organ?
The toolchain scrapes the web for the best current tool and converts it. That
is the thesis. It is also arbitrary third-party code entering your system.

**Why it needs you:** `BehavioralJudge` defines clean for *model output*.
Nothing defines clean for *imported code*. The Forge's greatest strength is
also its widest door.

### GAP 4 · Twins share blind spots
Fifty twins from one wrap share failure modes. A twin watching a twin will
confidently agree on a wrong answer.

**Partial answer already in your design:** the NPU Being is a different model
on different hardware — genuinely independent. **The gap:** which decisions
require independent review, and which are fine with twin consensus?

### GAP 5 · Boneyard freshness
Tools go to the boneyard. Tools rot — a repo good in August is obsolete in
October.

**Why it needs you:** what triggers re-evaluation? Age? Failure? A scheduled
sweep? Rebuilding on every use is safe but slow; caching is fast but stale.

### GAP 6 · What does the Copilot decide alone?
The copilot chooses which organs render up. That is a privileged decision made
by a small model.

**Why it needs you:** does organ selection pass the Gate? If yes, the copilot
is slow. If no, a 1–3B model has unilateral control over system composition.

### GAP 7 · The capsule format itself
Portability is the whole promise. Nothing defines the artifact: what goes in,
how it seals, how sockets are declared, how provenance travels, what happens
when a capsule built with organ X runs without organ X.

**Why it needs you:** this is the contract everything else conforms to.

---

# 8 · BUILD ORDER

Each is one branch, one organ, one commit. Baseline stays **9 failed** until
you deliberately move it.

| # | Build | Why now | Depends on |
|---|---|---|---|
| 1 | **Capsule format spec** | the contract everything conforms to | GAP 7 |
| 2 | **Hopper** | signed door onto an empty room | — |
| 3 | **Bus hardening** | two reviewers flagged it; a stalled consumer degrades the fabric | recovered 383L variant |
| 4 | **Gate PathwayRegistry** | the pre-declaration the proactive model rests on | recovered +25 |
| 5 | **Keychain** | 16GB makes flatten mandatory; needs a resume point | GAP 2, format spec |
| 6 | **FabricSandbox port** | closes M4 finding B (stripper isolation) | recovered bwrap code |
| 7 | **Copilot** | makes on-demand organs real | GAP 6 |
| 8 | **Splice / snips** | the recycling mechanism | GAP 1 |
| 9 | **Toolchain + Boneyard** | the thesis, operationalised | GAP 3, GAP 5 |
| 10 | **Sockets with memory** | outside world, re-authorized | — |
| 11 | **Guardian / Coupler review** | LOCKED to last — #1 attack surface | — |

---

# 9 · THE PROMPT — hand this to the coder

```text
You are building THE FORGE, an AI-native OS for one Pop!_OS workstation
(RTX 5080 16GB, Intel Arrow Lake NPU 13 TOPS, 93GB RAM).

READ FIRST, IN ORDER:
  1. ~/the-forge/FORGE_STATE.md        the live contract
  2. THE_FORGE_MASTER_LAYOUT.md §2     the locked vocabulary

THE VOCABULARY IN §2 IS FIXED. Do not invent a synonym for a term that
already exists. Five incompatible "hopper" implementations exist on this
disk because that rule did not. If you need a word that is not in §2, say
so and stop — do not coin one.

THE THESIS
Do not buy the tool. Forge it, use it, keep what it taught you, throw it
away. The Forge is a workshop that produces portable capsules; it is not
the product. Its output must run with the Forge, with fewer organs, or
with no Forge at all.

THE FIVE LAWS — break one and the work is wrong regardless of quality:
  1. ONE DOOR. Every privileged action passes FabricGate.authorize().
     New powers implement Capability; they never invent an entry.
  2. DEAF BY DEFAULT. No wildcard subscribe. The Overseer's tap is the
     single privileged exception.
  3. WATCHING != ACTING. The Watcher cannot act; the Commander cannot
     watch. They are one model, spliced, cryptographically walled.
  4. SYNC ON THE DECISION PATH. authorize() never awaits.
  5. NOTHING THROWN AWAY. Reclaim, don't delete. Wraps and vectors
     outlive the model.

THE SHAPE
The system is EMPTY by default. Layer -0 holds the skeleton, a small
resident copilot on GPU, and the Being on NPU. A task arrives, the copilot
decides what is needed, organs render up, work happens, snips are spliced
out, everything flattens. Robustness is a temporary state.

TWO TRUST ZONES
  Outside (sockets, web, couplers) -> HMAC, full crypto, the Gate.
  Inside (hopper routing, twin eligibility) -> cheap tag, routing only.
  Safe because routing is not authority: a mis-routed task still cannot
  act without passing the Gate.

HOUSE STYLE — match it, it is established in gate.py:
  stdlib-first; a dependency needs written justification
  @dataclass(frozen=True, slots=True) for anything signed
  canonical() returns a delimiter-escaped string; _esc() is mandatory
    (an unescaped | was a real signature-forgery vector here)
  bounded everything: queues, ledgers, retries, caches
  fail closed: unknown severity ranks critical; undeclared pathway denies
    before crypto runs
  decisions are values, not exceptions: return a GateDecision, offer
    .enforce() for callers who want the raise

THE DELIVERABLE THAT OUTLIVES YOU
Every organ carries a DESIGN THESIS docstring: what it replaces, what
problem it solves, what was tried and rejected, which laws constrain it.
Read gate.py's block before writing yours; its "WHAT I FIXED FROM THE
ORIGINAL" section is why nobody has reintroduced a probabilistic replay
guard. This project was rebuilt four times because reasoning was never
written down. Code is regenerable. Reasoning is not.

YOUR TASK
Take §8 of THE_FORGE_MASTER_LAYOUT.md and produce ONE brief per numbered
item. Each brief must state:
  - stakes: what breaks or stays impossible without it
  - invariants: what cannot bend, and which of the five laws apply
  - open: what you are deliberately leaving to the implementer's judgement
  - done: the test that proves it works
  - existing material: what is already on disk to read first, and whether
    it should be ported, mined for ideas, or ignored

Do not write implementation code in the briefs. Where §7 marks a GAP, do
not fill it — restate the question precisely enough that a human can answer
it, and say what depends on the answer.

Baseline is 9 failed / 125 passed. Any other number means you caused it.
```

---

# 10 · THE RULE

Five hoppers, two conduits, three `Finding` shapes, four path roots — none of
it happened because the code was bad. It happened because **the reasoning was
never written down**, so every fresh session re-derived it slightly
differently.

`FORGE_STATE.md` is read first and written last, enforced by a pre-commit hook.
§2 of this document is the vocabulary. A new word goes in the table or it does
not exist.

Instructions get skipped. Hooks do not.
