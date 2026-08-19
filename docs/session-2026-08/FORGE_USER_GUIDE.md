# THE FORGE — USER GUIDE

Everything you built, how to run it, and how to get the most out of the models.
Written to be read cold.

---

# ■ SECTION 1 · WHERE YOU ARE RIGHT NOW

## The three things that matter

```
~/the-forge/          THE SPINE — the only living code. 189 files.
                      Baseline: 9 failed / 125 passed.
                      Pushed to github.com/munnchue-gif/the-forge

~/FORGE_CABINET/      THE HARVEST — everything else, graded and archived.
                      ~1,700 files in 06_ARCHIVE_RAW.
                      This is what makes deleting safe.

~/FORGE_CABINET/00_MANIFEST/oracle.db
                      THE INDEX — 4,038 chunks, 970 files.
                      Ask it anything about your own work.
```

## Your next three actions

1. **Apply the 6 corrections** to `~/newapps/arch/src/data/frontiers.ts`
   (10 min, by hand, no model needed — see §7)
2. **Save this session's docs** into `~/the-forge/docs/` and push
3. **Build #1** — the capsule spec. Half of it already exists: R4 gives the
   manifest, `smart_capsule.py` gives the runtime.

---

# ■ SECTION 2 · THE COMMAND CHEAT SHEET

Every command starts the same way:

```bash
cd ~/FORGE_CABINET/_WORK/sorter
source ~/the-forge/.venv/bin/activate
```

## 2.1 · THE ORACLE — ask your own files anything

| Command | What it does |
|---|---|
| `python3 oracle.py --config config.yaml index` | build/refresh the index |
| `python3 oracle.py --config config.yaml index --root ~/newfolder` | add a new folder |
| `python3 oracle.py --config config.yaml ask "question"` | one question |
| `python3 oracle.py --config config.yaml --sources ask "q"` | show which files it read |
| `python3 oracle.py --config config.yaml chat` | interactive, `q` to quit |
| `python3 oracle.py --config config.yaml -k 15 ask "q"` | more context for broad questions |
| `python3 oracle.py --config config.yaml stats` | what's indexed |

**`-k` guide:** 8 for lookups · 15 for comparisons across files · 20+ only if
you're mapping a whole subsystem.

**Always use `--sources` when the answer surprises you.** It shows you exactly
what it read, so you can tell a good answer from a confident one.

## 2.2 · THE SORTER — find and grade files

| Command | What it does |
|---|---|
| `python3 scan.py --config config.yaml --root ~/folder` | walk + hash → `scan.jsonl` |
| `python3 archive_copy.py --config config.yaml` | verbatim copy → `06_ARCHIVE_RAW` |
| `python3 grade.py --config config.yaml` | score → GOLD/SILVER/BRONZE/DUP/QUARANTINE |
| `python3 tune.py --config config.yaml` | score histogram, tune thresholds |
| `python3 compare.py --config config.yaml` | AST-diff candidates vs your spine |
| `python3 compare.py --config config.yaml --file x.py --diff` | deep dive one file |
| `python3 xdoc.py ~/folder` | extract text from .docx/.xlsx/.pptx |
| `python3 port.py --config config.yaml --list` | what's safely portable |
| `python3 port.py --config config.yaml --module x.py` | port on an isolated branch |

**The order matters:** scan → archive → grade → compare. Skipping `grade` means
`compare` reads stale data (this bit you once).

## 2.3 · SALVAGE — model-assisted file inventory

```bash
python3 salvage.py --config config.yaml --dir ~/FORGE_REVIEW --dry-run
python3 salvage.py --config config.yaml --dir ~/FORGE_REVIEW --num-predict 4000
python3 salvage.py --config config.yaml --dir ~/FORGE_REVIEW --group crypto
```

Writes a parts sheet per file to `00_MANIFEST/salvage/`. Verdicts:
`PORT_NEARLY_AS_IS` → `MINE_MECHANISMS` → `READ_ONLY_REFERENCE` → `DISCARD`.

**Verdicts are suggestions, not decisions.** The same file scored differently
on two runs. Read the reasoning, not the label.

## 2.4 · GRID — isolate agents from each other

```bash
python3 grid.py --config config.yaml init
python3 grid.py --config config.yaml add --color GREEN --agent claude --organ gate
python3 grid.py --config config.yaml claim --color GREEN --agent claude --read ~/the-forge/forge/fabric
python3 grid.py --config config.yaml check      # audit for violations
python3 grid.py --config config.yaml status
```

