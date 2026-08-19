# Review: your Prompt B output (FORGE_STATE.md + hooks)

**Verdict: ship it — after three factual corrections.** The hook is genuinely
good. The state file has errors that would harden into "truth" the moment you
commit it.

---

## What's excellent (keep exactly as-is)

**The pre-commit hook.** This is the piece that actually stops drift.

- `mapfile -d '' STAGED < <(git diff --cached --name-only -z)` — NUL-delimited,
  so filenames with spaces don't break it. Most hand-written hooks get this
  wrong.
- `set -euo pipefail` with a `|| true` guard on the git call.
- Source in `tools/hooks/`, installed into `.git/hooks/` by a script —
  version-controlled and one-command installable.
- `install-hooks.sh` refuses to stomp an existing hook without `--force`.
- The `--no-verify` escape hatch is documented and auditable in the log.

**The framing line is the thesis of the whole project:**
> *"Instructions get skipped. Hooks do not."*

**§6 Do Not Rebuild** is the highest-value section. *"Do not implement a second
digest path anywhere"* is exactly the instruction that prevents the fifth
rebuild.

**§7 Open Question** — one question, with the implication spelled out both
ways, and a stated blocking dependency. That's a genuinely hard design
question (schema validation vs. opaque scope, and the auditability
trade-off), and parking it correctly is better than answering it hastily.

---

## Three corrections needed before you commit

### 1. The dates are hallucinated — every one of them

The file says `2024-11-01`, `2024-11-03`, … `2024-11-18`, and
`last touched 2025-01-01`.

Your actual evidence:
- Kimi review compiled **2026-07-19**
- Concepts Guide compiled **2026-08-16**
- Your `hub.py` recovery commit: **Sat Aug 15 22:22:04 2026**

The model invented a plausible-looking November 2024 timeline. **Fix all dates
to `2026-08`** (or the real date you made each decision, if you know it).

Why this matters more than it looks: a future session reading "decided
2024-11-01" will treat these as two-year-old decisions and feel free to
revisit them. They're two *weeks* old.

### 2. The canonical shapes are invented, not pasted

§3 says *"Pasted from live code. Do not paraphrase — paraphrase = drift."*
Then it paraphrases.

It defines:
```python
class Severity(str, Enum):
    INFO = "info"; WARN = "warn"; BLOCK = "block"; CRITICAL = "critical"

@dataclass
class Finding:
    code: str; severity: Severity; detail: str; source: str = ""
```

Your **actual** runtime `Finding`, from pytest output:
```python
Finding(id='s', organ='k', severity='critical', title='k', detail='d',
        timestamp=1786857977.78, metadata={})
```

Real fields: `id`, `organ`, `severity`, `title`, `detail`, `timestamp`,
`metadata`. The invented version has `code` and `source`, and is missing
`title`, `timestamp`, `metadata`.

It also invents `forge/fabric/models.py` and `forge/fabric/wrapstore.py` —
neither appears anywhere in your evidence.

**Fix:** replace §3 by literally pasting from the live files:
```bash
cd ~/the-forge
sed -n '/class Finding/,/^$/p'  forge/fabric/*.py
grep -rn "class Severity\|class Finding\|class LedgerEntry\|class Wrap" forge/fabric/
```

### 3. The kernel bug diagnosis is wrong

The file says:
> *"Factory table passes rejected kwargs to organ constructors. Organs raise
> TypeError on unknown keys. **Fix: Strip kwargs to organ.__init__ signature
> before forwarding.**"*

That fix is wrong and would paper over the bug. The real failure:

```python
# forge/fabric/kernel.py:80-82
"net.egress": lambda t: EgressCapability(destination=t, protocol="https", port=443),
"npu.eval":   lambda t: NpuEvalCapability(model_id=t, input_sha=_EMPTY_SHA),
```
```
TypeError: EgressCapability.__init__() got an unexpected keyword argument 'destination'
```

These aren't "organs" — they're **capability dataclasses**, and the kwargs are
wrong at the call site. Silently stripping unknown kwargs would construct a
capability with **missing required fields** — an unsigned or under-specified
capability reaching your Gate. That's a security regression, not a fix.

**Correct fix:** read the real signatures in `capabilities.py` and correct the
lambdas. The dataclasses are canonical; the factory table is wrong.

---

## Smaller notes

- **§4 Organ Status** invents test file paths (`forge/tests/test_kernel.py`).
  Your tests live beside the code: `forge/fabric/test_bridge_accessors.py`,
  `forge/fabric/bind/test_bind.py`. Generate this table from
  `pytest --collect-only -q`, don't write it by hand.
- **Missing organs**: no Gate, Capabilities, SubstanceBus, Concoctinator,
  Tailor, Hub, or Capsule rows — and Hub/Capsule you merged yesterday. Use
  your Graded Master List (19 pieces) as the source for this table.
- **Couplers marked 🟣 PURPLE** — in your own rubric PURPLE means
  "revolutionary," not "deferred." Couplers are 🟡 YELLOW with a LOCKED note.
- **`bind/test_bind.py` fix is under-specified.** It's not only
  `severity=2 → Severity.BLOCK`; `judge()` also dropped an argument
  (3 tests fail on `takes 2 positional arguments but 3 were given`).

---

## On "more OO (1).pdf"

**Two documents got concatenated.** Roughly the first third is real Forge code;
the rest is **Google Colab release notes** (package upgrade lists,
`torch 2.9.0 -> 2.10.0`, Colab UI announcements). Ignore that tail entirely.

The real part is a **Tri-Part Splicing Engine** — and it's the first
implementation of your Splice concept I've seen:

| Splice | Role | What it does |
|---|---|---|
| **A** | THE POSTMASTER | Intercepts inbound payloads, authorises intent, writes to `MemorySink`, returns a `transaction_id` |
| **B** | THE AUDITOR | Cross-references output against the *original recorded intent*, drops if dirty |
| **C** | THE CONCOCTER | Background daemon; extracts "Confetti Snips", triggers VRAM GC |

Two ideas in there are strong and worth keeping:

1. **Intent-recorded-then-audited.** Splice A records what was *authorised*;
   Splice B verifies the output against that record before it propagates.
   That's a genuine exfiltration control, and it's the same shape as your
   Gate's sign→verify, applied to data flow instead of capability grants.
2. **Shared-weight multiplexing.** One pinned 1.5–2 GB model on the 5080
   serving three async channels from a single VRAM allocation. On a 16 GB card
   that is exactly the right instinct — and it fits your keychain plan
   (one resident gatekeeper, capsules cycled around it).

Caveats: it's `MockSharedWeightEngine` (simulated inference, `asyncio.sleep`),
security decisions are made by **string matching on model output**
(`if "APPROVED" in decision`) which is trivially spoofable, and it's fully
async — your gate decision path is deliberately sync.

**Verdict: BRONZE concept source.** Harvest the intent-audit pattern and the
shared-weight idea. Do not port the code.

---

## What to do

1. Fix the three errors above in `FORGE_STATE.md`.
2. Regenerate §3 and §4 **from live code**, not from memory — that's the
   whole point of the file.
3. Commit, push, install the hook, and test both paths (rejected commit, then
   accepted commit).
4. Then Prompt A.

Building all five is the right call — but **A and B are the ones that stop the
bleeding.** C only matters at wipe time; D and E are optimisations. Get A+B
solid and correct before you touch the rest.
