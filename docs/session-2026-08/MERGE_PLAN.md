# Phase 6 — Merge Plan (decided from compare.py evidence)

Source: `forge-spine` candidates vs live `~/the-forge` spine, 2026-08-15.
Eight Python candidates resolved. **Nothing here is automated. One module at a
time, human-led, through Creation Blocks.**

---

## Decision table

| Candidate | Verdict | Evidence | **Decision** |
|---|---|---|---|
| `gate.py` | CANDIDATE_SUPERSET | +25 symbols, 0 spine-only (305L vs 250L) | **MERGE — but hand-port, see §1** |
| `ledger.py` | DIVERGED | +20 cand / +6 spine (288L vs 179L) | **MERGE second — real two-way merge** |
| `forge.py` | RECOVERY | no twin; 8 classes, 232L | **PORT AS NEW** |
| `capsule.py` | RECOVERY | no twin; 3 classes, 106L | **PORT AS NEW** |
| `validate_ledger.py` | RECOVERY | no twin; 160L, 0 classes (a test/validator) | **PORT AS NEW — after ledger.py** |
| `hub.py` | ~~DIVERGED~~ → **RECOVERY** | ~~+11/+2~~ **bogus match, see §2** | **PORT AS NEW** |
| `kernel.py` | DIVERGED | +1 cand / +6 spine (**91L vs 351L**) | **KEEP SPINE — discard candidate** |
| `__init__.py` | SAME_API | 17L vs **71L** spine | **KEEP SPINE — discard candidate** |

Two candidates that scored GOLD (110) and SILVER (60) lose to the spine on
inspection. That is the system working: **score ranks candidates against each
other, compare decides against upstream.** Never merge on score alone.

---

## §1 The gate.py finding — read this before merging

`compare.py` reports `only in spine (0)`, i.e. the candidate is a strict API
superset. That is true *for code symbols* and it is the strongest merge case in
the set. The candidate adds a coherent, genuinely new subsystem:

- `PathwayRegistry` + `PathwayDescriptor` — forward-declared pathways, so an
  undeclared `kind` is denied *before any crypto runs* (`DENY_PATH_NOT_DECLARED`)
- `Role` (KERNEL/OVERSEER/MODEL/EXTERNAL) with `may_inspect_registry` /
  `may_modify_registry` — registry mutation is now privilege-gated
- `revoke_vessel` / `clear_revocation` + `_revocation_epochs` — O(1) vessel
  revocation, epoch-compared against `issued_at`
- `vessel_id` bound into the HMAC body (not just a passenger field)
- `GateStats._bump()` — match-based counter dispatch replacing scattered `+=`
- Three new `Decision` members and their counters

**But the diff also shows the candidate deleted ~40 lines of design rationale**
— the "DESIGN THESIS" and "WHAT I FIXED FROM THE ORIGINAL" blocks explaining
*why* the replay ledger is exact rather than probabilistic, why no private
attribute reach, why decisions are values not exceptions. My tool compares AST
symbols; it cannot see that loss. It is real and it matters — that text is the
reasoning that keeps the next person from reintroducing a probabilistic replay
guard.

**So: do not copy the candidate file over the spine file.** Port the new
symbols *into* the spine file, keeping the spine's docstrings intact. The
merged result should be roughly 250L of documented spine + the new registry /
role / revocation subsystem, and it belongs in `BRONZE`-style prose too — the
rationale for pathways should be written down the way the original author wrote
down the replay-ledger rationale.

---

## §2 hub.py — RESOLVED: the DIVERGED verdict was a tool bug

The v3 `compare.py` matched your candidate `forge/fabric/hub.py` against

```
~/the-forge/.venv/lib/python3.12/site-packages/datasets/hub.py
```

— HuggingFace's dataset library, vendored inside the spine's virtualenv. The
"2 spine-only symbols" were `delete_from_hub` and `_delete_files`, HF API
functions with nothing to do with the Forge. The verdict was meaningless.

**Cause:** `find_spine_twin()` used `rglob(name)` while excluding only `.git`.
`grade.py` correctly applied the full denylist (`.venv`, `site-packages`, …);
`compare.py` did not. My bug — the two tools disagreed and the *less* careful
one was the one I told you to trust.

**Fixed in v4:** `find_spine_twin()` now applies `cfg.deny_dirs`, prefers a
twin whose parent directory also matches (`forge/fabric/hub.py` over a stray
`hub.py`), and the summary table prints **which upstream file it matched** so a
bogus twin is visible instead of silent.

**Corrected verdict: `hub.py` is RECOVERY** — there is no real `hub.py` in the
spine. It is `HubSocket`, a registry for external tool hubs (n8n, Intel/
OpenVINO, local model registries) that never takes KERNEL role and routes
execution through `CapsuleStore.register → expand → run under Gate`. Port it
in as a new module alongside `forge.py` and `capsule.py`.