## 2.5 · OLLAMA

| Command | What it does |
|---|---|
| `ollama ps` | what's loaded — **must say 100% GPU** |
| `ollama list` | what's downloaded |
| `ollama run gpt-oss:20b "ok"` | load a model into memory |
| `ollama stop gpt-oss:20b` | free the VRAM |
| `nvidia-smi` | actual GPU usage |

**If `ollama ps` shows any CPU split, stop.** The model is too big or the
context is too long. Everything will take hours instead of minutes.

## 2.6 · GIT — the safety net

```bash
git status --short                      # what changed
git --no-pager diff                     # review before committing
git checkout -b feat/thing              # new branch for new work
git add file && git commit -m "msg"     # commit
git push origin master
git checkout master && git branch -D feat/thing   # abandon completely
git stash list                          # you had a forgotten fix in here once
```

**One branch per organ. Never work on master.**

---

# ■ SECTION 3 · THE DAILY WORKFLOW

## Starting a session

```bash
cd ~/the-forge && source .venv/bin/activate
cat FORGE_STATE.md | head -40          # what's locked, what's broken
python3 -m pytest -q 2>&1 | tail -1    # confirm baseline: 9 failed / 125 passed
ollama ps                              # confirm GPU
```

## Before building anything

**Ask the Oracle first. Every time.**

```bash
cd ~/FORGE_CABINET/_WORK/sorter
python3 oracle.py --config config.yaml -k 15 --sources ask \
  "does an implementation of <the thing> already exist anywhere?"
```

This is the single habit that ends the rebuild loop. It took four seconds to
learn that no pull-with-refusal queue has ever existed — a fact that would have
taken a week to establish by hand.

## Ending a session

```bash
python3 -m pytest -q 2>&1 | tail -1    # did the baseline move?
git status --short                      # anything uncommitted?
# UPDATE FORGE_STATE.md §7 — what you did, what's next
git add -A && git commit -m "..." && git push
```

**Updating §7 is the whole game.** It is the difference between resuming and
starting over.

## Weekly

```bash
python3 oracle.py --config config.yaml index      # incremental, cheap
```

---

# ■ SECTION 4 · HOW TO GET THE MOST OUT OF THE MODELS

## 4.1 · What actually fits on 16 GB VRAM

| Model | VRAM | Use for |
|---|---|---|
| `nomic-embed-text` | 0.3 GB | embeddings only (Oracle) |
| `qwen2.5-coder:7b` | ~5 GB | fast edits, structured output |
| `qwen2.5-coder:14b` | ~9 GB | **best all-round coder for this box** |
| `gpt-oss:20b` | ~12 GB | reasoning, analysis, salvage |
| `qwen3-coder:30b` | ~18 GB | slight overflow, still usable |
| **70B anything** | ~40 GB | **does not fit — 1-3 tok/s, unusable** |

**A 70B on this machine is not "slower." It is a different activity.** A
500-line file becomes a 20-minute wait. You will stop using it.

## 4.2 · The settings that matter

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
printf '[Service]\nEnvironment="OLLAMA_CONTEXT_LENGTH=16384"\nEnvironment="OLLAMA_KEEP_ALIVE=30m"\nEnvironment="OLLAMA_FLASH_ATTENTION=1"\nEnvironment="OLLAMA_NUM_PARALLEL=1"\n' | sudo tee /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

**Context length matters more than model size.** Asking for 128k on a 16 GB
card blows the KV cache into system RAM and silently drops you to CPU speed.
That is the usual cause of "it worked yesterday."

## 4.3 · Known model quirks — these cost you hours

**gpt-oss:20b structured output is broken.** Verified on your machine:

```
format: {schema}   →  ""        empty
format: "json"     →  garbage
no format          →  clean JSON   ✅
```

**Ask for JSON in words and parse defensively.** Never use the `format` field
with this model.

**gpt-oss:20b burns tokens reasoning before answering.** Budget 2–4× the
tokens you think you need for `num_predict`, or you get truncated output.

**Local models hallucinate file paths confidently.** Your salvage run cited
`capsule.py`, `health_monitor`, and `commit_engine` as duplicates — none of
which exist in your spine. **Citations prove provenance, not truth.**

## 4.4 · Making the most of every call

Ordered by impact:

**1. Put stable content first, variable content last.** Context is processed
as a prefix. Same architecture context → same prefix → faster. Never interleave
stable and variable parts.

