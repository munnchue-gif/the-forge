"""Tests for the tamper-evident AuditLedger (M4 observer review, missing #1)."""

from hashlib import sha256
from dataclasses import replace

from fabric.ledger import AuditLedger, LedgerEntry, GENESIS


def _led():
    return AuditLedger(sha256(b"audit-key").digest())


def test_records_chain_and_verifies():
    led = _led()
    led.record("gate.allowed", {"kind": "fabric.splice", "audit": "a1"})
    led.record("gate.denied", {"kind": "net.egress", "reason": "policy"})
    led.record("gate.allowed", {"kind": "fabric.conform"})
    ok, bad = led.verify()
    assert ok is True and bad is None
    assert led.size() == 3


def test_first_entry_links_to_genesis():
    led = _led()
    e = led.record("gate.allowed", {})
    assert e.prev_hash == GENESIS
    assert e.seq == 0


def test_each_entry_links_to_previous():
    led = _led()
    e0 = led.record("a", {})
    e1 = led.record("b", {})
    assert e1.prev_hash == e0.entry_hash


def test_tampering_payload_is_detected():
    led = _led()
    led.record("gate.allowed", {"kind": "x", "audit": "a1"})
    led.record("gate.denied", {"kind": "y", "reason": "policy"})
    led.record("gate.allowed", {"kind": "z"})
    # Forge a past entry's payload (simulate an attacker editing the log).
    led._entries[1] = replace(led._entries[1],
                              payload={"kind": "y", "reason": "ALLOWED-LIE"})
    ok, bad = led.verify()
    assert ok is False
    assert bad == 1


def test_tampering_signature_is_detected():
    led = _led()
    led.record("gate.allowed", {})
    led._entries[0] = replace(led._entries[0], signature="deadbeef")
    ok, bad = led.verify()
    assert ok is False and bad == 0


def test_deleting_an_entry_breaks_the_chain():
    led = _led()
    led.record("a", {}); led.record("b", {}); led.record("c", {})
    del led._entries[1]                       # remove the middle entry
    ok, bad = led.verify()
    assert ok is False


def test_reordering_is_detected():
    led = _led()
    led.record("a", {}); led.record("b", {})
    led._entries.reverse()
    ok, bad = led.verify()
    assert ok is False


def test_binds_to_gate_emit():
    """The ledger is a drop-in sink for the gate's emit hook: every allow/deny
    gets chained automatically."""
    from fabric.gate import FabricGate
    from fabric.capabilities import SpliceCapability
    led = _led()
    gate = FabricGate(sha256(b"k").digest(),
                      emit=lambda topic, payload: led.record(topic, payload))
    cap = SpliceCapability(region_id="r", mode="split", sections=1, deaf=True)
    gate.authorize(gate.sign(cap))            # → emits gate.allowed → recorded
    gate.authorize(gate.sign(cap))            # another allowed
    assert led.size() >= 2
    ok, _ = led.verify()
    assert ok is True
    assert any(e.topic == "gate.allowed" for e in led.entries())
