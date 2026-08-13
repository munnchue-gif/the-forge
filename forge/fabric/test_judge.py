"""Tests for the BehavioralJudge — makes clean behavioral reviews."""
from __future__ import annotations

from hashlib import sha256

from fabric.sandbox import Concoctinator
from fabric.judge import BehavioralJudge, Verdict
from fabric.types import Finding, make_finding


def _arena():
    return Concoctinator()


def _concoct(arena, *, presets, tools):
    intent = {"presets": presets, "tool_binds": tools}
    return arena.concoct(intent=intent, model_id="m", snips=[], vectors=[])


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
    assert v.worst >= 3
