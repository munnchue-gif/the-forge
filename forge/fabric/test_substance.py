"""
Proof that Eugene's substance vision runs on the single FabricGate.

Scenario, in his words:
  - Pour two models into one capsule, split the center so they can't hear
    each other (SpliceCapability, deaf=True).
  - The wrap IS the training — each model boots pre-conformed
    (ConformCapability, wrap_sha binds the mold).
  - Later, pull it apart and take back the capsule with the saved vectors
    (ReclaimCapability, keep_vectors=True).

Every step is signed, replay-proof, and audited by the SAME gate that guards
spawn/mount/egress. No new gate code was written to support any of it.
"""

from __future__ import annotations

import hashlib

from fabric.gate import FabricGate, Decision
from fabric.capabilities import (
    ConformCapability, SpliceCapability, ReclaimCapability,
)

SECRET = b"substance-test-key-000000000000000"


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def test_two_models_one_capsule_split_center():
    """Two models in one capsule, deaf to each other — authorized as ONE
    splice action + two conform actions, all on the same gate."""
    g = FabricGate(SECRET)

    # The substance splits the capsule's center into two deaf sections.
    split = SpliceCapability(region_id="cap-alpha", mode="split",
                             sections=2, deaf=True)
    assert g.authorize(g.sign(split)).allowed

    # Pour model A into section 1 — pre-conformed by its wrap.
    conform_a = ConformCapability(
        capsule_id="cap-alpha", model_id="planner-7b",
        wrap_sha=_sha("presets:planner|tools:read,plan|vecs:v1"),
        seals_split=True,
    )
    # Pour model B into section 2 — a DIFFERENT wrap, different shape.
    conform_b = ConformCapability(
        capsule_id="cap-alpha", model_id="critic-7b",
        wrap_sha=_sha("presets:critic|tools:audit|vecs:v2"),
        seals_split=True,
    )
    assert g.authorize(g.sign(conform_a)).allowed
    assert g.authorize(g.sign(conform_b)).allowed


def test_wrap_is_the_training_tamper_evident():
    """Change one preset in the wrap and the mold no longer verifies —
    a model can never wake up in an unauthorized shape."""
    g = FabricGate(SECRET)
    real_wrap = _sha("presets:planner|tools:read,plan|vecs:v1")
    conform = ConformCapability("cap-alpha", "planner-7b", real_wrap)
    signed = g.sign(conform)

    # Attacker swaps the wrap for a more permissive one, reusing the token.
    tampered = signed.__class__(
        kind=signed.kind,
        canonical=signed.canonical.replace(real_wrap, _sha("presets:GODMODE")),
        token=signed.token, issued_at=signed.issued_at,
    )
    assert g.authorize(tampered).decision is Decision.DENY_SIGNATURE


def test_recycling_yard_reclaim_keeps_vectors():
    """Flatten the model, keep the wrap + learned vectors — reclaim as a
    first-class, audited action."""
    g = FabricGate(SECRET)
    vecs = _sha("learned-vectors-after-session")
    reclaim = ReclaimCapability("cap-alpha", keep_vectors=True, vector_sha=vecs)
    d = g.authorize(g.sign(reclaim))
    assert d.allowed and d.kind == "fabric.reclaim"


def test_merge_dissolves_the_seam():
    """The reverse direction — two sections flow back into one."""
    g = FabricGate(SECRET)
    merge = SpliceCapability(region_id="cap-alpha", mode="merge",
                             sections=1, deaf=False)
    assert g.authorize(g.sign(merge)).allowed


def test_isolation_cannot_be_silently_removed():
    """A replayed merge (trying to dissolve a wall twice / sneak a second
    dissolve past) is caught — isolation removal is always fresh + audited."""
    g = FabricGate(SECRET)
    merge = SpliceCapability("cap-alpha", "merge", 1, deaf=False)
    signed = g.sign(merge)
    assert g.authorize(signed).allowed
    assert g.authorize(signed).decision is Decision.DENY_REPLAY


def test_split_blocked_by_policy_when_sections_too_high():
    """A safety policy can cap how finely the substance may shard itself —
    plugged in WITHOUT touching the crypto core."""
    g = FabricGate(SECRET)

    def cap_sections(signed, tenant):
        if signed.kind == "fabric.splice" and "n=" in signed.canonical:
            n = int(signed.canonical.split("n=")[1].split("|")[0])
            if n > 8:
                return f"refusing to shard into {n} sections (max 8)"
        return None

    g.add_policy(cap_sections)
    too_many = SpliceCapability("cap-alpha", "split", 64, deaf=True)
    assert g.authorize(g.sign(too_many)).decision is Decision.DENY_POLICY
    ok = SpliceCapability("cap-alpha", "split", 4, deaf=True)
    assert g.authorize(g.sign(ok)).allowed
