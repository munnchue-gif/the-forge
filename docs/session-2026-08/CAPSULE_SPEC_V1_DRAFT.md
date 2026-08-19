# CAPSULE SPEC v1 — DRAFT

**Status: DRAFT. Not authority.**
Check every line against the two sources before you trust it:

- `FORGE_ARCHITECTURE_REVIEW.md` **R4**, line 417 — the manifest half
- `~/FORGE_REVIEW/c44-capsule/smart_capsule.py` — the runtime half

This document exists to join them. Where it and a source disagree, the
source wins and this file gets corrected.

---

## 0. What a capsule is

Two sessions described it two ways and both are right.

**At rest** it is a content-addressed archive with a signed manifest — a
`.suit.zip` you can hand to someone.

**In flight** it is, in the words of the `SmartCapsule` docstring:

> *"a secure micro-hypervisor matrix — it entirely determines what happens
> inside its walls. The SwarmOrchestrator is simply an ignition key; the
> capsule's immutable slot manifesto governs all execution."*

The manifest is not metadata *about* the capsule. The manifest **is** the
authority; the runtime enforces it. Nothing inside a capsule may grant
itself something the manifest did not already list.

---

## 1. Container format

From `master_pack.md:258` (repeated at `:1018` — the file contains a
duplicate of itself; do not be confused):

```
my_capsule.suit.zip
├── manifest.json      REQUIRED
├── constraints.yaml   REQUIRED
└── state.json         OPTIONAL (absent = DRAFT with no runtime state)
```

Missing `manifest.json` raises, with this exact message:

```
CapsuleParseError: Capsule missing required 'manifest.json'
```

Keep the message byte-identical. It is already referenced elsewhere.

---

## 2. Manifest

R4's schema, with correction **C4** applied (identity and provenance head
split apart) and `spec_version` added.

```yaml
spec_version: 1                      # C4. Never ship a format without one.

identity:
  capsule_id:   "018f3a2b-..."       # uuid-v7, time-ordered
  content_hash: "sha256:..."         # hash(core_manifest) — STABLE
  name:         "human-readable"

provenance:
  provenance_head: "sha256:..."      # hash(entry_n || head_{n-1}) — MOVES
  parent_id:       "018f3a2a-..."    # null if root
  merged_from:     []                # capsule_ids, for merge lineage
  created_at:      "2026-08-19T..."
  created_by:      "..."

capabilities:                        # exhaustive. Absent = denied.
  - kind: "fabric.splice"
    region_id: "..."
    mode: "split"
    sections: 2
    deaf: true

lifecycle:
  state: "DRAFT"                     # see §3

integrity:
  checksum:  "sha256:..."            # over the payload
  signature: "..."                   # required to leave DRAFT
```

### Why `content_hash` and `provenance_head` are two fields

They have opposite requirements and one value cannot satisfy both.

- **Identity must be stable.** The same capsule must still be the same
  capsule tomorrow, or references rot.
- **A provenance head must change on every append**, or the chain proves
  nothing about history.

One hash doing both was the bug behind correction C4. Two fields.

### On capabilities

`capabilities` is **exhaustive and closed**. Anything not listed is denied.

This is the Gate's model, and it is the reason the Gate beats the threat
regex in `peer_review.py`. That regex enumerates badness — it misses
`rm -r -f /`, `rm --recursive --force`, `find . -delete`, and anything
base64-encoded. Denylists are unbounded by construction. **The Gate
enumerates goodness, which is bounded.** `peer_review.py`'s patterns stay
advisory only; they are not a boundary and must never be treated as one.

---

## 3. Lifecycle

R4's state machine, unchanged:

```
DRAFT ──validate──> VALIDATED ──activate──> ACTIVE
                                              │  │
                                     pause────┘  └────archive
                                        │              │
                                      PAUSED ──────> ARCHIVED
```

- **DRAFT** — mutable, unsigned, may not hold capabilities
- **VALIDATED** — signature verified, manifest frozen, not yet running
- **ACTIVE** — running, slices live
- **PAUSED** — frozen, state retained, resumable
- **ARCHIVED** — terminal, read-only

Signature verification happens on `DRAFT → VALIDATED`, and this mirrors
`promote_to_l1` in `forge_security.py`, which verifies a signature before
moving code to L1. Same gate, same reasoning: **the transition is the
checkpoint, not the residence.**

---

## 4. Runtime — the A/B slice model

From `smart_capsule.py`. This is the part R4 does not have.

A capsule holds **two slices**. One is ACTIVE (serving), one is SHADOW
(receiving writes). They never alias.

```
SliceState:
    history          list
    memory_vectors   ...      # independent namespace per slice
    validation_score float
    token_count      int
    crumbs           list[dict[str, Any]]   # RESERVED — see §6
    last_commit_id   str
```

**API** (as built):

```
slice_a / slice_b
get_active_slice()
get_shadow_slice()
get_slice(id)
commit_slice_swap() -> SliceID
cold_drop_shadow()
find_slot(agent_name)
```

**Invariants the 21 existing tests enforce:**

