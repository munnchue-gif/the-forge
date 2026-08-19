# THE FORGE — Multi-Account Isolation Architecture + Rebuild Plan

Built from the 14 PDFs you've now supplied. This is the layout, the anti-drift
mechanism, and the prompts, in the order you should execute them.

---

## PART 0 — What these new PDFs proved

Three of them are **more authoritative than anything you'd sent before**:

### The Graded Master List — your own rubric, already done
You graded 19 pieces yourself, with weak spots and next bricks. Two of them
name real security bugs in precise terms:

| Piece | Weak spot you identified | Fix you specified |
|---|---|---|
| **Gate** | *"Rejects 2 identical legit actions as false replay"* | *"Add a nonce field"* |
| **Capabilities** | *"Unescaped `\|` delimiter — crafted name could shift signed string"* | *"Escape/hash the delimiter"* |

Both are **real vulnerabilities**, found by you, and the M5 doc confirms both
shipped. That delimiter injection is a genuine signature-forgery vector — most
people never find that in their own code.

### Kimi review + Deep Dive — independent audit, test velocity tracked
```
M4: 53 tests → M5: 92 → M6: 108 → (your live tree today: 134)
```
Growth +104% M4→M6. And the reviewer's verdict on distro-hopping:
**"RECOMMENDATION: Do NOT migrate"** — the RTX 5080 issues are
distro-agnostic. Relevant to your wipe plan: a fresh OS won't fix hardware
friction, and you already solved the NPU.

### Your two prompt templates — you already invented the anti-drift tool
- `External Observer Prompt (paste at each milestone)`
- `Helper Agent Onboarding Prompt`

You wrote these to hand context to a fresh model. **That is exactly the
mechanism I've been arguing you need.** It already exists. It just wasn't
enforced automatically, so it got skipped when sessions ran out.

### The "Whoa, stop right there" PDF — the drift, caught live
A model reading a pasted ZIP binary, seeing only filenames, and saying *"cancel
that, we need those documents first."* That's a session discovering mid-flight
that it lacked context. Perfect specimen of the failure mode.

---

## PART 1 — Why AIs keep touching files you told them not to

You described it exactly: *"even if they're told not to look at them, they
start trying to fix them... or they just start a new project."*

Three real causes, three real fixes:

| Cause | Fix |
|---|---|
| The files are **visible**. Any `ls`, `grep`, or repo scan surfaces them, and a helpful model treats visible brokenness as work. | **Physical isolation.** Not instructions — different directories, different repos, different accounts. |
| The model can't tell **canonical from archive**. Nothing in the filesystem says "this is dead." | **Machine-readable status.** A `FORGE_STATE.md` at repo root + `.forge-archive` marker files. |
| Running out of context mid-task → the next session **re-derives** rather than resumes. | **Read-first/write-last contract**, enforced by a git pre-commit hook, not by hope. |

**Instructions in a prompt cannot fix a filesystem problem.** Isolation has to
be structural.

---

## PART 2 — The multi-account, multi-model architecture

Your design, formalised. This is genuinely good — it's the same
"deaf-by-default, one Gate" principle applied to your *workflow* rather than
your code.

### The shape

```
                    ┌──────────────────────────────┐
                    │   HOME ACCOUNT (munnchue)    │
                    │   the single source of truth │
                    │                              │
                    │   Drive: FORGE_MASTER/       │
                    │   GitHub: the-forge (master) │
                    │   Obsidian: ForgeVault       │
                    └──────────────┬───────────────┘
                                   │ read-only mount / API
              ┌────────────────────┼────────────────────┐
              │                    │                    │
     ┌────────▼───────┐   ┌────────▼───────┐   ┌────────▼───────┐
     │ ACCOUNT: AMBER │   │ ACCOUNT: JADE  │   │ ACCOUNT: SLATE │
     │ organ: gate    │   │ organ: hopper  │   │ organ: keychain│
     │ Drive: A-AMBER │   │ Drive: B-JADE  │   │ Drive: C-SLATE │
     │                │   │                │   │                │
     │ repo: amber-01 │   │ repo: jade-01  │   │ repo: slate-01 │
     │ repo: amber-02 │   │ repo: jade-02  │   │ repo: slate-02 │
     │  (model 01,02) │   │  (model 01,02) │   │  (model 01,02) │
     └────────┬───────┘   └────────┬───────┘   └────────┬───────┘
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   │  PR only — never direct push
                    ┌──────────────▼───────────────┐
                    │   THE ARENA (vote / grade)   │
                    │   compare.py + observer      │
                    │   prompt + your rubric       │
                    └──────────────┬───────────────┘
                                   │ merge winner only
                              HOME / master
```

