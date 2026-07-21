# THE FORGE — Master One-Page Whitesheet

**Home:** munnchue@gmail.com · **Status:** 119/119 tests green · M6 done, model-binding scripts ready · **Machine:** Pop!_OS · RTX 5080 (16GB) · Intel Arrow Lake NPU · 93GB RAM

---

## THE MODEL (what I'm building, in one breath)
An omnipresent, sentient local AI **fabric**. Raw models are never used bare — the moment they touch the system they get **wrapped, sealed, and gated**, becoming the "animated alien" version. One overseer sees all; every section is **deaf by default** (selective memory, not everyone-knows-everything). The fabric can **splice, concoct, recycle, and re-pour** models — so we can literally design anything.

---

## THE BOARD (folders = big categories, files = the parts)
| # | Category | Holds |
|---|----------|-------|
| 01 | Omnipresent Sentient Fabric | Overseer, VectorConduit, SubstanceBus, Our Own Data |
| 02 | The Trust Door (Security) | Gate, Capabilities |
| 03 | The Substance & Body | Substance, Skeleton, Awakening, Pieces/LEGO |
| 04 | The Wardrobe | Wrap, Wardrobe, **Embedded Tailor 🔴**, Capsule Shrink/Restore |
| 05 | Couplers, Sockets & Adapters | Couplers A/B, Sockets & Layers, Socket Coupler |
| 06 | Capsules & Memory | Capsule Architecture, VectorMemory |
| 07 | The Proving Ground | Concoctinator, Open Threads |
| 08 | Models & The Concoct Engine | Concoct Engine, Hugging Face intake |
| 90 | Archive | changed / retired parts (nothing deleted) |
| 91 | Solene's Input | my recommendations |
| 92 | Deep Dive | web-research intake for next phase |
| 93 | Progress | milestones + layers |

---

## GRADES (your rubric)
🟢 solid · 🟡 needs a look · 🔴 weak/missing · 🟣 revolutionary · 🟠 needs custom work

- **🟢 GREEN (built):** Gate (+nonce), Capabilities (+escape), SubstanceBus, Overseer, Wrap, VectorConduit, VectorMemory (+burn), Concoctinator, **Embedded Tailor**, AuditLedger, BehavioralJudge, **ForgeKernel** (boots!), **Couplers A/B (trusted)**, Capability Attenuation, Skeleton, Capsule Architecture, Pieces/LEGO
- **🟡 YELLOW:** Substance, Wardrobe, Sockets & Layers, Hugging Face intake
- **🟠 ORANGE:** Capsule Shrink/Restore, Concoct Engine (mergekit backend chosen)
- **🟣 PURPLE:** The Awakening, Our Own Data
- **🔴 RED:** *(none open — Embedded Tailor is now built 🟢)*

---

## WHERE WE ARE
✅ M1 Trust Core · ✅ M2 The Being Closes · ✅ M3 Proving Ground
✅ M4 The System Wakes (Embedded Tailor) · ✅ M5 Hardening + Kernel Bootstrap (BOOTS)
✅ M6 Couplers (trusted version) + Capability Attenuation
🚧 **Bind real models** — Ollama→RTX capsules, brain→NPU via OpenVINO GenAI ← **NEXT (on the PC)**
⬜ M7 DJ Booth GUI (last, thin)

---

## THE NEXT BRICK
**Bind real models** — the first hands-on-the-PC step. Small brain → Intel NPU via OpenVINO GenAI (only viable Linux NPU path); capsule workhorses → RTX 5080 via Ollama; mergekit for splicing. Scripts + tested shims are in `bind/`. Run after the mirror review.

*Nothing is ever thrown away — retired parts move to Archive as a record.*
