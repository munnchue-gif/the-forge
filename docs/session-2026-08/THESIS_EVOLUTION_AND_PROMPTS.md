# THE THESIS — what changed, and the prompts to rebuild from it

Two things in one file:

- **Part A** — the thesis as it evolved, with each shift stated as
  *before → after → what it invalidates*. Use this to explain the design to
  any model, and to check whether a piece on disk belongs to an old era.
- **Part B** — the prompts. One to get the build layout back, then one per
  piece.

---

# PART A · THE THESIS, AND HOW IT MOVED

## The thesis in one paragraph

> The Forge is a **workshop, not a product**. It sits at layer −0 on bare
> metal, almost entirely empty. When a task arrives it *renders up* only the
> organs that task needs, pulling tools from a keychain and a boneyard,
> building or scraping what it lacks. AI models are **disposable tools** —
> wrapped on entry so they never hold control, used, then spliced for their
> valuable **snips** and ejected. What persists is never the model: it is the
> vectors, the metadata, the wraps, and the resume points. The output is a
> **capsule** — a portable, self-contained artifact that runs with the Forge,
> with fewer organs, or with no Forge at all. The system stays powerful by
> staying empty, and stays current by never depending on any single tool.

---

## The seven shifts

Each of these changed the design. Each invalidates code and documents written
before it.

---

### SHIFT 1 · Standing system → ground state

| | |
|---|---|
| **Before** | A fixed set of organs, all running. Boot the Forge, the fabric is alive, work arrives. |
| **After** | Layer −0 is nearly empty. A task arrives → copilot decides what is needed → organs render up → work → flatten → empty again. |
| **Why** | *"There's too much restriction and it just evaporates the model."* A permanently-running organ set is overhead that crowds out the thing you actually want to do. |
| **Invalidates** | Any design that assumes an organ is available without rendering it. Any boot sequence that starts everything. Documents that list "the organs" as a running set rather than a catalogue. |
| **Key consequence** | **The system stays capable by staying empty.** Because almost nothing is resident, there is always headroom to spawn an organ that did not exist five minutes ago. |

---

### SHIFT 2 · The Forge is the product → the Forge is the workshop

| | |
|---|---|
| **Before** | You build the Forge, then you run the Forge. It is the system. |
| **After** | You build **things** in the Forge, encapsulate them, and run them without it. The Forge is where the guardrails are *while building*. |
| **Why** | *"I don't want that holding me back on the Forge. That's going to be created on the Forge and managed... but when I make my other content creation bot, I encapsulate it. I could pull it off and put it back on, with or without the Forge."* |
| **Invalidates** | Any organ that assumes it will always be present at runtime. Any capsule that cannot run standalone. Tight coupling between a product and the fabric that built it. |
| **Key consequence** | **The capsule format is the most important contract in the system.** Portability is the whole promise; without a defined artifact it stays an intention. |

---

### SHIFT 3 · Keep the model → keep what the model made

| | |
|---|---|
| **Before** | Choose a good model, build around it, maintain it. |
| **After** | Pull the best current model as a tool. Splice out the **snips**. Eject the model. Keep vectors, cache, metadata, wraps. |
| **Why** | *"New tools are constantly coming... it's not designed to have AI as my main model."* A model chosen today is obsolete in a week; a system built around one inherits that decay. |
| **Invalidates** | Fine-tuning pipelines. Model-specific prompts baked into organs. Anything that treats weights as the asset. |
| **Key consequence** | **Splicing is load-bearing, not an optimisation.** The whole flatten-and-recycle loop depends on snips carrying history without bulk. If snips are weak, everything above them is weak. |
| **Exception** | A model that proves genuinely good gets **encapsulated as-is** — tar/zip, offloaded from GPU, brought back later with cache and vectors intact. Keep-path versus discard-path. |

---

### SHIFT 4 · Push dispatch → pull with eligibility

| | |
|---|---|
| **Before** | A scheduler assigns task → agent. |
| **After** | Nobody is assigned anything. Agents **take**. Tasks carry an eligibility hash; a twin can only see what it is eligible for. Release can be immediate, time-gated, dependency-gated, or **dissolving**. |
| **Why** | *"Some models aren't as good and they'll all be waiting on that one to finish. Mine doesn't work that way... I could have 50 models and that's not going to slow my system down."* |
| **Invalidates** | Every `hopper.py` on disk — all four are throttles or drains, not pull queues. Any design with a per-worker queue. |
| **Key consequence** | A stalled agent holds exactly one task. There is no queue behind a slow worker, because there is no queue *per* worker. |
| **Precision** | **"50 agents on one wrap," never "50 models."** 16 GB holds ~one 20B at Q4. Fifty twins sharing weights is achievable (continuous batching, per-twin adapters, shared-weight multiplexing). Fifty independent models is not. |

