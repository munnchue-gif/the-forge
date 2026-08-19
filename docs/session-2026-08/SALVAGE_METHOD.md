# SALVAGE — harvesting mechanisms instead of files

Your question: *"Even if a file doesn't have my philosophy, if it's built
really well, couldn't we look at the lines and fix it — or pile similar pieces
together and have a model reconfigure them?"*

**Yes. That is the correct workflow, and it is what "mine it, don't port it"
should have meant all along.** Here is the method, plus a major finding from
the two files you just opened.

---

# 1 · THE FINDING — `security_guard.py` is a second Gate

Look at the class list:

```
GuardedCommand
GuardStats
SignatureError
ReplayError
ExpiredTokenError
SlotAccessDenied
SecurityGuard
```

`SignatureError` · `ReplayError` · `ExpiredTokenError` — that is **the same
error taxonomy as your live Gate.** Signature verification, replay protection,
token expiry. `GuardStats` mirrors `GateStats`. `GuardedCommand` mirrors
`SignedCapability`.

This is not a random security file. It is **a parallel implementation of the
Gate concept**, built by a different session, in a different lineage.

And the detail that makes it valuable: **653 lines, zero `async def`.**

Everything else in that lineage is async-heavy — `bus_516` has 8, `subkernel`
has 11, the test file has 14. `security_guard.py` is the only large recovered
organ that is **already compatible with Law 4** (sync on the decision path).

It does not need an architecture rewrite to be readable against your Gate. It
needs a **diff**.

```bash
cd ~/FORGE_REVIEW/gold-2026-08-17
grep -nE "def |raise |replay|nonce|expire|signature" security_guard* | head -40
```

The question to answer: does it do anything your Gate does not? Slot access
control (`SlotAccessDenied`) has no equivalent in your `capabilities.py`.

---

# 2 · THE CAVEAT — the threat regex is a speed bump, not a boundary

`peer_review.py`'s denylist is genuinely useful. It is also incomplete by
nature, and that must be written down before anyone mistakes it for security.

It catches `rm -rf`, `mkfs`, `dd if=`, fork bombs, `curl | bash`, `DROP TABLE`.

It does not catch:

```bash
rm -r -f /                          # separated flags
rm --recursive --force /            # long flags
find . -delete                      # different tool
python -c "import shutil; shutil.rmtree('/')"
echo cm0gLXJmIC8= | base64 -d | sh  # encoded
```

**Denylists enumerate badness, which is unbounded.** This is fine as
defence-in-depth and worth keeping — but it belongs *behind* the Gate, never
*instead of* it. Your architecture already says this: the Gate is the boundary
because it enumerates *goodness* (declared pathways), which is bounded.

**Salvage verdict:** take the pattern table as a starting denylist, take
`_is_dangerous()` returning `(bool, matched_pattern)` as a good shape, and
document that it is advisory. Do not let it become the authorization check.

---

# 3 · THE METHOD — group by MECHANISM, not by file

A file is an accident of who wrote it and when. A **mechanism** is the thing
worth keeping. So the parts bin is organised by what a piece *does*.

```
~/FORGE_PARTS/
  crypto/          signature, nonce, replay ledger, expiry, hash chains
  isolation/       namespaces, cgroups, deaf sections, sandboxing
  queueing/        bounded queues, DLQ, backpressure, teardown
  lifecycle/       spawn, flatten, reclaim, resume, WAL
  taxonomy/        error hierarchies, enums, verdict types, threat tables
  tests/           any test suite — tests encode intent
  _SOURCE.md       what came from where, and its era
```

Each extracted piece gets a one-line header saying where it came from and
which era it belongs to (per the seven shifts).

## What transfers well

| Transfers | Why |
|---|---|
| **Algorithms** | An exact time-bucketed replay ledger is the same algorithm in any architecture |
| **Error taxonomies** | `SignatureError / ReplayError / ExpiredTokenError` is a design decision, not code |
| **Data shapes** | Frozen dataclasses, manifest schemas, verdict objects |
| **Rule tables** | Threat patterns, capability lists, staleness weights |
| **Tests** | The clearest statement of intent you can recover |
| **Docstrings** | Often the *only* place the reasoning survives |

## What does not transfer

| Does not transfer | Why |
|---|---|
| **async/sync structure** | Law 4 says sync on the decision path. An async organ is a rewrite, not a port. |
| **Vocabulary** | Era-specific names create the fifth hopper |
| **Import graphs** | `from backend.kernel_bus import` assumes a tree you do not have |
| **Lifecycle assumptions** | Anything that assumes organs are always running is pre-Shift 1 |

---

# 4 · THE EXTRACTION PASS

Do this once, over the whole review folder, before building anything.

For each file, produce a **parts sheet** — not a port, an inventory:

