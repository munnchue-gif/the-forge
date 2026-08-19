# FORGE — SESSION HANDOFF

**Paste this whole file as the first message of any new chat.** It is
self-contained. Nothing before it is needed.

Last updated: 2026-08-17 · Status: frontier answers drafted, 6 corrections
pending, sections 3–7 incomplete.

---

# 0 · HOW TO USE THIS FILE

This is a **loop**, not a document. Each cycle:

```
  1. pick ONE section from §7 WORK QUEUE
  2. paste this file + that section's brief into a fresh chat
  3. get the output
  4. review it against §5 LAWS and §6 CORRECTIONS
  5. fix what is wrong, keep what is good
  6. update §7 (mark done, add new findings)
  7. repeat
```

**Rule:** update §7 before ending any session. That single habit is what
prevents starting over. Everything else here is stable reference.

---

# 1 · THE THESIS

> Do not buy the tool. Do not depend on the tool. Forge the tool, use it, keep
> what it taught you, and throw the tool away.

**THE FORGE IS A WORKSHOP, NOT A PRODUCT.**

It sits at the lowest layer of one machine, almost entirely empty. A task
arrives → it renders up only what that task needs → work happens → what was
learned is extracted → everything flattens → empty again.

AI models are **disposable tools**: wrapped on entry so they never hold
control, used, stripped for what they produced, ejected. What persists is never
the model — it is vectors, metadata, extracts, and resume points.

The output is a **capsule**: a portable artifact that runs inside the Forge,
with fewer organs, or with no Forge at all. You build a thing in the workshop,
then carry the thing out.

**Four commitments:**

1. **Models are disposable tools.** Obsolete in a month. Never build around one.
2. **The system is empty by default.** It stays capable *because* it stays empty
   — there is always headroom to spawn what did not exist five minutes ago.
3. **Knowledge outlives its maker.** A later model wears what an earlier model
   learned and picks up as if it had been there.
4. **Nothing acts without a pre-declared pathway.** Proactive, not reactive.
   Runtime asks *was this declared and does it verify* — never *should I allow*.

---

# 2 · THE MACHINE

```
GPU   RTX 5080, 16 GB VRAM     the workhorse — HARDEST constraint
                               ~one 20B model at Q4. Everything follows.
NPU   Arrow Lake, 13 TOPS      different silicon, different model
                               → genuinely independent judgement
CPU   Core Ultra 9 275HX
RAM   93 GB system             SOFTEST constraint. Be extravagant.
                               Separate pool from VRAM — do not confuse.
OS    Pop!_OS, recent kernel   no cloud, ever
```

---

# 3 · THE SHAPE

```
┌──────────────────────────────────────────────────┐
│ PRODUCTS — portable capsules, Forge optional     │
├──────────────────────────────────────────────────┤
│ ORGANS — snap on/off, only what this task needs  │
├──────────────────────────────────────────────────┤
│ THE FORGE — itself a removable layer             │
├──────────────────────────────────────────────────┤
│ GROUND — locked, always on:                      │
│   GPU: small resident model (the Copilot)        │
│   NPU: persistent memory (the Being)             │
└──────────────────────────────────────────────────┘
                  BARE METAL PC
```

Lifecycle: `intent → interpret → render up → post work → agents pull → work →
extract → keep or seal → flatten → empty`

**Robustness is a temporary state. Anything still running when the task is done
is a bug.**

---

# 4 · THE LOCKED VOCABULARY

A new word goes in this table or it does not exist. Five incompatible "hopper"
implementations exist on disk because this table did not.

### Substance
| Term | Meaning |
|---|---|
| **Fabric** | The living substance. Encapsulates, sandboxes, liquefies, builds tools on demand. Wraps the model so it never holds control. |
| **Wrap** | The mold that IS the training. SHA-256 fingerprint of a conformation manifest. Identity, not behaviour. |
| **Baptism** | Wrap-conform. The moment a raw model becomes wrapped. No bypass exists. |
| **Capsule** | Sealed portable artifact: wrap + vectors + cache + metadata + sockets + provenance. |
| **Snip** | A spliced extract — delta, fact, or vector carrying history without bulk. |
| **Wardrobe** | WrapStore. Knowledge-suits a later model wears. |

