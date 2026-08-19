# FORGE ORACLE — install guide

A local model that has read every Forge file you own and answers with
citations. Read-only. Nothing leaves the machine.

**Time:** ~10 min setup, then 15–30 min for the first index (unattended).

---

# PART 1 · INSTALL

## Step 1 — Pull the embedding model

```bash
ollama pull nomic-embed-text
```

274 MB. This is a *different* model from your chat model — it only turns text
into vectors, it never writes prose. Both can be loaded at once; together they
use about 12.5 GB of your 16 GB.

**Verify:**

```bash
ollama list | grep nomic
```

## Step 2 — Install the vector store

```bash
cd ~/the-forge && source .venv/bin/activate
pip install sqlite-vec
```

`sqlite-vec` is a SQLite extension. No database server, no daemon — the whole
index is one file.

**Verify:**

```bash
python3 -c "import sqlite_vec, sqlite3; d=sqlite3.connect(':memory:'); d.enable_load_extension(True); sqlite_vec.load(d); print('ok', d.execute('select vec_version()').fetchone()[0])"
```

Should print `ok v0.1.9` or similar.

## Step 3 — Install the script

Download `oracle.py` from the viewer, then:

```bash
cp ~/Downloads/oracle*.py ~/FORGE_CABINET/_WORK/sorter/
ls -l ~/FORGE_CABINET/_WORK/sorter/oracle.py
```

~374 lines. It must sit beside `forgelib.py` — it imports `Config` and
`assert_writable` from it.

---

# PART 2 · BUILD THE INDEX

## Step 4 — First index

```bash
cd ~/FORGE_CABINET/_WORK/sorter
source ~/the-forge/.venv/bin/activate
python3 oracle.py --config config.yaml index
```

Default roots: `~/the-forge`, `~/FORGE_REVIEW`, `~/forge_sorter`,
`00_MANIFEST`.

You will see a live counter:

```
[47/210] 892 chunks · smart_capsule.py
```

**Leave it running.** First pass embeds everything; expect 15–30 minutes.

## Step 5 — Add the big pile

Once the first index finishes, add the unharvested material:

```bash
python3 oracle.py --config config.yaml index \
  --root "$HOME/Downloads/ForgeOS-Arch-Rev " \
  --root ~/Forge/backend \
  --root ~/newapps/arch/src
```

Note the trailing space inside the quotes on the first path — that folder
really is named that way.

This is **incremental**: already-indexed files are skipped by SHA. Only new
material gets embedded.

## Step 6 — Check what it holds

```bash
python3 oracle.py --config config.yaml stats
```

```
187 files · 1,204 chunks · 9.4MB

by kind:
  code      812
  doc       291
  test       78
  config     23
```

If `test` is 0, your test files were not reached — check your roots.

---

# PART 3 · USE IT

## One-shot question

```bash
python3 oracle.py --config config.yaml ask "where is the capsule format defined?"
```

## Show which files it used

```bash
python3 oracle.py --config config.yaml --sources ask "does a Hopper with pull semantics exist anywhere?"
```

Prints the retrieved chunks and their distances before the answer. Use this
whenever the answer surprises you — you can see exactly what it read.

## Interactive — best for going back and forth

```bash
python3 oracle.py --config config.yaml chat
```

```
? what does cold_drop_shadow do
? which files implement a bus
? what is a crumb in SliceState
? q
```

`q` or Ctrl-D exits. This is the mode you want when you are exploring rather
than looking something up.

## Retrieve more context for hard questions

```bash
python3 oracle.py --config config.yaml -k 15 ask "compare every bus implementation"
```

Default is 8 chunks. Raise `-k` for questions that span many files; lower it
for precise lookups.

---

# PART 4 · QUESTIONS WORTH ASKING FIRST

Start with one you already know the answer to — that tells you whether
retrieval is any good:

```
what mechanisms exist for capsule slicing and where are they implemented?
```

Then the ones that actually save you time:

```
does an implementation of pull-with-refusal work distribution exist anywhere?
which files define SliceState and what fields does it have?
what is a crumb?
list every place a replay ledger is implemented
what does master_pack.md say about .suit.zip
which files mention seL4 and what do they claim
show me everything about VRAM enforcement
what is the difference between the four bus implementations
where is FORGE_STATE.md contradicted by the code
```

That last one is the highest-value question in the list.

---

# PART 5 · KEEPING IT CURRENT

Re-index after any significant work. It is incremental, so it is cheap:

```bash
python3 oracle.py --config config.yaml index
```

Unchanged files are skipped by SHA. Force a full rebuild only if you change
chunking or the embedding model:

```bash
python3 oracle.py --config config.yaml index --force
```

Optional — a weekly systemd timer, same pattern as `forge-sweep`:

```ini
# ~/.config/systemd/user/forge-oracle.service
[Unit]
Description=Re-index the Forge Oracle

[Service]
Type=oneshot
WorkingDirectory=%h/FORGE_CABINET/_WORK/sorter
ExecStart=%h/the-forge/.venv/bin/python3 oracle.py --config config.yaml index
```

---

# PART 6 · WHAT IT IS AND IS NOT

**It is:** a search engine over your own files, with a model that reads the
results and answers in plain language, citing each file.

**It is not:** a coding agent. It cannot write, move, or delete anything.
Every write goes through `assert_writable()` into `00_MANIFEST/oracle.db`.
Tested: it refuses the spine, refuses your home directory, allows only the
cabinet.

**Why it exists:** five hoppers, two conduits, three `Finding` shapes, four
path roots — every one of them because a session could not see what earlier
sessions had built. The Oracle makes "does this already exist?" a four-second
question.

The prompt carries one instruction that matters more than the rest:

> *If two excerpts disagree, say both and name which files. Disagreement
> between eras is information, not an error.*

So it will show you all four bus implementations and tell you they conflict,
rather than confidently picking one.

---

# TROUBLESHOOTING

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: sqlite_vec` | not installed in the venv | activate the venv, `pip install sqlite-vec` |
| `embed failed: HTTP 404` | embedding model missing | `ollama pull nomic-embed-text` |
| `no index` | never indexed | run `index` first |
| Indexing is very slow | embed model on CPU | `ollama ps` — should show 100% GPU |
| Answers cite the wrong files | not enough context | raise `-k`, and use `--sources` to see what it read |
| Answers are vague | chat model too small | `--model qwen2.5-coder:14b` |
| `SafetyError` | tried to write outside the cabinet | that is the guard working; check `config.yaml` |
| Stats show 0 chunks for a root | wrong path or all files skipped | check the path; note the trailing space in `ForgeOS-Arch-Rev ` |

**Disk use:** roughly 3 KB per chunk. A 1,200-chunk index is about 10 MB.
It lives at `~/FORGE_CABINET/00_MANIFEST/oracle.db` and is safe to delete —
re-indexing rebuilds it.
