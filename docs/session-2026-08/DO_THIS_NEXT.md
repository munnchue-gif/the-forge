# DO THIS NEXT — the whole procedure, nothing assumed

Date: 2026-08-19
Read top to bottom. Do not skip to the middle.

**Three rules for this document:**

1. **One command at a time.** Never paste a block. Your terminal echoes
   multi-line pastes back at itself and you end up stuck on a `>` prompt.
   If that happens: **Ctrl+C**, then retype the single line you meant.
2. **Filenames with `.py` and `.md` get mangled** by your chat client into
   links. Every command below uses a **glob** (`salvage*.py`, `frontiers*`)
   or tab-completion instead. That is deliberate. Keep doing it.
3. **Activate the venv before any Python.**
   `source ~/the-forge/.venv/bin/activate`

---

## PART 0 — What you are about to do, in one paragraph

There are 31 documents from this session sitting in a chat workspace and
nowhere else. If the tab closes, they are gone. Step 1 gets them onto your
disk and into git in about four minutes, using **one download**, not 31.
Step 2 is six small hand-edits to a TypeScript file — no model, no scripts,
about ten minutes. Step 3 is the first real build: the capsule spec, which
is already two-thirds written and just needs to be joined together.

Do them in that order. Step 1 is the only one that is urgent.

---

# PART 1 — GET THE DOCS ONTO YOUR PC  (do this first, today)

## 1.1 Download one file

In the file viewer, download:

    forge_rescue_2026-08-19.sh

That single file contains all 31 documents, all 16 sorter tools, and the
extracted reference text. It is a shell script with a compressed archive
glued onto the end of it. Nothing else to download.

It lands in `~/Downloads`.

## 1.2 Look before you leap

    cd ~/Downloads

then

    bash forge_rescue*.sh --dry

`--dry` prints every action it *would* take and writes nothing. Read that
output. It should say it will create `~/the-forge/docs/session-2026-08`
and stage tools into `~/FORGE_CABINET/_WORK/sorter_incoming`.

If it says **STOP: No /home/mancier/the-forge** — you are in the wrong
place or the wrong user. Fix that before continuing.

## 1.3 Run it for real

    bash forge_rescue*.sh

**What it does, precisely:**

| Where | What lands there | Safety |
|---|---|---|
| `~/the-forge/docs/session-2026-08/` | the 31 markdown documents | `cp -n` — never overwrites |
| `~/FORGE_CABINET/_WORK/sorter_incoming/` | the 16 sorter tools | **staged, NOT installed** |
| `~/FORGE_CABINET/_WORK/session_incoming/` | extracted reference text | `cp -rn` — never overwrites |

**It does not touch `~/FORGE_CABINET/_WORK/sorter/`.** That is the
directory a harvest agent clobbered `forgelib.py` in once. It gets a
separate `_incoming` folder and you decide, by hand, what moves across.

If any doc already exists and differs, it prints
`!! differs, kept YOURS:` and leaves your copy alone.

## 1.4 Commit it — one line at a time

    cd ~/the-forge

then

    git add docs

then

    git commit -m "docs: session artifacts 2026-08"

then

    git push

**That is the moment the risk goes away.** Everything after this is
recoverable work. Everything before it was not.

## 1.5 Then, separately, decide about the tools

Do this later, not now. The staged tools are not urgent.

    diff -rq ~/FORGE_CABINET/_WORK/sorter ~/FORGE_CABINET/_WORK/sorter_incoming

That lists which files differ. For each one you actually want, look at the
difference first:

    diff ~/FORGE_CABINET/_WORK/sorter/oracle*.py ~/FORGE_CABINET/_WORK/sorter_incoming/oracle*.py

and only then copy that single file across. One file, one decision.

**Two patches you specifically want from `oracle*.py`:** the
`.aider.chat.history.md` skip (73 junk chunks polluting the index) and the
dedup fix (same file indexed from two roots showed doubled sources). The
dedup fix works the moment you copy it. The skip patch needs a re-index to
take effect.

---

# PART 2 — THE SIX CORRECTIONS TO `frontiers.ts`

**File:** `~/newapps/arch/src/data/frontiers.ts` (24 KB)

