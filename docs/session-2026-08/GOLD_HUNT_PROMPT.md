# GOLD HUNT — find the unique code across all 10 unscanned repos

## Why this is needed

The harvest so far found **0 GOLD**. Every GOLD you have came from one root:

| Root | Scanned | GOLD found |
|---|---|---|
| `~/forge-spine` | ✅ | **7** (4 merged, 3 pending) |
| `~/harvest_zips` | ✅ | 0 (docs + React UI) |
| **the other 10 repos** | ❌ | **unknown** |

`forge-spine` alone yielded `gate.py` (+25 symbols beyond your live spine),
`forge.py`, `hub.py`, `capsule.py`, `validate_ledger.py`. That hit rate on
**one** root is the reason to scan the rest.

## The 10 unscanned roots (confirmed on your disk)

```
~/forge-workspace/the-forge
~/forge-workspace/the-forge-ui
~/forge-workspace/git-concoctinating
~/core_Forge-unziped
~/Videos/the-forge-repo/the-forge
~/ALLFORGE/the-forge
~/ALLFORGE/the-forge-repo/the-forge
~/forge-os/the-forge
~/Forge
~/forge-os-locked-pc
```

Skip `~/forge-os/llama.cpp` — third-party source, not yours.

---

## RUN THIS FIRST (no bot needed — 10 minutes, mechanical)

You already own every tool. One root at a time, so you can inspect between runs:

```bash
cd ~/FORGE_CABINET/_WORK/sorter && source ~/the-forge/.venv/bin/activate

for R in ~/forge-workspace/the-forge \
         ~/core_Forge-unziped \
         ~/ALLFORGE/the-forge \
         ~/ALLFORGE/the-forge-repo/the-forge \
         ~/Videos/the-forge-repo/the-forge \
         ~/forge-os/the-forge \
         ~/forge-os-locked-pc \
         ~/Forge \
         ~/forge-workspace/git-concoctinating ; do
  [ -d "$R" ] || { echo "MISSING $R"; continue; }
  echo "════════ $R"
  python3 scan.py --config config.yaml --root "$R" 2>&1 | tail -3
  python3 archive_copy.py --config config.yaml 2>&1 | tail -2
  python3 grade.py --config config.yaml 2>&1 | tail -6
done
```

Then the two commands that actually answer "where is the good code":

```bash
python3 tune.py    --config config.yaml | head -40
python3 compare.py --config config.yaml
```

`compare.py` is the one that matters. It AST-diffs every GOLD/SILVER Python
candidate against your live spine and returns one of:

- **RECOVERY** — no upstream twin → unique code, port it
- **CANDIDATE_SUPERSET** — strictly richer than live → strong merge case
- **DIVERGED** — both sides have unique symbols → human merge
- **SPINE_SUPERSET** — live is ahead → discard
- **SAME_API** — bodies differ only

**Do not skip `archive_copy.py`.** It is what makes deleting these repos safe
later.

---

## THEN the bot prompt (for the ambiguous middle only)

Once `grades.csv` exists for all roots, a local model is useful for the files
the heuristic scores between BRONZE and GOLD — where "is this a real organ or
a stub?" needs judgement. Paste this into your coder bot:

```text
You are grading recovered source files for THE FORGE, a local AI-runtime OS.
You are NOT writing code. You are deciding which files contain unique,
valuable work worth porting into the live spine.

CONTEXT YOU MUST READ FIRST:
  ~/the-forge/FORGE_STATE.md   — locked decisions, vocabulary, organ status

HARD RULES:
- READ ONLY. Do not write, move, or delete any file.
- Do not "fix" anything you find broken. Report it.
- Do not create new files or start a new project.
- The live spine ~/the-forge is authoritative. Candidates are proposals.

INPUT:
  ~/FORGE_CABINET/00_MANIFEST/grades.csv     heuristic scores
  ~/FORGE_CABINET/00_MANIFEST/concepts.csv   concept -> file index

TASK: for every candidate scoring 15-70 in grades.csv, open the file and
classify it into exactly one bucket:

  UNIQUE_ORGAN   a complete, working fabric organ with no equivalent in the
                 live spine. Real classes, real logic, not a stub.
  RICHER_VARIANT a file whose live twin exists but this version has more
                 working symbols (name the extra classes/functions).
  DESIGN_ONLY    prose, spec, or docstring-heavy file with a good IDEA but
                 no working implementation. Say what the idea IS in one line.
  STUB           skeleton only: empty functions, pass, NotImplementedError.
  NOISE          generated, vendored, duplicated, or third-party.

FOR EACH, OUTPUT EXACTLY:
  path | bucket | 1-line why | concepts touched | risk if merged

PRIORITISE files touching these concepts (from FORGE_STATE.md vocabulary):
  Gate, Overseer, Watcher, Commander, VectorConduit, Wrap, WrapStore,
  Concoctinator, EmbeddedTailor, Capability, Splice, Reclaim, Hopper,
  Keychain, Ledger, BehavioralJudge, SubstanceBus

FLAG SEPARATELY, at the top of your report:
  - any file implementing HOPPER or KEYCHAIN (both are NOT BUILT — these are
    the only two genuinely missing organs)
  - any capability verb not in: Spawn, Mount, Egress, NpuEval, Conform,
    Splice, Reclaim
  - any file whose docstring describes a design decision that is NOT already
    in FORGE_STATE.md §1

END WITH: the 10 highest-value files, ranked, with the single reason each
one is worth a human's next hour.
```

---

## What to expect, based on evidence

**Likely GOLD:**
- `~/forge-workspace/the-forge` and `~/ALLFORGE/the-forge` — full checkouts of
  a working era; most likely to hold organ variants
- `~/core_Forge-unziped` — a git repo, so it has history
- `~/forge-os-locked-pc` — "locked" suggests a deliberate snapshot

**Likely noise:**
- `~/Videos/the-forge-repo/the-forge` — a copy in Videos is almost certainly
  an unzip dump
- `~/forge-workspace/the-forge-ui` — React, belongs in `the-forge-ui`
- `~/forge-workspace/git-concoctinating` — the Base44 command board

**Two things to watch for specifically:**

1. **Hopper and Keychain.** Both are NOT BUILT. Your Graded Master List and the
   Concepts Guide describe them, but no implementation has surfaced. If a
   `hopper.py` exists in any of these repos, that is the single most valuable
   find available — the whole `SpawnCapability` path assumes it.

2. **A second `overseer.py`.** Your live one is 268L / 26 symbols. The
   `Forge-NG` fragment quoted a docstring your live file may not have
   (*"even though it's disconnected, it can still communicate telepathically"*
   — Eugene's original vision). If a fuller variant exists, the prose alone is
   worth recovering.

---

## Safety reminders

- `grid.py` exists if you want a bot working under enforced isolation:
  `python3 grid.py --config config.yaml add --color GREEN --agent <bot> --organ hunt`
  then `claim --read ~/FORGE_CABINET/00_MANIFEST` and nothing else.
- The sorter is copy-only. Nothing in these 10 repos will be modified.
- After the sweep, `06_ARCHIVE_RAW` holds a verbatim copy of everything — that
  is what makes the eventual wipe safe.
