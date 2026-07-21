# THE APP — the window into the Forge (built by Fable 5)

This is the **GUI / "DJ Booth"** — a thin control surface for the Forge. Fable 5 builds
this. It is a Base44-built web app (not an agent).

## The one rule
**This app holds NO logic and NO secrets.** It is glass. It:
- **shows** the Forge (the read-only Overseer feed, wraps, audit ledger, section map), and
- **requests** actions by asking the Forge to mint a gate-signed, narrowed capability.

Every decision happens in the Forge's gate on the PC. If the app ever computes a
decision or holds a signing key, the zero-trust model is broken.

## Build against the contract
See [`../contract/FORGE_APP_CONTRACT.md`](../contract/FORGE_APP_CONTRACT.md) for the exact
endpoints and request shapes. Don't invent endpoints — if you need a new action, it gets
added to the Forge first, then the contract, then here.

## Suggested views (v1)
1. **Live feed** — the Overseer tap (`GET /feed`): sections lighting up, findings, heartbeat.
2. **Capability panel** — faders/buttons that `POST /mint` narrowed grants; render the gate's decision.
3. **WrapStore browser** — `GET /wraps`: the recycling yard, what's sealed/reclaimed.
4. **Audit ledger** — `GET /ledger`: the hash-chained log, live (tamper-evidence visible).
5. **Health/topology** — `GET /health` + `/sections`: what's booted, NPU/RTX/CPU load.

## Bridge to the Forge
The Forge exposes a thin FastAPI over a secured tunnel (Tailscale / Cloudflare Tunnel).
The app is a **trusted remote tenant** through Coupler A / HomeBay — authenticated
transport, least-privilege grants. Keep the transport auth (mTLS/tunnel identity) real
so a stolen grant can't be replayed from another machine.
