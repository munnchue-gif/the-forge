# THE HOPPER + THE TWINS — design spec, in the architect's words

Captured 2026-08-17. This is the definitive spec for Brief 1 and supersedes
every `hopper.py` on disk.

---

## 1 · The problem it solves

> *"Some models aren't as good and they'll all be waiting on that one to
> finish. Mine doesn't work that way. They can all grab from the hopper."*

Standard dispatch: a scheduler assigns task→agent. The moment one agent stalls,
everything queued behind it stalls. Head-of-line blocking.

The Hopper inverts it. **Nobody is assigned anything. Agents take.**

> *"It holds a bunch of stuff and then it issues the commands... I could have
> 50 models and that's not going to slow my system down."*

A stalled agent holds exactly one task. The other 49 keep pulling. There is no
queue behind a slow worker because there is no queue *per* worker.

---

## 2 · Not every agent can take every task

This is the part no existing implementation has:

> *"the hopper has different tasks for different models so they won't be able
> to pull certain ones unless they're a certain model"*

Tasks are **not** generic work items. Each carries an eligibility constraint,
and a twin can only see — let alone pull — what it is eligible for.

> *"we'd have a hash on some of the feed just like a mathematical thing so they
> can line up with it and it will go to some models and not others"*

**You already own this primitive.** It is the same HMAC machinery the Gate
uses. A task carries a hash; a twin carries a key; the hash either lines up or
the task is invisible to that twin. No policy engine, no ACL table — the math
decides.

Implication worth stating: eligibility should be **structural, not advisory**.
A twin should not be able to pull an ineligible task and be refused. It should
not be able to *see* it.

---

## 3 · Compartmentalised and time-released commands

> *"some of the commands are compartmentalized, so you don't want to give some
> commands until a certain time or when something's done, or you have it
> dissolve or disappear"*

Three release conditions, all first-class:

| Condition | Meaning |
|---|---|
| **Time-gated** | not visible until T |
| **Dependency-gated** | not visible until task X completes |
| **Dissolving** | visible for a window, then gone whether taken or not |

A dissolving command is a genuinely good security property — an order that
expires unclaimed cannot be replayed later by a compromised twin. It is the
Gate's replay window applied to work rather than capabilities.

---

## 4 · The twins

> *"instead of installing a bunch of stuff where it takes up my GPU, I install
> like a big model and slice it down into like 10 models"*

One set of weights. Many agents. This is correct and it is the only way the
50-agent claim works on 16 GB — see §7 for the honest constraint.

> *"you make some bigger, some smaller, some faster, some have different
> abilities, and it gives it a melting pot so they can all learn. If they're
> all the same, it won't matter."*

**Deliberate heterogeneity.** Identical twins produce identical answers, which
makes cross-checking worthless. Differentiation is what makes the melting pot
generate signal instead of echo.

### The wall between twins

> *"some will be twins where they're on the same wrap. So they're both in the
> same wrap, but there's a wall between them and they can't see or hear."*

**This capability already exists in your codebase.** From `capabilities.py`:

```python
class SpliceCapability:
    region_id: str
    mode: str        # "split" | "merge"
    sections: int    # >=2 for split
    deaf: bool = True
```

> *"deaf: If True, sections get independent SubKernelBus namespaces so they are
> cryptographically deaf to each other's events."*

Same wrap, split into sections, cryptographically deaf. That is exactly the
wall — written months ago, signed by the Gate, audited on every split. And
because it rides the Gate, **isolation can never be silently removed.**

### The conduit through the wall

> *"but then there's also a conduit where the overseer can hear and see
> between"*

The Overseer's tap. Deaf twins, one privileged listener. That is Law 2 with
its single documented exception, and it is already how `SubstanceBus` is built.

---

## 5 · Overseer and Commander are one model, spliced

> *"the overseer watches everything but can't interact. But the commander is
> the one that goes and does the interacting, and then they're the same model.
> They're just spliced into different versions of themselves."*

This closes a question that has been open all session. Watcher and Commander
are not two organs that happen to cooperate — they are **one intelligence
split by the same splice mechanism as the twins**, with the wall enforcing the
separation.

Which means the safety property is not a convention. It is the same
cryptographic deafness:

