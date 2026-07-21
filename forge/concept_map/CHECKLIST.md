# M5 — Hardening Pass (from the M4 Observer Review)

## Status: security fixes + 3 new organs DONE. Tests 53 -> 82.

### Security fixes (both shipped, regression-tested)
- ✅ **Gate nonce** — two legit identical actions no longer falsely blocked as replay; a true token replay is still caught. Nonce bound into the HMAC (can't be swapped).
- ✅ **Capabilities delimiter escape** — a `|` smuggled into any caller-controlled field is escaped, so it can't shift canonical boundaries to forge a different-but-same-signature action.

### New organs (each with its own tests)
- ✅ **AuditLedger** (fabric/ledger.py) — tamper-evident hash-chained + HMAC-signed audit log. verify() catches edit / delete / reorder / forged-signature. Binds to the gate's emit hook. **8 tests.**
- ✅ **BehavioralJudge** (fabric/judge.py) — finally defines what "CLEAN" means. Grades a concoction's realized shape (dangerous tools, toxic combos like read+egress, preset bounds, gate-would-deny) and blocks dangerous shapes from promoting to live. Pluggable rules. **8 tests.**
- ✅ **VectorMemory.burn()** (fabric/conduit.py) — purges poisoned vectors; a burned ref is tombstoned and can't be silently re-absorbed; lineage purge via predicate. **3 tests.**

### Deeper tests the review demanded
- ✅ **Property-based tests** (fabric/test_properties.py, Hypothesis) — replay ledger proven across thousands of generated inputs: zero false negatives, zero false-positive lockout; nonce fix holds for arbitrary caps; bounded queue never overflows + exact drop accounting; no canonical collision via delimiter. **5 property tests.**
- ✅ **Full system audit** — every cross-module import resolves; 11 organs; ~2750 non-test lines.

### Adopted-but-queued (design ready)
- ⏳ **Capability attenuation** (macaroon-style caveats) — for the coupler/remote phase (M6), where we hand narrowed rights to remote callers.
- ⏳ **NPU seat binding** — research decided: **OpenVINO GenAI** (only viable Linux NPU path; ipex-llm is Windows-only).

### Test totals
| Milestone | Tests |
|-----------|-------|
| M4 (before) | 53 |
| **M5 (now)** | **82** |

### NEXT
1. Kernel bootstrap — make forge_ng BOOT as a living process (main.py), not just import.
2. Coupler threat-model + interface stubs (before real models).
3. Bind real models (Ollama -> RTX capsules; brain -> NPU via OpenVINO GenAI).
4. Couplers last (highest hacker surface).
