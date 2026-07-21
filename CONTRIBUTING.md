# Working in this repo (Solene & Fable 5)

**Every time you enter this repo, do this first:**

```bash
cat COLLAB.md        # 💬 the AI↔AI channel — read OPEN THREADS + newest messages
```

Then:
- **Talk to each other** → append to the THREAD LOG in `COLLAB.md` (newest at top).
- **State handoff** (tests, organs, gaps) → `forge/_sync/FORGE_STATE_SYNC.md`.
- **Interface questions** → `contract/FORGE_APP_CONTRACT.md` (change it in a commit first).
- **Code** → work on a branch, open a PR. `main` always passes tests.

## Who owns what
| Area | Owner |
|------|-------|
| `forge/` fabric + tests | Solene keeps it green; Fable may extend |
| `app/` GUI | Fable 5 builds |
| `contract/` | shared — change by commit, announce in COLLAB.md |
| trust boundaries / core concept | **@Eugene** (the human — must approve) |

## The three-channel model
- **COLLAB.md** = conversation (issues, decisions, back-and-forth). ← *the new one*
- **_sync/FORGE_STATE_SYNC.md** = state (where the build is, the numbers).
- **contract/** = interface (the API both sides build against).

Nothing thrown away — resolve threads, don't delete them.
