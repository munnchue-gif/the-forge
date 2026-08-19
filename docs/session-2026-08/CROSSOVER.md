# CROSSOVER — how to resume THE FORGE in a new session

Date frozen: 2026-08-19

**Purpose.** This file exists so that when this chat hits its limit, the next
one starts where you stopped instead of re-deriving the architecture for the
fifth time. Re-derivation is the disease. This file is the cure.

---

## PART A — THE COLD-START PROMPT

Open a new chat. Paste the block between the lines below **as your first
message**. Nothing else. Don't summarise it in your own words — that
reintroduces drift.

---BEGIN PASTE---

I'm resuming a long-running project called THE FORGE — a local-first,
security-hardened AI-native OS on one Pop!_OS workstation. Read this brief
fully before answering. Do not propose an architecture; one exists.

MACHINE
- Pop!_OS Linux, user `mancier`, home /home/mancier
- MSI Vector HX 16 A2XWIG, Core Ultra 9 275HX, 96GB DDR5,
  RTX 5080 Laptop 16GB VRAM, Intel Arrow Lake NPU 13 TOPS
- venv: source ~/the-forge/.venv/bin/activate  (required before any Python)
- Ollama: gpt-oss:20b (12GB, 100% GPU, ctx 16384) + nomic-embed-text

HOW TO TALK TO ME
- Plain talk. Direct answers. Tell me when I'm wrong rather than agreeing.
  An accurate objection is worth more than agreement.
- One concrete next step at a time. I get overwhelmed by the scale.
- My terminal mangles filenames: `.py` and `.md` become markdown links.
  ALWAYS use globs (salvage*.py, frontiers*) or tab-completion in commands.
- Never give me multi-line paste blocks. They echo back and hang my shell
  on a `>` prompt. One command per line, run one at a time.
- Don't recommend Cursor (cloud backend, can't reach localhost:11434).
  VS Code Remote-SSH + Continue.dev is the answer.
- I was burned by aider, which broke a lot. Don't push autonomous agents.
  Working pattern: narrow job, full context pre-loaded, no write access to
  anything real, escalates instead of guessing.
- NEVER write into ~/the-forge or ~/FORGE_CABINET/_WORK/sorter/ unreviewed.
  A harvest agent clobbered forgelib.py once already.

THE CORE PROBLEM
The project has been rebuilt from scratch four times. Not because the code
was bad — because the reasoning was never written down, so each new session
re-derived the architecture slightly differently and forked the tree.
Three central concepts (wardrobe, flatten, baptize) existed only in my head
with ZERO hits anywhere on disk, while the things they named were already
built and tested. The fix is written vocabulary + FORGE_STATE.md, not code.

WHERE THE TRUTH LIVES (read these, in this order)
1. ~/the-forge/FORGE_STATE.md              <- the handoff contract
2. ~/the-forge/docs/session-2026-08/DO_THIS_NEXT.md
3. ~/the-forge/docs/session-2026-08/FORGE_HANDOFF.md
4. ~/the-forge/docs/session-2026-08/CAPSULE_SPEC_V1_DRAFT.md
5. ~/the-forge/docs/session-2026-08/  (33 docs total)

I also have a local RAG index over 4,038 chunks / 970 files. Ask it things
instead of guessing. Usage:
  cd ~/FORGE_CABINET/_WORK/sorter
  python3 oracle.py --config config.yaml -k 12 --sources ask "question"

BUILT AND TESTED — DO NOT REBUILD THESE
gate.py (10 tests) · capabilities.py (7 verbs) · overseer.py (268L) ·
wrap.py (6 tests, this IS the wardrobe) · sandbox.py (9 tests, this IS the
Concoctinator) · tailor.py (7 tests, this IS "the missing organ") ·
judge.py (8 tests, this defines CLEAN) · ledger.py (8 tests, hash-chained) ·
VectorMemory.burn() · Caveat/macaroon attenuation (9 tests) · capsule.py ·
hub.py · kernel.py · test_properties.py

BASELINE: 9 failed / 125 passed. At least 6 of the 9 are STALE TESTS,
not broken code:
- bind/test_bind.py (5 tests) pinned to era-1 Finding shape. Current Finding
  is era 3, where severity is a STRING.
- test_request_action_unknown_op — kernel.py:373-379 deliberately catches
  ValueError and returns {allowed: False, reason}. Correct fail-closed
  design. The test is wrong.
- test_sequence.py (1) returns rolled_back where done expected — may be real.

NOT BUILT (confirmed absent across all 4,038 chunks)
Hopper (pull-with-refusal work queue) · Keychain · Toolchain · Boneyard ·
Copilot · Surface · Splice · capsule format spec

WHERE I AM RIGHT NOW
[EDIT THIS LINE before pasting — say exactly what you just finished
 and what you were about to do next]

Confirm you've read this, then tell me the single next step.

---END PASTE---

**Before you paste it, edit the `WHERE I AM RIGHT NOW` line.** That one line
is worth more than the rest of the file, because everything else is already
on disk and recoverable — only your current position isn't.

---

## PART B — SAVE THIS FILE FIRST

This document is useless in a chat window. Get it onto disk.

Download `CROSSOVER.md` from the viewer, then, one line at a time:

    mv ~/Downloads/CROSSOVER* ~/the-forge/docs/session-2026-08/

then

    cd ~/the-forge

then

    git add docs

then

    git commit -m "docs: crossover resume brief"

then

    git push

Now it survives the tab closing, the account limiting, and the laptop dying.

---

## PART C — THE FIVE-COMMAND STATUS CHECK

