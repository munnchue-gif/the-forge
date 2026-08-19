# THE FORGE — the actual design, in your words

Written from your description, 2026-08-17. This supersedes the layer-cake
reading in earlier docs. Where prior documents conflict with this, **this
wins** — those were reconstructions from artifacts; this is the intent.

---

## The correction that matters

Earlier docs treated the Forge as a **fixed set of organs that are always
running**. That is wrong, and you named the failure exactly:

> *"there's too much restriction and it just evaporates the model, which is
> the original idea."*

The Forge is not a standing system. It is a **ground state that materialises
what it needs, does the work, and collapses back to nothing.**

```
        ┌──────────────────────────────────────────────┐
        │  LAYER −0 · BARE METAL SKELETON              │
        │  always present · almost nothing running     │
        └────────────────────┬─────────────────────────┘
                             │ a task arrives
                             ▼
        ┌──────────────────────────────────────────────┐
        │  RENDER UP                                    │
        │  pull tools from the keychain                 │
        │  embed only what this task needs, shrunk      │
        │  spawn the capsule                            │
        └────────────────────┬─────────────────────────┘
                             ▼
        ┌──────────────────────────────────────────────┐
        │  DO THE WORK                                  │
        │  capsule forges · model is a wrapped tool     │
        │  NPU observer watches the whole time          │
        └────────────────────┬─────────────────────────┘
                             ▼
        ┌──────────────────────────────────────────────┐
        │  FLATTEN                                      │
        │  splice out the valuable snips                │
        │  keep vectors, cache, metadata                │
        │  eject the model · clear the GPU              │
        │  collapse back to −0                          │
        └──────────────────────────────────────────────┘
```

**Nothing persists between tasks except the keychain and the wardrobe.**
That is the whole point. The system is advanced *because* it is doing simple
things and then getting out of the way.

---

## The lineage — how the idea evolved

You named this yourself, and it explains every naming collision in the repos:

```
WARDROBE  →  CAPSULE  →  FABRIC
```

| Era | Idea |
|---|---|
| **Wardrobe** | Each garment is a memory — a text file, a completed task, a scraped result, another model's output. You put on the parts you need. A *concoction of wardrobes*: mix-and-match knowledge. |
| **Capsule** | The garment becomes a container. Encapsulation, shrink, offload. |
| **Fabric** | The container becomes the substance itself — it can capsulise, sandbox, liquefy, or build a specialised tool on demand. It hears you. It wraps the model so the model never holds control. |

Each era left code on disk under its own vocabulary. That is why `hopper`
means four different things and `conduit` means two — **they are from
different eras of the same evolving idea, not from confusion.**

---

## The thing that keeps it light: SPLICING

> *"we have the memory and weights spliced, pulling only the parts to give the
> whole history without keeping large files"*

This is the load-bearing mechanism and it appears everywhere in your artifacts
under different names — Confetti Snips, splice, the Concoct Engine.

**What it does:** after a model has worked, you do not keep the model and you
do not keep a transcript. You keep **snips** — the extracted deltas, facts,
and vectors that carry the *history* without the *bulk*.

Those snips are then:
- re-encoded into **fabric wraps** — so a *different* model can wear them
  later and "pick up just like they were there the first time"
- stored on the **keychain** as metadata, never as weights
- recombined by the **Concoctinator** into new knowledge-suits on demand

That is what makes going back in time possible. The persistent memory lives on
the **NPU** — separated deliberately, because the NPU is the observer and the
observer must outlive every capsule.

---

## Why models are disposable

> *"It's not designed to have AI as my main model... new tools are constantly
> coming, so it's all getting the brand new stuff and then keeping the data
> from it and offloading the models."*

A model chosen today is obsolete in a week. So:

- **Never** build the system around a specific model
- Pull the best current model as a **tool**, per task
- Keep what it produced; discard what produced it
- If a model was genuinely good, **encapsulate it as-is** (tar/zip, offloaded
  from GPU) so it can be brought back — cache, vectors, metadata intact
- Otherwise **flatten or eject** — the snips already hold the history

The GPU keychain exists to enforce this. 16 GB means one resident model at a
time, at full power, then cleared.

---

## Sockets — the outside world

> *"all the outside connections are custom sockets that have a memory and will
> reconnect with ease... these can be set up ahead of time with the app"*

A socket is not a config file. It is a **remembered connection** — it knows
what it connected to, how, and with what credentials-shape, and it can
re-establish itself without being reconfigured. Pre-provisioned through the
app, so the fabric can reach out the moment a task needs it.

This is `hub.py` (already merged) plus the Socket Coupler (recovered, 483L,
unreviewed) plus the memory layer that makes reconnection cheap.

---

## The mission, stated plainly

> *"This is an OS bridging the human experience with AI and leveraging the
> whole field to serve the human's needs (for real this time)."*

And the constraint that follows from it:

> *"I would prefer it to be the bare metal system embedded into the PC... the
> layers on top give it robustness, but as soon as it's done with the task, it
> flattens and goes back down and clears everything off."*

**Robustness is a temporary state, not a permanent one.** Any design that
leaves organs running between tasks is fighting the architecture.

---

## What this changes about the briefs

| Brief | Correction |
|---|---|
| **Hopper** | Four meanings across four eras. Settle the names first (see below) before writing any of them. |
| **Keychain** | Not just a metadata log — it is the **tool store the system renders up from**. It holds what to pull, in what shrunk form, for what task. Bigger than described. |
| **Splice** | Promoted. This is not one organ among ten — it is the mechanism that makes the whole flatten-and-recycle loop possible. |
| **Concoctinator** | Not only a sandbox. It is the **recycler** that turns snips into wearable knowledge-suits. Both roles are real; the sandbox is how it tests them. |
| **Bus / Overseer / Gate** | Unchanged. These are the −0 layer and stay resident. |

### The naming split, resolved

Four things currently called Hopper:

| Real organ | Job | Evidence |
|---|---|---|
| **Hopper** | pull-with-refusal work queue; a slow agent never blocks a fast one | your spec |
| **SlotGovernor** | caps concurrent sandboxes; semaphore + cgroups | `___215.pdf` |
| **OutputDrain** | throttled event drain with WAL | `~/Forge/backend/hopper.py` |
| **Flatten** | revoke vessel tokens → inscribe ledger → return slot to pool | `ConnectionMap.tsx` |

The fourth is not a hopper at all — **it is the flatten path**, which is the
most important operation in the whole system and had no name.

Same for Conduit:

| Real organ | Job |
|---|---|
| **VectorConduit** | the NPU bond — observer, persistent memory |
| **Surface** | human ↔ system interface; shapes intent in, sanitises out |

---

## The one risk worth naming

The Meta-Forge prompt in `docs/` ends with:

> *"Execute this entire build plan autonomously right now. Do not ask any
> follow-up questions."*

That instruction is how you got five hoppers. A model told not to ask, and not
given the existing vocabulary, will invent its own — every time, confidently.

The fix is not to stop using bold prompts. It is to hand every one of them
`FORGE_STATE.md` **first**, with the vocabulary table, so invention happens
where you want it and nowhere else.