No script. No model. Open it in an editor and make six edits. This is
faster and safer by hand than any tooling, because each edit is a judgment
call about meaning, not a mechanical substitution.

## Before you start

    cd ~/newapps/arch

then

    git add -A

then

    git commit -m "checkpoint before frontier corrections"

Now you can undo anything with `git checkout -- src/data/frontiers*`.

Open the file. In VS Code: `code ~/newapps/arch` then Ctrl+P and type
`frontiers`. Each correction below tells you **what to search for**, so you
never need to type the filename again.

---

### C1 — F5, the staleness formula divides by zero-ish

**Search for:** `novelty_pressure`

**The bug:** the formula is

    S = (days / halflife) × (1 + failure_rate) × novelty_pressure

When `novelty_pressure` is `0` — which is the normal state for a stable,
boring component nobody has challenged — the whole product collapses to
`S = 0`. A file can be two years old with a 90% failure rate and score
perfectly fresh. The multiplier was meant to *amplify* staleness, but with
no floor it *erases* it.

**Change to:**

    S = (days / halflife) × (1 + failure_rate) × max(1.0, novelty_pressure)

**Why `max` and not `1 + novelty`:** with `1 + novelty` you can never have
a neutral term; every component gets inflated. `max(1.0, ...)` means
novelty pressure can only ever make something *more* stale, never less.
Age and failure rate stand on their own. That is the correct direction —
novelty is evidence *for* staleness, never evidence against it.

---

### C2 — F4, a cost item that contradicts its own matrix

**Search for:** `first 3` (or `bypass`)

**The bug:** F4 establishes an irreversibility × novelty matrix and states
plainly that **high irreversibility → NPU sync sign-off, always.** Then a
cost item further down grants the first three exercises a bypass of the
NPU check, as a warm-up optimisation.

Those cannot both be true. "Always" with an exemption is not always. And
the exemption is aimed at exactly the wrong window: the first three runs of
anything are when you understand it *least*.

**Change:** delete that cost item entirely. Do not soften it, do not make
it configurable. The matrix is the rule.

The line worth keeping in mind while you do it: *"The NPU's value is
independence, not intelligence."* A bypass costs you the independence,
which was the entire point. It was never being used for its brains.

---

### C3 — F1, embeddings must be recomputed on ingestion

**Search for:** `embedding_vec`

**The bug:** the extract schema carries `embedding_vec` as a field, which
implies the vector travels with the claim and gets used on arrival. It
cannot. A vector is only meaningful inside the model and dimensionality
that produced it. An extract from a foreign model carries numbers that look
valid, index without error, and return silent nonsense on retrieval. That
is worse than a crash.

**Change:** rename the field to `origin_embedding`, and add a comment
stating it is **provenance only — never used for retrieval**. The receiving
system re-embeds the `assertion` text with `nomic-embed-text` at ingestion.

**Why keep it at all:** it tells you which model's semantic space the claim
was born in, which matters when you are auditing why two extracts that
should have matched didn't.

---

### C4 — F7, one hash is doing two incompatible jobs

**Search for:** `capsule_id`

**The bug:** a single content hash is being used both as the capsule's
identity and as its provenance chain head. Those have opposite
requirements. Identity must be **stable** — the same capsule is the same
capsule tomorrow. A provenance head must **change on every append**, or the
chain proves nothing.

One value cannot be both stable and always-changing.

**Change:** split into two fields.

    capsule_id     = hash(core_manifest)              // stable identity
    provenance_head = hash(entry_n ‖ head_{n-1})      // moves every append

Also add a `spec_version` field to the manifest while you are in there.
Every format that lacked one has regretted it, and you have personally
watched this project fork four times over undeclared assumptions.

---

### C5 — F3 + F6, the automation boundary is in the wrong place

**Search for:** `palette` (F6), then `STAGE` (F3)

**The bug:** F3 and F6 together imply the Toolchain needs human approval to
build anything. That is too strict in one place and too loose in another.

**The correct split, and the reasoning:**

- The **Toolchain may BUILD automatically.** Organs in the Boneyard are
  *inert* — not wired to the bus, holding no capabilities, unable to run.
  Building an inert artifact is not a privileged act. Gating it just makes
  you the bottleneck on work that cannot hurt you.
