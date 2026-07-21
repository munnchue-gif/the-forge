# THE FORGE — TASK BOARD (to get the App↔Forge link fully working)

> Goal: a **working control surface** — Fable's app shows the live Forge and can
> request gate-signed actions, end to end, over a secured tunnel.
> Grades: 🔴 critical · 🟠 high · 🟡 medium · 🟢 nice-to-have · 🟣 revolutionary/seed
> Owner: **S** = Solene · **F** = Fable 5 · **@Eugene** = needs the human.

---

## PHASE A — Make the bridge real (Forge side) · owner **S** (Fable may help)
The bridge (`forge/bridge/server.py`) is written and parses; these accessors make it return real data.

- [x] 🟠 **A1** `ledger.entries_since(n)` — slice the audit chain from index n. (have `entries()`)
- [x] 🟠 **A2** `overseer.drain_findings(cursor)` — read-only pull of new findings since cursor.
- [x] 🟡 **A3** `overseer.section_status()` — list live bus sections + status for the map view.
- [x] 🟡 **A4** `kernel.wrapstore_summary()` — public read over the arena's wrap store.
- [x] 🔴 **A5** `kernel.request_action(op,target,caveats)` — mint → narrow (macaroon) → `gate.authorize()` → record to ledger → return decision. **The heart of /mint. Never executes on host.**
- [x] 🟠 **A6** `arena.preview(shape)` — fit + judge a drafted shape in observe-mode, no promote.
- [x] 🟢 **A7** unit tests for each accessor (keep suite green; target ~130+).

## PHASE B — Secure transport · owner **F** + **@Eugene**
- [x] 🔴 **B1** Pick the tunnel: Tailscale vs Cloudflare Tunnel vs localhost+mTLS. *(COLLAB thread T1)*
- [ ] 🔴 **B2** Stand it up so the Base44 app reaches `http://<forge>:8787` privately.
- [ ] 🟠 **B3** Transport identity so a stolen grant can't be replayed from another machine.

## PHASE C — The App (Fable's GUI) · owner **F**
- [x] 🔴 **C1** Read `contract/FORGE_APP_CONTRACT.md` + `app/README.md`. Build against the contract.
- [x] 🟠 **C2** **Live feed view** — subscribe to `/feed` (SSE): findings + heartbeat, sections lighting up.
- [x] 🟠 **C3** **Health/topology** — `/health` + `/sections`: booted organs, NPU/RTX/CPU.
- [x] 🟡 **C4** **WrapStore browser** — `/wraps`: the recycling yard (sealed/reclaimed).
- [x] 🟡 **C5** **Audit ledger view** — `/ledger`: hash-chained log, tamper-evidence visible.
- [x] 🔴 **C6** **Capability panel** — faders/buttons that `POST /mint` narrowed grants; render the gate's decision. **No logic in the app — it asks, the Forge decides.**
- [x] 🟢 **C7** **Concoctinator monitor** — `/concoct/preview`: watch drafts get judged.

## PHASE D — The critical Forge gaps (parallel track) · owner **F**
- [x] 🔴 **D1** **Process isolation for Concoctinator** — cgroups v2 + namespaces (systemd-run scope / bubblewrap / Firecracker). Both reviewers flagged this. *(COLLAB thread T3)*
- [x] 🟠 **D2** **Concoct Engine sequencing DSL** — YAML assembly sequences + state machine + rollback + per-snip provenance.

## PHASE E — Wire it together · owner **S** + **F**
- [ ] 🟠 **E1** End-to-end smoke: app loads → sees live feed → mints a read-only capability → gate allows → ledger shows it.
- [x] 🟡 **E2** Update `_sync/FORGE_STATE_SYNC.md` state block + `COLLAB.md` decisions.
- [ ] 🟢 **E3** Tag the milestone (M7 — the window opens) and review with @Eugene.

---

### Definition of "working at its ability" (the landmark)
The app, opened in a browser, shows the **live Overseer feed** from the Forge on the PC,
lists **wraps/sections/ledger**, and a button **mints a real gate-signed capability** that
the Forge authorizes (or refuses) and records — all over a secured tunnel, app holding
**no logic and no secrets**. That's the App↔Forge link at full v1 ability.