### Organs
| Term | Meaning | Zone |
|---|---|---|
| **Skeleton** | Layer −0. Bare metal, pinned. | resident |
| **Copilot** | Small GPU model. Decides what renders up. Never does heavy work. | resident |
| **Being** | NPU intelligence. Vectors, memory, independent checker. | resident |
| **Gate** | The one door. Verifies declarations, never negotiates. | resident |
| **Overseer** | Watcher half. Sees everything, cannot act. | resident |
| **Commander** | Acting half. Same model, spliced, walled. | resident |
| **Ledger** | Hash-chained audit. | resident |
| **Splice** | Splits into deaf sections. Powers twins, the wall, extraction. | resident |
| **Hopper** | Pull-with-refusal work queue. Eligibility-hashed. Never blocks. | on demand |
| **Tailor** | Strips old wraps, drafts new shapes. | on demand |
| **Concoctinator** | Sandbox **and** recycler. Tests drafts; turns snips into suits. | on demand |
| **Keychain** | The resume point. Continue the thought, not reload the model. | on demand |
| **Sockets** | Remembered connections. Cheap reconnect, re-authorized every time. | on demand |
| **Toolchain** | Finds, evaluates, converts external repos into organs. | on demand |
| **Boneyard** | Where built tools rest. The library. | storage |
| **Surface** | Human ↔ system interface. Shapes intent in, sanitises out. | on demand |

### Operations
| Term | Meaning |
|---|---|
| **Render up** | Pull from keychain/boneyard, embed shrunk, spawn. |
| **Flatten** | Extract snips → keep vectors → revoke tokens → inscribe → clear GPU → return slot. |
| **Encapsulate** | Seal for portability. The keep-path vs flatten's discard-path. |
| **Flatline** | Emergency kill. Overseer detects, Commander executes. |
| **Twin** | One wrap, spliced into N deaf agents. Deliberately unequal. |

