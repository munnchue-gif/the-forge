# The 11 failures — diagnosed from the Mistral feed

The old feed is too different to use as a build guide, but it dated one thing
precisely: **the shape of `Finding` before the refactor.**

## The smoking gun

Old feed (line 3596), constructing a Finding:

```python
Finding(section_id="sys", kind="anomaly", detail=..., severity=1)
```

Your current runtime, from the pytest failure output:

```python
Finding(id='s', organ='k', severity='critical', title='k', detail='d',
        timestamp=1786857977.78, metadata={})
```

Every field changed. `section_id`→`id`, `kind`→`organ`, and critically
**`severity` went from `int` to a string enum** (`1` → `'critical'`). A `title`,
`timestamp`, and `metadata` were added.

That single refactor explains the `bind/test_bind.py` cluster outright:

| Failure | Cause |
|---|---|
| `test_seat_clamps_severity` — `assert 'critical' == 3` | test written against int severity |
| `test_seat_parses_findings_from_model_json` — `NameError: Finding` | `Finding` moved; test's import no longer resolves |
| 3 × `judge() takes 2 positional args but 3 were given` | `judge(observations, memory)` → `judge(observations)`; memory became internal |

**The tests are older than the code.** They are not describing a bug; they are
describing an API that was deliberately replaced and never re-synced.

## The other cluster is different — that one is a real bug

`test_bridge_accessors.py` fails because **live code calls itself wrongly**:

```python
# forge/fabric/kernel.py:80-82
"net.egress": lambda t: EgressCapability(destination=t, protocol="https", port=443),
"npu.eval":   lambda t: NpuEvalCapability(model_id=t, input_sha=_EMPTY_SHA),
```

→ `TypeError: EgressCapability.__init__() got an unexpected keyword argument 'destination'`

This is not a stale test. `kernel.py`'s capability factory table passes kwargs
the capability dataclasses do not accept, so `request_action()` raises
`TypeError` **before it ever reaches the gate**. Any caller using
`request_action` for egress or npu.eval is broken right now.

This is the same `kernel.py` that `compare.py` graded **DIVERGED, +6 spine-only
symbols**. The kernel and its capability definitions drifted apart.

## Two brains, one door

The feed confirms the architecture you described:

```
forge/bind/openvino_seat.py    ← NPU / OpenVINO   (Intel, 13 TOPS)
forge/bind/ollama_capsule.py   ← RTX / Ollama     (5080, 16GB)
```

Two model seats behind one `FabricGate`. That is a coherent design, and it is
why `gate.py`'s `PathwayRegistry` (the CANDIDATE_SUPERSET find) matters — it is
the mechanism that keeps two brains from becoming two doors.

`codex` appears **0 times** in the old feed and 3 times in your current logs.
It is the newest organ, added after this architecture settled — consistent with
your read that it is where things went sideways.

## Test count moved too

Old README: `python -m pytest -q   # expect 119 passing`
Today: `11 failed, 123 passed` = **134 tests**.

15 tests were added since that README. The suite grew while parts of it went
stale — normal for fast work, but it means "expect 119" is no longer a usable
baseline. **Your baseline is `11 failed, 123 passed`.** Anything else after a
port means the port did it.

## What to do, in order

1. **Finish the recoveries.** `forge.py` next, then `ledger.py`'s two-way
   merge, then `validate_ledger.py`. None of them touch the failing code.
2. **Fix `kernel.py`'s factory table** — real bug, small blast radius. Read the
   actual `EgressCapability` / `NpuEvalCapability` definitions and correct the
   kwargs. Do this *after* the ledger merge, since `compare.py` says the
   candidate `kernel.py` has 6 symbols yours lacks and one of them may be the
   corrected factory.
3. **Re-sync `bind/test_bind.py` to the new `Finding`** — mechanical, do it
   last. Update field names, expect string severity, drop the `memory` arg.

Do not merge the candidate `kernel.py` to fix this. It is 91 lines against your
351 and would lose far more than it repairs.