### Naming scheme

```
<COLOR>-<MODEL#>-<ORGAN>-<SEQ>

amber-01-gate-003        Amber account, model 01, gate work, 3rd attempt
jade-02-hopper-001       Jade account, model 02, hopper work, 1st attempt
slate-01-keychain-007
```

Every artifact self-identifies: which account, which model, which organ, which
attempt. **Provenance is in the name**, so a file can never become anonymous.

### The mirror-with-different-names trick

You asked for a mirrored copy with changed names. Do it like this:

| Master (home) | Mirror (worker accounts) |
|---|---|
| `the-forge` | `<color>-fabric` |
| `forge/fabric/gate.py` | `fabric/door.py` |
| `forge/fabric/overseer.py` | `fabric/watcher.py` |
| `forge/fabric/hopper.py` | `fabric/sorter.py` |
| `FORGE_STATE.md` | `STATE.md` |

Why it works: a model in the Amber account **grepping for "forge" finds
nothing**. It cannot accidentally reach into master's namespace, cannot
"helpfully" fix a file it shouldn't see, and cannot confuse the two trees. The
rename is enforced by a mapping file, applied on export/import.

**One warning:** keep the mapping in exactly one place
(`MIRROR_MAP.json`, home account only). Two copies of a rename map is a new
drift source. Generate the mirror; never hand-edit it.

### Virtual drive per model

Your instinct — *"instead of a melting pot, isolate then vote"* — is correct
and it has a name: **N-version programming**. Independent implementations,
compared afterward. It's how avionics does redundancy.

Cheapest correct implementation on Pop!_OS: **git worktrees**, not VMs.

```bash
# one repo, N isolated working directories, zero VM overhead
git worktree add ../amber-01-gate  -b amber-01-gate
git worktree add ../jade-02-hopper -b jade-02-hopper
```

Each model gets a directory that *is* a branch. It cannot see the others'
files. Merging is a normal PR. If you want harder isolation later, add
`systemd-run --scope -p PrivateNetwork=yes` per worker (Prompt 5 in the build
pack).

---

## PART 3 — The Arena (voting layer)

You already have three of the four pieces:

| Piece | Status |
|---|---|
| Independent implementations | git worktrees, above |
| Structural comparison | **`compare.py`** — already built and working |
| Review prompt | **your External Observer Prompt** — already written |
| Scoring rubric | **your Graded Master List rubric** — already written |

What's missing is the harness that runs them together. That's `arena.py`,
Prompt 4 below — ~150 lines, not a new system.

**Your rubric, reused verbatim:**

```
🟢 GREEN     solid, built, tested
🟡 YELLOW    needs a look
🟠 ORANGE    needs custom work
🔴 RED       weak / missing
🟣 PURPLE    revolutionary
★☆☆☆☆       priority (1-5)
```

Columns from your master list: `Piece | Type | Grade | What It Is | What Part
It Serves | Weak Spots | Upgrade / Next Brick`.

Don't invent a new rubric. This one is yours, it's proven, and it already
caught two security bugs.

---

## PART 4 — The collection bot (before the wipe)

You want a bot on the GPU to gather and categorise everything. **You already
have 80% of it** — the cabinet sorter. What it needs for a full-drive sweep:

1. **Model-assisted grading** for files the heuristics score in the middle
   band. Only those — running an LLM over 40,000 files is a waste.
2. **Content clustering** — group near-identical copies across 11 repos so you
   review a cluster once, not 11 times.
3. **PDF/doc extraction** — you have many PDFs; the sorter currently
   quarantines them as binary.

That's `harvest.py`, Prompt 3. It reuses `scan.py` + `grade.py` and adds an
Ollama call for the ambiguous middle.

**Model for the job:** `qwen3-coder:30b` if it fits alongside your work, else
`gpt-oss:20b`. Grading is short-context classification — a 20B is plenty.
Keep `OLLAMA_CONTEXT_LENGTH=8192` for this task; you're classifying snippets,
not reasoning over repos.

---

## PART 5 — Order of operations (do NOT reorder)