1. Slices are **distinct objects** — tests assert on `id()`, not equality,
   specifically to catch aliasing. Preserve that when porting.
2. A shadow write **never** mutates the active slice.
3. `cold_drop` leaves the active slice pristine, resets *all* shadow
   fields, and is **idempotent**.
4. Vector namespaces are independent per slice.

**8 of those tests are `def`, not `async def`.** The core slice model is
synchronous and therefore **Law 4 compatible** — it ports without dragging
an event loop along. This is the most useful single fact about the file.

### The `commit_slice_swap` bug — delete, do not repair

Shipped code, around line 146:

```python
def commit_slice_swap(self) -> SliceID:
    old_active = self.active_slice
    if self.active_slice == SliceID.SLICE_A:
        self.slice_a, self.slice_b = self.slice_b, self.slice_a
        self.slice_b.cold_drop()
        self.active_slice = SliceID.SLICE_A
    else:
        self.slice_a, self.slice_b = self.slice_b, self.slice_a
        self.slice_a.cold_drop()      # destroys the just-promoted data
        self.active_slice = SliceID.SLICE_A
```

Both branches swap identically. The `else` then cold-drops the slice it
just promoted. It is unreachable only because `active_slice` is
unconditionally reassigned to `SLICE_A` on both paths.

**Correct form:**

```python
def commit_slice_swap(self) -> SliceID:
    self.slice_a, self.slice_b = self.slice_b, self.slice_a
    self.slice_b.cold_drop()
    self.active_slice = SliceID.SLICE_A
    return self.active_slice
```

Repairing the `else` would preserve a branch modelling a state that cannot
occur. Someone later tidies the "redundant" `SLICE_A` assignment, the
branch becomes reachable, and the data loss ships. **Remove the state, not
the symptom.**

---

## 5. Promotion

Constants imported by the tests, from `services.health_monitor`:

```
AUTO_PROMOTE_LATENCY_IMPROVEMENT_PCT
AUTO_PROMOTE_VALIDATION_THRESHOLD
MANUAL_APPROVAL_WINDOW_SECONDS
```

Two paths:

- **Auto-promote** — fires when validation score and latency improvement
  both clear their thresholds.
- **Manual approve** — below threshold, promotion blocks and issues an
  HMAC token valid for `MANUAL_APPROVAL_WINDOW_SECONDS`. Wrong token
  rejected; expired token rejected; no pending approval returns false.

All four rejection paths already have tests. They exist. Port them.

**Open item — M4 finding C, promotion atomicity.** Still open. A swap
interrupted mid-flight has no defined recovery. Note it in the spec as a
known gap rather than pretending it is handled. This spec does not close
it.

---

## 6. `crumbs` — RESERVED

**Semantics undefined as of v1.**

The only evidence across all 4,038 indexed chunks is one line in
`test_capsule_slicing.py:641`:

```python
shadow.crumbs = [{"crumb": "breadcrumb"}]
```

That is placeholder text written to make a test pass.

**Rule for v1:**

> `crumbs` MUST be preserved verbatim across swaps and serialisation.
> `crumbs` MUST NOT be interpreted by any organ.
> Meaning may be assigned in a later spec_version.

Do not invent a definition. Inventing meanings for half-remembered fields
is the exact mechanism that forked this tree four times. Reserving costs
nothing and stops the next session from confidently guessing.

---

## 7. What this spec does NOT cover

State it plainly so nobody assumes otherwise:

- **Promotion atomicity** (M4 finding C) — open
- **Stripper isolation** (M4 finding B) — the fix is `FabricSandbox`, not
  a capsule concern
- **SubstanceBus covert channel** (M4 Risk 2) — a compromised organ can
  modulate queue timing and padding to signal another. Named *exfiltration
  path #1*. Not addressed here.
- **Wrap provenance chain** (M4 Missing 3) — that is the **Keychain**, not
  built
- **Dead man's switch** (M4 Missing 4) — fail-secure, alert Overseer. Not
  built.
- **Portability modes** `FULL | TETHERED | SKELETON` and degradation policy
  `REQUIRED | DEGRADE | SKIP` — described in frontier F7, deferred to v2

---

## 8. Checklist

- [ ] Read `sed -n '260,410p' test_capsule*.py`; override the DISCARD grade
- [ ] Delete the `else` branch in `commit_slice_swap`
- [ ] Write `manifest.json` schema (§2) with C4 applied
- [ ] Pin `.suit.zip` container + exact `CapsuleParseError` message
- [ ] Write `crumbs` RESERVED clause
- [ ] Port the 8 sync slice tests first — they need no event loop
- [ ] Port the 13 async tests second
- [ ] Record promotion atomicity as a known open gap

---

**Reminder about the safety property this all serves** — Eugene's original,
from `Forge-NG.md`:

> *"the thing that watches cannot act, and the thing that acts cannot watch
> on its own — it acts only on the watcher's findings, and only through the
> gate."*

A capsule is the unit that gets watched. That is why the manifest is
authority and the runtime is only enforcement.