- The **palette only GROWS by human review.** The palette is the set of
  declaration templates the Copilot may choose from. That *is* the security
  boundary, and F6 already says so: *"Autonomy bounded not by trust in the
  model but by the structure of its choices."* Widen the palette and you
  have widened the model's reachable action space permanently.

So: automate the building, gate the vocabulary. Edit both sections so they
agree on that. Right now they gate the wrong one.

While you are in F3, keep its closing line intact: *"There is no STAGE 6
that makes the code 'trusted'."* Nothing above changes that.

---

### C6 — `App.tsx`, one orphan and one ghost

**File:** `~/newapps/arch/src/App.tsx`

**Search for:** `SECTION_IDS`

Two separate problems:

**The orphan —** `TrustZonesSection.tsx` exists in
`src/components/sections/` and is never imported anywhere. Working
component, invisible. Import it and render it in the section list.

**The ghost —** `cuts` appears in `SECTION_IDS` but has no component
behind it. Either write `CutsSection.tsx` or remove `cuts` from the array.

**Pick removal.** You do not currently have a settled definition of what a
"cut" is, and inventing one right now to fill a slot in an array is exactly
the drift mechanism that has cost you four rebuilds. Delete the entry. If
the concept turns out to be real, it comes back with a definition attached.

## When the six are done

    cd ~/newapps/arch

then

    npm run build

then, if it builds

    git add -A

then

    git commit -m "frontiers: 6 corrections (staleness floor, NPU bypass, re-embed, hash split, automation boundary, orphan section)"

---

# PART 3 — BUILD #1, THE CAPSULE SPEC

**Do not start this until Parts 1 and 2 are done and pushed.**

## Why this one is first

Because `FORGE_ARCHITECTURE_REVIEW.md` says so, in R4, in writing:

> *"When: Phase 0. Capsule schema is the core data contract. Nothing else
> can be built properly without it."*

W5 lists "Capsule Schema Is Undefined" as a weakness. Everything downstream
— Hopper, Keychain, Toolchain, Boneyard — moves capsules around. Define the
thing being moved before building the movers.

## The thing you may not realise

**You have already written roughly two-thirds of this, twice, in two places
that never met.**

| Half | Where | What it has | What it lacks |
|---|---|---|---|
| **Manifest** | `FORGE_ARCHITECTURE_REVIEW.md` **R4**, line 417 | identity, provenance (`parent_id`, `merged_from[]`), capabilities, checksum, `uuid-v7`, lifecycle `DRAFT→VALIDATED→ACTIVE→PAUSED→ARCHIVED` | any runtime |
| **Runtime** | `~/FORGE_REVIEW/c44-capsule/smart_capsule.py` (17 K) | dual A/B slices, shadow writes, cold drop, commit swap, 21 tests already written against it | any manifest |

Neither knows the other exists. R4 describes a capsule at rest;
`smart_capsule.py` runs one in flight. Build #1 is the join.

I have written the merged draft for you as
`CAPSULE_SPEC_V1_DRAFT.md`, in this same folder. It is a **draft** — read
it against the two sources and correct it. Do not treat it as authority.

## The order of work

**Step 1 — read the slice mechanics and override a bad verdict.**

    cd ~/FORGE_REVIEW/c44-capsule

then

    sed -n '260,410p' test_capsule*.py

`salvage.py` graded `test_capsule_slicing.py` as **DISCARD**. That verdict
is wrong and you should overrule it. It is 737 lines and 21 tests, and it
is the **written specification for Build #1** — a spec that happens to be
executable. The grader saw test scaffolding and scored it as disposable.

Note while reading: the **8 slice-mechanics tests are `def`, not
`async def`.** The core slice model is synchronous, which means it is Law 4
compatible and can be ported without dragging an event loop in. That is the
single most valuable fact in the file.

Note also: the tests assert on `id()`, not equality. They are deliberately
catching *aliasing* — two slices that look equal but are the same object.
Preserve that when you port them; it is the bug the whole A/B design exists
to prevent.

**Step 2 — delete the dead branch, do not fix it.**

In `smart_capsule.py`, around line 146:

