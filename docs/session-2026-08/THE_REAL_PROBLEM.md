# Why this keeps happening — and the one change that stops it

You said: *"I think this keeps happening and trying to fix it will only give me
another version of the missing concept... I've done this again and again for
the last year."*

You're right about the pattern. I want to be precise about the cause, because
the fix you're proposing treats the wrong one.

---

## The cause is not your code. It's context death.

In your own words: *"ran out of token and started up with a different model
causing it to branch."*

That is the whole loop:

```
model has full context  →  builds something excellent
      ↓
context window fills / session ends
      ↓
new model, new account, no memory of the decisions
      ↓
it rebuilds the concept from scratch, slightly differently
      ↓
new folder, new repo, new "the-forge"
      ↓
11 forge git repos on one drive
```

**11 git repos. 14 top-level forge folders/archives in `$HOME` alone.** Not
because you build badly — because each session started blind and forked.

Evidence from your own artifacts, three eras of one dataclass:

| Era | `Finding` shape |
|---|---|
| Mistral feed | `Finding(section_id=, kind=, severity=1)` |
| App manual | `Finding(verdict=, reason=, meta={})` |
| Live today | `Finding(id=, organ=, severity='critical', title=, timestamp=, metadata={})` |

Three models, three shapes, none wrong on its own. Nobody handed the next one
the decision. Same story with `forge/<organ>/` → `forge/fabric/`, and with
async → sync `authorize()`.

---

## Why a full wipe + reinstall will not break the loop

Your plan: clear the PC, reset the OS, reinstall GitHub + Obsidian, have coder
bots rewrite everything from the concept map.

The hard question: **what is different next time the context window runs out?**

If the answer is "nothing," you get a 12th repo — just on a cleaner disk. The
wipe removes *symptoms* (folder sprawl). It does not touch the *mechanism*
(no durable memory across sessions).

Worse, you'd be wiping the one thing that finally broke the tie between
versions. Today, for the first time, you have:

- a **graded, hash-indexed inventory** of what exists (`grades.csv`)
- an **AST-level comparison** against the live spine (`compare.py`)
- **two modules already recovered and pushed** (`hub.py`, `capsule.py`)
- a **concept ledger** (`concepts.csv`) mapping ideas → files
- `06_ARCHIVE_RAW` holding verbatim copies

That is the map you said you needed. Wiping now means rebuilding the map before
you can rebuild the code.

---

## What's actually true in what you said

Three things you're right about, and they matter:

1. **"The build can't get better than what is shown after you see the real
   map."** Correct — and the map now exists. `compare.py` proved your cabinet
   `gate.py` was *ahead* of your live spine by 25 symbols. You'd have never
   known by eye.

2. **"The written thoughts are the creative power."** Also correct, and it's
   why the sorter grades docs into BRONZE and indexes every concept mention.
   Your `STATUS.md`, `MYTHOS.md`, `NEXT_ISOLATION_HOPPER.md` are the seed
   corn. Code is regenerable; the reasoning is not.

3. **"Coder bots can rewrite the pieces quickly."** True. Writing code was
   never your bottleneck. **Deciding which version is canonical** was.

---

## The one change that actually stops the loop

Not a wipe. A **handoff contract**: a single file, in the spine, that any model
reads first and updates last.

```
~/the-forge/FORGE_STATE.md      ← committed to git, read-first, write-last
```

It holds, and only holds:

- **LOCKED decisions** with dates and one-line rationale
  ("`authorize()` is sync — never async. Reason: cannot stall the event loop.")
- **Current organ status** — which exist, which are stubs, which are broken
- **The canonical dataclass shapes** (`Finding`, `Capability`, `LedgerEntry`)
- **What NOT to rebuild** and where it lives
- **Open question for the next session** — exactly one

Every new session starts: *"Read FORGE_STATE.md, then continue."* Every session
ends by updating it. It is the thing you have never had, and it costs ~200
lines.

Your Obsidian + Git plan is right — but point it at *this*, not at note-taking
in general. Obsidian Git auto-commits the vault; `FORGE_STATE.md` lives in the
code repo so it can never drift from the code.

---

## If you still want to clean house — do it in this order

Not a wipe. A **collapse**, using the tool you already have.

**Phase A — finish the current recovery (1 session)**
Port `forge.py`, merge `ledger.py`, then `validate_ledger.py`. `forge-spine`
is then fully harvested and deletable.

**Phase B — run the sorter over the other 10 repos (2-3 sessions)**
Add roots one at a time to `config.yaml`:
`forge-os-locked-pc`, `forge-workspace/the-forge`, `forge-os/the-forge`,
`ALLFORGE/the-forge`, `ALLFORGE/the-forge-repo/the-forge`,
`Videos/the-forge-repo/the-forge`, `core_Forge-unziped`, `Forge`,
`the-forge-repo.tar.gz`, `forge-board-core(2).zip`.

Each one: scan → archive → grade → compare → port the GOLD recoveries.
You will find more `gate.py`-class wins. Guaranteed — that pattern held on the
very first root.

**Phase C — write FORGE_STATE.md** from what the cabinet proved, not from
memory.

**Phase D — then, and only then, delete.** `06_ARCHIVE_RAW` has verbatim
copies; the manifests record what existed. Deleting is safe *because* the
cabinet exists.

**Phase E — fresh OS if you still want one.** By then you're restoring one
repo + one vault, not archaeology.

---

## On the capsule → fabric change

You said the last big change was *"when the capsule became fabric and is alive
managing everything without giving it too much power — the spawning forge
sandbox wrapper overseeing all."*

That is a real architectural decision, and it is **written down nowhere in your
repo**. It explains the `forge/<organ>/` → `forge/fabric/` collapse that broke
`kernel.py`'s factory table. It is exactly the kind of thing FORGE_STATE.md
exists to hold — a decision whose *consequences* outlive the session that made
it.

Write that one down first.

---

## Bottom line

You do not have a code problem. You have a **memory problem**, and you have
been solving it by rebuilding — which is the most expensive possible fix.

The cabinet already broke the pattern this week: it found 25 symbols your live
spine was missing and got two modules merged and pushed. That is more forward
progress than a rebuild would give you in a week.

Finish the harvest. Write the state file. Then wipe from a position of
strength.
