"""
Proof of the wrap-seal / recycling-yard lifecycle on the single gate.

The wrap IS the training (one hash), the mold checks itself (one comparison),
reclaim keeps the vectors, and re-pour brings the exact shape back. No heavy
machinery — the fabric bridges it with the hashing it already runs.
"""

from __future__ import annotations

from fabric.gate import FabricGate, GateDenied
from fabric.wrap import WrapStore

SECRET = b"wrap-test-key-000000000000000000000"


def _store_and_gate():
    return WrapStore(), FabricGate(SECRET)


def test_seal_produces_deterministic_mold():
    """Same shape → same fingerprint, regardless of dict/list order."""
    store, gate = _store_and_gate()
    w1, _ = store.seal(gate, capsule_id="cap", model_id="m",
                       presets={"b": "2", "a": "1"}, tool_binds=["read", "plan"])
    store2, gate2 = _store_and_gate()
    w2, _ = store2.seal(gate2, capsule_id="cap", model_id="m",
                        presets={"a": "1", "b": "2"}, tool_binds=["plan", "read"])
    assert w1.wrap_sha == w2.wrap_sha        # order-independent mold


def test_seal_is_gate_authorized():
    store, gate = _store_and_gate()
    wrap, audit = store.seal(gate, capsule_id="cap", model_id="planner",
                             presets={"role": "planner"}, tool_binds=["read"])
    assert audit and store.shelf_size() == 1


def test_mold_self_verifies_and_detects_tamper():
    store, gate = _store_and_gate()
    wrap, _ = store.seal(gate, capsule_id="cap", model_id="planner",
                         presets={"role": "planner"}, tool_binds=["read"])
    assert store.verify(wrap)                # honest mold verifies

    # Tamper: swap a preset after sealing, keep the old sha.
    tampered = wrap.__class__(
        model_id=wrap.model_id,
        presets=(("role", "GODMODE"),),
        tool_binds=wrap.tool_binds,
        vector_ref=wrap.vector_ref,
        wrap_sha=wrap.wrap_sha,              # stale fingerprint
        sealed_at=wrap.sealed_at,
    )
    assert not store.verify(tampered)        # mold rejects the altered shape


def test_reclaim_keeps_vectors_and_repours():
    """Recycling yard: flatten the model, keep wrap + vectors, pour it back."""
    store, gate = _store_and_gate()
    learned = b"\x01\x02\x03learned-vectors"
    wrap, _ = store.seal(gate, capsule_id="cap", model_id="critic",
                         presets={"role": "critic"}, tool_binds=["audit"],
                         vectors=learned)

    kept, audit = store.reclaim(gate, capsule_id="cap", wrap_sha=wrap.wrap_sha,
                                keep_vectors=True)
    assert kept and audit

    # Re-pour: same shape, same vectors, brought back from the yard.
    repoured_wrap, repoured_vecs = store.repour(wrap.wrap_sha)
    assert repoured_wrap is not None
    assert repoured_vecs == learned


def test_reclaim_without_keeping_clears_the_shelf():
    store, gate = _store_and_gate()
    wrap, _ = store.seal(gate, capsule_id="cap", model_id="tmp",
                         presets={"role": "tmp"}, tool_binds=[],
                         vectors=b"disposable")
    assert store.shelf_size() == 1
    store.reclaim(gate, capsule_id="cap", wrap_sha=wrap.wrap_sha,
                  keep_vectors=False)
    assert store.shelf_size() == 0           # nothing left on the shelf
    w, v = store.repour(wrap.wrap_sha)
    assert w is None and v is None


def test_replayed_seal_is_blocked():
    """Replaying the EXACT SAME signed token is a replay — the gate refuses it,
    so an intercepted authorization can't be reused. (A fresh re-sign of the
    same action IS allowed — see test_legit_reseal_is_allowed — because it
    carries a new nonce.)"""
    store, gate = _store_and_gate()
    from fabric.capabilities import ConformCapability
    cap = ConformCapability(capsule_id="cap", model_id="m",
                            wrap_sha="deadbeef", seals_split=False)
    signed = gate.sign(cap)
    gate.enforce(signed)                      # first use of THIS token
    # Replaying the same token object is a replay.
    try:
        gate.enforce(signed)
        assert False, "expected GateDenied on replayed token"
    except GateDenied:
        pass


def test_legit_reseal_is_allowed():
    """Two legitimate identical conforms (freshly signed) BOTH authorize — the
    nonce makes each mint unique. This is the M4 observer-review fix."""
    store, gate = _store_and_gate()
    from fabric.capabilities import ConformCapability
    cap = ConformCapability(capsule_id="cap", model_id="m",
                            wrap_sha="deadbeef", seals_split=False)
    gate.enforce(gate.sign(cap))
    gate.enforce(gate.sign(cap))   # fresh nonce → not a replay → allowed
