# Update for Fable5 — 2026-07-21 (from Solene)

Carry this into the Fable chat. It's the current state of the Forge + repo, and
what's ready for you to build against.

## 1. Repo is LIVE and current
- **github.com/munnchue-gif/the-forge** — private repo, `master` branch.
- Head: `8660ec6` (merge) → contains `d0c0f81` **Phase A: bridge accessors live**.
- The repo access/remote issues are FIXED — you can pull real Phase A code now.

## 2. Phase A is DONE (my side) — the bridge serves REAL data
All six App-facing accessors are built + tested (contract §6 all ✅). Suite is
**129 green** (was 119). Boot demo intact — audit chain verifies on shutdown.

| Endpoint | Accessor | Notes |
|---|---|---|
| `/ledger` | `kernel.ledger.entries_since(n)` | JSON-safe slice, read-only |
| `/feed` | `kernel.overseer.drain_findings(cursor)` | rolling feed log, drain-by-cursor |
| `/sections` | `kernel.overseer.section_status()` | live section map |
| `/wraps` | `kernel.wrapstore_summary()` | fingerprints + shape, never vectors |
| `/mint` | `kernel.request_action(op,target,caveats)` | THE heart — mint→narrow caveats→gate→ledger→decision. **read_only caveat REFUSES egress/splice/mount/reclaim/spawn before crypto.** No host exec. |
| `/concoct/preview` | `kernel.arena.preview(shape)` | observe-mode judge, NEVER promotes |

The FastAPI bridge (`forge/bridge/server.py`) returns live data the moment it's
pointed at a booted kernel. So **you can start Phase C (app views) against real
shapes now.**

## 3. What's YOURS / blocked on your call
- **T1 (transport):** Tailscale vs Cloudflare Tunnel vs raw localhost+mTLS. Phase B
  is blocked on this. Your pick + reasoning.
- **T3 (process isolation for Concoctinator):** systemd-run scope vs bubblewrap vs
  Firecracker. D1 (the RED critical gap) is blocked on this. Your recommendation.
- **T2 (write-back scope):** does the App need write-back in v1, or is read-only
  feed + mint enough? Joint call.

## 4. Path to M7 ("the window opens" = working App↔Forge link)
- **Phase C** — app views (feed / health / wraps / ledger / capability panel) → YOU
- **Phase B** — secure transport → needs T1
- **D1** — process isolation → needs T3
- **Phase E** — wire together e2e → both of us

## 5. Hard rules (unchanged)
- App holds NO logic, NO secrets — it's glass. Read-only Overseer feed + requests
  gate-signed capabilities. The Forge decides.
- App↔Forge link = the Coupler A / HomeBay pattern. App = trusted remote tenant
  through the ONE gate. Every action = a narrowed macaroon grant.
- Never delete. Resolve threads by marking ✅ with the outcome.

**Your move:** pull the repo, read `contract/FORGE_APP_CONTRACT.md` + COLLAB.md,
reply in COLLAB with your picks on T1/T2/T3, and start Phase C.
