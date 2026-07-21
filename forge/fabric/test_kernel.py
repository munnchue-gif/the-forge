"""Tests for the ForgeKernel boot sequence (revised plan, step 2).

These are the tests that prove forge_ng BOOTS and runs a heartbeat — not just
that its parts import."""

from hashlib import sha256

from fabric.kernel import ForgeKernel, boot_forge
from fabric.conduit import HeuristicSeat


def _secret():
    return sha256(b"test-secret").digest()


def test_boot_stands_up_every_organ():
    k = ForgeKernel(secret=_secret()).boot()
    for organ in ("ledger", "gate", "bus", "overseer", "conduit",
                  "wraps", "arena", "tailor", "judge"):
        assert getattr(k, organ) is not None, f"{organ} not booted"
    assert k.stats.booted is True


def test_boot_records_a_chained_audit_entry():
    k = ForgeKernel(secret=_secret()).boot()
    assert k.ledger.size() >= 1
    ok, bad = k.ledger.verify()
    assert ok is True and bad is None


def test_double_boot_refused():
    k = ForgeKernel(secret=_secret()).boot()
    raised = False
    try:
        k.boot()
    except RuntimeError:
        raised = True
    assert raised is True


def test_tick_runs_the_heartbeat():
    k = ForgeKernel(secret=_secret()).boot()
    # Open a section and push telemetry the brain can see.
    k.overseer.split_region("cap", sections=1)
    k.bus.publish("cap.s0", "telemetry", {"state": "ok"})
    findings = k.tick()
    assert isinstance(findings, list)
    assert k.stats.ticks == 1


def test_gate_decisions_are_chained_during_run():
    """Every gate decision made while running is recorded in the audit chain."""
    k = ForgeKernel(secret=_secret()).boot()
    before = k.ledger.size()
    from fabric.capabilities import SpliceCapability
    cap = SpliceCapability(region_id="r", mode="split", sections=1, deaf=True)
    k.gate.authorize(k.gate.sign(cap))       # emits gate.allowed → recorded
    assert k.ledger.size() > before
    ok, _ = k.ledger.verify()
    assert ok is True


def test_shutdown_verifies_audit_chain():
    k = ForgeKernel(secret=_secret()).boot()
    k.overseer.split_region("cap", sections=1)
    k.bus.publish("cap.s0", "t", {"state": "ok"})
    k.tick()
    ok, bad = k.shutdown()
    assert ok is True and bad is None
    assert k.stats.booted is False


def test_shutdown_detects_tampered_audit_chain():
    """If someone edits the audit log while the kernel runs, shutdown catches it."""
    from dataclasses import replace
    k = ForgeKernel(secret=_secret()).boot()
    # Tamper with a past audit entry.
    k.ledger._entries[0] = replace(k.ledger._entries[0],
                                   payload={"organs": "TAMPERED"})
    ok, bad = k.shutdown()
    assert ok is False
    assert bad == 0


def test_health_snapshot():
    k = ForgeKernel(secret=_secret()).boot()
    h = k.health()
    assert h["booted"] is True
    assert "audit_entries" in h
    assert h["bus_sections"] >= 0


def test_boot_forge_convenience():
    k = boot_forge(_secret(), seat=HeuristicSeat())
    assert k.stats.booted is True
    k.shutdown()


def test_tick_before_boot_raises():
    k = ForgeKernel(secret=_secret())
    raised = False
    try:
        k.tick()
    except RuntimeError:
        raised = True
    assert raised is True
