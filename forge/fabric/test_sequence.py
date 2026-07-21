"""Tests for fabric.sequence (D2) — spec parsing, state machine, rollback, provenance."""

import pytest

from fabric.sandbox import Concoctinator
from fabric.sequence import SequenceError, SequenceRunner, parse_spec


def spec(steps):
    return {"name": "t", "steps": steps}


def test_parse_rejects_bad_specs():
    with pytest.raises(SequenceError):
        parse_spec({"name": "x", "steps": []})
    with pytest.raises(SequenceError):
        parse_spec(spec([{"id": "a", "action": "explode"}]))
    with pytest.raises(SequenceError):
        parse_spec(spec([{"id": "a", "action": "concoct"},
                         {"id": "a", "action": "concoct"}]))


def test_concoct_then_judge_done_with_provenance():
    runner = SequenceRunner(Concoctinator())
    run = runner.run(spec([
        {"id": "build", "action": "concoct", "model_id": "m1",
         "snips": ["attn.0", "mlp.3"]},
        {"id": "verdict", "action": "judge", "use": "build"},
    ]))
    assert run.status == "done"
    assert [r.status for r in run.records] == ["done", "done"]
    snips = {p["snip"] for p in run.provenance}
    assert snips == {"attn.0", "mlp.3"}
    assert all(p["sequence"] == "t" and p["concoction_id"] for p in run.provenance)


def test_bad_reference_fails_and_rolls_back():
    runner = SequenceRunner(Concoctinator())
    run = runner.run(spec([
        {"id": "build", "action": "concoct", "model_id": "m1", "snips": ["a"]},
        {"id": "oops", "action": "strip", "use": "nope"},
    ]))
    assert run.status == "rolled_back"
    assert run.error and "oops" in run.error
    rb = [r for r in run.records if r.step_id.startswith("rollback:")]
    assert len(rb) == 1 and rb[0].status == "done"


def test_explicit_strip_keeps_vectors_by_default():
    arena = Concoctinator()
    runner = SequenceRunner(arena)
    run = runner.run(spec([
        {"id": "build", "action": "concoct", "model_id": "m1",
         "snips": ["a"], "vectors": b"vec"},
        {"id": "reclaim", "action": "strip", "use": "build"},
    ]))
    assert run.status == "done"
    cid = run.records[0].detail["concoction_id"]
    assert arena.get(cid).vectors == b"vec"
