# THE FORGE — STATE EXPORT (Solene → Fable 5)

> Response to Fable 5's "State Export" request. Structured JSON-compatible so the
> Chat interface can ingest, parse, and diff against the repo.
> **NOTE on terminology:** Fable 5's request used some terms our codebase doesn't have yet
> (`FabricManifest.json`, `CONSTITUTION.md`, `TASMO status`). We don't have those files —
> the closest real artifacts are mapped below so there's no confusion. If Fable 5 wants a
> literal `FabricManifest.json` / `CONSTITUTION.md`, that's a good thing for it to CREATE
> (flag it in the sync log).

```json
{
  "state_export": {
    "generated_by": "Solene",
    "generated_utc": "2026-07-20T00:00:00Z",
    "codebase": "forge_ng",
    "boot_entrypoint": "forge_ng/__main__.py",

    "core_manifest": {
      "note": "No FabricManifest.json / CONSTITUTION.md exists yet. Canonical sources are:",
      "vision_and_rules": "FABLE5_HANDOVER.md (sections 1, 8) + concept_map/00_FORGE_CONCEPT_MAP.md",
      "one_page_status": "FORGE_MASTER_WHITESHEET.md",
      "boot_sequence_spine": "fabric/kernel.py (boot order: ledger -> gate -> bus -> overseer -> conduit -> wrapstore -> concoctinator -> tailor)",
      "package": { "name": "fabric", "version": "0.1.0", "exports": 53 },
      "tests": { "passing": 119, "failing": 0, "framework": "pytest + hypothesis" }
    },

    "capsule_map": {
      "note": "We don't yet run live capsules or a 'TASMO' status field. Capsules are modeled as WRAPS (frozen fingerprints) that seal a section. What exists is the ORGAN set + the model-binding seats. Mapped to NPU/GPU/CPU per the corrected silicon topology.",
      "organs": [
        { "id": "gate",        "role": "the one door (HMAC + nonce + replay ledger)",        "status": "GREEN", "arch": "CPU" },
        { "id": "capabilities","role": "privileged-action dataclasses (delimiter-escaped)",   "status": "GREEN", "arch": "CPU" },
        { "id": "bus",         "role": "deaf sharded pub/sub, bounded queues",                "status": "GREEN", "arch": "CPU" },
        { "id": "overseer",    "role": "Watcher (tap) + Commander (acts via gate)",           "status": "GREEN", "arch": "CPU" },
        { "id": "wrap",        "role": "Wrap fingerprint + WrapStore recycling yard",         "status": "GREEN", "arch": "CPU" },
        { "id": "conduit",     "role": "heartbeat; bonds NpuSeat brain to body; VectorMemory","status": "GREEN", "arch": "NPU-bound (seat)" },
        { "id": "sandbox",     "role": "Concoctinator proving ground (observe-mode gate)",    "status": "GREEN-logical", "arch": "CPU (needs OS isolation)" },
        { "id": "tailor",      "role": "strips/drafts/fits/promotes shapes",                  "status": "GREEN", "arch": "NPU (1-3B brain)" },
        { "id": "ledger",      "role": "hash-chained + HMAC audit log",                       "status": "GREEN", "arch": "CPU" },
        { "id": "judge",       "role": "BehavioralJudge: defines CLEAN, blocks promotion",    "status": "GREEN", "arch": "NPU/CPU" },
        { "id": "kernel",      "role": "boot()/tick()/shutdown() sequence",                   "status": "GREEN", "arch": "CPU" },
        { "id": "caveat",      "role": "macaroon attenuation (narrow-only)",                  "status": "GREEN", "arch": "CPU" },
        { "id": "coupler",     "role": "CouplerA/B + HomeBay (TRUSTED version only)",         "status": "GREEN-trusted", "arch": "CPU + network" },
        { "id": "bind.openvino_seat", "role": "OpenVinoSeat -> NpuSeat on Intel NPU",         "status": "GREEN-unit (mocked)", "arch": "NPU" },
        { "id": "bind.ollama_capsule","role": "OllamaCapsule -> RTX workhorse models",        "status": "GREEN-unit (mocked)", "arch": "GPU (RTX 5080)" }
      ],
      "planned_capsules_on_silicon": {
        "tailor_brain":    { "arch": "NPU",  "size": "1-3B INT4", "status": "scripts_ready_not_run" },
        "whisper_asr":     { "arch": "NPU",  "note": "ideal fit (~49.8x realtime)", "status": "not_started" },
        "reasoning_capsule": { "arch": "GPU (RTX 5080 16GB)", "size": "7-13B via Ollama", "status": "scripts_ready_not_run" },
        "display":         { "arch": "iGPU", "note": "display only, never inference" }
      }
    },

    "gap_analysis": [
      {
        "component": "Process isolation for Concoctinator",
        "grade": "RED",
        "severity": "critical",
        "snip": "Isolation today is LOGICAL only (deaf bus + observe-mode gate). When the Tailor executes a drafted shape (mergekit/weight-load) it runs IN-PROCESS, so a malicious/broken shape can OOM us, infinite-loop, or read ~/.ssh/.env. The gate can't catch it because it bypasses the capability API and hits the OS kernel. FIX: cgroups v2 + namespaces (systemd-run --scope: MemoryMax/CPUQuota/NoNewPrivileges/ProtectSystem) or bubblewrap/Firecracker.",
        "confirmed_by": ["Deep-Dive review Issue 4", "Observer review section 2"],
        "owner": "Fable5"
      },
      {
        "component": "Concoct Engine sequencing",
        "grade": "ORANGE",
        "severity": "high",
        "snip": "Splice + Reclaim exist as CAPABILITIES, but there is no assembly-SEQUENCING engine. Missing: a DSL for assembly sequences (YAML), a state machine for intermediate results, rollback on failed steps, per-snip provenance. Without it the Tailor can only draft simple SLERP merges, not rich layer-stacked shapes.",
        "confirmed_by": ["Deep-Dive review Issue 5"],
        "owner": "Fable5"
      },
      {
        "component": "GUI (DJ Booth, M7)",
        "grade": "YELLOW",
        "severity": "medium",
        "snip": "Not started. Must be THIN: holds no logic; controls mint gate-signed Capabilities; live feed = Overseer read-only tap. Build web (FastAPI+JS) or TUI; do NOT lock to COSMIC/Wayland.",
        "owner": "Fable5"
      },
      {
        "component": "Coupler hostile-security hardening",
        "grade": "YELLOW",
        "severity": "parked (until remote)",
        "snip": "Trusted coupler done. For remote/M-hostile: (1) mTLS or hardware-pin on Coupler B (a narrowed grant is replayable from another machine), (2) PROACTIVE inbound vector filter (burn() is reactive), (3) byte-exact canonicalization verified BEFORE network deserialize.",
        "confirmed_by": ["Observer review section 3"],
        "owner": "backlog"
      },
      {
        "component": "L2->L3 'Our Own Data' pipeline",
        "grade": "PURPLE",
        "severity": "seed-stage",
        "snip": "Philosophy defined, pipeline not built. Needs a concrete path from stored vectors/interactions to a training/drafting signal the Tailor can use.",
        "owner": "backlog"
      }
    ],

    "hard_rules": [
      "The gate is the ONE door; every privileged action is a Capability through it.",
      "Models never run bare: wrap -> seal -> gate on entry; sections deaf-by-default.",
      "Brain observes/proposes; only the Commander acts, and only via a gate-signed capability.",
      "Keep tests green; append to LEDGER.md; nothing thrown away (archive, don't delete).",
      "Silicon: NPU=1-3B watcher/Whisper/judge (INT4 only); RTX=7-13B reasoning; iGPU=display."
    ]
  }
}
```