Run these at the start of any new session and paste the output into the
chat. It takes thirty seconds and it grounds the new model in reality
instead of the summary's memory of reality.

    cd ~/the-forge && git log --oneline -5

then

    git status --short

then

    source ~/the-forge/.venv/bin/activate && python -m pytest -q 2>&1 | tail -5

then

    ls ~/the-forge/docs/session-2026-08 | wc -l

then

    ls ~/FORGE_CABINET/00_MANIFEST/oracle.db

Expected right now: 33 docs, baseline 9 failed / 125 passed, clean tree.
**If the numbers differ from that, trust the terminal, not the brief.**

---

## PART D — WHAT'S LEFT, RANKED

Cross items off here as you go. This is the resume pointer.

| # | Task | Effort | State |
|---|---|---|---|
| 1 | Push docs to GitHub | 2 min | ← doing now |
| 2 | Remove `.aider.chat.history.md` from the repo + `.gitignore` | 5 min | |
| 3 | Investigate the `Updated \`forge/fabric/gate.py` paste artifact | 5 min | |
| 4 | Re-index Oracle (kills 73 aider chunks) | 10 min unattended | |
| 5 | 6 corrections to `frontiers.ts` | 10 min | see DO_THIS_NEXT §2 |
| 6 | Fix the 6 stale tests → baseline ~3 failed | 30 min | |
| 7 | **Build #1 — capsule spec** | a session | R4 + smart_capsule are 2/3 of it |
| 8 | Build #2 — Hopper (from zero, never existed) | a session | |
| 9 | Index `~/openhuman` before installing any of it | 15 min | unexamined agent system |
| 10 | `sudo apt install ripgrep fd-find fzf bat tmux jq` | 2 min | |
| 11 | `mv "$HOME/Downloads/ForgeOS-Arch-Rev " ~/Downloads/ForgeOS-Arch-Rev` | 1 min | trailing space, breaks commands |

---

## PART E — CORRECTION TO MY OWN CAPSULE DRAFT

`CAPSULE_SPEC_V1_DRAFT.md` §3 has an incomplete lifecycle machine. You
pasted the real R4 and it is richer:

```
DRAFT → VALIDATED → ACTIVE → PAUSED → ARCHIVED
                 ↓         ↓
              INVALID    DESTROYED

ACTIVE → EXECUTING → ACTIVE (on completion)
       → EXECUTING → FAILED → ACTIVE (on retry) | PAUSED (on max retries)
```

Missing from my draft: `INVALID`, `DESTROYED`, `EXECUTING`, `FAILED`.

**`EXECUTING` is the important one.** It's the state that makes M4 open
finding C (promotion atomicity) *expressible*: a swap interrupted mid-flight
is a capsule stuck in `EXECUTING` with no defined recovery. Without that
state in the machine you cannot even name the bug, let alone fix it.

Also fold in from R4, which my draft under-specified: `required_capabilities`
vs granted `capabilities` (two different lists), `min_context_window`,
`preferred_sockets`, and the memory reference block
(`conversation_id` / `working_memory_id` / `long_term_memory_id`).

---

## PART F — THINGS A NEW SESSION WILL GET WRONG

Pre-empt these. Every one has already cost real time.

1. **It will suggest rebuilding something that exists.** The wardrobe is
   `wrap.py`. The Concoctinator is `sandbox.py`. The Foundry is `tailor.py`.
   "The missing organ" was built at M4 — the filename label is stale.
2. **It will treat `Finding.severity` as an int.** It's a **string** in era 3.
3. **It will trust `peer_review.py`'s threat regex as a security boundary.**
   It is advisory only. It misses `rm -r -f /`, `rm --recursive --force`,
   `find . -delete`, and anything base64'd. Denylists enumerate badness and
   are unbounded; the Gate enumerates goodness and is bounded.
4. **It will propose seL4 or Intel SGX.** SGX is deprecated on consumer CPUs
   (Xeon only), TDX is Xeon-only, and the 275HX has neither. seL4 has no
   Linux userland, so no Ollama/CUDA/OpenVINO. Design toward it, build
   nothing.
5. **It will suggest async everywhere.** `authorize()` is SYNC by locked
   decision — it must not stall the event loop. The 8 core slice-mechanics
   tests are `def`, not `async def`, and that's deliberate: Law 4 compatible.
6. **It will invent a meaning for `crumbs`.** Don't let it. The only evidence
   in 4,038 chunks is `[{"crumb": "breadcrumb"}]` in one test line. It is
   RESERVED: preserve verbatim, never interpret.
7. **It will call the HopperQueue in `fabric_sandbox_hopper.py` "the Hopper".**
   It isn't. That's the **SlotGovernor** — an `asyncio.Semaphore` with
   `acquire_slot`/`release_slot` and no refusal path. Five different things
   have been called "hopper"; the real one has never been built.

---

## PART G — THE ONE-PARAGRAPH VERSION

If you have room for nothing else, paste this:

> I'm resuming THE FORGE, a local-first security-hardened AI-native OS on
> Pop!_OS. It's been rebuilt 4 times because reasoning was never written
> down. The architecture already exists — read
> `~/the-forge/docs/session-2026-08/DO_THIS_NEXT.md` and
> `~/the-forge/FORGE_STATE.md` before proposing anything. There's a local
> RAG index of 4,038 chunks: `cd ~/FORGE_CABINET/_WORK/sorter && python3
> oracle.py --config config.yaml -k 12 --sources ask "..."`. Talk plain,
> object when I'm wrong, one step at a time, never give me multi-line paste
> blocks, always use globs in commands because my terminal mangles `.py` and
> `.md` filenames.