```
FILE: security_guard.py  (653L, sync, backend/ lineage, pre-Shift 1)

MECHANISMS PRESENT
  · signature verification with expiry        → crypto/    HIGH value
  · replay detection                          → crypto/    compare to live ReplayLedger
  · slot access control (SlotAccessDenied)    → taxonomy/  NO EQUIVALENT in live spine
  · GuardStats counters                       → taxonomy/  mirrors GateStats

VERDICT
  · sync already — Law 4 compatible, unusually portable
  · duplicate of live Gate concepts — diff, do not merge
  · SlotAccessDenied is genuinely new — extract it

DISCARD
  · import coupling to backend.kernel_bus
  · any naming from the backend/ era
```

Ten files, ten sheets. Then you know what you actually have, at the level of
mechanisms rather than filenames.

---

# 5 · THE RECONFIGURATION PROMPT

Once the bin is grouped, this is the prompt. It works because you are asking
for **one mechanism at a time**, with the target architecture stated.

```text
You are salvaging a MECHANISM, not porting a file.

TARGET ARCHITECTURE — everything you produce must satisfy these:
  · sync on the decision path; async only off the hot path
  · stdlib-first; a dependency needs written justification
  · bounded everything — queues, ledgers, retries, caches
  · fail closed — unknown ranks critical, undeclared denies before
    expensive checks
  · decisions are values: return a verdict object with reason + audit id
  · vocabulary is locked (see the handoff §4) — a word not in that table
    does not exist

SOURCE MATERIAL — [N] implementations of the same mechanism, from different
eras of the same project. They disagree. That disagreement is information.

[paste the extracted pieces, each with its origin header]

YOUR TASK
  1. Identify what each implementation does that the others do not.
  2. Say which behaviours are ESSENTIAL to the mechanism and which are
     accidents of the architecture they came from.
  3. Produce ONE implementation for the target architecture above.
  4. Name what you deliberately dropped, and why.
  5. If two sources conflict on a security property, take the STRICTER one
     and say so — a conflict means someone learned something.

DO NOT
  · preserve the original naming if it conflicts with the locked vocabulary
  · carry over async structure onto the decision path
  · keep an import graph that assumes a different tree
  · merge by concatenation. If you cannot decide, present both and ask.

REQUIRED OUTPUT: a DESIGN THESIS docstring stating what this replaces, what
each source contributed, what you rejected, and which laws constrain it.
```

Point 5 matters most. When two versions of a replay guard disagree, the
stricter one usually exists because the looser one was found to be broken.

---

# 6 · THE PILES YOU ALREADY HAVE

From the eight files, grouped by mechanism:

**CRYPTO / GATE — 3 implementations, all doing signature+replay+expiry**
- live `gate.py` (10 tests, nonce + delimiter escape — **the reference**)
- recovered `gate.py` PathwayRegistry (+25 symbols)
- `security_guard.py` (653L, sync, `SlotAccessDenied` is new)

→ *Diff all three. The live one wins on prose; the others may win on coverage.*

**QUEUEING / BUS — 4 implementations**
- live `bus.py` (95L)
- `bus_516.py` (383 substantive lines, DLQ + two-phase teardown)
- `c44` bus (91L)
- refactoring bus (290L)

→ *Four attempts at one mechanism. The 516 is the most complete.*

**ISOLATION — 2 mechanisms, non-overlapping**
- `subkernel.py` (508L) — deaf namespaces, `SWARM_EOF` teardown
- `FabricSandbox` — bwrap + systemd-run, OS-level

→ *Not competitors. One is logical isolation, one is process isolation. Keep both.*

**LIFECYCLE — the throttle family**
- five `hopper.py` variants, all `OutputHopper`

→ *One mechanism worth extracting: **WAL journalling** so no approved task is
silently dropped. That belongs in the real Hopper. Everything else discard.*

**CHECKING**
- `peer_review.py` — rule-based verdicts, advisory only

→ *Take the pattern table and the `(bool, reason)` return shape.*

**TESTS — the highest-value pile**
- `test_capsule_slicing.py` (737L raw / 568 substantive)
- `test_security_guard.py` (383L)
- `test_hopper.py`, `test_peer_review.py`

→ *Read these FIRST. They state intent more clearly than the implementations,
and a test suite for a thing you have not built yet is a specification.*

---

# 7 · THE ORDER

1. **Read `test_capsule_slicing.py`.** 568 lines of tests for capsule slicing,
   and capsule format is Build #1. This is a spec someone already wrote.
2. **Diff `security_guard.py` against your live Gate.** Sync, same taxonomy,
   one novel concept. Highest-value comparison in the pile.
3. **Extract WAL from the hopper family**, discard the rest.
4. **Group the four buses** and run the reconfiguration prompt on that pile.
5. Everything else after.

The general rule: **a mechanism with three implementations and a test suite is
nearly free to rebuild correctly.** A mechanism with one implementation and no
tests is a sketch. Sort by that, and the pile stops being intimidating.
