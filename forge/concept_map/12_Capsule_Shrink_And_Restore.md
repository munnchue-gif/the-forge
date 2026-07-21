# 12 · Capsule Shrink & Restore (time-travel resume)

Parent: [[00_FORGE_CONCEPT_MAP]] · comes off [[11_Sockets_And_Layers]]

## The idea
When a capability layer (e.g. video) is done for now, you **decouple** it. The
whole thing **capsulizes** — shrinks into a small encapsulated **data pack**.

- Keep it on the PC, or **offload to USB / Ventoy**.
- Optionally **encrypt it right there** (USB could even carry its own adapter).
- Later, **plug the socket back in** → the whole thing **spawns back up, fires
  up right where you left off** — "like going back in time."

## Why this matters
It's suspend/resume for an entire specialized Forge-personality. No rebuild, no
retrain — the state is sealed in the pack (ties to the [[02_The_Forge_Skeleton]]
wrap fingerprint: the pack's identity is sealed, so a tampered pack won't fire).

## Buildable primitives it maps to (already have most)
- Wrap = the sealed identity of the pack.
- WrapStore reclaim/repour = shrink (keep vectors) → restore.
- Encryption-at-rest + USB adapter = NEW small piece to design later.

## Open
- Format of the data pack (single encrypted blob? dir?) → [[99_Open_Threads]]