**Re-run the whole comparison on v4** before acting on any other verdict — the
same bug could have affected any candidate whose basename collides with
something in `site-packages`. `gate.py`, `ledger.py`, and `kernel.py` all
matched real `forge/fabric/` paths, so those verdicts stand, but confirm with
the new "matched upstream file" column.

---

## §2b All eight verdicts confirmed on v4

Every row now shows a real `forge/fabric/` twin or a genuine `-`. The
site-packages bug is dead. Final confirmed state:

- **4 RECOVERY**: `forge.py` (232L), `validate_ledger.py` (160L),
  `capsule.py` (106L), `hub.py` (66L) — 564 lines of work with no upstream
  equivalent at all.
- **1 CANDIDATE_SUPERSET**: `gate.py` — hand-port per §1.
- **2 DIVERGED**: `ledger.py` (real two-way merge), `kernel.py` (spine 351L
  vs 91L, +6 spine-only — keep spine).
- **1 SAME_API**: `__init__.py` — spine 71L vs 17L, keep spine.

## §3 Recommended order

0. ~~Re-run compare.py on v4~~ **done — all twins confirmed real (§2b).**
1. **`forge.py`, `capsule.py`, `hub.py`, `validate_ledger.py`** — pure
   RECOVERY, no conflict, lowest risk. Use `port.py` (v5), which puts each on
   its own `cabinet/recover/<name>` branch and leaves master untouched:

   ```bash
   python3 port.py --config config.yaml --list
   python3 port.py --config config.yaml --module hub.py --dry-run
   python3 port.py --config config.yaml --module hub.py
   cd ~/the-forge && git show cabinet/recover/hub
   git checkout cabinet/recover/hub && python -m pytest
   git checkout master && git merge --no-ff cabinet/recover/hub
   ```

   Port `validate_ledger.py` **last** of the four — it validates the ledger,
   so land it after the `ledger.py` merge in step 3 if you want it testing the
   merged version. Order within the other three does not matter.
2. **`gate.py`** — the big one. Hand-port per §1. Commit alone.
3. **`ledger.py`** — two-way merge; the +6 spine-only symbols must survive.
4. **`validate_ledger.py`** — port after ledger.py so it validates the merged
   version, not the old one.
5. **`kernel.py`, `__init__.py`** — no action. Spine wins.

One module, one commit, tests green before the next. If a merge goes wrong,
`git checkout` the spine file and the cabinet copy is still untouched in
`06_ARCHIVE_RAW`.

---

## §4 First Creation Block (gate.py)

```text
Port the PathwayRegistry subsystem from the cabinet gate.py into the live
spine gate.py. Do NOT replace the file.

Live file  : ~/the-forge/forge/fabric/gate.py        (250L, authoritative)
Candidate  : ~/forge-spine/forge/fabric/gate.py      (305L, reference only)

ADD to the live file, preserving every existing docstring and comment:
  - Role(str, Enum) with may_inspect_registry / may_modify_registry
  - Direction, ClearanceLevel enums
  - PathwayDescriptor (frozen dataclass, __post_init__ validation)
  - PathwayRegistry with _Missing sentinel, register/deregister/_lookup/
    list_pathways/pathway_registered/__len__, role-gated mutation
  - FabricGate: pathway_registry ctor param, _revocation_epochs,
    register_pathway/deregister_pathway/list_pathways/pathway_registered,
    revoke_vessel/clear_revocation
  - Decision: DENY_PATH_NOT_DECLARED, DENY_PATH_SUSPENDED, DENY_REVOKED
  - GateStats: matching counters + _bump(decision) dispatch
  - SignedCapability.vessel_id, bound into the HMAC body in sign() and
    verified in authorize()
  - authorize(): Axis-0 pathway check BEFORE crypto; revocation check after
    replay; keep the existing ordering of freshness -> signature -> replay

PRESERVE from the live file, verbatim:
  - The DESIGN THESIS and WHAT I FIXED FROM THE ORIGINAL docstring blocks
  - The ReplayLedger class docstring explaining exactness vs probabilistic
  - All existing method docstrings

THEN write a new docstring block explaining WHY forward-declared pathways
exist (deny-before-crypto on undeclared kinds), in the same voice.

Constraint: existing public API must not break. sign/authorize/enforce/stats/
ledger_size keep working for callers that pass no vessel_id and no registry.
Add tests for: undeclared pathway denied, suspended pathway denied, revoked
vessel denied for tokens issued before the epoch and allowed after.
```

---

## §5 Then close the loop

```bash
python3 file_into_cabinet.py --config config.yaml     # shelve the graded copies
python3 diff_spine.py --config config.yaml --vault ~/Obsidian/ForgeOS
```

After the merges land and tests pass, `~/forge-spine` has given up everything
it had — `06_ARCHIVE_RAW` holds all 17 files, so the folder itself is then
disposable. **One root down.** Next roots, in rising order of mess:
`forge-os-locked-pc`, `forge-workspace`, `forge-os`, `Forge`, `ALLFORGE`,
`core_Forge-unziped`, plus the `Videos/`, `Music/`, and `Downloads/ForgeOS-Arch-Rev/`
copies the find turned up.
