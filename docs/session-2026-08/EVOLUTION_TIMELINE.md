# THE FORGE — EVOLUTION TIMELINE

The backstory and the tree. Every entry is dated from an artifact on disk, not
from memory. Where a date is uncertain it says so.

**The turn you named:** capsule + forge + overseer + sandbox stopped being
separate organs and became **fabric** — a substrate that animates and
strengthens whatever it touches. Everything before that turn is a component
list. Everything after is a material.

---

# FIRST — did `fabric.py` exist?

Ask the index. It searches by meaning, so it will find the file even if it was
named something else:

```bash
cd ~/FORGE_CABINET/_WORK/sorter
python3 oracle.py --config config.yaml -k 15 --sources ask \
  "which file defines the fabric itself as a living substance that animates and strengthens what it touches, rather than a directory of organs?"
```

And the direct check:

```bash
find ~ -name "fabric*.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null
grep -rl "class Fabric\|class Substance\|the living substance" ~/the-forge ~/Forge \
  "$HOME/Downloads/ForgeOS-Arch-Rev " ~/FORGE_REVIEW 2>/dev/null | grep -v /.venv/
```

**What is already known:** your live spine has `forge/fabric/` as a
**directory**, not a `fabric.py` module. No scan this session surfaced a
`fabric.py`. So one of three things is true — and the search above will say
which:

1. it exists in an unscanned corner (`Videos/`, `Music/`, `ALLFORGE/`, Ventoy)
2. it was renamed — the fabric became the *directory*, which is itself the
   architectural statement: fabric is not a module, it is the medium every
   organ lives in
3. it was never written — the turn happened in your thinking and in the
   directory layout, but no single file ever held it

Option 2 is the most likely and the most interesting. Collapsing
`forge/<organ>/` into `forge/fabric/*` is exactly what "it all became fabric"
looks like when expressed in a filesystem.

---

# THE TIMELINE

## ERA 0 · THE WARDROBE — *the original idea*
**No dated artifact. Reconstructed from your account.**

> *"Each piece of clothing you put on is like a memory — a text file, a task
> another model did, a scraped result. I was going to make a concoction of
> wardrobes where you could put on different parts of the data."*

Knowledge as garments. Mix and match what a model wears.

**Survives as:** `WrapStore`. The wardrobe was never lost — it was renamed and
built. 6 tests.

---

## ERA 1 · THE ORGAN LIST — *`forge/<organ>/`*
**Artifact: THE APP + FORGE — Complete User Manual (57pp)**

Paths: `forge/kernel/kernel.py`, `forge/arena/concoctinator.py`,
`forge/bridge/server.py`

Each organ its own package. `request_action()` is **async**. `Finding` is
`(verdict, reason, meta)`.

The App/Forge split appears here, with the **Glass Rule** stated for the first
time: *"The App holds NO logic, NO secrets, NO decisions... never receives
signing keys."*

**Ends when:** the organ directories collapse into `forge/fabric/`.

---

## ERA 2 · THE BACKEND LINEAGE — *`backend/kernel/`*
**Artifacts: FORGE KERNEL REVIEW (108pp) · `~/Forge/backend/`**

A parallel, fully async system. `KernelBus` (516L), `SubKernel` (508L) with
`SWARM_EOF` two-phase teardown, `CommitEngine`, `CapsuleManager`,
`HealthCheckMonitor`, `OutputHopper` with WAL.

Strong ideas here that still stand: per-subscriber queues with dead-letter
overflow — *"a stalled consumer never affects peers"* — and one isolated bus
per swarm.

**Never merged into the spine.** Different Event model, async everywhere.
Mine it, do not port it.

---

## ERA 3 · FORGE-NG — *`forge_ng/fabric/`*
**Artifacts: Concepts Guide · Whitesheet · Graded Master List**
**Dated: M4 review 2026-07 · Kimi review 2026-07-19**

**This is the turn.** Not a rename — a reconception. The organ list becomes a
**substance**.

> *"An omnipresent, sentient local AI fabric. Raw models are never used bare —
> the moment they touch the system they get wrapped, sealed, and gated,
> becoming the animated alien version."*

The vocabulary that survives to today is coined here: Gate as the one door ·
Wrap as the mold that IS the training · Overseer split Watcher/Commander ·
VectorConduit bonding to the NPU without fusing · Concoctinator as the proving
ground · **the Substance itself**.

Milestones M1–M6 complete. 119/119 tests green.

**Your live `gate.py` docstring still opens `"Forge-NG — FabricGate"`.** The
current spine *is* this era, moved.

---

## ERA 4 · THE FORMAL REVIEW — *the outside eyes*
**Artifacts: M4 Observer Review · Kimi Deep Dive (2026-07-19) ·
FORGE_ARCHITECTURE_REVIEW (W1–W14, R1–R12)**

Three independent reviews. What they produced:

- M4 raised 10 findings; **7 are now closed** (BehavioralJudge, AuditLedger,
  Caveat attenuation, `VectorMemory.burn()`, nonce, delimiter escape,
  property tests)
- Kimi: *"do NOT distro-hop — RTX 5080 issues are distro-agnostic"*
- Architecture review: **R4 specifies the capsule schema**, R1 the event
  contract, R3 a resource governor, R9 a capability registry
- **S8 defines the Arena**: blind review, cross-review, argument, merge, voting

