# THE FORGE ↔ APP CONTRACT

> **The single source of truth for how the App (cloud, built by Fable 5) talks to
> the Forge (local, on Eugene's PC).** Both sides build against THIS file. If you
> change the interface, change it here first, in a commit, so the other side sees it.
>
> **Golden rule:** the App holds NO logic and NO secrets. It is glass. It *shows*
> the Forge (read-only feed) and *requests* actions (by asking the Forge to mint a
> gate-signed capability). Every decision stays in the Forge's gate on the PC.

---

## 1. Topology

```
┌────────────────────┐         secured tunnel          ┌───────────────────────┐
│   THE APP (cloud)  │   (Tailscale / CF Tunnel /      │   THE FORGE (your PC) │
│   built by Fable 5 │    mTLS localhost bridge)       │   forge_ng, gated     │
│                    │ ──────────────────────────────▶ │                       │
│  - live feed view  │   GET  /feed   (read-only tap)  │  HomeBay / Coupler A  │
│  - capability UI   │   POST /mint   (ask to act)     │  → FabricGate (door)  │
│  - wrapstore view  │   GET  /wraps  /ledger /health  │  → Overseer tap       │
│  NO logic/secrets  │ ◀────────────────────────────── │  → AuditLedger        │
└────────────────────┘         signed responses        └───────────────────────┘
```

The App is a **trusted remote tenant** — exactly the Coupler A / HomeBay pattern
already built in `forge/fabric/coupler.py`. It authenticates over the tunnel and
every action it requests is a **narrowed macaroon grant** (`forge/fabric/caveat.py`).

---

## 2. The HTTP interface (Forge exposes this; App consumes it)

> Forge side: a thin FastAPI wrapper around the kernel — **it adds no logic, it just
> exposes the gate + overseer over localhost/tunnel.** App side: fetch these.

### READ (safe, read-only — the "visual of what's going on")
| Method | Path | Returns |
|--------|------|---------|
| `GET` | `/health` | `{ "booted": bool, "tests_ok": bool, "uptime_s": int, "organs": [...] }` |
| `GET` | `/feed` | SSE/websocket stream of Overseer findings + heartbeat ticks (read-only tap) |
| `GET` | `/wraps` | list of wraps in the WrapStore: `[{id, fingerprint, sealed, reclaimed}]` |
| `GET` | `/ledger?since=<n>` | audit-chain entries (hash-chained, tamper-evident) |
| `GET` | `/sections` | current bus sections + status (for the live map view) |

### ACT (privileged — always through the gate, never executed by the app)
| Method | Path | Body → Effect |
|--------|------|---------------|
| `POST` | `/mint` | `{op, target, caveats[]}` → Forge mints a **narrowed** capability, runs it through `FabricGate.authorize()`, returns `{allowed, finding?}`. App NEVER gets a raw signing key. |
| `POST` | `/concoct/preview` | ask the Concoctinator to fit+judge a drafted shape (observe-mode); returns the judgment, does NOT promote |

**Never expose:** the HMAC secret, `key_resolver`, raw `Capability.sign()`, or any
path that executes on the host without going through the gate.

---

## 3. Capability request shape (what a fader/button sends)

```json
{
  "op": "npu.eval | hopper.spawn | coupler.mount | net.egress | fabric.conform | fabric.splice | fabric.reclaim",
  "target": "<section or wrap id>",
  "caveats": ["read_only", "expires_in:60", "only_section:<id>"]
}
```
The Forge stamps it into a macaroon, narrows it, authorizes at the gate, logs to the
ledger, and returns the decision. The **App just renders the result.**

---

## 4. Security invariants (must hold, both sides)

1. App = glass: no logic, no secrets, no host execution. It asks; the Forge decides.
2. Every action → a **narrowed** grant (least privilege, TTL'd).
3. The read feed is **read-only** (Overseer tap) — it can never mutate state.
4. Transport is authenticated (mTLS / tunnel identity) — a stolen grant must not be
   replayable from another machine (this is the M-hostile coupler backlog item).
5. The Forge is the **one door**. If the app needs a new action, add the capability
   in the Forge first, then expose it here — never a side-channel.

---

## 5. Versioning

Bump `contract_version` on any breaking change and note it in the sync log.

```json
{ "contract_version": "0.1.0", "last_changed_utc": "2026-07-20", "by": "Solene" }
```

---

## 6. Forge-side accessors the bridge needs (build checklist)

The bridge (`forge/bridge/server.py`) is written and parses. It calls these kernel/organ
methods. Ones marked **TODO** don't exist yet — they are small, read-only public accessors
to add on the Forge side (no logic, just safe exposure). Until they exist the bridge returns
`[]`/`503`/`501` gracefully (never fakes data).

| Endpoint | Calls | Exists? |
|----------|-------|---------|
| `/health` | `kernel.organ_names()` | ✅ exists |
| `/ledger` | `kernel.ledger.verify()` | ✅ exists |
| `/ledger` | `kernel.ledger.entries_since(n)` | ✅ built |
| `/feed` | `kernel.overseer.drain_findings(cursor)` | ✅ built |
| `/sections` | `kernel.overseer.section_status()` | ✅ built |
| `/wraps` | `kernel.wrapstore_summary()` | ✅ built |
| `/mint` | `kernel.request_action(op,target,caveats)` | ✅ built (narrow→gate→ledger) |
| `/concoct/preview` | `kernel.arena.preview(shape)` | ✅ built (observe-mode) |

**Rule:** these accessors are READ-ONLY except `request_action`, which must route through
`FabricGate.authorize()` and record to the ledger — it never executes on the host directly.