```
STAGE 1  ── Capture (before touching anything)
  1.1  Write FORGE_STATE.md on the OLD pc, commit, push
  1.2  Run harvest.py over the whole old drive → FORGE_CABINET
  1.3  Push cabinet manifests + 06_ARCHIVE_RAW to Drive/Ventoy
  ✅ gate: grades.csv exists and you have read it

STAGE 2  ── Consolidate
  2.1  Finish recoveries: forge.py, ledger.py, validate_ledger.py
  2.2  Fix kernel factory table (real bug)
  2.3  Merge gate PathwayRegistry
  2.4  Re-sync bind tests
  ✅ gate: test baseline improves from 11 failed → ≤2 failed

STAGE 3  ── Structure the anti-drift system
  3.1  Create MIRROR_MAP.json + export script
  3.2  Set up worker accounts (color/organ/model naming)
  3.3  Build arena.py
  3.4  Obsidian vault + Git plugin + MCP, pointed at FORGE_STATE.md
  ✅ gate: a worker account can produce a PR that arena.py grades

STAGE 4  ── Wipe (only now)
  4.1  Verify cabinet is on Ventoy AND Drive AND GitHub
  4.2  Fresh Pop!_OS (Kimi: do NOT distro-hop — 5080 issues follow you)
  4.3  Restore: one repo, one vault, one cabinet
  ✅ gate: pytest matches pre-wipe baseline exactly
```

**Each stage has a gate. Do not pass a gate on optimism.**

---

## PART 6 — THE PROMPTS

One per session. Paste `FORGE_STATE.md` above each one.

---

### PROMPT A — The isolation exporter (build first, it protects everything else)

```text
Build ~/the-forge/tools/mirror_export.py — produces a renamed, isolated copy
of the Forge for a worker account, so a model in that account can never see
or reach the master namespace.

Problem being solved: AI sessions in other accounts see files they were told
to ignore, then "helpfully" modify them or fork the project. Prompt
instructions do not prevent this. Physical renaming does.

Requirements:
  - Read MIRROR_MAP.json:
      {
        "repo":   {"the-forge": "amber-fabric"},
        "paths":  {"forge/fabric": "fabric"},
        "files":  {"gate.py": "door.py",
                   "overseer.py": "watcher.py",
                   "hopper.py": "sorter.py",
                   "FORGE_STATE.md": "STATE.md"},
        "tokens": {"forge": "amber", "Forge": "Amber",
                   "FORGE": "AMBER", "fabric": "weave"}
      }
  - export(src_repo, dest_dir, map_file, *, account, organ, model_no)
      * copy the tree, applying path + filename renames
      * rewrite file CONTENTS with the token map, whole-word only
        (re.sub with \b boundaries — never substring-mangle)
      * skip .git entirely; the mirror is a fresh repo
      * write MIRROR_PROVENANCE.json: source sha, map sha, timestamp,
        account, organ, model_no
      * write STATE.md derived from FORGE_STATE.md with tokens applied
  - verify(dest_dir) -> list[str]: return every remaining occurrence of any
    master token. Must be EMPTY or the export fails loudly.
  - reimport(mirror_dir, out_patch) : reverse the token map and emit a patch
    against master, so work comes home in master's vocabulary.

Hard rules:
  - Never write inside src_repo. Reuse the assert_writable() guard pattern
    from FORGE_CABINET/_WORK/sorter/forgelib.py.
  - Whole-word replacement only. "forge" must not corrupt "forget".
  - Deterministic: same input + same map = byte-identical output.
  - Stdlib only.

Tests: round-trip export→reimport equals the original; verify() catches a
planted leaked token; substring safety ("forget" survives untouched);
provenance file is written and valid.

Branch: feat/mirror-export
```

---

### PROMPT B — FORGE_STATE.md, with enforcement

