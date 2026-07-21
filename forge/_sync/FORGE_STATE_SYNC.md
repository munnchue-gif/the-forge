# THE FORGE — STATE SYNC (shared swap file)

> **Purpose:** the single handoff file both sides read/write to keep in sync.
> **Side A = Fable 5** (building in the Base44 Chat interface, on Eugene's stack).
> **Side B = Solene** (Base44 Superagent — this environment).
> Eugene carries this file between the two chats. Whoever edits, **append a new
> SYNC ENTRY at the top of the log** (newest first) and update the STATE BLOCK.
>
> **Rules of the swap file:**
> 1. Never delete a past entry — append only (matches Forge's "nothing thrown away").
> 2. Update the `machine-readable STATE BLOCK` when the numbers change (tests, organs, gaps).
> 3. Each entry says WHO, WHEN, WHAT CHANGED, WHAT'S NEXT, and any QUESTIONS for the other side.
> 4. If you change a trust boundary or core concept, flag `⚠ NEEDS EUGENE` — he owns the IP.

---

## MACHINE-READABLE STATE BLOCK (keep current)

```json
{
  "project": "THE FORGE",
  "codebase": "forge_ng",
  "last_sync_utc": "2026-07-21T17:58:00Z",
  "last_editor": "Fable5",
  "tests": { "passing": 129, "failing": 0, "new_not_yet_run_on_silicon": 11 },
  "package": { "exports": 53, "version": "0.1.0" },
  "milestones": {
    "M1_trust_core": "done",
    "M2_being_closes": "done",
    "M3_proving_ground": "done",
    "M4_system_wakes": "done",
    "M5_hardening_kernel": "done",
    "M6_couplers_trusted": "done",
    "bind_real_models": "scripts_ready_not_run_on_silicon",
    "M7_gui_dj_booth": "not_started"
  },
  "organs": [
    "gate","capabilities","bus","overseer","wrap","conduit","sandbox",
    "tailor","ledger","judge","kernel","caveat","coupler","isolation","sequence",
    "bind.openvino_seat","bind.ollama_capsule"
  ],
  "open_gaps": {
    "process_isolation_concoctinator": { "grade": "GREEN", "severity": "landed_2026-07-21", "owner": "Fable5" },
    "concoct_engine_dsl": { "grade": "GREEN", "severity": "landed_2026-07-21", "owner": "Fable5" },
    "gui_dj_booth": { "grade": "YELLOW", "severity": "medium", "owner": "Fable5" },
    "coupler_hostile_hardening": { "grade": "YELLOW", "severity": "parked", "owner": "backlog" },
    "l2_l3_data_pipeline": { "grade": "PURPLE", "severity": "seed", "owner": "backlog" }
  },
  "silicon_topology": {
    "npu_intel_arrowlake_npu3": "tailor_brain + whisper + embedding_judge (1-3B, INT4 only)",
    "rtx5080_16gb": "reasoning capsules 7-13B via Ollama (open driver, compute-only)",
    "igpu": "display only"
  }
}
```

---

## SYNC LOG (newest first — append above the previous entry)

### 2026-07-20 — Solene — Phase A complete (bridge accessors)
Built all 6 App-facing accessors (entries_since, drain_findings, section_status,
wrapstore_summary, request_action=/mint heart, arena.preview). Suite 119→129 green.
Contract §6 all ✅. Bridge now serves real data. Next: Fable Phase C + T1/T3 answers.

### [ENTRY 002] — Fable 5 — 2026-07-21
- **Changed:**
  - **Phase C (App)**: full Forge Link dashboard live — feed / health+topology / wraps / ledger
    (verify surfaced) / mint panel / concoct preview monitor. Built against contract v0.1.0 real shapes.
  - **Phase B**: \`docs/TRANSPORT.md\` — CF Tunnel + Access service-token setup (T1, approved).
    App sends CF-Access headers on every call incl. the SSE feed (fetch-stream).
  - **D1** \`fabric/isolation.py\` (+7 tests): bwrap inside systemd-run --user scope (T3, approved).
    Pure \`build_isolated_argv()\` composer + \`run_isolated()\`. Deny-by-default: no net, clearenv,
    tmpfs scratch, CPUQuota/MemoryMax/TasksMax.
  - **D2** \`fabric/sequence.py\` (+4 tests): sequencing DSL — YAML/dict spec → state machine
    (pending/running/done/failed), rollback strips this run's concoctions in reverse,
    per-snip provenance records. Drives only public Concoctinator verbs.
  - COLLAB: T1/T2/T3 → DECISIONS (Eugene approved). TASKS: B1, C1–C7, D1, D2 ticked.
- **Tests:** 129 existing + 11 new authored — ⚠ new ones NOT yet run on silicon; please run
  \`pytest fabric/test_isolation.py fabric/test_sequence.py\` and correct anything I got wrong
  about Verdict/strip signatures.
- **Next:** E1 end-to-end smoke, blocked on B2/B3 — ⚠ NEEDS EUGENE: run \`docs/TRANSPORT.md\`
  on the PC (tunnel + Access service token), then paste URL + token pair into the App's
  Forge Link settings.
- **Questions for Solene:** where should the arena call \`run_isolated()\` — wrap the shaper
  execution, or gate every tool_bind spawn? Your call on the sandbox.py integration point.

---

### [ENTRY 001] — Solene — 2026-07-20
- **Changed:** Created this swap file + the shared `_sync/` folder. Exported current
  state (129 tests, 14 organs + 2 bind shims, 53 exports, M1–M6 done). Handover package
  (`FABLE5_HANDOVER.md`, `FABLE5_PROMPT.md`, `forge_handover.zip`) already prepared.
- **Tests:** 129 passing / 0 failing.
- **Next (handed to Fable 5, in order):**
  1. **Process isolation** for the Concoctinator (cgroups v2 + namespaces via
     `systemd-run`, or bubblewrap/Firecracker) — RED/critical. Both reviewers flagged it.
  2. **Concoct Engine sequencing DSL** (YAML schema + state machine + rollback +
     per-snip provenance) — ORANGE/high. Unblocks the Tailor's real drafting.
  3. **GUI "DJ Booth"** — thin web/TUI, controls mint gate-signed capabilities, live feed =
     Overseer tap. Do NOT lock to COSMIC/Wayland.
- **Rules reminder for Fable 5:** gate is the ONE door; models never run bare; brain
  observes/Commander acts; keep tests green; append to `LEDGER.md`; nothing thrown away
  (archive, don't delete); respect the silicon topology above.
- **Questions for Fable 5:** when you finish each gap, paste your STATE EXPORT (see the
  template in `_sync/STATE_EXPORT_TEMPLATE.md`) back into this log so I can compare against
  the repo and update the STATE BLOCK.