**2. Retrieve, don't dump.** RAG cuts context 50–80% versus sending whole
files. That's what the Oracle does — 8 relevant chunks instead of 970 files.

**3. Put the important thing at the start or the end.** Models perform
measurably worse on information buried in the middle of a long context. Task
instructions first, background in the middle.

**4. One narrow question per call.** `salvage.py` works because it asks one
thing with full context. An open-ended "fix my architecture" gets you a fifth
hopper.

**5. Right-size per task.** Grading and classification → 7b. Code generation →
14b. Analysis and comparison → 20b. Don't use the big model for sorting.

**6. Prune between turns.** Completed tool output, verbose logs, and repeated
instructions are dead weight. In long chats, restate the current state
compactly instead of relying on scrollback.

## 4.5 · Cloud chats — making them last

You hit context limits in long sessions. Three things help:

- **Paste `FORGE_HANDOFF.md` as the first message of a new chat.** It is
  self-contained: thesis, vocabulary, laws, what exists, what's broken, and
  where you left off. Nothing before it is needed.
- **Send one file at a time**, not folders. A 133 KB `master_pack.md` will
  consume most of a window on its own.
- **Prefer text over PDF.** PDF extraction mangles indentation and has twice
  produced the wrong document entirely (Colab release notes, a Next.js
  template). Use `.py`, `.md`, `.txt`.

---

# ■ SECTION 5 · TOOLS WORTH INSTALLING

## 5.1 · Install these first (10 minutes, permanent payoff)

```bash
sudo apt install ripgrep fd-find fzf bat tmux jq
```

| Tool | Replaces | Why |
|---|---|---|
| **ripgrep** (`rg`) | grep | 10–100× faster, respects `.gitignore` |
| **fd** | find | sane syntax, no `-name` quoting pain |
| **fzf** | manual file picking | fuzzy-find anything interactively |
| **bat** | cat | syntax highlighting + line numbers |
| **tmux** | multiple windows | sessions survive disconnects |
| **jq** | manual JSON reading | your `.jsonl` manifests become readable |

**ripgrep alone would have saved you hours today:**

```bash
rg "commit_slice_swap" ~/Downloads ~/Forge --type py
rg -l "class Fabric" ~ --glob '!.venv'
```

Fast enough to search everything you own in under a second, and it skips
`node_modules` and `.venv` by default — no more `-not -path` chains.

## 5.2 · Handling the trailing-space folder

`~/Downloads/ForgeOS-Arch-Rev ` has a trailing space and has broken a dozen
commands. Fix it once:

```bash
mv "$HOME/Downloads/ForgeOS-Arch-Rev " ~/Downloads/ForgeOS-Arch-Rev
```

Or always capture it in a variable:

```bash
S=$(find ~/Downloads -maxdepth 1 -type d -name "ForgeOS-Arch-Rev*" | head -1)
```

## 5.3 · Context packing for cloud chats

```bash
pip install repomix        # or: npx repomix
repomix ~/the-forge/forge/fabric --output /tmp/fabric.txt
```

Packs a whole directory into one prompt-ready file with a token count. Useful
when you need a cloud model to see a subsystem at once.

## 5.4 · Editor — VS Code Remote-SSH

Already the right answer. **Do not switch to Cursor** — it routes every request
through its own cloud backend, so `localhost:11434` is unreachable and you'd
need a public tunnel to use your local model. That defeats the point.

```bash
# on the Pop!_OS box, once
sudo apt install -y openssh-server && sudo systemctl enable --now ssh
```

Then in VS Code: install **Remote - SSH**, connect, and install the **Python**
extension on the remote. Add **Continue** if you want local-model chat inside
the editor — it calls `localhost:11434` directly, no tunnel.

For markdown files like these guides: `Ctrl+Shift+V` renders them properly.

## 5.5 · Agents — the honest assessment

You said an agent "messed a lot of things up." That matches what happened here:
one rewrote `forgelib.py`, another produced a fifth hopper.

**The failure was never capability. It was visibility.** An agent that cannot
see what exists will rebuild it, confidently, every time.

The pattern that works is what you already have:

| Property | Why it matters |
|---|---|
| **Narrow job** | one question per call |
| **Full context pre-loaded** | laws, vocabulary, what's built |
| **No write access to anything real** | output goes to a review folder |
| **Escalates instead of guessing** | `questions_for_human` field |

`salvage.py` has all four. That's why it processed 8 files with zero drift.

