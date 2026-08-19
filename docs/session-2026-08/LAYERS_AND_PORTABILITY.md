# THE FORGE IS THE WORKSHOP, NOT THE PRODUCT

Captured 2026-08-17. This is the layering model and it changes the tree.

---

## The reframe

> *"That's to build what you want and then you encapsulate it. So now I can
> apply that onto just the PC and use it... I don't want that holding me back
> on the Forge."*

Every prior doc assumed the Forge is the thing you run. It isn't. **The Forge
is the thing you build things *with*.** Its output — an encapsulated capsule —
is portable and can run with the Forge, with a different set of organs, or
with no Forge at all.

```
   ┌───────────────────────────────────────────────────────────┐
   │ PRODUCTS  (portable, encapsulated, run anywhere)          │
   │   content-bot.capsule · kali-lab.capsule · scraper.capsule│
   │   ↑ built here, then lifted out                           │
   └───────────────────────────────────────────────────────────┘
   ┌───────────────────────────────────────────────────────────┐
   │ ORGANS  (snap on / snap off, per task)                    │
   │   tailor · concoctinator · wardrobe · hopper · sockets    │
   │   only what THIS task needs · flatten when done           │
   └───────────────────────────────────────────────────────────┘
   ┌───────────────────────────────────────────────────────────┐
   │ THE FORGE  (itself modular — removable)                   │
   │   gate · overseer/commander · splice · ledger             │
   └───────────────────────────────────────────────────────────┘
   ┌───────────────────────────────────────────────────────────┐
   │ LAYER −0  SKELETON · locked, pinned, always on            │
   │   + EMBEDDED MODEL (small, resident, the copilot)         │
   │   + NPU BEING (vectors, meta, cache — the alien substrate)│
   └───────────────────────────────────────────────────────────┘
                        BARE METAL PC
```

The skeleton is the only permanent thing. **Even the Forge is a layer you can
take off.**

---

## Two trust zones, two costs

> *"cryptographic hash for outside sockets... for inside the hopper and task
> within the PC, it could be much lighter"*

Correct, and it is the right instinct. The boundary is the machine.

| Zone | Threat | Mechanism |
|---|---|---|
| **Outside** — sockets, adapters, web, remote couplers | an attacker who can forge a request | **HMAC.** Full cryptographic verification. This is the Gate. |
| **Inside** — hopper routing, twin eligibility, organ signalling | no attacker; only mistakes | **Cheap hash / tag match.** Routing, not authorization. |

The reason this is safe: **routing is not authority.** A twin that somehow
pulled an ineligible task still cannot *do* anything with it — every
privileged action goes through the Gate regardless. So the inside hash only
has to prevent accidents, and can be a plain non-cryptographic tag.

That keeps the hot path fast and the perimeter hard. Note your own caution
about socket memory:

> *"it has memory of other connections out on the web. Now, that might be
> compromised."*

Right. A remembered socket is a stored credential. Treat reconnection as a
**fresh authorization**, not a resumption — the memory should hold *where and
how*, never a bearer token that grants access on replay.

---

## The embedded model — the resident copilot

> *"something that's on the GPU that takes up minimal space but still stays
> within the system... that would be like my copilot also. It would answer
> questions and help extract the data I needed or go find answers within the
> system."*

This is the piece that makes on-demand organs possible. It is always up, it is
small, and its job is **deciding what to bring up** — not doing the work.

| | |
|---|---|
| **Size** | 1–3B, quantized. Must leave the GPU free for the working model. |
| **Role** | interpret intent → decide which organs are needed → render them up → hand off → flatten after |
| **Also** | answers questions about the system, finds data in the cabinet, extracts what you ask for |
| **Never** | does the heavy work itself. It is the shell, not the tool. |

Closest existing analogue: an init system. It is `systemd` for the fabric —
tiny, resident, starts and stops units on demand.

**Two resident intelligences, deliberately different:**

- **NPU · the Being** — vectors, meta, cache, persistent memory. Outlives every
  capsule. Different hardware, different model, so its judgement is genuinely
  independent of anything running on the GPU.
- **GPU · the Embedded Copilot** — small, resident, decides what to render up.

They are not twins. That is the point.

---

## Organs on demand

> *"what if I'm just needing to do something simple? I don't need every organ
> running."*

The correct default is **nothing running**. A task arrives, the copilot decides
what it needs, those organs render up, the work happens, everything flattens.

And crucially:

> *"if I ran into something that required me to spawn something else or make a
> different organ, I'd have the room and power to do so"*

Because almost nothing is resident, there is always headroom to create an organ
that did not exist five minutes ago. **The system stays capable by staying
empty.**

---

## Portability — what encapsulation actually buys

> *"You could literally have one of those encapsulated models that you liked...
> and get rid of the Forge because you don't need all that."*

A capsule is a self-contained artifact: weights or a weight reference, vectors,
cache, metadata, its wrap, its socket definitions, its provenance. Which means:

- run it **on the Forge** — full oversight, gated, watched
- run it **with fewer organs** — lighter, faster
- run it **with no Forge** — just the PC and the capsule
- **shelve it** and bring it back later, knowing exactly where it left off

> *"it's not the model that I need, it's plugging the model back in so it knows
> where it's at to do these tasks again or to finish something."*

That sentence is the Keychain's actual job description. Not a metadata log —
**a resume point.**

Build it on the Forge *because* the Forge is where the guardrails are. Then
lift it out once it is proven.

---

## The honest note on "they can't cause trouble"

> *"they won't even have the pass or they won't even have arms. They can't even
> walk. They can't see. They're not a model. They're wrapped."*

This is right, and it is the strongest security property you have. Worth being
precise about what it does and does not cover:

**What the wrap prevents:** unauthorized action. A wrapped model with no egress
capability cannot reach the network no matter what it decides to do. There is
no pathway declared, so `DENY_PATH_NOT_DECLARED` fires before any crypto runs.
It has no arms.

**What it does not prevent:** misuse of a capability it *was* granted. If a
capsule is legitimately given file-write to a directory, it can write bad files
there. The wrap bounds the blast radius; it does not make the occupant wise.

That is exactly what the Overseer and the flatline path are for:

> *"models watching and commanding agents that start issues can be flatlined
> since the overseer never misses a thing"*

Wrap bounds what is *possible*. Overseer catches what is *unwise*. Flatten ends
it. Three layers, each doing one job — and none of them requires trusting the
model.

---

## What this changes

| | Before | Now |
|---|---|---|
| **Tree** | fixed organ list, all resident | −0 skeleton + copilot resident; everything else on demand |
| **Keychain** | metadata store | **resume point** — plug a capsule back in where it left off |
| **Gate** | all boundaries | **perimeter only**; inside routing is cheap |
| **Forge itself** | the system | **a removable layer** — products outlive it |
| **New piece** | — | **the embedded copilot** — small resident model that decides what renders up |
| **NPU** | "the observer" | the Being — persistent memory *and* the independent checker |

**A capsule format spec is now a first-class deliverable.** Portability is the
whole promise, and portability means a defined artifact: what goes in, how it
is sealed, how it declares its sockets, how it resumes. Without that spec,
"lift it out and run it elsewhere" stays an intention.