---

### SHIFT 5 · Two cooperating organs → one model, spliced and walled

| | |
|---|---|
| **Before** | Overseer watches; Commander acts. Two organs that agree to stay separate. |
| **After** | **One intelligence, split by the same splice primitive as the twins.** The wall is cryptographic deafness, not convention. |
| **Why** | *"They're the same model. They're just spliced into different versions of themselves."* |
| **Already built** | `SpliceCapability(region_id, mode, sections, deaf=True)` — *"sections get independent SubKernelBus namespaces so they are cryptographically deaf to each other's events."* Signed by the Gate. Isolation can never be silently removed. |
| **Key consequence** | The safety property becomes physical: the Watcher **cannot** reach the action path. Not "is not supposed to." |
| **Same primitive, three jobs** | twins · the Watcher/Commander wall · snip extraction. Splice is one mechanism doing all three. |

---

### SHIFT 6 · Reactive gate → proactive one-way verification

| | |
|---|---|
| **Before** | A request arrives, the gate evaluates it, the gate answers. |
| **After** | Pathways are **declared in advance**. At runtime the gate asks one question — *was this declared, and does the token verify?* It does not negotiate. |
| **Why** | *"If the commands are issued, then it's already got a path because everything's done ahead of time. It's not reactive. It's proactive."* |
| **Already built** | The recovered `gate.py` `PathwayRegistry`: an undeclared `kind` is denied **before any crypto runs** (`DENY_PATH_NOT_DECLARED`). +25 symbols, waiting to be ported. |
| **Key consequence** | Negotiation is where injection lives, because the requester influences the evaluation. A one-way gate removes that surface entirely — nothing the caller says changes the shape of the question. |
| **Answers your question** | The one-way gate is **not** a problem. It is the reason the system is safe. |

---

### SHIFT 7 · Uniform crypto → two trust zones

| | |
|---|---|
| **Before** | Everything HMAC-signed, everywhere. |
| **After** | **Outside** (sockets, web, couplers) → full HMAC, the Gate. **Inside** (hopper routing, twin eligibility, organ signalling) → cheap tag. |
| **Why** | *"Cryptographic hash for outside sockets... for inside the hopper and tasks within the PC, it could be much lighter."* |
| **Why it is safe** | **Routing is not authority.** A twin that somehow pulled an ineligible task still cannot *do* anything — every privileged action passes the Gate regardless. The inside tag only has to prevent accidents. |
| **Key consequence** | Hard perimeter, fast interior. The hot path stays light without weakening the boundary. |
| **Caution you raised yourself** | A remembered socket is a stored credential. It must hold *where and how*, **never a bearer token that grants access on replay.** Reconnection is a fresh authorization. |

---

## How to use Part A

Pick any file on disk and ask which era it belongs to:

- Does it assume organs are always running? → **pre-Shift 1**
- Does it assume the Forge is always present? → **pre-Shift 2**
- Is it built around a specific model? → **pre-Shift 3**
- Does it assign work to agents? → **pre-Shift 4**
- Are Watcher and Commander separate classes with no splice? → **pre-Shift 5**
- Does the gate evaluate requests rather than verify declarations? → **pre-Shift 6**
- Is everything HMAC'd uniformly? → **pre-Shift 7**

That is a mechanical test for whether recovered code is current or archaeology.

---

# PART B · THE PROMPTS

## PROMPT 0 — get the build layout back

**Use this first.** It does not write code. It produces the plan you will then
feed back in, piece by piece.