R4's verdict on ordering — *"Phase 0. Nothing else can be built properly
without it"* — independently matches Build #1.

---

## ERA 5 · THE CURRENT SPINE — *`forge/fabric/`*
**Dated: today. 189 files, 9 failed / 125 passed.**

The collapse happened. Every organ now lives inside `fabric/` as a peer.

**This is the architectural statement made physical:** there is no `fabric.py`
because the fabric is not a module — it is the medium the organs live in.

Also this era: `Finding` becomes `(id, organ, severity:str, title, detail,
timestamp, metadata)` — the third shape. `authorize()` becomes **sync**,
deliberately. `capsule` becomes `fabric`.

---

## ERA 6 · THE HARVEST — *2026-08-15 → 08-19*

| Date | Event |
|---|---|
| 08-15 | Cabinet built. `forge-spine` scanned: 7 GOLD. |
| 08-15 | `hub.py` and `capsule.py` recovered and merged. |
| 08-17 | Kernel factory table fixed — **`/mint` was broken for 5 of 7 verbs in production.** Baseline 11 → 9. |
| 08-17 | Sandbox severity fix recovered from a forgotten `git stash`. |
| 08-17 | 44 Office docs extracted. ~1,900 files graded, 1,700 archived. |
| 08-17 | `FORGE_STATE.md` written, committed, pushed. |
| 08-18 | Vocabulary locked. Four "hoppers" resolved into distinct organs. |
| 08-18 | `salvage.py` — 8 files inventoried by local model. |
| 08-19 | **Oracle indexed 4,038 chunks across 970 files.** |
| 08-19 | Oracle confirms: **no pull-with-refusal queue has ever existed.** |

---

# THE NAMING TREE

One idea, six vocabularies. This is why five "hoppers" existed.

```
                    THE WARDROBE
                   (knowledge as garments)
                          │
                    ┌─────┴─────┐
                    │  CAPSULE  │  containment, shrink, offload
                    └─────┬─────┘
                          │
                    ┌─────┴─────┐
                    │  FABRIC   │  ← THE TURN
                    └─────┬─────┘   substance, not container
                          │         animates what it touches
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   forge/<organ>/    backend/kernel/    forge_ng/fabric/
   (App manual)      (Kernel Review)    (Concepts Guide)
        │                 │                 │
        └─────────────────┴────────┬────────┘
                                   │
                            forge/fabric/
                          (the live spine)
```

## The Rosetta table

| Concept | Era 0–1 | Era 2 | Era 3 | Era 4 | Today |
|---|---|---|---|---|---|
| knowledge store | Wardrobe | — | WrapStore | — | **WrapStore** |
| entry ritual | — | — | wrap-conform | — | **Baptism** |
| the proposer | — | — | Embedded Tailor | **Foundry** | **Tailor** |
| the arena | — | — | Concoctinator | Foundry sandbox | **Concoctinator** |
| multi-model review | — | peer_review | — | **S8 Arena** | *unbuilt* |
| work queue | — | OutputHopper | — | — | **Hopper** *(unbuilt)* |
| slot limiter | — | HopperQueue | — | Resource Governor (R3) | **SlotGovernor** |
| the wall | — | SubKernelBus | Splice `deaf=True` | plugin isolation | **Splice** |
| finding | `section_id/kind/severity:int` | — | `verdict/reason/meta` | — | `id/organ/severity:str/...` |
| capsule format | — | `.suit.zip` | — | **R4 schema** | *both halves, unmerged* |

**Foundry = Tailor.** Confirmed by the Oracle: *"an AI-powered engine that
never touches production and only submits proposals for human approval."* That
is the EmbeddedTailor's job description in a fourth vocabulary.

---

# THE THREE MOMENTS THAT MATTER

If this becomes a story, these are the beats.

**1. The turn — capsule becomes fabric.**
A container holds a thing. A substance *becomes* the thing. Once the fabric
could capsulise, sandbox, liquefy, or build a tool on demand, the architecture
stopped being a list of parts and started being a material with properties.
Everything downstream — render-up, flatten, twins, splice — follows from that
single reframing.

**2. The inversion — the Forge is the workshop, not the product.**
> *"That's to build what you want and then you encapsulate it. I could pull it
> off and put it back on, with or without the Forge."*

The moment the output became portable, the Forge stopped being the thing you
run and became the thing you build *with*. That makes the capsule format the
most important contract in the system — which R4 independently concluded.

**3. The diagnosis — it was never a code problem.**
Five hoppers, two conduits, three `Finding` shapes, four path roots. Not
carelessness. **Context death**: each session started blind and re-derived the
architecture slightly differently.

The proof is measurable — searching every artifact for the project's own
vocabulary found `wardrobe`, `flatten`, and `baptize` at **zero occurrences**,
while the things they named were already built and tested.

The fix was not a rewrite. It was `FORGE_STATE.md`, a locked vocabulary, and
an index that makes *"does this already exist?"* a four-second question.

---

# WHAT THIS TIMELINE IS FOR

When this is worth attention, the story is not *"I built an AI OS."* It is:

> **A system rebuilt four times, not because the code failed, but because the
> reasoning was never written down — and the fix was making memory
> structural rather than hoping for it.**

That is a more interesting claim than the architecture, and every artifact
needed to prove it is now indexed and dated.