```text
Create ~/the-forge/FORGE_STATE.md AND the hook that makes it non-optional.

PART 1 — the file. Under 200 lines. Sections:

  1. LOCKED DECISIONS (date + one-line reason). Seed with:
     - authorize() is SYNC, never async — must not stall the event loop
     - canonical root is forge/fabric/ — supersedes forge/<organ>/,
       backend/kernel/, forge_ng/fabric/
     - models are wrapped (SHA-256) on entry; no raw model ever runs
     - deaf-by-default; no wildcard subscribe; Overseer holds the only tap
     - couplers built LAST — #1 attack surface
     - NPU path is OpenVINO GenAI only (ipex-llm is Windows-only,
       intel-npu-acceleration-library is deprecated)
     - DO NOT distro-hop; RTX 5080 issues are distro-agnostic (Kimi review)
     - capsule became fabric: the spawning sandbox wrapper that oversees
       all without holding kernel authority

  2. VOCABULARY (the Rosetta stone — stop re-deriving these):
       wardrobe   = WrapStore
       baptism    = wrap-conform
       flatten    = Reclaim capability
       commander  = the acting half of Overseer
       conduit    = VectorConduit (hears, cannot order)
       suit       = Wrap / the Substance

  3. CANONICAL SHAPES — paste real dataclasses from live code for Finding,
     Capability, LedgerEntry, Wrap. Note: Finding.severity is a STRING enum.

  4. ORGAN STATUS — name, file, tests, GREEN/YELLOW/ORANGE/RED/PURPLE,
     using the Graded Master List rubric.

  5. KNOWN BROKEN, with file:line:
     - forge/fabric/kernel.py:80-82 factory table passes rejected kwargs
     - bind/test_bind.py — 5 tests pinned to a pre-refactor Finding
     - BASELINE: 11 failed, 123 passed. Any other number = you caused it.

  6. DO NOT REBUILD — what exists and where.

  7. OPEN QUESTION — exactly one, for the next session.

PART 2 — enforcement. Create .git/hooks/pre-commit (and commit a copy at
tools/hooks/pre-commit with an install script):
  - if any file under forge/ is staged AND FORGE_STATE.md is not staged,
    REJECT with:
       "FORGE_STATE.md not updated. Update the state contract or use
        --no-verify if this is genuinely a no-op change."
  - always allow docs-only commits.

This is the anti-drift core. Instructions get skipped; hooks do not.

Commit: docs(state): add handoff contract + enforcement hook
```

---

### PROMPT C — The harvest bot (GPU-assisted, for the whole old drive)

```text
Build ~/FORGE_CABINET/_WORK/sorter/harvest.py — full-drive collection with
local-model assistance, extending the existing sorter.

Existing pieces to reuse, do not rewrite: scan.py (walk+sha256),
grade.py (heuristic scoring), forgelib.py (Config, assert_writable).

Add three things:

1. DOCUMENT EXTRACTION
   - .pdf via pypdf, .docx via python-docx, .html via stdlib html.parser
   - extracted text feeds the SAME concept scoring as .md files
   - currently these are quarantined as binary; they are often the most
     valuable artifacts (architecture guides, reviews, graded lists)

2. CONTENT CLUSTERING
   - group files by normalised-content similarity, not just exact sha
   - normalise: strip whitespace, comments, and docstrings before hashing
   - emit clusters.csv: cluster_id, member_count, best_member, members
   - purpose: 11 repos hold near-identical copies; review the cluster once

3. MODEL-ASSISTED GRADING (the ambiguous middle band ONLY)
   - for files scoring between thresholds.bronze and thresholds.gold,
     call a local Ollama model
   - POST http://127.0.0.1:11434/api/generate, stream=false
   - send: path, first 2000 chars, the heuristic score and reasons
   - ask for STRICT JSON: {"grade":"GOLD|SILVER|BRONZE|QUARANTINE",
                            "confidence":0.0-1.0, "why":"one sentence",
                            "concepts":["..."]}
   - if the model disagrees with the heuristic by more than one grade,
     mark it REVIEW and never auto-file it
   - --model flag, default gpt-oss:20b; --no-model to skip entirely
   - hard timeout 30s per file; on any failure keep the heuristic grade

Hard rules:
  - copy-only; assert_writable() on every write
  - resumable: skip files already in graded.jsonl unless --force
  - print a running count; this will process tens of thousands of files
  - the model NEVER decides alone — it adjusts a heuristic score, and
    disagreement escalates to human review

Tests: pdf text extraction works; clustering groups reformatted duplicates;
model failure falls back cleanly; REVIEW is set on large disagreement.

Branch: feat/harvest-bot
```

---

### PROMPT D — The Arena (isolate → compare → vote → merge)

