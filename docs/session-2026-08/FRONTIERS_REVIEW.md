# Review — frontiers.ts

**Verdict: this is real design work.** Every frontier states its cost honestly,
several answers are sharper than the question. Four technical flaws, one
unresolved contradiction, two orphaned sections.

---

## The best answers

**F3 — "Code is never trusted. It is confined and fingerprinted."**
> *"There is no STAGE 6 that makes the code 'trusted'... Trust is a property of
> the gate's declaration, not the code's content."*

That is the correct frame and it is stated better than I stated the question.
It also refuses the tempting wrong answer (static analysis for maliciousness)
with the right reason: false negatives.

**F4 — "The NPU's value is independence, not intelligence."**
The irreversibility × novelty matrix routes scarce independent compute exactly
where mistakes cannot be undone. This is the strongest single answer in the set.

**F6 — "Autonomy bounded not by trust in the model but by the structure of its
choices."**
Declaration templates separate *choosing a tool* from *authorizing a
capability*. Those were conflated in every prior version of this design. And it
self-critiques correctly: *"a template that accepts a 'config blob' parameter is
as dangerous as free selection."*

**F2 — "Pathways must be re-declared, not replayed."**
Replaying a declaration ledger would bypass verification. Subtle, correct, and
easy to get wrong.

**F7 — degradation policy `REQUIRED | DEGRADE | SKIP`.**
This is the answer to "what happens when a capsule runs without organ X," and
it makes portability honest instead of aspirational.

---

## FLAW 1 · F5's staleness formula has a zero-propagation bug

```
S = (days_since_build / decay_halflife) × (1 + failure_rate) × novelty_pressure
```

It is multiplicative. If `novelty_pressure` is 0 — no new snips have arrived
about that domain — then **S = 0 regardless of age or failure rate.**

Concretely: a security-adjacent organ, six months old, failing 40% of calls, in
a domain nobody has touched recently, scores **zero** and is never flagged.
That is the exact failure the frontier exists to prevent.

**Fix:** floor the multiplier, or make the terms additive.

```
S = (days/halflife) × (1 + failure_rate) × max(1.0, novelty_pressure)
```

Now novelty pressure can only *raise* staleness, never cancel it. Age and
failure remain independently sufficient.

---

## FLAW 2 · F4's cost note contradicts F4's own matrix

The cost section says:

> *"A threshold of 3 means the first 3 exercises of any pathway bypass NPU on
> the high-irreversibility path — this is the window of risk."*

But the matrix says:

- High irreversibility + **high** novelty → NPU sync + Overseer
- High irreversibility + **low** novelty → NPU sync

A pathway exercised fewer than 3 times *is* high-novelty, so it lands in
quadrant 4 and gets **both** walls. High irreversibility gets NPU sign-off
**always**, in every quadrant it appears.

**The design is safer than its own cost note claims.** Delete that cost item —
it describes a hole the matrix does not have. Leaving it in invites someone to
"fix" a non-problem and weaken the matrix.

---

## FLAW 3 · F1's embedding anchor undermines the thing F1 exists to do

The mechanism anchors `embedding_vec` to the producing model at extraction
time. The cost section admits the consequence:

> *"Cross-model embedding spaces are not aligned. A later model querying by
> embedding will find approximate rather than exact matches."*

But the entire purpose of a snip is that **a later, different model** wears it.
So retrieval degrades precisely in the primary use case. The mechanism is
optimised for the case that does not matter.

**Fix — re-embed on ingestion.** The typed claim's `assertion` text is
architecture-agnostic; only the vector is not. So:

- store `embedding_vec` as `origin_embedding` — useful for provenance and for
  comparing what the *producer* thought was similar
- when a new model loads a snip bundle, **re-embed the assertion text in its
  own space** and index that
- retrieve primarily on `claim_type` + `task_id` + text, with embedding as a
  secondary ranking signal

Cost is one embedding pass per snip per model generation, which is cheap and
happens off the hot path. This turns the honest limitation into a solved
problem.

---

## FLAW 4 · F7's capsule_id is unstable against its own provenance chain

Two statements in the same manifest spec conflict:

- `capsule_id` = hash of the full manifest (pre-signature)
- `provenance_chain` = ordered list, part of the manifest, appended to by
  *"the full history of what touched this capsule"*

If provenance is inside the hashed manifest and grows over time, **the capsule
ID changes every time anything touches the capsule.** Identity is supposed to
be stable; content-addressing makes it mutable here.

**Fix — split the hash.**

```
capsule_id      = hash(core_manifest)        immutable: wrap_ref, snip_bundle,
                                             organ_manifest, runtime_contract,
                                             socket_topology, spec_version
provenance_head = hash(entry_n ‖ provenance_head_{n-1})   append-only chain
seal_signature  = sign(capsule_id ‖ provenance_head)
```

Now identity is fixed at seal, provenance is tamper-evident, and both are
covered by one signature. This is the same hash-chain pattern the AuditLedger
already uses, so it reuses a proven mechanism.

**Also missing from the manifest: `spec_version`.** The section is titled
"The Capsule Specification (v1)" but no field records that. A format that
cannot declare its own version cannot be evolved — the first capsule opened by
a v2 reader has no way to say what it is.

---

## THE CONTRADICTION · F3 and F6 disagree about self-extension

| | Says |
|---|---|
| **F3** | Toolchain scrapes, confines, fingerprints, and admits code to the boneyard — automated pipeline |
| **F6** | *"The system does not self-extend; it signals and waits."* Human review queue for palette growth |

Both cannot be true as written. And the thesis is on F3's side — *"the system
scrapes the world for the best current tool and converts it"* is the whole
point of the workshop.

**Resolution — they are describing different gates, and the split is correct:**

- The **Toolchain may BUILD** an organ automatically: fetch, confine,
  fingerprint, burn provenance, store in boneyard. Fully automated. Nothing has
  been authorized yet — an organ in the boneyard is inert.
- The **palette may only GROW by human review.** Moving an organ from boneyard
  to pre-approved palette is the authorization step, and that stays
  human-gated.

So the system self-extends its *library* automatically and its *authority*
manually. That is coherent, it preserves the thesis, and it puts the human
exactly where the irreversible decision is.

**Write it down explicitly in both frontiers** — otherwise the first
implementer picks one and the other silently becomes wrong.

---

## Two orphaned sections in the app

1. **`SECTION_IDS` includes `"cuts"` but no `CutsSection.tsx` exists.** Dead nav
   link, and the observer never resolves `#cuts`. Section F — *what would you
   cut* — was asked for and is missing.
2. **`TrustZonesSection.tsx` exists but `App.tsx` never imports it.** Written,
   rendered nowhere.

Both are one-line fixes, but the missing cuts section is the substantive one:
that was the section where the previous layout revealed its worst reasoning, so
its absence removes a useful signal.

---

## What to do

1. Floor the novelty multiplier in F5 — `max(1.0, novelty_pressure)`
2. Delete F4's phantom cost item
3. Add re-embedding-on-ingestion to F1
4. Split `capsule_id` from `provenance_head` in F7; add `spec_version`
5. State the build-vs-authorize split in both F3 and F6
6. Wire `TrustZonesSection`; write or remove `cuts`

None of these are rewrites. The design underneath is sound — these are the
four places where the reasoning is good but the mechanism does not quite
implement it.
