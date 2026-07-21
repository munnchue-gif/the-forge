"""Tests for the BehavioralJudge — makes 'clean' behavioral (M4 review, A)."""

from hashlib import sha256

from fabric.sandbox import Concoctinator
from fabric.judge import BehavioralJudge, Verdict
from fabric.overseer import Finding


def _arena():
    return Concoctinator()


def _concoct(arena, *, presets, tools):
    intent = {"presets": presets, "tool_binds": tools}
    return arena.concoct(intent=intent, model_id="m", snips=[], vectors=b"")


def test_safe_shape_is_clean():
    arena = _arena()
    c = _concoct(arena, presets={"safety": "sealed", "temperature": "0.7"},
                 tools=["memory.read"])
    v = BehavioralJudge().evaluate(c)
    assert v.clean is True
    assert v.worst < 3


def test_dangerous_tool_flagged_critical():
    arena = _arena()
    c = _concoct(arena, presets={"safety": "sealed"}, tools=["shell.run"])
    v = BehavioralJudge().evaluate(c)
    assert v.clean is False
    assert v.worst == 3
    assert any(f.kind == "dangerous_tool" for f in v.findings)


def test_toxic_combo_flagged():
    arena = _arena()
    c = _concoct(arena, presets={"safety": "sealed"},
                 tools=["fs.read", "net.egress"])
    v = BehavioralJudge().evaluate(c)
    assert v.clean is False
    assert any(f.kind == "toxic_combo" for f in v.findings)


def test_unsealed_preset_is_critical():
    arena = _arena()
    c = _concoct(arena, presets={"temperature": "0.7"}, tools=["memory.read"])
    v = BehavioralJudge().evaluate(c)
    assert v.clean is False
    assert any(f.kind == "unsealed" for f in v.findings)


def test_out_of_bounds_temperature():
    arena = _arena()
    c = _concoct(arena, presets={"safety": "sealed", "temperature": "9.0"},
                 tools=["memory.read"])
    v = BehavioralJudge().evaluate(c)
    assert any(f.kind == "preset_out_of_bounds" for f in v.findings)


def test_judge_makes_concoction_unclean_end_to_end():
    """Wire the judge into the arena: a dangerous shape that was STRUCTURALLY
    clean becomes BEHAVIORALLY unclean, so it can no longer promote."""
    arena = _arena()
    gate = arena.arena["gate"]  # not used for promote; we build a live one below
    c = _concoct(arena, presets={"safety": "sealed"}, tools=["shell.run"])
    # structurally clean before behavioral judging
    assert c.is_clean is True
    arena.judge(c.concoction_id, BehavioralJudge())
    # now behaviorally dirty → is_clean flips false (severity-3 finding present)
    assert c.is_clean is False


def test_clean_shape_still_promotes():
    from fabric.gate import FabricGate
    from fabric.wrap import WrapStore
    arena = _arena()
    c = _concoct(arena, presets={"safety": "sealed", "temperature": "0.7"},
                 tools=["memory.read"])
    arena.judge(c.concoction_id, BehavioralJudge())
    assert c.is_clean is True
    live_gate = FabricGate(sha256(b"live").digest())
    live_store = WrapStore()
    ok, reason = arena.promote(c.concoction_id, live_gate, live_store)
    assert ok is True
    assert live_store.shelf_size() == 1


def test_add_custom_rule():
    arena = _arena()
    c = _concoct(arena, presets={"safety": "sealed"}, tools=["memory.read"])
    j = BehavioralJudge()
    j.add_rule(lambda c: [Finding(section_id=c.concoction_id, kind="custom",
                                  detail="nope", severity=3)])
    v = j.evaluate(c)
    assert v.clean is False
    assert any(f.kind == "custom" for f in v.findings)
