# THE FORGE — clean build prompt

Hand this to the coder whole. It carries the vision, the physics, and the
frontiers. It does not carry the mess.

---

```text
You are architecting THE FORGE from a clean slate.

You are not maintaining anything. You are not fixing anything. You are
building the system this description implies, and you have latitude over
every decision the description does not explicitly fix.

Read the whole thing before you write a line. The shape matters more than
any individual piece.


═══════════════════════════════════════════════════════════════════
THE MACHINE
═══════════════════════════════════════════════════════════════════

One Pop!_OS workstation. Nothing runs in a cloud. Ever.

  GPU   NVIDIA RTX 5080, 16 GB VRAM      the workhorse
  NPU   Intel Arrow Lake, 13 TOPS        a second, independent mind
  CPU   Intel Core Ultra 9 275HX
  RAM   93 GB system memory              enormous headroom
  OS    Pop!_OS, recent kernel

The 16 GB VRAM ceiling is the single hardest constraint in the design.
Roughly one 20B model at Q4 fits. Everything about how this system
handles models follows from that number.

The 93 GB of system RAM is the softest constraint. You have room to be
extravagant there. Note that VRAM and system RAM are separate pools —
do not confuse them.

The NPU matters for a reason beyond throughput: it is different silicon
running a different model. Anything it concludes is genuinely independent
of anything the GPU concluded. That independence is worth more than its
FLOPS.


═══════════════════════════════════════════════════════════════════
THE THESIS
═══════════════════════════════════════════════════════════════════

Do not buy the tool. Do not depend on the tool. Forge the tool, use it,
keep what it taught you, and throw the tool away.

THE FORGE IS A WORKSHOP, NOT A PRODUCT.

It sits at the lowest layer of the machine, almost entirely empty. When a
task arrives, it renders up only what that task needs — pulling tools it
has already built, and building or finding the ones it lacks. AI models
are disposable tools: wrapped on entry so they never hold control, used,
stripped for what they produced, and ejected.

What persists is never the model. It is the vectors, the metadata, the
distilled extracts, and the resume points.

The output is a CAPSULE — a portable, self-contained artifact that can run
inside the Forge, with a reduced set of organs, or with no Forge at all.
You build a thing in the workshop, then you carry the thing out.

Four commitments follow, and everything else is downstream of them:

  1. MODELS ARE DISPOSABLE TOOLS
     A model chosen today is obsolete in a month. Never build around one.
     Pull the best current model for the task, keep what it produced,
     eject it. If one proves genuinely exceptional, seal it whole so it
     can be brought back — but that is the exception, not the plan.

  2. THE SYSTEM IS EMPTY BY DEFAULT
     Nothing runs between tasks. Capability materialises on demand and
     collapses after. The system stays capable BECAUSE it stays empty:
     there is always headroom to spawn something that did not exist five
     minutes ago. A permanently-running organ set is overhead crowding out
     the thing you actually wanted to do.

  3. KNOWLEDGE OUTLIVES ITS MAKER
     Extracts, vectors, wraps, and metadata persist. Weights do not. A
     later model should be able to wear what an earlier model learned and
     pick up as though it had been there the whole time.

  4. NOTHING ACTS WITHOUT A PRE-DECLARED PATHWAY
     The system is proactive, not reactive. Pathways are declared before
     anything runs. At runtime the question is only: was this declared,
     and does it verify? Not: should I allow this?


═══════════════════════════════════════════════════════════════════
THE SHAPE
═══════════════════════════════════════════════════════════════════

    ┌───────────────────────────────────────────────────────┐
    │ PRODUCTS — portable capsules, Forge optional          │
    ├───────────────────────────────────────────────────────┤
    │ ORGANS — snap on, snap off, only what this task needs │
    ├───────────────────────────────────────────────────────┤
    │ THE FORGE — itself a removable layer                  │
    ├───────────────────────────────────────────────────────┤
    │ GROUND — locked, pinned, always on:                   │
    │   a small resident model on GPU                       │
    │   a persistent memory on NPU                          │
    └───────────────────────────────────────────────────────┘
                       BARE METAL PC

The lifecycle of any task:

    intent
      → interpret it, decide what is needed
      → render up those organs (build or find what is missing)
      → post the work; agents take it
      → work happens, every privileged act through the one door
      → extract what was learned
      → keep it or seal it
      → flatten: revoke, record, clear the GPU, collapse
      → empty again

Robustness is a temporary state. Anything still running when the task is
done is a bug.


═══════════════════════════════════════════════════════════════════
THE LANGUAGE
═══════════════════════════════════════════════════════════════════

These words carry specific meaning. Use them for these meanings. If you
need a concept that is not here, name it explicitly and say why — a new
word is fine, an accidental synonym for an existing one is not.

  FABRIC        the living substance; it can encapsulate, sandbox,
                liquefy, or build a specialised tool on demand
  WRAP          the mold that IS the training — a fingerprint of a
                conformation manifest, applied before the model runs, so
                it wakes already shaped. Identity, not behaviour.
  BAPTISM       the moment of wrapping. There is no unwrapped path in.
  CAPSULE       a sealed portable artifact: wrap, vectors, cache,
                metadata, sockets, provenance. The workshop's output.
  SNIP          a spliced extract — the delta, fact, or vector carrying
                history without bulk
  WARDROBE      the store of wraps; knowledge-suits a later model wears
  SPLICE        splits one thing into sections that cannot hear each
                other. One primitive, three uses: twins, the
                watcher/actor wall, and extraction.
  TWIN          one wrap split into many agents. Deliberately unequal —
                some larger, faster, differently able. Identical twins
                produce identical answers, which is worthless.
  GATE          the one door. Verifies declarations. Does not negotiate.
  OVERSEER      the watching half. Sees everything, cannot act.
  COMMANDER     the acting half. Acts only on findings, only through the
                gate. Same intelligence as the Overseer, split and walled.
  HOPPER        holds work. Agents take from it; nothing is assigned.
  KEYCHAIN      the resume point — what to pull, in what form, to put a
                capsule back exactly where it left off
  BONEYARD      where built tools rest between uses
  TOOLCHAIN     finds, evaluates, converts, and rebuilds external tools
                into usable organs
  SOCKETS       remembered outside connections; cheap to reconnect,
                re-authorized every time
  FLATTEN       the collapse: extract, revoke, record, clear, return
  ENCAPSULATE   the keep-path: seal for portability or shelving


═══════════════════════════════════════════════════════════════════
THE PROPERTIES THAT MUST HOLD
═══════════════════════════════════════════════════════════════════

These are physics, not preference. How you achieve them is yours. That
they hold is not negotiable.

  ONE DOOR
    Every privileged action passes a single authorization point. New
    capabilities are expressed in the existing contract; they never
    invent a second way in. If there are two doors, there is no door.

  DEAF BY DEFAULT
    Components cannot hear each other. Isolation is structural, not
    conventional — a component should be unable to observe another, not
    merely discouraged from it. Exactly one privileged observer exists.

  WATCHING IS NOT ACTING
    The thing that watches cannot act. The thing that acts cannot watch
    on its own — it acts on the watcher's findings, through the door.
    Enforce this with the same mechanism that separates twins, so it is
    a physical property rather than a promise.

  THE DECISION PATH DOES NOT WAIT
    Authorization is synchronous and fast. It must never be able to stall
    the system. Do asynchronous work elsewhere, freely.

  NOTHING IS THROWN AWAY
    Reclaim, do not delete. What a thing learned outlives the thing.

  FAIL CLOSED
    Unknown severity ranks as critical. An undeclared pathway denies
    before any expensive check runs. An unparseable input is a refusal,
    not a default.


═══════════════════════════════════════════════════════════════════
TWO TRUST ZONES
═══════════════════════════════════════════════════════════════════

The boundary is the machine itself.

  OUTSIDE — sockets, adapters, the web, anything remote
    A real adversary who can forge a request. Full cryptographic
    verification. This is where the door is.

  INSIDE — work routing, agent eligibility, organ signalling
    No adversary. Only mistakes. Cheap checks are correct here.

This is safe for one reason, and it is worth internalising: ROUTING IS
NOT AUTHORITY. An agent that somehow receives work it should not have
still cannot do anything with it — every privileged act passes the door
regardless. So the inside check only has to prevent accidents.

Hard perimeter, fast interior.

One consequence: a remembered connection is a stored credential. It
should hold WHERE and HOW, never a token that grants access on replay.
Reconnection is a fresh authorization, not a resumption.


═══════════════════════════════════════════════════════════════════
LESSONS ALREADY PAID FOR
═══════════════════════════════════════════════════════════════════

Traps found the expensive way. Free to you. Not constraints on your
design — just holes you do not need to fall in.

  · A signed string built by joining fields with a delimiter is forgeable
    if the delimiter is not escaped. A crafted name shifts the boundary
    and changes what was signed. Escape or hash every field.

  · A replay guard that evicts probabilistically has false negatives, and
    a false negative in a replay guard is a vulnerability, full stop.
    Make it exact and bound it by time, not by capacity.

  · Two legitimate identical actions must both succeed. A naive replay
    ledger rejects the second one. A per-mint nonce bound into the
    signature fixes it without weakening anything.

  · A fingerprint identifies; it does not constrain behaviour. Identity
    and authority are different things and must not be conflated.

  · A queue that drops silently under load hides its own failure.
    Backpressure must be counted, logged, and inspectable.

  · Persistent memory that survives a model's removal also survives that
    model's corruption. There must be a way to burn it.

  · Deciding security by pattern-matching model output — checking whether
    the text contains "APPROVED" — is trivially spoofable. A model that
    mentions the word in an explanation passes. Never do this.


═══════════════════════════════════════════════════════════════════
THE CREATIVE FRONTIERS
═══════════════════════════════════════════════════════════════════

Seven questions have no settled answer. They are not oversights — they
are the genuinely hard parts, and they are where the design becomes
yours.

Do your best work here. For each, I want your reasoning, your chosen
mechanism, and an honest account of what it costs. If you find something
better than what the question assumes, say so.

  1. WHAT IS AN EXTRACT?
     When a model finishes, we keep a distilled trace instead of the
     model. But what IS that trace? A diff, an embedding, a structured
     claim, a weight delta, something else entirely? The answer decides
     whether a later model genuinely picks up where the last left off, or
     merely reads a summary. This is the load-bearing question of the
     whole design.

  2. HOW DOES A CAPSULE RESUME?
     Not reload — resume. Restoring what it was doing, what it had
     decided, what it was about to do next. What must be captured, and
     when, for a sealed capsule to continue a thought rather than restart
     one?

  3. WHAT MAKES FOUND CODE TRUSTWORTHY?
     The system scrapes the world for the best current tool and converts
     it into an organ. That is the thesis. It is also arbitrary
     third-party code entering the machine. There is a good answer for
     what makes MODEL OUTPUT clean. There is no answer yet for what makes
     IMPORTED CODE clean. The greatest strength here is also the widest
     door.

  4. WHO CHECKS THE CHECKERS?
     Agents split from one wrap share weights, and therefore share blind
     spots. One twin reviewing another will confidently agree on the same
     wrong answer. The NPU is different hardware running a different
     model, so its judgement is genuinely independent. Which decisions
     require that independence, and which are fine with consensus among
     twins?

  5. WHEN DOES A TOOL GO STALE?
     Tools rest in the boneyard between uses. A tool that was excellent
     in August is obsolete in October. Rebuilding on every use is safe
     and slow; caching is fast and rots. What triggers re-evaluation —
     age, failure, a sweep, something smarter?

  6. WHAT MAY THE RESIDENT MODEL DECIDE ALONE?
     A small always-on model chooses which organs materialise for a task.
     That is a privileged decision made by a limited intelligence. If it
     must pass the door for every choice, the system is slow. If it does
     not, a small model has unilateral control over system composition.
     Where is the line?

  7. WHAT IS A CAPSULE, EXACTLY?
     Portability is the entire promise, and portability requires a
     defined artifact. What goes in. How it seals. How it declares what
     it needs from the outside. How provenance travels with it. What
     happens when a capsule built with a given organ runs somewhere that
     organ does not exist. This is the contract everything else conforms
     to — settle it first, in writing, before building against it.


═══════════════════════════════════════════════════════════════════
WHAT EXCELLENCE LOOKS LIKE HERE
═══════════════════════════════════════════════════════════════════

  · SMALL AND SHARP over large and general. This system earns capability
    from structure, not from scale. If a piece is big, ask what it is
    doing that structure could do instead.

  · STDLIB FIRST. A dependency is a thing that can rot, break, or turn
    hostile. Each one needs a reason worth writing down.

  · BOUNDED EVERYTHING. Queues, ledgers, retries, caches, logs. Anything
    unbounded is a denial of service that has not been discovered yet.

  · DECISIONS ARE VALUES. Return a verdict object with a reason and an
    audit id. Offer a raise-on-deny convenience for callers who want it.
    This makes the security core testable without exception pyramids.

  · THE METAPHOR SERVES THE ENGINEERING. The language here is vivid on
    purpose — it helps reasoning. But if a metaphor ever hides a simpler
    primitive, take the primitive and keep the name.

  · WRITE DOWN WHY. Every component carries a design thesis at the top:
    what it replaces, what problem it solves, what you tried and
    rejected, and which properties constrain it. Not decoration — this is
    the part that survives you. Code is regenerable; reasoning is not.


═══════════════════════════════════════════════════════════════════
YOUR DELIVERABLE
═══════════════════════════════════════════════════════════════════

Design this system. Specifically:

  A. THE ARCHITECTURE — the components you have chosen, what each owns,
     and how they compose. Show the dependency structure. Show which are
     resident and which materialise on demand.

  B. THE CAPSULE SPECIFICATION — settle frontier 7 first, in writing.
     Everything else conforms to it.

  C. YOUR ANSWERS TO THE FRONTIERS — for each of the seven, your chosen
     mechanism, your reasoning, and the honest cost. Where you are
     uncertain, say which experiment would settle it.

  D. THE BUILD ORDER — with a one-line reason per position. Prefer an
     order that produces something runnable early over one that is
     theoretically tidy.

  E. WHERE YOU WOULD GO FURTHER — capabilities this thesis makes possible
     that it does not yet describe. Be concrete about cost. Push the
     design; do not flatter it.

  F. WHAT YOU WOULD CUT — anything here that adds weight without buying
     capability or safety. An accurate objection is worth more than
     agreement. But if you propose removing something that implements one
     of the properties above, show what replaces it — the property has to
     hold either way.

Design first. Code second, and only where the design is settled.
```

---

## A note on what this prompt leaves out

Deliberately absent: the existing test baseline, the recovered files, the
four incompatible hoppers, the specific bugs.

**The trade:** you get a genuinely fresh design unencumbered by legacy
decisions. You also lose automatic reuse of things already proven — the gate
with its nonce and delimiter fixes, the behavioral judge, the hash-chained
ledger, the attenuation chain.

The security lessons from those are preserved in **LESSONS ALREADY PAID FOR**,
so the new design inherits the knowledge without inheriting the code.

Recommended: run this prompt cold, then compare what comes back against
`THE_FORGE_MASTER_LAYOUT.md §6` yourself. Where the new design independently
arrives at something you already built, that is strong confirmation. Where it
diverges, that is the interesting conversation.
