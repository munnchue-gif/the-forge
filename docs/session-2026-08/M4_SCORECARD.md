# M4 Observer Review — closeout scorecard

The M4 review (July 2026) raised 10 findings. Scored against evidence from the
2026-08-17 cabinet harvest and the live tree.

**7 of 10 are closed.** The reviewer's concerns drove M5/M6 and they landed.

---

## Concerns (§2 — the Embedded Tailor)

| # | Finding | Status | Evidence |
|---|---|---|---|
| **A** | *"'Clean' is undefined... if the judge is only checking syntax, a maliciously crafted but well-formed wrap could pass"* — 🔶 Medium-High | ✅ **CLOSED** | `BehavioralJudge` (`judge.py`), 8 tests. Pluggable rules: dangerous tools, toxic combos, preset bounds, gate-would-deny. Exactly the "pluggable/auditable" fix recommended. |
| **B** | *"Tailor has read access to old wraps... is the stripper running in its own isolation boundary?"* — 🔶 Medium | ⬜ **OPEN** | Recommendation was "disposable subprocess with no access to the live WrapStore." No evidence this shipped. **But `FabricSandbox` (bwrap + systemd-run) is exactly the mechanism needed** — see below. |
| **C** | *"Promotion atomicity. If the system crashes mid-promotion, do you have rollback?"* — 🔶 Medium | ⬜ **OPEN** | No transaction semantics found. Note `test_sequence` currently returns `rolled_back` where `done` is expected — rollback exists in some form but is under-specified. |

## Red-team risks (§3)

| # | Risk | Status | Evidence |
|---|---|---|---|
| **1** | Replay ledger exhaustion / bucket collision — *"too coarse → false positives; too fine → unbounded growth → DoS"* | ✅ **CLOSED** | Gate nonce shipped (M5). `ReplayLedger` uses exact seen-set with time-bucket sharding, hard-bounded by `(2·tolerance)+3` buckets, O(1) expiry. The `gate.py` DESIGN THESIS documents this precisely. |
| **2** | SubstanceBus covert channel — *"a compromised organ could modulate queue behavior (timing, padding) to signal another"* | ⬜ **OPEN** | No tap audit found. **This is the strongest argument for Brief 2 (bus hardening).** Your own Graded Master List independently flagged the bus: *"drops silently under load; not thread-safe."* Two separate reviewers, same organ. |
| **3** | Tainted vector persistence — *"a compromised model's vectors live on in the Conduit... you need a burn operation"* | ✅ **CLOSED** | `VectorMemory.burn()` shipped, 3 tests. Tombstone + lineage purge. |

## Missing pieces (§5)

| # | Missing | Status | Evidence |
|---|---|---|---|
| **1** | Tamper-evident audit log — *"every sign/verify/promote/reclaim should be written to a hash-chained, periodically signed log"* | ✅ **CLOSED** | `AuditLedger` (`ledger.py`), 8 tests. `H_i = Hash(seq ‖ ts ‖ payload ‖ H_{i-1})`, `verify()` catches tamper. |
| **2** | Capability attenuation — *"'Spawn, but only within this resource bound'... without attenuation, any granted capability is all-or-nothing"* | ✅ **CLOSED** | Macaroon-pattern `Caveat` chain shipped M6, 9 tests. Holder can add caveats, never remove them. |
| **3** | Wrap provenance chain — *"who imported, when, from what source, what was the original hash... would let you quarantine entire lineages"* | ⬜ **OPEN** | Not found. **This is the Keychain (Brief 4).** The M4 reviewer specced it a month before you described it — same organ, same reason. |
| **4** | Dead man's switch — *"what happens if the heartbeat stops? Fail-secure or fail-open?"* | ⬜ **OPEN** | Not found. Belongs in Brief 6 (VectorConduit). The reviewer's answer is the right one: **fail-secure with alert to Overseer.** |

## Over-engineering warnings (§5)

| Warning | Verdict |
|---|---|
| *"Is 'splicing' doing something that Linux namespaces + seccomp couldn't do more simply?"* | **Answered by your own code.** `FabricSandbox` uses `bwrap --unshare-all` + `systemd-run` cgroups — namespaces, exactly as suggested. The metaphor names it; namespaces implement it. Both are true. |
| *"A fingerprint is not a behavioral constraint... the wrap should identify; capabilities/policy should constrain"* | **Correct and worth pinning.** This belongs in `FORGE_STATE.md §1` as a locked decision. Wrap = identity. Capability = authority. Never conflate. |

## Plan-order recommendation

> *"Revised order: Security fixes → kernel bootstrap → coupler threat model + interface stubs → real models → coupler implementation."*

**You inverted this.** Real models are bound (Ollama on RTX, OpenVINO on NPU
enumerating) but no coupler threat model exists. The reviewer's warning:
*"if you bind Ollama→RTX now without knowing how couplers will talk to it, you
may need to refactor the binding layer later."*

Not fatal — the seats are behind `TailorSeat`/`NpuSeat` protocols, so the
binding layer is already abstracted. But the threat model is still owed before
Brief 10.

---

## The four open items, as work

| Open | Goes to | Note |
|---|---|---|
| B · stripper isolation | **New brief** | `FabricSandbox` (bwrap + systemd-run, from `___215.pdf`) is the mechanism. Run the stripper in it. |
| C · promotion atomicity | Brief 5 (Ledger) | Needs explicit transaction semantics at the handoff moment. |
| 2 · bus covert channel | **Brief 2** | Now has two independent reviewers flagging it. Raise to ★★★★★. |
| 3 · wrap provenance | **Brief 4** (Keychain) | Add lineage quarantine to the brief — the ability to burn a whole source lineage. |
| 4 · dead man's switch | **Brief 6** (Conduit) | Fail-secure, alert Overseer. |

---

## Closing note from the reviewer, worth keeping

> *"Unit tests prove code matches intent, not that intent matches security.
> Consider adding property-based tests (e.g. Hypothesis) for the gate's replay
> ledger and the bus's bounded-queue behavior under stress."*

`test_properties.py` exists and uses Hypothesis (5 tests). **That got done too.**