```text
You are the architect for THE FORGE, an AI-native OS on one Pop!_OS
workstation (RTX 5080 16GB, Intel Arrow Lake NPU 13 TOPS, 93GB RAM).

I am giving you a thesis that EVOLVED. Seven shifts changed the design, and
code exists on disk from every era. Your job is not to write code. Your job
is to produce the BUILD LAYOUT: the order, the dependencies, and one brief
per piece, so I can hand you those briefs one at a time afterwards.

=== THE THESIS ===

The Forge is a WORKSHOP, NOT A PRODUCT. It sits at layer -0 on bare metal,
almost entirely empty. When a task arrives it renders up only the organs
that task needs, pulling tools from a keychain and a boneyard, building or
scraping what it lacks. AI models are DISPOSABLE TOOLS - wrapped on entry
so they never hold control, used, then spliced for their valuable SNIPS
and ejected. What persists is never the model: it is the vectors, the
metadata, the wraps, and the resume points. The output is a CAPSULE - a
portable, self-contained artifact that runs with the Forge, with fewer
organs, or with no Forge at all. The system stays powerful by staying
empty, and stays current by never depending on any single tool.

=== THE SEVEN SHIFTS (each invalidates earlier work) ===

1. STANDING SYSTEM -> GROUND STATE
   Layer -0 is nearly empty. Organs render up per task, then flatten.
   Invalidates: anything assuming an organ is always available.
   Consequence: the system stays capable by staying empty.

2. PRODUCT -> WORKSHOP
   You build things IN the Forge, encapsulate them, run them WITHOUT it.
   Invalidates: any organ assuming it will be present at runtime.
   Consequence: the capsule format is the most important contract.

3. KEEP THE MODEL -> KEEP WHAT IT MADE
   Pull the best current model as a tool, splice out snips, eject it.
   Invalidates: fine-tuning, model-specific coupling, weights-as-asset.
   Consequence: splicing is load-bearing, not an optimisation.

4. PUSH DISPATCH -> PULL WITH ELIGIBILITY
   Nobody is assigned work. Agents take. Tasks carry an eligibility hash;
   a twin only sees what it is eligible for. Release conditions:
   immediate, time-gated, dependency-gated, dissolving.
   Invalidates: every hopper.py on this disk (all are throttles).
   Precision: "50 agents on ONE wrap," never "50 models." 16GB holds
   about one 20B at Q4.

5. TWO ORGANS -> ONE MODEL, SPLICED AND WALLED
   Overseer and Commander are one intelligence split by the same splice
   primitive as the twins. The wall is cryptographic deafness.
   Already built: SpliceCapability(region_id, mode, sections, deaf=True)
   gives sections independent SubKernelBus namespaces.
   Consequence: the Watcher CANNOT reach the action path. Physical, not
   conventional.

6. REACTIVE GATE -> PROACTIVE ONE-WAY VERIFICATION
   Pathways are declared in advance. At runtime the gate asks only: was
   this declared, and does the token verify? It does not negotiate.
   Already built (recovered, unmerged): PathwayRegistry denies an
   undeclared kind BEFORE any crypto runs. +25 symbols.
   Consequence: negotiation is where injection lives. Removing it removes
   the surface.

7. UNIFORM CRYPTO -> TWO TRUST ZONES
   Outside (sockets, web, couplers) = full HMAC, the Gate.
   Inside (hopper routing, twin eligibility) = cheap tag.
   Safe because ROUTING IS NOT AUTHORITY - a mis-routed task still cannot
   act without passing the Gate.
   Caution: a remembered socket holds WHERE and HOW, never a bearer token.
   Reconnection is a fresh authorization.

=== THE FIVE LAWS (break one and the work is wrong) ===

1. ONE DOOR. Every privileged action passes FabricGate.authorize().
2. DEAF BY DEFAULT. No wildcard subscribe. The Overseer's tap is the
   single privileged exception.
3. WATCHING != ACTING. Enforced by splice, not convention.
4. SYNC ON THE DECISION PATH. authorize() never awaits.
5. NOTHING THROWN AWAY. Reclaim, don't delete.

=== WHAT ALREADY EXISTS (do not rebuild) ===

Built and tested: Gate (10 tests, nonce + delimiter escape shipped),
Capabilities (7 verbs), Overseer+Commander (268L, 26 symbols),
Wrap/WrapStore (6 tests - this IS the wardrobe), Concoctinator (9 tests,
OBSERVE mode), EmbeddedTailor (7 tests), BehavioralJudge (8 tests - this
defines CLEAN), AuditLedger (8 tests, hash-chained), VectorMemory.burn(),
Caveat attenuation (9 tests), Capsule, Hub, Kernel, property tests.
Baseline: 9 failed / 125 passed.

Recovered but unmerged, on disk: gate.py PathwayRegistry (+25 symbols),
bus.py variant (383L vs live 95L, adds DLQ + two-phase teardown +
SubKernelBus), FabricSandbox (bwrap --unshare-all + systemd-run cgroups,
real namespace isolation without Docker), splicing_engine.py (261L,
intent-recorded-then-audited), socket_coupler.py (483L, unreviewed),
security_guardian.py (485L, unreviewed).

NOT BUILT: Hopper (as specced), Keychain, Toolchain, Boneyard, Copilot,
capsule format, Surface, sockets-with-memory.

=== THE GAPS - do NOT fill these ===

Seven questions have no answer on disk. Where a piece depends on one, say
so and restate the question precisely. Do not invent an answer.

G1. What IS a snip? Diff, embedding, structured claim, weight delta? This
    determines whether a later model genuinely picks up where the last
    left off, or only gets a summary.
G2. How does a capsule RESUME mid-task, not just reload?
G3. What makes a scraped repo trustworthy enough to become an organ?
    BehavioralJudge defines clean for model OUTPUT. Nothing defines clean
    for imported CODE.
G4. Twins share blind spots. Which decisions require a non-twin reviewer?
    (The NPU Being is a different model on different hardware.)
G5. Boneyard freshness - what triggers re-evaluation of a stale tool?
G6. What does the Copilot decide alone? If organ selection passes the
    Gate it is slow; if not, a 1-3B model has unilateral control over
    system composition.
G7. The capsule format itself - what goes in, how it seals, how sockets
    are declared, what happens when a capsule built with organ X runs
    without organ X.

=== YOUR OUTPUT ===

Produce a BUILD LAYOUT containing:

A. DEPENDENCY GRAPH. Which pieces must exist before which. Show it as a
   graph, not a list. Mark anything blocked on a GAP.

B. BUILD ORDER, with a one-line justification per position. Prefer
   ordering that produces something runnable early over ordering that is
   theoretically tidy.

C. ONE BRIEF PER PIECE. For each, exactly:
   - STAKES: what stays impossible without it
   - INVARIANTS: what cannot bend, and which of the five laws apply
   - EXISTING MATERIAL: what is already on disk to read, and whether to
     port it, mine it for ideas, or ignore it
   - OPEN: what you are deliberately leaving to the implementer
   - DONE: the test that proves it works
   - BLOCKED BY: which GAP, if any

D. WHERE THE DESIGN COULD GO FURTHER. Given the thesis, name capabilities
   that become possible but are not yet described. Be concrete and be
   honest about cost. I want the design pushed, not flattered.

E. WHAT YOU WOULD CUT. Anything in this thesis that adds cognitive weight
   without buying security or capability. An accurate objection is worth
   more than agreement.

Do NOT write implementation code. This is the map, not the build.
```

