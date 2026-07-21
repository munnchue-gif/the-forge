# PASTE-IN PROMPT FOR CLAUDE FABLE 5

Copy everything below the line into Fable 5, and attach the `forge_handover.zip`
(the whole codebase + concept map + reviews). Fable 5 uses long context actively and
self-corrects mid-task, so give it the full package — it thrives on load.

────────────────────────────────────────────────────────────────────────────

You are the new lead engineer and architect on **THE FORGE** — a local-first,
security-hardened, AI-native operating system built on a zero-trust model where raw AI
models are treated as hostile, untrusted binaries. I'm handing you the entire project:
the vision, ~4,400 lines of real tested Python (119 passing tests, 14 organs), the
concept map, the hardware truth, and two external technical reviews.

**Read `FABLE5_HANDOVER.md` first — it is the complete brief.** Then read the code in
`forge_ng/fabric/`, the concept map in `forge_ng/concept_map/`, and the two reviews.

I want you loaded with maximum context and running many tasks in parallel — you perform
best that way. You have **full creative license**: extend, refactor, re-architect,
rename, or replace anything you can justify, as long as you (a) preserve the core
philosophy (the "alien substance" / one-door / deaf-by-default / bonded-not-fused
principles), (b) preserve the security guarantees, and (c) **never silently throw
anything away** — retire to an archive with a note instead of deleting.

Build in **proper layers** (Layer 0 silicon → Layer 6 GUI, per §7 of the handover) and
**troubleshoot everything as you go**. Concretely, I want you to:

1. **Restate the architecture back to me** in your own words to prove the mirror, then
   give me your plan and anything you intend to change (and why).
2. **Close the two critical gaps** both reviewers flagged:
   - **Process isolation** for the Concoctinator (cgroups v2 + namespaces via
     `systemd-run`, or bubblewrap / Firecracker) — hard memory/CPU/filesystem limits so
     a malicious or broken drafted shape cannot OOM us or read host files. Add a test
     proving a bad wrap can't take down the Overseer.
   - **The Concoct Engine sequencing DSL** — a YAML assembly-sequence schema + a state
     machine for intermediate results + rollback on failed steps + per-snip provenance,
     so the Embedded Tailor has something rich to draft into.
3. **Build the GUI ("DJ Booth")** — the payoff. Make it **gooey** but **thin**: it holds
   NO logic; every control mints a gate-signed Capability, and the live feed is the
   Overseer's read-only tap. Web-based (FastAPI + JS) or a TUI — do NOT lock it to the
   COSMIC/Wayland desktop. Do it in layers, troubleshooting each.
4. **Respect the silicon topology:** NPU (Intel Arrow Lake, 1–3B, INT4 only) = the
   Embedded-Tailor brain + Whisper + embedding/judge; RTX 5080 (16 GB) = the reasoning
   capsules (7–13B) via Ollama; iGPU = display only. The NPU is a watcher/drafter, not
   the reasoning brain.
5. **Keep the test suite green and growing** (property-based tests via Hypothesis are
   already in use). **Append to `LEDGER.md`** for every significant change, and hand me
   back a clear **"what I changed and why"** summary for review.

Obey the hard rules in §8 of the handover. When you hit a genuine new trust boundary or
a major conceptual fork, flag it for me rather than silently deciding — I own the concept.

Now go. Load yourself up with the whole thing and start building.
