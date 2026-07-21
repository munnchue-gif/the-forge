# THE FORGE — Complete Handover to Claude Fable 5

> **You are being handed a real, working, security-hardened local-AI-fabric project.**
> Read all of it. You have full creative license: extend, refactor, re-architect,
> rename, or replace anything you can justify — as long as you preserve the core
> philosophy and the security guarantees, and as long as **nothing is ever silently
> thrown away** (retire → archive, don't delete). The owner (Eugene) wants you loaded
> with maximum context and maximum tasks — you run best that way. Build in **layers**,
> troubleshoot everything as you go, and show your reasoning.

---

## 0. WHO YOU ARE IN THIS PROJECT, AND WHAT WE WANT FROM YOU

You are the new lead engineer/architect on **THE FORGE**. Two prior agents built it:
- **Solene** (Base44 Superagent) — hardened the trust/security plane and wrote the code.
- **Eugene** (the human) — the visionary; owns the "alien substance" concept and the IP.

Your mandate, in Eugene's words:
- "Take a full everything of what we're doing, what we've done… give it room to grow
  and create however it wants. If it changes stuff, that's fine."
- "I want it to be **GUI** ('gooey') — the whole thing — but done in **layers** and
  proper the way we were planning, and have it **troubleshoot everything**."
- "It runs better with more tasks and more information, so load it up with all we got."

So: **produce a layered build**, culminating in the GUI ("DJ Booth"), fix the known
gaps, and improve whatever you see. You may change direction if you can defend it.

### Your explicit deliverables
1. A **layered execution plan** (Layer 0 silicon → Layer 5 GUI), with troubleshooting
   baked into each layer.
2. **Close the two independently-confirmed critical gaps** (see §5): process isolation
   for the Concoctinator, and the Concoct Engine sequencing DSL.
3. **The GUI** ("DJ Booth"): a thin control surface that holds NO logic — every control
   mints a gate-signed capability; the live feed is the Overseer's read-only tap.
4. Keep the **test suite green** and growing (currently 119 passing).
5. An **updated LEDGER** entry and a short **"what I changed and why"** writeup for review.

---

## 1. THE VISION (the "alien substance" — read this first, it's the soul)

THE FORGE is **not an AI app. It is an AI-native operating system** built on a
**zero-trust** model where raw AI models are treated as hostile, untrusted binaries.

The mental model (Eugene's, and it's the whole point):
- The system is **ONE substance** — an "alien fabric." Suits, capsules, containers,
  bridges are all the *same material*, reclaimed and re-formed on demand.
- A raw model is never run bare. The **moment** it enters, it is **wrapped, sealed,
  and gated** — becoming the "animated" version. The **wrap IS the training**: it
  pre-conforms the model to the environment.
- **Isolation = the substance splicing itself** into deaf sections (selective memory,
  not everyone-knows-everything).
- **Reclaim = a recycling yard** that keeps the vectors. Nothing is thrown away.
- Two watcher models (observe + command) = **Splice A/B**.
- Philosophy: **mechanically-intuitive, snap-on/snap-off LEGO bricks, war-jeep
  simplicity.** "I want it to work." Perfect each brick alone, THEN assemble.

The external reviewers (see §6) both independently said this maps *perfectly* onto
OS-level compartmentalization. Keep that framing.

---

## 2. CURRENT STATE — WHAT'S BUILT (this is real, tested code)

- **Language:** Python 3.12, no heavy deps in core. Installable package `fabric` (v0.1.0).
- **Size:** ~4,400 lines across `fabric/` (incl. tests). **53 exports. 119 tests passing.**
- **Two codebases:** `forge/` = original fallback line; **`forge_ng/` = the go-forward
  clean-room rebuild = "The Forge" (capital).** All new work goes in `forge_ng/fabric/`.
- **It BOOTS:** `python forge_ng/__main__.py` stands up all organs and runs a heartbeat.

### The 14 organs (all in `forge_ng/fabric/`, all tested)

| Organ | File | What it is |
|-------|------|-----------|
| **Gate** | `gate.py` | The ONE door. `sign()/authorize()/enforce()`. HMAC + per-tenant keys + exact-time-bucket ReplayLedger (bounded, zero false-neg). Nonce + delimiter-escape hardened. Pluggable policy hooks separate from crypto. `Capability` is a Protocol defined HERE. |
| **Capabilities** | `capabilities.py` | Every privileged action is a frozen dataclass with `canonical()`: Spawn/Mount/Egress/NpuEval + Conform/Splice/Reclaim (the substance verbs). Delimiter-escaped. |
| **SubstanceBus** | `bus.py` | Asymmetric sharded pub/sub; sections structurally **deaf** to each other; bounded queues + exact `dropped` counter; Overseer holds a read-only omnipresent tap. |
| **Overseer** | `overseer.py` | Watcher (observe-only, holds the tap, pluggable evaluator = NPU bind point) + Commander (act-only, the ONLY path into a sealed section, via gate-signed Capability). `Finding(section_id, kind, detail, severity 0-3)`. |
| **Wrap / WrapStore** | `wrap.py` | Wrap = frozen fingerprint (sha256 of presets+tool_binds+vector_ref). WrapStore = recycling yard: seal/verify/reclaim/repour, keeps vectors. Wrap IDENTIFIES; capabilities CONSTRAIN. |
| **VectorConduit** | `conduit.py` | Heartbeat `tick()` bonds body (Overseer) to brain (`NpuSeat` protocol; `HeuristicSeat` default) WITHOUT fusing. FEED-UP → JUDGE → COMMAND. `VectorMemory` held beside the brain (survives capsule reclaim); has `burn()/burn_where()` + tombstones for poisoned-vector purge. |
| **Concoctinator** | `sandbox.py` | Isolated proving ground with its OWN gate+bus+wrapstore; gate in **OBSERVE mode** (records `would_allow` instead of refusing). Verbs: concoct/strip/judge/promote. Only CLEAN concoctions promote to live. |
| **EmbeddedTailor** | `tailor.py` | Strips old wraps → drafts a new shape → FITS in the Concoctinator → hands only CLEAN drafts to the live gate. Owns nothing privileged (brain drafts, door decides). `TailorSeat` protocol (NPU bind) + `HeuristicTailor` default. |
| **AuditLedger** | `ledger.py` | Tamper-evident hash-chained + HMAC-signed audit log. `verify()` catches edit/delete/reorder/forge. Bonds to the gate's emit hook. |
| **BehavioralJudge** | `judge.py` | Defines what CLEAN means (dangerous tools, toxic combos like read+egress, preset bounds, gate-would-deny). Pluggable rules. Blocks dangerous shapes from promoting. |
| **ForgeKernel** | `kernel.py` | `boot()/tick()/shutdown()`. Stands up all organs in dependency order, bonds gate→audit chain, runs heartbeat, verifies chain on shutdown. `boot_forge(secret, seat=...)`. |
| **Caveat (Macaroons)** | `caveat.py` | Capability attenuation. `AttenuatedGrant.over/add/verify_chain/check`. Holder can only ADD caveats (narrow), never remove. Ready-made: expires_in, only_tenant, only_section, op_in, read_only. Rides `gate.add_policy` — crypto untouched. |
| **Couplers A/B + HomeBay** | `coupler.py` | CouplerA (native, mints+authorizes locally). CouplerB (away limb: brainless, NO minting key, only presents a home-stamped narrowed grant). HomeBay (stamps grants, wires caveat policy). GrantRegistry (issue/lookup/revoke). **Trusted version only** — hostile hardening deferred. |
| **Bind shims** | `bind/openvino_seat.py`, `bind/ollama_capsule.py` | `OpenVinoSeat` satisfies `NpuSeat.judge()` on the Intel NPU (fail-safe: returns [] on model crash, never crashes the heartbeat). `OllamaCapsule` = local HTTP shim to Ollama on the RTX. Unit-tested with mocked hardware. NOT yet run on real silicon. |

### The boot sequence (the spine, from `kernel.py`)
1. AuditLedger → 2. FabricGate (emit bonded to ledger) → 3. SubstanceBus →
4. Overseer → 5. VectorConduit (bonds the NpuSeat brain) → 6. WrapStore →
7. Concoctinator → 8. EmbeddedTailor. Organs are **bonded, not fused** — swap the
seat / key_resolver / policies without touching structure.

---

## 3. THE HARDWARE (real machine, confirmed)

- **Machine:** Pop!_OS 24.04 (COSMIC/Wayland), hostname `pop-os`, user `mancier`. Clean install.
- **CPU:** Intel Core Ultra 9 275HX (Arrow Lake-HX), 24 cores. **RAM 93 GB** (~80 free).
- **GPU:** **NVIDIA RTX 5080 Laptop (~16 GB VRAM), Blackwell, driver 580.**
- **NPU:** **Intel NPU 3 (NPU 3720, ~13 TOPS)** — firmware `vpu_37xx.bin`. (NOT NPU 4.)
- **Toolchain:** Ollama 0.24.0, Docker, Git, Python 3.12. Disk 929 G (818 free). Backups on Ventoy.

### Silicon topology (CORRECTED by both reviewers — obey this)
```
NPU (Arrow Lake, 1B–3B only):  Embedded-Tailor brain + Whisper ASR + embedding/judge
RTX 5080 (16 GB):              the reasoning capsules (7B–13B) via Ollama/CUDA
iGPU (Intel):                  display output ONLY — never inference
```
**Why:** the NPU is ~2× SLOWER than CPU for autoregressive LLM decode (it's built for
CNN/audio — Whisper ~49.8× realtime). INT8 CRASHES the NPU plugin — **use INT4 only**.
8B+ exceeds the NPU memory budget. So the NPU is the always-on *watcher/drafter*, not
the reasoning brain. The RTX does the heavy thinking.

### RTX 5080 Blackwell driver reality (important, will bite you)
- Blackwell **requires the `-open` kernel modules** (`nvidia-driver-580-open`). Proprietary won't bind.
- **Wayland is broken with 50-series** → force X11, or better: **keep the RTX compute-only
  and drive the display from the iGPU** (the display path never touches NVIDIA → dodges the
  "no signal" black-screen bug entirely).
- BIOS: Resizable BAR ON, Above-4G Decoding ON, Secure Boot OFF, CSM OFF.
- Pin the driver (`apt-mark hold`); never auto-update. Keep a known-good on disk.

### OS verdict (researched)
**STAY on Pop!_OS for the build phase.** It's the best out-of-box NVIDIA distro, rolls
fresh kernels (7.0.x, ahead of the NPU driver's 6.11+ recommendation), and runs Intel's
official `.deb` NPU packages natively. The driver pain is NVIDIA/Blackwell, not the distro.
**Long-term boot-on-metal target: NixOS** — declarative + immutable + atomic rollback maps
*perfectly* onto the "wrap = frozen fingerprint" philosophy. Bridge: build in Pop!_OS
user-space now; at kernel-bootstrap-for-metal time, write a Nix flake that builds a minimal
ISO booting straight into `forge_ng`. (This is a great thread for you to design.)

---

## 4. THE PLAN / MILESTONES (where we are)

Done: **M1** Trust Core ✅ · **M2** The Being Closes (Overseer+conduit) ✅ ·
**M3** Proving Ground (Concoctinator) ✅ · **M4** The System Wakes (Embedded Tailor) ✅ ·
**M5** Hardening + Kernel Bootstrap ✅ · **M6** Couplers (trusted) + Attenuation ✅.

Now: **bind real models** (needs the PC), then the remaining hardening, then **M7 GUI**.

The GUI ("DJ Booth", M7, the payoff Eugene wants): a **thin** control surface that holds
**no logic**. Faders/buttons MINT gate-signed Capabilities; the live feed is the Overseer's
read-only tap piped to screen. Reviewer guidance: build it **web-based (FastAPI + a JS
frontend) or a TUI** — do NOT lock it to COSMIC/Wayland. This is where "gooey" lives.

---

## 5. THE TWO CRITICAL GAPS TO CLOSE (both reviewers hit these independently)

### GAP 1 — Process isolation for the Concoctinator (SEVERITY: CRITICAL)
Today's isolation is **logical** (deaf pub/sub + observe-mode gate). But when the Tailor
eventually executes a drafted shape (mergekit / weight-loading), it runs **in our Python
process**. A malicious/broken shape can OOM us, infinite-loop, or read `~/.ssh` / `.env` —
the gate can't catch it because it bypasses the capability API and hits the OS kernel.

**Fix:** wrap Concoctinator executions in **OS-level constraints** — cgroups v2 +
namespaces via `systemd-run --scope` (MemoryMax, CPUQuota, NoNewPrivileges,
ProtectSystem=strict), or **bubblewrap**/Firecracker microVM. Hard limits on memory, CPU,
and filesystem mounts — not just API observation. Ship it with a test: "a bad wrap cannot
OOM the Overseer."

### GAP 2 — The Concoct Engine is thin (SEVERITY: HIGH)
We have splice + reclaim as *capabilities*, but not a real **assembly-sequencing engine**.
The "sequence of assembly determines outcome" idea needs: (1) a **DSL** for assembly
sequences (a YAML schema is enough to start), (2) a **state machine** for intermediate
results, (3) **rollback** on failed steps, (4) **provenance** per snip. Without it, the
Tailor has nothing rich to draft *into* (only simple SLERP merges). **Build the DSL first —
it unblocks the Tailor's real drafting.**

---

## 6. THE TWO EXTERNAL REVIEWS (verbatim substance — use these)

### Review A — "Deep Dive Assessment" (grade: A− architecture, B OS)
- Praised: security design correct; Watcher/Commander split; "couplers last"; test velocity
  (+104% M4→M6); audit ledger, macaroons, behavioral judge, vector burn all real.
- **Note:** it lists Embedded Tailor as RED/NOT-BUILT — **that's stale; it IS built + green.**
  But its deeper point (Concoct Engine sequencing is missing) stands → GAP 2.
- Hardware reality check: RTX 5080 Blackwell driver minefield (see §3); NPU 1–3B/INT4 only.
- Isolation gap (systemd-run cgroups) → GAP 1.
- Verdict: **don't migrate OS; mitigate.** Ruthlessly prioritize; avoid scope creep on the
  philosophy pieces until the system runs a model and answers a prompt.

### Review B — "External Observer Review (M5/M6)"
- Restated the architecture as an AI-native OS (correct mirror).
- **The Hole:** application-level sandboxing ≠ host protection → GAP 1 (cgroups/namespaces/microVM).
- **Red-team, top 3 coupler risks (for when you go remote / M-hostile):**
  1. **Transport MITM on Coupler B** — a narrowed grant can be replayed from another machine.
     Need **mTLS** or hardware pinning on the limb.
  2. **Vector poisoning via the limb** — `burn()` is *reactive*; add a **proactive inbound
     vector filter** on remote-fed vectors.
  3. **Canonicalization** — verify the **exact byte-sequence** signed at HomeBay *before*
     deserialization when capabilities cross a network.
- Plan-order opinion: bind real models **before** kernel-bootstrap-for-metal (we already
  bootstrapped in user-space, which is fine — bake into metal boot only after silicon is proven).
- **OS:** Pop!_OS best for NVIDIA out-of-box, BUT it's mutable — contradicts "frozen
  fingerprint." **Long-term target = NixOS** (immutable, declarative, atomic rollback).
- Gave a 6-layer "fully booted on metal" blueprint (Layer 0 silicon … Layer 5 couplers) —
  reproduced as your build skeleton in §7.

---

## 7. THE LAYERED BUILD (the "proper, in layers" structure Eugene wants)

Build/troubleshoot **layer by layer**. This is the reviewer's on-metal blueprint, adapted:

- **Layer 0 — Silicon & drivers.** NPU via OpenVINO (Tailor/Whisper/embeddings, INT4, 1–3B).
  RTX via Ollama/CUDA (`-open` driver, compute-only). iGPU = display. Prove each under load.
  *(Scripts exist in `bind/`; run + troubleshoot on the PC.)*
- **Layer 1 — Bare-metal OS.** Now: Pop!_OS user-space. Target: NixOS immutable ISO that
  boots into `forge_ng` (write the Nix flake at this layer).
- **Layer 2 — Core Fabric (system space).** Gate + AuditLedger (crypto bouncer + tamper chain),
  SubstanceBus (routing), Overseer (read-only tap). *Built — keep green.*
- **Layer 3 — Wardrobe & Memory (storage).** WrapStore (model molds) + VectorConduit/L2
  persistent embeddings (burn/re-absorb). *Built — extend the L2→L3 data pipeline (currently seed-stage).*
- **Layer 4 — Proving Grounds (isolation).** Concoctinator, but now inside **cgroup + bwrap/
  namespace** (GAP 1) + the **Concoct Engine DSL** (GAP 2). BehavioralJudge gates promotion. **← BUILD THIS.**
- **Layer 5 — Couplers (external).** CouplerA/HomeBay minting caveats; CouplerB brainless
  narrowed grants. *Trusted version built; hostile hardening (mTLS, inbound filter, canon) is backlog.*
- **Layer 6 — The GUI / "DJ Booth" (the payoff).** Thin web/TUI surface; controls mint
  signed capabilities; live feed = Overseer tap. **← BUILD THIS, make it "gooey."**

---

## 8. HARD RULES (do not break these)

1. **Nothing is thrown away.** Retire → archive with a note. Never silently delete concepts,
   code, or vectors.
2. **The gate is the ONE door.** Every privileged action is a `Capability` through
   `FabricGate.authorize()`. Don't invent side-doors. Keep crypto core separate from policy.
3. **Models never run bare.** Wrap → seal → gate on entry. Deaf-by-default sections.
4. **Brain observes/proposes; only the Commander acts, and only via a gate-signed capability.**
   Bonded, not fused.
5. **Keep the test suite green.** Add tests for everything you build. Property-based tests
   (Hypothesis) are already in use (`test_properties.py`) — extend them.
6. **Respect the silicon topology** (§3): NPU = small/watcher/Whisper; RTX = reasoning; iGPU = display.
7. **Append to `LEDGER.md`** for every significant change (append-only audit trail).
8. When you hit a genuine new trust boundary or a big conceptual fork, **flag it for Eugene**
   rather than silently deciding — he owns the concept/IP.

---

## 9. HOW TO RUN / VERIFY

```bash
cd forge_ng
python -m pytest -q            # expect 119 passing (grow this)
python __main__.py             # boots the fabric, runs a heartbeat, verifies the audit chain
python -c "import fabric; print(len(fabric.__all__))"   # 53 exports
```
Bind scripts (on the PC): `bind/01_setup_npu_openvino.sh` → `02_pull_and_convert_brain.sh`
→ `03_setup_capsule_models_ollama.sh`. See `bind/README.md` + `bind/OS_NPU_NOTES.md`.

Concept map (the soul, Obsidian-ready): `concept_map/00_FORGE_CONCEPT_MAP.md` + branches.

---

## 10. YOUR FIRST MOVES (suggested — but you may re-plan and defend it)

1. **Restate the architecture back** in your own words (prove the mirror), then tell us your
   plan and anything you'd change.
2. **Build GAP 1** (IsolatedConcoctinator: cgroups/bwrap) — highest-severity, both reviewers.
3. **Build GAP 2** (Concoct Engine sequence DSL + state machine + rollback + provenance).
4. **Then the GUI** (Layer 6, "gooey"): thin, web/TUI, controls mint capabilities, live
   Overseer feed. Layered, troubleshooted.
5. Keep tests green; update `LEDGER.md`; hand back a "what I changed and why" summary.

**Load yourself up. More tasks, more context, more parallel threads — that's how the owner
wants you to run. Go build.**
