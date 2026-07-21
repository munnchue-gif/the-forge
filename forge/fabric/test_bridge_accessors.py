"""
Phase A — tests for the App-facing accessors the bridge depends on.
Boots a REAL kernel and exercises every accessor end-to-end (contract §6).
"""
from hashlib import sha256
import pytest
from fabric.kernel import boot_forge


@pytest.fixture
def k():
    kernel = boot_forge(sha256(b"test-secret").digest())
    yield kernel
    try:
        kernel.shutdown()
    except Exception:
        pass


def test_organ_names(k):
    names = k.organ_names()
    assert "gate" in names and "ledger" in names and "arena" in names


def test_ledger_entries_since(k):
    # boot already recorded at least one entry
    all_e = k.ledger.entries_since(0)
    assert len(all_e) >= 1
    # slicing from the end returns nothing new
    assert k.ledger.entries_since(len(all_e)) == []
    # entries are JSON-safe dicts
    assert isinstance(all_e[0], dict) and "topic" in all_e[0]


def test_overseer_drain_and_sections(k):
    k.tick()  # produce a heartbeat cycle
    findings = k.overseer.drain_findings(0)
    assert isinstance(findings, list)
    sections = k.overseer.section_status()
    assert isinstance(sections, list)


def test_wrapstore_summary_empty_then_populated(k):
    assert k.wrapstore_summary() == []
    # seal a wrap through the live gate, then it should appear
    k.wraps.seal(k.gate, capsule_id="c1", model_id="m1",
                 presets={"temp": "0"}, tool_binds=["read"])
    summ = k.wrapstore_summary()
    assert len(summ) == 1 and summ[0]["model_id"] == "m1"


def test_request_action_readonly_npu_allowed(k):
    # a read-ish op with read_only caveat should pass the gate
    d = k.request_action("npu.eval", "brain", ["read_only"])
    assert d["allowed"] is True
    assert d["op"] == "npu.eval"


def test_request_action_readonly_refuses_egress(k):
    # read_only caveat must REFUSE a write/egress op — before it even hits crypto
    d = k.request_action("net.egress", "1.2.3.4", ["read_only"])
    assert d["allowed"] is False
    assert "read_only" in (d["finding"] or "")


def test_request_action_unknown_op(k):
    with pytest.raises(ValueError):
        k.request_action("evil.op", "x", [])


def test_request_action_logged_to_ledger(k):
    before = k.ledger.size()
    k.request_action("npu.eval", "brain", [])
    assert k.ledger.size() > before  # the mint decision was recorded


def test_arena_preview_no_promote(k):
    out = k.arena.preview({"model_id": "m", "presets": {"temp": "0"},
                           "tool_binds": ["read"]})
    assert "clean" in out and "findings" in out
    assert out["would_promote"] in (True, False)
    # preview must NOT promote into the live wrapstore
    assert k.wrapstore_summary() == []


def test_preview_dirty_shape_flags(k):
    # a toxic combo (read + egress) should be judged not-clean
    out = k.arena.preview({"model_id": "m", "presets": {},
                           "tool_binds": ["read", "egress"]})
    assert out["clean"] is False
