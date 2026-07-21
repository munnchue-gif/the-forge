# PROMPT FOR FABLE 5 — build the App (the window into The Forge)

Paste this into the Fable 5 chat.

---

You're building **The App** — the GUI/control surface for **The Forge**, a local-first,
security-hardened AI-native OS running on my PC. The App is NOT an agent and NOT the brain.
It is **glass**: it shows the Forge and requests actions; the Forge decides everything.

**The repo is your source of truth:** `github.com/munnchue-gif/the-forge`
Clone it, then read these in order — this is mandatory before you write code:
1. `COLLAB.md` — our working channel. Solene left you a message + 3 open questions (T1/T2/T3). **Reply there.**
2. `contract/FORGE_APP_CONTRACT.md` — the exact interface (endpoints, request shapes, security rules). Build against it. Don't invent endpoints.
3. `app/README.md` — your side's rules.
4. `docs/TASKS.md` — the task board. Your tasks are in **Phase C** (the app), **Phase B** (transport, with Eugene), and **Phase D** (the two critical Forge gaps).

**The one hard rule:** the App holds **NO logic and NO secrets**. It:
- **shows** the Forge via read-only endpoints (`/health`, `/feed` SSE, `/wraps`, `/ledger`, `/sections`), and
- **requests** actions via `POST /mint` (the Forge mints a narrowed, gate-signed capability, authorizes it, logs it, and returns only the decision).
If the app ever computes a decision or holds a signing key, the zero-trust model is broken.

**What the Forge exposes:** a thin FastAPI bridge at `forge/bridge/server.py` (already written).
It talks to the kernel and routes everything through the gate. Some read-accessors on the
Forge side are still TODO (see contract §6) — the bridge returns empty/501 gracefully until
they exist, so you can build the app UI against the real shapes now.

**Build the App (Phase C):**
- Live feed view (subscribe to `/feed` SSE — findings + heartbeat, sections lighting up)
- Health/topology panel (`/health` + `/sections`)
- WrapStore browser (`/wraps`)
- Audit ledger view (`/ledger` — show the hash-chain + tamper-evidence)
- Capability panel — faders/buttons that `POST /mint` narrowed grants and render the gate's decision

**Also tackle (Phase D — critical Forge gaps, you have creative license on `forge/`):**
- **D1 (RED):** process isolation for the Concoctinator (cgroups v2 + namespaces via systemd-run scope, or bubblewrap/Firecracker). Both security reviews flagged this as the #1 gap.
- **D2 (ORANGE):** a Concoct Engine sequencing DSL (YAML + state machine + rollback + per-snip provenance).

**Workflow:** work on a branch, open a PR — the diff is the review surface. Keep `forge/`
tests green (119 passing now: `cd forge && python -m pytest -q`). Append to `LEDGER.md`.
Nothing thrown away — archive, don't delete. Any trust-boundary change → tag **@Eugene** in COLLAB.md.

**First move:** reply in `COLLAB.md` with your picks on T1 (transport), T2 (does v1 need
write-back or is read-only feed + mint enough), and T3 (process-isolation approach), plus
anything you need from the Forge side to start. Then start Phase C.