If you want an autonomous editor later, **Aider** is the least-bad option —
git-native, so every change is a commit and `git revert` is your undo. Run it
with `--no-auto-commits` and review every diff. But not until the spine is
stable.

---

# ■ SECTION 6 · PROMPTS THAT WORK

## 6.1 · Starting a fresh chat

```
[paste FORGE_HANDOFF.md in full]

Continue THE FORGE. The handoff above is complete context.
WORK ON: [one item from §7]
If you hit a question the handoff does not answer, STOP and ask.
Do not guess and do not start a parallel implementation.
```

That last line is the one that prevents the fifth hopper.

## 6.2 · Oracle questions worth asking

```bash
# before building anything
"does an implementation of X already exist anywhere?"

# finding lost work
"which files describe <concept> and what do they say?"
"list every distinct implementation of <mechanism> and how they differ"

# finding drift
"where is FORGE_STATE.md contradicted by the code?"
"which documents disagree about <thing>?"

# understanding a subsystem
"what is <term> and where is it defined?"
"what does <file> do and what depends on it?"
```

## 6.3 · The salvage prompt pattern

Already built into `salvage.py`, but the shape generalises:

```
[architecture context: laws, vocabulary, what exists]
[the file]
Answer ONLY in this JSON shape: {...}
If you cannot decide, put it in questions_for_human. Do not guess.
```

## 6.4 · What never to do

- **Never** ask an open-ended "improve my architecture" — you get a new vocabulary
- **Never** let a model write into `~/the-forge` or `_WORK/sorter/` unreviewed
- **Never** accept a verdict without reading its reasoning
- **Never** paste a multi-line block into a terminal that's mid-command

---

# ■ SECTION 7 · THE WORK QUEUE

## 7a · Six corrections pending (do these first — no model needed)

In `~/newapps/arch/src/data/frontiers.ts`:

| # | Fix |
|---|---|
| C1 | F5 formula: `× max(1.0, novelty_pressure)` — currently `novelty=0` makes staleness **zero** regardless of age or failure rate |
| C2 | F4: delete the "first 3 exercises bypass NPU" cost item — contradicts its own matrix |
| C3 | F1: re-embed snips on ingestion; keep `origin_embedding` for provenance only |
| C4 | F7: split `capsule_id` (immutable core) from `provenance_head` (hash chain); add `spec_version` |
| C5 | F3 + F6: state that Toolchain may BUILD automatically, but the palette only GROWS by human review |
| C6 | `App.tsx`: wire `TrustZonesSection`; write or remove `cuts` |

## 7b · Build order

| # | Piece | Status |
|---|---|---|
| 1 | **Capsule spec** | R4 has the manifest, `smart_capsule.py` has the runtime — merge them |
| 2 | **Hopper** | Oracle confirmed: never built. Starts from zero. |
| 3 | **Bus hardening** | `bus_516.py` recovered — DLQ + two-phase teardown |
| 4 | **Gate PathwayRegistry** | +25 symbols waiting; **preserve the prose** |
| 5 | Keychain | resume point, not a keyring |
| 6 | FabricSandbox | bwrap + systemd-run, recovered |
| 7 | Copilot | blocked on frontier F6 |
| 8 | Splice / snips | blocked on frontier F1 |
| 9 | Toolchain + Boneyard | Oracle: **no prior spec exists anywhere** |
| 10 | Sockets | — |
| 11 | Guardian / Coupler review | LOCKED to last |

## 7c · Unread, high value

```
01_The_Substance.md          the "alien glue" file you were looking for
00_FORGE_CONCEPT_MAP.md      + the whole numbered series (03, 11, ...)
FORGE_ARCHITECTURE_REVIEW.md W1-W14, R1-R12 — a formal review
master_pack.md               133KB, includes the .suit.zip format
FABLE5_HANDOVER.md           "the 14 organs"
~/openhuman/                 an agent system, never installed
```

---

# ■ SECTION 8 · THE RULE

Five hoppers. Two conduits. Three `Finding` shapes. Four path roots.

None of it happened because the code was bad. **It happened because the
reasoning was never written down**, so every fresh session re-derived it
slightly differently.

Proof: searching every artifact you own for your own vocabulary found
`wardrobe`, `flatten`, and `baptize` at **zero occurrences** — while the things
they named were already built and tested.

The fix is three habits:

1. **Ask the Oracle before building.** Four seconds versus a week.
2. **Update `FORGE_STATE.md §7` before you stop.** Always.
3. **A new word goes in the vocabulary table, or it does not exist.**

Code is regenerable. Reasoning is not.