> *"the thing that watches cannot act, and the thing that acts cannot watch on
> its own — it acts only on the watcher's findings, and only through the gate."*

The Watcher physically cannot reach the action path. Not "is not supposed to."

---

## 6 · Proactive, not reactive — and the one-way gate

> *"if the commands are issued, then it's already got a path because
> everything's done ahead of time. It's not reactive. It's proactive. It
> configures everything beforehand so it stays safe."*

> *"So the gate's a one-way gate, so I don't know if that's a problem here"*

**It is not a problem. It is the correct design, and it is why the system is
safe.**

A two-way gate has to negotiate: *may I? → let me evaluate → here is your
answer.* Negotiation is where injection lives, because the requester influences
the evaluation.

A one-way gate cannot negotiate. It answers one question — *was this pathway
declared in advance, and does this token verify?* — and the answer is yes or
no. Nothing the caller says can change the shape of the question.

**Your recovered `gate.py` already implements this.** `PathwayRegistry` denies
an undeclared `kind` **before any crypto runs** (`DENY_PATH_NOT_DECLARED`). No
declaration, no door. A new capability cannot talk its way in.

So: pre-declared pathways + one-way verification + tokens minted ahead of time
= a system where the runtime decision is trivial and unspoofable, because all
the thinking happened before anything was running.

That is worth writing into `FORGE_STATE.md §1` as a locked decision, in exactly
these terms: **the gate does not negotiate; it verifies a declaration.**

---

## 7 · The honest constraint

> *"I could have 50 models and that's not going to slow my system down."*

True for **agents**, not for **models**. 16 GB VRAM holds roughly one 20B model
at Q4. Fifty independent models is not physically possible on this card.

Fifty *twins* sharing one set of weights **is** possible, and it is what you
described. The mechanisms that make it real:

- **Continuous batching** — one weight set, many concurrent sequences, each
  twin with its own context. This is what vLLM does.
- **Per-twin adapters** (LoRA-style) — small per-twin deltas over shared
  weights, giving the "some bigger, some smaller, different abilities"
  differentiation cheaply.
- **Shared-weight multiplexing** — already sketched in your recovered
  `splicing_engine.py`: one pinned model, three async channels, one VRAM
  allocation.

So the design holds. The wording to keep is **"50 agents on one wrap,"** not
"50 models." Anyone implementing from "50 models" will try to load 50 and fail.

### And one real caution about twin cross-checking

Twins sharing weights share **failure modes**. If the base model has a blind
spot, every twin has the same blind spot, and a twin watching a twin will
confidently agree on a wrong answer.

This does not break the design — it bounds it:

- **Task parallelism** → twins are ideal. Cheap, fast, isolated.
- **Security cross-checking** → at least one checker should be a *different
  base model*, not a twin. Your NPU seat is the natural home for it: different
  hardware, different model, genuinely independent judgement.

That is arguably why the NPU/GPU split exists in the first place. Worth making
explicit rather than incidental.

---

## 8 · What this means for the build

| Piece | Change |
|---|---|
| **Hopper** | Now fully specified. Eligibility-hashed tasks, compartmented release, dissolving orders, pull-never-blocks. |
| **Splice** | Promoted again. It is the mechanism behind twins, the Watcher/Commander wall, *and* snip recycling. Three jobs, one primitive. |
| **Gate** | One-way verification is a locked decision, not an open question. PathwayRegistry port (Brief 3) becomes higher priority — it is the pre-declaration mechanism the whole proactive model rests on. |
| **NPU seat** | Reframed: not just "the observer" but **the independent checker** whose value comes from *not* being a twin. |

### Brief 1, restated

Build `fabric/hopper.py`:

- tasks carry an **eligibility hash**; ineligible twins cannot see them
- **release conditions**: immediate / time-gated / dependency-gated / dissolving
- `pull()` never blocks, never waits, never assigns
- leases expire; refusal is an outcome; dead-letter after N attempts
- **sorts work, never executes, never calls the Gate**
- must sustain ~50 concurrent pullers without contention

Open: whether eligibility reuses the Gate's HMAC directly or a cheaper
non-security hash (routing is not authorization — the Gate still decides
authority, so the routing hash may not need to be cryptographic at all). State
which you chose and why.