---

## PROMPT 1 — the per-piece template

After Prompt 0 returns the layout, use this for each piece. Fill the four
bracketed slots from that layout.

```text
Build [PIECE] for THE FORGE.

CONTEXT - read first, in this order:
  1. ~/the-forge/FORGE_STATE.md          the live contract
  2. THE_FORGE_MASTER_LAYOUT.md §2       the LOCKED vocabulary

THE VOCABULARY IN §2 IS FIXED. Do not invent a synonym for a term that
already exists. Five incompatible "hopper" implementations exist on this
disk because that rule did not. If you need a word that is not in §2, say
so and stop - do not coin one.

THE FIVE LAWS:
  1. ONE DOOR - every privileged action passes FabricGate.authorize()
  2. DEAF BY DEFAULT - no wildcard subscribe; Overseer's tap is the one
     privileged exception
  3. WATCHING != ACTING - enforced by splice, not convention
  4. SYNC ON THE DECISION PATH - authorize() never awaits
  5. NOTHING THROWN AWAY - reclaim, don't delete

RELEVANT SHIFTS: [paste the 2-3 shifts from Part A that govern this piece]

STAKES: [from the layout]
INVARIANTS: [from the layout]
EXISTING MATERIAL: [file paths, and port / mine / ignore]
OPEN - yours to decide, state your choice and why: [from the layout]
DONE: [the test]

HOUSE STYLE - established in gate.py, match it:
  stdlib-first; a dependency needs written justification
  @dataclass(frozen=True, slots=True) for anything signed
  canonical() returns a delimiter-escaped string; _esc() is mandatory -
    an unescaped | was a real signature-forgery vector in this codebase
  bounded everything: queues, ledgers, retries, caches
  fail closed: unknown severity ranks critical; undeclared pathway denies
    before crypto runs
  decisions are values, not exceptions: return a GateDecision, offer
    .enforce() for callers who want the raise

REQUIRED: a DESIGN THESIS docstring at the top stating what this replaces,
what problem it solves, what you tried and rejected, and which laws
constrain it. Read gate.py's block first - its "WHAT I FIXED FROM THE
ORIGINAL" section is why nobody has reintroduced a probabilistic replay
guard. This project was rebuilt four times because reasoning was never
written down. Code is regenerable; reasoning is not.

CONSTRAINT: baseline is 9 failed / 125 passed. Any other number after your
change means you caused it. Work on branch feat/[piece]. Show me the diff
before committing.

If you hit a question the brief does not answer, STOP and ask. Do not
guess and do not start a parallel implementation.
```

---

## How to run this

1. **Prompt 0** → get the layout, the dependency graph, and the briefs.
2. Read section **D** (where it could go further) and **E** (what it would
   cut) yourself. Those are the two places a model will tell you something
   you did not already know.
3. For each piece: **Prompt 1**, filled from the layout.
4. One branch, one piece, one commit. Baseline stays 9 failed until you move
   it deliberately.
5. Anything that hits a GAP comes back to you. **You answer it, then it goes
   in `FORGE_STATE.md §1` as a locked decision, with a date.**

That last step is the loop that stops the fifth rebuild.