**Retired:** `OutputDrain` (was hopper #1) · `SlotGovernor` (was hopper #2) ·
`VectorConduit` = the NPU bond only; the human interface is **Surface**.

---

# 5 · THE FIVE LAWS

Physics, not preference. How you achieve them is open. That they hold is not.

1. **ONE DOOR** — every privileged action passes `FabricGate.authorize()`. New
   powers implement `Capability`; they never invent an entry. *If there are two
   doors, there is no door.*
2. **DEAF BY DEFAULT** — no wildcard subscribe. Isolation is structural, not
   conventional. The Overseer's tap is the single privileged exception.
3. **WATCHING ≠ ACTING** — the Watcher cannot act; the Commander cannot watch.
   Enforced by splice, so it is physical, not a promise.
4. **SYNC ON THE DECISION PATH** — `authorize()` never awaits. Async freely
   elsewhere.
5. **NOTHING THROWN AWAY** — reclaim, don't delete.

**Plus: FAIL CLOSED.** Unknown severity ranks critical. Undeclared pathway
denies *before* expensive checks. Unparseable input is a refusal, not a default.

### Two trust zones
| | Outside (sockets, web, remote) | Inside (routing, eligibility) |
|---|---|---|
| Threat | real adversary forging requests | no adversary, only mistakes |
| Mechanism | full HMAC — the Gate | cheap tag |

Safe because **routing is not authority** — a mis-routed task still cannot act
without the Gate. Hard perimeter, fast interior.

A remembered socket holds *where and how*, **never a bearer token**.
Reconnection is a fresh authorization.

---

# 6 · LESSONS ALREADY PAID FOR

Traps found expensively. Free to whoever reads this.

- A signed string built by joining fields is **forgeable if the delimiter is
  not escaped**. A crafted name shifts the boundary. Escape every field.
- A replay guard that evicts probabilistically has **false negatives** — a
  vulnerability, full stop. Make it exact, bound it by time not capacity.
- Two legitimate identical actions must both succeed. A per-mint **nonce** bound
  into the signature fixes this without weakening anything.
- A fingerprint **identifies**; it does not constrain behaviour. Identity and
  authority are different things.
- A queue that **drops silently** under load hides its own failure.
  Backpressure must be counted, logged, inspectable.
- Persistent memory that survives a model's removal also survives its
  **corruption**. There must be a burn operation.
- **Never** decide security by pattern-matching model output
  (`if "APPROVED" in text`). Trivially spoofable.

---

# 7 · WORK QUEUE — where we left off

## 7a · CORRECTIONS PENDING (do these first — they are small and known)

| # | Where | Fix | Why |
|---|---|---|---|
| C1 | `frontiers.ts` F5 | `S = (days/halflife) × (1+failure) × **max(1.0, novelty)**` | Multiplicative formula: `novelty=0` → S=0. A 6-month-old security organ failing 40% in a quiet domain scores **zero**. |
| C2 | `frontiers.ts` F4 | **Delete** the cost item about "first 3 exercises bypass NPU" | Contradicts its own matrix — a pathway under 3 uses IS high-novelty → quadrant 4 → gets both walls. The design is safer than its cost note claims. |
| C3 | `frontiers.ts` F1 | Add **re-embed on ingestion**: keep `origin_embedding` for provenance; re-embed `assertion` text in the reader's space and index that | Anchoring vectors to the producing model degrades retrieval in the *primary* use case — a different model wearing the snip. |
| C4 | `frontiers.ts` F7 | Split: `capsule_id = hash(core_manifest)` immutable; `provenance_head = hash(entry_n ‖ head_{n-1})` append-only; `seal_signature = sign(capsule_id ‖ provenance_head)`. **Add `spec_version`.** | Hashing the full manifest *including* growing provenance makes the ID change every time anything touches it. Identity must be stable. |
| C5 | F3 + F6 | State explicitly: **Toolchain may BUILD automatically** (boneyard organs are inert); **palette may only GROW by human review** | F3 says automated admission; F6 says "does not self-extend." Different gates — self-extend the *library*, hand-authorize the *authority*. |
| C6 | `App.tsx` | Wire `TrustZonesSection` (exists, never imported). Write or remove `cuts` (in `SECTION_IDS`, no component). | Dead nav link; orphaned section. |
| C7 | `seed.ts` / `schema.ts` | `notes` needs a unique constraint (`onConflictDoNothing` is a no-op without one → 3 new rows per request). Make `category`/`refType` enums. Add FK on `refId`. `updatedAt` needs `.$onUpdate()`. Move `seed()` out of the request path. | Violates **bounded everything**. |

## 7b · SECTIONS INCOMPLETE

`architecture.ts` (10,695c) · `buildorder.ts` (6,341c) · `further.ts` (10,276c)
— drafted but unreviewed. `cuts` — missing entirely.

## 7c · BUILD ORDER

| # | Piece | Blocked by | Status |
|---|---|---|---|
| 1 | **Capsule format spec** | F7 (answered, needs C4) | spec drafted |
| 2 | **Hopper** | nothing | not started |
| 3 | **Bus hardening** | nothing | not started |
| 4 | **Gate PathwayRegistry** | nothing | recovered code waiting |
| 5 | **Keychain** | F2 (answered) + #1 | not started |
| 6 | **FabricSandbox port** | nothing | recovered code waiting |
| 7 | **Copilot** | F6 (answered, needs C5) | not started |
| 8 | **Splice / snips** | F1 (answered, needs C3) | not started |
| 9 | **Toolchain + Boneyard** | F3 (answered) + F5 (needs C1) | not started |
| 10 | **Sockets with memory** | #1 | not started |
| 11 | **Guardian / Coupler review** | all prior | LOCKED to last |

---

# 8 · WHAT ALREADY EXISTS

**Baseline: 9 failed / 125 passed, 189 files.** Any other number after a change
means you caused it.

### Built and tested — DO NOT REBUILD
`gate.py` (10 tests, nonce + delimiter escape) · `capabilities.py` (7 verbs) ·
`overseer.py` (268L, Watcher+Commander) · `wrap.py` (6 tests — **this is the
wardrobe**) · `sandbox.py` (9 tests, OBSERVE mode — **the Concoctinator**) ·
`tailor.py` (7 tests — built at M4, the "missing organ" label was stale) ·
`judge.py` (8 tests — **this defines CLEAN**) · `ledger.py` (8 tests,
hash-chained) · `VectorMemory.burn()` (3 tests) · Caveat attenuation (9 tests) ·
`bus.py` (95L — **weak, see below**) · `capsule.py` + `hub.py` (merged
2026-08-15) · `kernel.py` (factory table fixed 2026-08-17) ·
`test_properties.py` (Hypothesis, 5 tests)

### Recovered, on disk, unmerged
| Piece | Verdict |
|---|---|
| `gate.py` PathwayRegistry | +25 symbols, CANDIDATE_SUPERSET — **port it, preserve the prose** |
| `bus.py` variant (383L vs 95L) | +21 symbols: DLQ, two-phase teardown, SubKernelBus |
| `FabricSandbox` | bwrap `--unshare-all` + systemd-run cgroups — **real isolation, no Docker** |
| `splicing_engine.py` (261L) | intent-recorded-then-audited. Strong idea, **flawed code** (mock inference, string-match security) |
| `socket_coupler.py` (483L) | unreviewed, #1 attack surface |
| `security_guardian.py` (485L) | unreviewed |
| `test_judge.py` (74L vs 24L) | +6 symbols |

### Known broken
1. `bind/test_bind.py` — 5 tests pinned to an old `Finding` shape. **Stale
   tests, not broken code.** `severity` is now a string enum; `judge()` lost an
   argument.
2. `test_sequence.py` — 1 test rolls back where it should complete.

### Locked decisions
- `authorize()` is **SYNC**, never async
- Canonical root is `forge/fabric/` (supersedes `forge/<organ>/`,
  `backend/kernel/`, `forge_ng/fabric/`)
- **Do NOT distro-hop** — RTX 5080 issues are distro-agnostic
- **seL4 is a future substrate, not a task** — no Linux userland means no
  Ollama/CUDA/OpenVINO
- **Intel SGX is unavailable** — deprecated on consumer CPUs; Xeon only
- Couplers built **LAST** — #1 attack surface
- NPU path is **OpenVINO GenAI only**

---

# 9 · FRONTIER ANSWERS (current, with corrections applied)

**F1 · What is an extract?** Typed claim bundle:
`{claim_type, assertion, confidence_interval, evidence_refs[], embedding_vec,
model_of_origin, task_id, snip_id, provenance_hash}`. `claim_type` ∈ FACT |
DECISION | PREFERENCE | UNCERTAINTY | REFUSAL | STRUCTURAL. **UNCERTAINTY and
REFUSAL are first-class — ignorance is information.** *+C3: re-embed on
ingestion.*

**F2 · How does a capsule resume?** Continuation manifest with five fields:
PENDING_WORK, DECIDED_PATHWAYS, VECTOR_CONTEXT (snip IDs not vectors),
SOCKET_TOPOLOGY, CONTINUATION_INTENT. Snapshots at **gate checkpoints only**.
**Pathways are re-declared, not replayed** — replaying would bypass
verification.

**F3 · What makes found code trustworthy?** Five stages: namespace isolation →
capability declaration (seccomp-enforced) → behavioural fingerprint →
provenance burn → gate declaration. *"There is no stage 6 that makes code
trusted. Trust is a property of the gate's declaration, not the code's
content."* *+C5.*

**F4 · Who checks the checkers?** Classify by **irreversibility × novelty**.
High irreversibility → NPU synchronous sign-off, always. High+high → NPU +
mandatory Overseer finding. *"The NPU's value is independence, not
intelligence."* *+C2: delete the phantom cost item.*

**F5 · When does a tool go stale?** `S = (days/halflife) × (1+failure_rate) ×
novelty_pressure`. Halflife per category: security 7d, general 30d, stable 90d.
Nightly sweep quarantines S>2.0, suspends S>4.0. *+C1: floor the novelty
multiplier.*

**F6 · What may the resident model decide alone?** **Pre-approved palette** of
declaration templates. The Copilot fills in parameters; it cannot generate new
pathway shapes. Novel needs → capability request to a human queue. *"Autonomy
bounded not by trust in the model but by the structure of its choices."* *+C5.*

**F7 · What is a capsule?** Content-addressed archive, signed JSON manifest.
Degradation policy per organ: **REQUIRED | DEGRADE | SKIP**. Portability modes:
FULL | TETHERED | SKELETON. *+C4: split ID from provenance, add
`spec_version`.*

---

# 10 · THE PER-SECTION PROMPT

Fill the brackets from §7c and paste after this file.

```text
Continue THE FORGE. The handoff above is complete context.

WORK ON: [ONE section from §7]

BEFORE YOU START:
  - §4 vocabulary is LOCKED. A word not in that table does not exist. If you
    need a new concept, name it explicitly and say why — never coin an
    accidental synonym.
  - §5 laws are physics. How you satisfy them is yours; that they hold is not.
  - §6 lessons are free — do not rediscover them.
  - §8 lists what exists. Do not rebuild it.

DELIVER:
  - the design, with your reasoning
  - honest cost for every choice
  - what you deliberately left open, and why
  - the test that proves it works
  - what you would CUT — an accurate objection beats agreement.
    But if you propose removing something that implements a §5 law, show
    what replaces it. The law holds either way.

CONSTRAINT: baseline is 9 failed / 125 passed. Design first, code second,
and only where the design is settled.

If you hit a question this file does not answer, STOP and ask. Do not guess,
and do not start a parallel implementation. That is how five incompatible
"hopper" files came to exist.
```

---

# 11 · THE RULE

Five hoppers. Two conduits. Three `Finding` shapes. Four path roots. None of it
happened because the code was bad — **it happened because the reasoning was
never written down**, so every fresh session re-derived it slightly
differently.

This file is the fix. Update §7 before you stop.

**Code is regenerable. Reasoning is not.**