```text
Build ~/the-forge/tools/arena.py — grade N independent implementations of the
same organ and pick a winner. Implements N-version programming: isolated
attempts, compared afterward, never merged blind.

Inputs: 2+ git branches (or worktree paths) that each implement the same
organ, plus the organ name.

Requirements:
  - spawn(organ, n, *, base="master")
      create n git worktrees named <color>-<model#>-<organ>-<seq>,
      each on its own branch, each with a copy of the task prompt
  - collect(organ) -> list[Candidate]
      find all worktrees/branches for that organ
  - grade(candidates) -> ArenaReport
      For each candidate compute:
        * tests_pass / tests_fail   (run pytest -q in the worktree)
        * delta_vs_baseline         (baseline from FORGE_STATE.md)
        * api_surface               (AST: classes + public functions)
        * lines, docstring_coverage
        * concept_hits              (terms from FORGE_STATE.md vocabulary)
        * gate_violations           (writes outside allowed paths, new
                                     network calls, async on decision path,
                                     wildcard bus subscribe)
      Reuse the AST logic in FORGE_CABINET/_WORK/sorter/compare.py.
  - report(organ) -> writes ARENA/<organ>.md with:
        * a table using the Graded Master List rubric columns:
          Piece | Grade | What It Is | Weak Spots | Next Brick
        * per-candidate symbol diff (only in A / only in B)
        * a RECOMMENDED winner with explicit reasoning
        * the External Observer Prompt, pre-filled with the diff, ready to
          paste into a second AI for an independent opinion
  - promote(organ, winner) -> creates a PR-ready branch merged from winner
        onto base, and REFUSES if tests regress against baseline

Hard rules:
  - arena.py NEVER auto-merges. It recommends; a human promotes.
  - Any candidate with gate_violations is disqualified regardless of score.
  - Grades use the existing rubric: GREEN/YELLOW/ORANGE/RED/PURPLE + ★1-5.
  - Read-only against every candidate except when promote() is called.

Tests: two toy branches are graded and ranked; a gate violation disqualifies;
promote refuses on test regression; report renders valid markdown.

Branch: feat/arena
```

---

### PROMPT E — Obsidian + MCP wiring (last, after structure exists)

```text
Wire Obsidian as the memory layer for the Forge, with MCP access.

Two repos, never one:
  - the-forge   : code. Human commits only. NEVER auto-committed.
  - forge-vault : notes. Obsidian Git auto-commit every 10 minutes.

Vault structure:
  00 Inbox/          unsorted capture
  10 State/          FORGE_STATE.md (symlink to the repo copy — one source)
  20 Cabinet/        auto-dropped REPORT.md from diff_spine.py
  30 Concepts/       one note per concept, linked to concepts.csv rows
  40 Arena/          ARENA/<organ>.md reports
  50 Daily/          session logs
  90 Archive/

Tasks:
1. Install the Obsidian Git plugin; auto-commit 10m, auto-push on,
   auto-pull on start. Add .gitignore for .obsidian/workspace.json and
   workspace-mobile.json.
2. Install the Local REST API plugin; copy the API key.
3. Register three NARROW MCP servers:
     - obsidian    : uvx mcp-obsidian, env OBSIDIAN_API_KEY
     - filesystem  : scoped to ~/FORGE_CABINET ONLY (never $HOME)
     - github      : the-forge + forge-vault only
4. Write tools/session_start.sh that prints FORGE_STATE.md and the current
   test baseline, so every session begins with the contract in context.
5. Write tools/session_end.sh that: runs pytest, appends the result to
   50 Daily/<date>.md, and reminds you to update the OPEN QUESTION.

Hard rule: the filesystem MCP is scoped to the cabinet. Do not give a
filesystem MCP your whole home directory — unscoped filesystem access across
sessions is how the sprawl happened in the first place.
```

---

## PART 7 — Honest cautions

**The mirror rename adds real cost.** Every merge back through `reimport()` is
a translation step, and translation steps can fail. It's worth it *only*
because you're running multiple accounts. If you consolidate to one account
later, drop the mirror and keep the worktrees.

**Multi-account use may conflict with provider terms.** Check the ToS for each
service you're using this way. The technical design is sound either way; I'm
flagging the policy question because it's your risk to weigh, not mine to
assume.

**Don't build all five tools before using any.** Prompt A and B alone stop the
bleeding. C is only needed for the wipe. D and E are optimisations. If you
build A+B this week and nothing else, you're ahead.

**Kimi's warning applies directly to your wipe plan:** the 5080 friction is
distro-agnostic, and you already fixed the NPU. A fresh OS gets you a clean
disk, not a smoother stack — so wipe for tidiness, not for a fix.

---

## PART 8 — What to do in the next hour

1. `git worktree add ../forge-state -b docs/forge-state`
2. Run **Prompt B**. Get `FORGE_STATE.md` + the pre-commit hook committed.
3. Push it.

That single file is what converts "start over for the fifth time" into
"resume." Everything else in this document is optional by comparison.
