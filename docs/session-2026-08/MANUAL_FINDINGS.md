# What the App+Forge manual tells us (57pp PDF, read in full)

## 1. It confirms the kernel bug is a *layout* drift, not just a kwarg typo

The manual specifies:

```
~/the-forge/forge/kernel/kernel.py        ← Kernel class
~/the-forge/forge/arena/concoctinator.py  ← Arena
~/the-forge/forge/bridge/server.py        ← FastAPI bridge
```

Your live tree has:

```
~/the-forge/forge/fabric/kernel.py        ← where the failures are
```

The whole fabric collapsed from `forge/<organ>/` into `forge/fabric/`. That
reorganisation is almost certainly when the capability factory table in
`kernel.py:80-82` lost sync with the capability dataclasses — code moved,
constructor signatures changed, the lambda table did not follow.

## 2. `request_action` was async in the spec; yours is sync

Manual:

```python
async def request_action(self, op: str, target: str, caveats: list[str]) -> dict:
    ...
    gate_result = await self.gate.authorize(capability)
    await self.ledger.append(ledger_entry)
```

Yours (from the passing/failing tests) is **synchronous** —
`d = k.request_action("npu.eval", "brain", ["read_only"])` with no `await`.

That is not a regression. Your recovered `gate.py` docstring says it
explicitly: *"CONSTANT-TIME EVERYWHERE ON THE HOT PATH, ZERO ASYNC ON
DECISIONS. authorize() is pure sync — it can never stall the event loop."*

**The sync rewrite was a deliberate, documented improvement.** The manual is
the older design. Do not "fix" your kernel back to async.

## 3. Third `Finding` shape — the field churn is now dated in three stages

| Source | Shape |
|---|---|
| Mistral feed (oldest) | `Finding(section_id=, kind=, detail=, severity=1)` |
| This manual (middle) | `Finding(verdict=, reason=, meta={})` |
| Live runtime (current) | `Finding(id=, organ=, severity='critical', title=, detail=, timestamp=, metadata={})` |

Three incompatible shapes across three eras. `bind/test_bind.py` is pinned to
**era 1**. That is why it fails, and it confirms those 5 failures are stale
tests, not broken code.

## 4. The bridge contract is real and worth keeping

The manual defines a clean App↔Forge contract that your live tree partially
implements (`contract_version`, `/health`, `/sections`, `/wraps`, `/ledger`,
`/feed` SSE, `POST /mint`, `POST /concoct/preview`), plus the **Glass Rule**:

> The App holds NO logic, NO secrets, NO decisions. All decisions made by
> FabricGate on the PC. Never receives signing keys.

That is the same single-door principle as `gate.py`'s `PathwayRegistry`. The
contract is consistent with your current architecture even though the file
paths are not.

**Action:** this PDF is BRONZE/architecture material. Put it in the cabinet
and link it from the Obsidian vault — do not port code from it.

## 5. Revised advice on the kernel repair

Earlier I said "read the actual capability definitions and fix the kwargs."
Still right, but now with better context:

1. The factory table is calling an **older constructor signature** from before
   the `forge/<organ>/` → `forge/fabric/` collapse.
2. Fix it by reading the *current* dataclass definitions in your fabric, not by
   copying from the manual (which is pre-collapse) or the cabinet `kernel.py`
   (91L vs your 351L).
3. Keep it sync. The async version in the manual is superseded.