```python
def commit_slice_swap(self) -> SliceID:
    old_active = self.active_slice
    if self.active_slice == SliceID.SLICE_A:
        self.slice_a, self.slice_b = self.slice_b, self.slice_a
        self.slice_b.cold_drop()
        self.active_slice = SliceID.SLICE_A
    else:
        self.slice_a, self.slice_b = self.slice_b, self.slice_a
        self.slice_a.cold_drop()      # <-- destroys what it just promoted
        self.active_slice = SliceID.SLICE_A
```

Both branches perform the identical swap. The `else` branch then cold-drops
`slice_a` — the slice it has just promoted to active. It is data loss
written down.

It has never fired, because `active_slice` is unconditionally set to
`SLICE_A` at the end of both paths, so the `else` is unreachable.

**Delete the `else` branch and the `if` condition. Keep the body once.**
Do not repair the else. Repairing it preserves a branch that models a state
the type system says cannot exist, and someone — probably you, in four
months — will later "fix" the unconditional `SLICE_A` assignment and
resurrect the data loss. Remove the state, not the symptom.

Also delete `old_active` if nothing reads it.

**Step 3 — write the manifest schema.** Take R4's YAML, add C4's
`capsule_id` / `provenance_head` split and `spec_version`. Draft is in
`CAPSULE_SPEC_V1_DRAFT.md`.

**Step 4 — pin the `.suit.zip` container.** From `master_pack.md` (line
258, and again at 1018 — the file is duplicated inside itself, so do not
be confused when you find it twice):

    zip my_capsule.suit.zip manifest.json constraints.yaml state.json

Parse failure raises `CapsuleParseError: Capsule missing required
'manifest.json'`. Keep that exact behaviour and message.

**Step 5 — leave `crumbs` undefined, on purpose, in writing.**

`SliceState` has fields `history`, `memory_vectors`, `validation_score`,
`token_count`, `crumbs`, `last_commit_id`. `crumbs` is
`list[dict[str, Any]]` and its semantics exist nowhere. The only evidence
in 4,038 indexed chunks is one test line:

    shadow.crumbs = [{"crumb": "breadcrumb"}]

That is a placeholder someone typed to make a test pass.

**Write into the spec: `crumbs` — RESERVED, semantics undefined as of
v1, MUST be preserved verbatim across swaps, MUST NOT be interpreted.**

Do not invent a meaning. Inventing meanings for half-remembered fields is
the precise mechanism that forked this tree four times. Reserving it costs
nothing and stops the next session from confidently making something up.

---

# PART 4 — THE SMALL THINGS

Do these whenever, one at a time. They remove friction that has already
cost you real time.

**Install the tools you keep wishing you had:**

    sudo apt install ripgrep fd-find fzf bat tmux jq

**Rename the trailing-space folder.** It has broken about a dozen commands.

    mv "$HOME/Downloads/ForgeOS-Arch-Rev " ~/Downloads/ForgeOS-Arch-Rev

The quotes on the first path are load-bearing — that is the whole problem.

**Index `~/openhuman` with the Oracle before installing any of it.** It is
an agent system sitting on your disk that has never been examined. Read it
through the index first. You were burned by aider; do not run an unread
agent system.

---

# PART 5 — THE THREE STALE TESTS

Your baseline is **9 failed / 125 passed**. Not all nine are bugs.

- **`bind/test_bind.py`, 5 tests** — pinned to era-1
  `Finding(section_id=, kind=, detail=, severity=1)`. Current `Finding` is
  era 3, where **severity is a string**. Stale tests, working code. Port
  them to era 3 or delete them, but do not "fix" `Finding`.
- **`test_request_action_unknown_op`** — not a bug. `request_action`
  deliberately catches `ValueError` at `kernel.py:373-379` and returns
  `{allowed: False, reason: ...}` so that `/mint` gives the App a clean
  refusal instead of a 500. That is correct fail-closed design. **The test
  is stale.** Rewrite the assertion.
- **`test_sequence.py`, 1 test** — returns `rolled_back` where `done` is
  expected. This one is worth actually investigating; it may be real.

Fixing the stale tests takes the baseline from 9 failed to about 3 without
touching a line of production code.

---

# THE ORDER, ON ONE LINE

**Part 1 today** (four minutes, removes the only unrecoverable risk) →
**Part 2 when you have ten quiet minutes** → **Part 3 when you are fresh.**

If you only do one thing: run the rescue script and `git push`.
