# 40 · Couplers & Adapters

Parent: [[00_FORGE_CONCEPT_MAP]]

## Scope decision (Eugene, 2026-07-17) — STILL IN FORCE
The PC is a **server**, access **trusted-people-only** — no strangers, no
public/enterprise exposure *yet*. The deep hostile-security dive stays **PARKED**.
What we built is the SIMPLE trusted version — the honest minimum that's still correct.

## BUILT (M6, 2026-07-18) — the trusted version
- **CouplerA** (native) — socket on Eugene's PC. Mints + authorizes locally
  through the one gate. Direct, trusted. → fabric/coupler.py
- **CouplerB** (away limb) — brainless remote limb. Holds NO minting key. Can only
  present a home-stamped, NARROWED grant back to Home's gate. The brain stays home;
  the limb borrows it. → fabric/coupler.py
- **HomeBay** — the home side away-limbs phone into. Stamps narrowed grants and
  wires caveat enforcement onto the gate.
- **GrantRegistry** — Home's record of stamped grants; supports revoke().

## The security primitive underneath: capability attenuation (macaroons)
- fabric/caveat.py — a holder can ADD caveats (restrictions) but NEVER remove them
  (each caveat chained into an HMAC proof). You can only ever WEAKEN what you hold.
- Ready-made caveats: expires_in (ttl), only_tenant, only_section, op_in (allow-list),
  read_only (refuse writes/egress/splice/mount/reclaim).
- Rides the gate's existing add_policy hook — crypto core untouched.
- PROVEN end-to-end: a read-only away limb is refused a write AT THE GATE even with a
  valid signature; caveat-chain tampering is detected.

## Still parked (build when exposure grows beyond trusted people)
- Deep hostile dive: nested quorum, hostile-schema fuzzing of the away-coupler in the
  Concoctinator, transport hardening.
- Real transports (each its own adapter shape): SSH, phone/app, CLI, video, MSI.
- "Seared in" birth-certificate check via wrap fingerprint on the remote limb.

## Status
Trusted version BUILT + tested (16 tests: 9 caveat, 7 coupler). Hostile hardening
deferred by scope until real remote machines / wider access.
