# The organ architecture, as you described it — and where the code for it is

Your verbal spec, written down so it stops living only in your head. Then a
map of which existing artifact already implements each piece.

## The design (your words, formalised)

| Organ | Can hear? | Can command? | Why split that way |
|---|---|---|---|
| **Conduit** | **yes** | **no** | Hears everything on the fabric. Deliberately cannot issue orders — listening power and acting power must never sit in one organ. |
| **Commander** | **no** | **yes** | Issues orders. Deliberately deaf, so it cannot react to raw feed content — it acts only on what is formally handed to it. |
| **Overseer** | **yes, always** | no | Always on, sees all feeds + metadata. **Spliced**: keeps counts and snippets, never the full text. Watches for known-bad patterns and emits a warning feed. Sits at the live gate. |
| **Hopper** | — | — | Sorts work. **Pull-based**: any agent pulls whenever free, drops results whenever done, and can drop a task *back* if it is too hard. A slow agent never blocks the next one. |
| **Gate** | — | authorises | The one door. Every privileged action passes through it. |

The through-line: **hearing and acting are never the same organ**, and no
organ can block another. That is the same principle as the Glass Rule (the App
shows and requests; the Gate decides) and the same principle as
`PathwayRegistry` (undeclared paths are denied before any crypto).

## The Overseer "splice" — the important bit

You said it precisely: *"spliced so it's not an internal huge log — cut down
into just a little snippet to give it a count of everything without the heavy
text files piling up."*

That is **counters + bounded samples, not a log**. The Kernel Review PDF has a
working version of exactly this in `HealthCheckMonitor`:

```python
self._tokens.append(self._bus.subscribe("*", self._on_any_event))   # hears everything

async def _on_any_event(self, event: Event):
    evt_name = str(event.event_type)
    self.counters[evt_name] = self.counters.get(evt_name, 0) + 1     # count only
```

Wildcard subscribe → increment a counter → never retain the payload. Plus a
`_sweep_loop` that escalates peers to `degraded` at 12s and `offline` at 30s,
publishing `SERVICE_DEGRADED` / `SERVICE_OFFLINE` — that is your "it releases a
feed when it sees something that's going to hurt it."

**This is the Overseer pattern you described, already written.** Different
lineage (`backend/kernel/`, not `forge/fabric/`), so port the *pattern*, not
the file.

## The Hopper — not in this PDF, but you already have a design note

`Hopper`, `Commander`, `Conduit`, and `Splice` appear **zero times** in the
Kernel Review. But your cabinet scan found:

```
35  BRONZE  prompts/NEXT_ISOLATION_HOPPER.md
```

That is the Hopper design note, sitting in `03_BRONZE`. What you described —
pull-when-free, drop-back-if-too-hard, no head-of-line blocking — is a
**work-stealing queue with task re-queue on refusal**. The closest thing in the
Kernel Review is the DLQ backpressure rule:

> *"If the queue is full (backpressure), the event is routed to the
> dead-letter queue instead of blocking or raising. This is the critical
> isolation point — a stalled consumer never affects peers."*

Same guarantee, different mechanism. The Hopper needs pull semantics; the bus
gives push-with-overflow. Worth reading side by side when you build it.

## What this PDF is, and is not

**Is:** a complete, coherent async kernel from a *different* lineage —
`backend/kernel/bus.py`, `subkernel.py`, `capsule_manager.py`,
`commit_engine.py`, `health_monitor.py`, plus tests. Strong ideas in it:

- `SubKernel` / `SubKernelBus` — one isolated bus per swarm, outer bus never
  reachable from inside the boundary (129 mentions; it is the centrepiece)
- Two-phase teardown: inject `SWARM_EOF` sentinel into every queue, *then*
  cancel and join tasks — no leaked coroutine frames
- Per-subscriber queues with DLQ overflow — one stalled consumer cannot stall
  the fabric
- `publish_threadsafe()` via `loop.call_soon_threadsafe`

**Is not:** portable into `the-forge`. It is `backend/`-rooted, fully async,
and uses a different Event/Topic model than your `forge/fabric/` organs. Your
gate is deliberately **sync** on the decision path.

**Verdict: BRONZE — concept source, not code source.** File it in the cabinet,
mine the SubKernel isolation and sentinel-teardown patterns when you build the
Hopper and Conduit. Do not merge it.

## Where each organ stands today

| Organ | Status |
|---|---|
| Gate | **live** in `forge/fabric/gate.py`; `PathwayRegistry` recovery pending (CANDIDATE_SUPERSET, +25 symbols) |
| Overseer | pattern exists (this PDF); needs a `forge/fabric/` implementation |
| Conduit | named in your README's 14 organs; design not yet written down |
| Commander | not yet in code |
| Hopper | design note in `03_BRONZE/prompts/NEXT_ISOLATION_HOPPER.md` |
| Capsule | **merged today** — `forge/fabric/capsule.py` |
| Hub | **merged today** — `forge/fabric/hub.py` |
| Ledger | live; two-way merge pending |
| Kernel | live but **broken factory table** (see BASELINE_DRIFT.md) |

## On the Google Drive plan

Good instinct — one sorted pile beats twenty uploads. When it is ready:

- **A `.zip` or `.tar.gz` of the tree is the best single artifact.** I can
  unpack it and walk every file, which beats PDFs (PDF extraction mangles
  indentation, and code loses its shape).
- If you want the sorter to grade the Drive contents, drop them into a local
  folder and add it as a root in `config.yaml`. Same scan → grade → compare
  flow you already ran on `forge-spine`.
- Keep PDFs for prose/architecture docs. Use archives for anything with code.
