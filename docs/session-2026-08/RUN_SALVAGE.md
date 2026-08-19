# Running salvage.py — step by step

Total: about 30 minutes, most of it waiting on the model.

---

## STEP 0 · Preflight (30 seconds)

```bash
cd ~/FORGE_CABINET/_WORK/sorter
source ~/the-forge/.venv/bin/activate
ollama ps
```

**`ollama ps` must show `100% GPU` and `CONTEXT 16384`.**
If it is empty, nothing is loaded — run `ollama run gpt-oss:20b "ok"` first.
If PROCESSOR shows any CPU split, stop; the run will take hours instead of
minutes.

---

## STEP 1 · Install the script

Download `salvage.py` from the viewer, then:

```bash
cp ~/Downloads/salvage.py ~/FORGE_CABINET/_WORK/sorter/
ls -l ~/FORGE_CABINET/_WORK/sorter/salvage.py
```

Should be ~367 lines. If the filename mangles again, use a glob:
`cp ~/Downloads/salvage*.py ~/FORGE_CABINET/_WORK/sorter/`

---

## STEP 2 · Dry run — costs nothing, tells you everything

```bash
python3 salvage.py --config config.yaml --dir ~/FORGE_REVIEW --dry-run
```

Expected output:

```
[1/8] bus_516.py               516L  8 async  [dry-run · prompt ~5200 tok]
[2/8] hopper.py                151L  2 async  [dry-run · prompt ~2100 tok]
...
[8/8] test_capsule_slicing.py  737L 14 async  [dry-run · prompt ~7400 tok]
```

**Read the async column now** — it is computed in Python, not by the model, so
it is reliable. Anything with 0 async is Law 4 compatible and unusually
portable. Anything over 10 is deep in the `backend/` lineage.

**Any prompt over ~12,000 tokens will be truncated** against your 16k context.
Note which files those are; they get the special treatment in Step 4.

---

## STEP 3 · The real run (15–25 min)

```bash
python3 salvage.py --config config.yaml --dir ~/FORGE_REVIEW --group crypto
```

Watch the verdict column as it goes:

```
[1/8] bus_516.py    516L  8 async  MINE_MECHANISMS         94s
[2/8] hopper.py     151L  2 async  DISCARD                 41s
```

**If you see `TRUNCATED — RAISE --NUM-PREDICT`**, that file needs a rerun:

```bash
python3 salvage.py --config config.yaml --dir ~/FORGE_REVIEW \
  --file <thatfile>.py --num-predict 4000
```

**If everything comes back `UNPARSEABLE`**, the model rejected the JSON schema.
One-line fix — open `salvage.py`, find the `ask(` call in `main()`, and add
`schema=False`:

```python
resp = ask(args.model, prompt, args.timeout, args.num_predict, schema=False)
```

That falls back to plain `format:"json"` and still works, just less strictly.

---

## STEP 4 · The big file, separately

`test_capsule_slicing.py` is 737 lines and will hit the truncation limit. It is
also the highest-value file in the pile — 568 substantive lines of tests for
capsule slicing, and capsule format is Build #1.

Give it room:

```bash
python3 salvage.py --config config.yaml --dir ~/FORGE_REVIEW \
  --file test_capsule_slicing.py --max-chars 40000 --num-predict 4000 \
  --timeout 600
```

This one will take several minutes. That is expected.

---

## STEP 5 · Read the results

```bash
cd ~/FORGE_CABINET/00_MANIFEST/salvage
cat INDEX.md
```

Files are sorted `PORT_NEARLY_AS_IS` → `MINE_MECHANISMS` →
`READ_ONLY_REFERENCE` → `DISCARD`. Read top-down.

Then the two that matter most:

```bash
cat security_guard.md
cat test_capsule_slicing.md
```

**The check on whether this actually worked:** does `security_guard.md`
independently report `sync_safe: true` and list `SlotAccessDenied` under NOVEL?
I found both by hand. If the model finds them too, the pre-loaded context is
doing real work and you can trust the other seven sheets. If it misses them,
the context needs tightening before you rely on it.

Then scan every sheet for escalations:

```bash
grep -A3 "QUESTIONS FOR HUMAN" *.md
grep -A3 "LESSONS VIOLATED" *.md
```

Those are the two sections the model was told to escalate rather than guess.

---

## STEP 6 · Feed a pile to the reconfiguration prompt

```bash
cat INDEX-crypto.md
```

That is your crypto pile — every file carrying a signature/replay/expiry
mechanism. Three implementations of the Gate concept exist. Take that list,
paste the relevant sources, and run the reconfiguration prompt from
`SALVAGE_METHOD.md §5`.

Other piles worth generating once the first run is done:

```bash
python3 salvage.py --config config.yaml --dir ~/FORGE_REVIEW --group queueing
python3 salvage.py --config config.yaml --dir ~/FORGE_REVIEW --group isolation
```

*(These re-run the model. If you would rather not, the group data is already in
each sheet — the flag just collates it.)*

---

## Safety notes

- **Nothing is modified.** Sheets go to `00_MANIFEST/salvage/`, guarded by
  `assert_writable()`. Your review folder and spine cannot be touched.
- **The model never decides a merge.** Verdicts are inventory categories.
  `questions_for_human` exists so it escalates instead of guessing.
- **Ctrl-C is safe** at any point. Completed sheets are already written; rerun
  and it redoes only what is missing.

---

## If something goes sideways

| Symptom | Cause | Fix |
|---|---|---|
| `Connection refused` | Ollama not running | `sudo systemctl start ollama` |
| Every file `SKIPPED` | model not pulled | `ollama pull gpt-oss:20b` |
| Every file `UNPARSEABLE` | schema rejected | pass `schema=False` (Step 3) |
| One file `TRUNCATED` | response cut off | rerun with `--num-predict 4000` |
| Takes >5 min per file | model on CPU | check `ollama ps`, fix context length |
| `SafetyError` | writing outside cabinet | that is the guard working — check `config.yaml` |
