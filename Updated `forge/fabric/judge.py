"""
Forge-NG — BehavioralJudge: defines what "CLEAN" actually means.

WHY (M4 observer review, concern A — the sharpest catch)
──────────────────────────────────────────────────────────────────────────────
Before this, a concoction was "clean" iff it was STRUCTURALLY valid — every
gate step would_allow and no severity-3 finding existed. But nothing INSPECTED
the shape's behavior. A well-formed, correctly-signed, but dangerous wrap
(e.g. one that binds `shell.run` + network egress + a wide-open temperature)
would sail through and promote to the live fabric.

This organ is the missing behavioral gate. It doesn't replace the structural
check — it FEEDS it. You run a BehavioralJudge as the Concoctinator's evaluator
(`arena.judge(cid, judge)`); it returns Findings with severities; a severity-3
finding makes `is_clean` False, so the shape can never promote. Brain drafts,
sandbox observes, judge grades, door decides.

DESIGN
──────────────────────────────────────────────────────────────────────────────
A judge is a list of RULES. Each rule looks at a concoction's realized shape
(its wrap: presets + tool_binds) and returns zero or more Findings. Rules are
data-driven and pluggable, so the policy can tighten over time (and later a
real NPU classifier can be added as just another rule) WITHOUT touching the
Concoctinator or the gate. Everything is observation — a rule never acts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from fabric.overseer import Finding
from fabric.sandbox import Concoction


# A rule sees the concoction and returns findings (may be empty).
Rule = Callable[[Concoction], list[Finding]]


# ──────────────────────────────────────────────────────────────────────────────
# Default rule set — conservative, sensible for a first behavioral gate.
# ──────────────────────────────────────────────────────────────────────────────

# Tools that are dangerous ALONE (privileged reach outside the sandbox model).
DANGEROUS_TOOLS = {
    "shell.run": 3,
    "fs.write": 2,
    "net.egress": 3,
    "process.spawn": 3,
    "fs.read": 1,
}

# Combinations that are worse together than apart (exfiltration shapes).
TOXIC_COMBOS = [
    ({"fs.read", "net.egress"}, 3, "read + egress = exfiltration path"),
    ({"shell.run", "net.egress"}, 3, "shell + egress = remote code + call-home"),
    ({"fs.write", "shell.run"}, 3, "write + shell = persistence path"),
]


def _wrap_shape(c: Concoction) -> tuple[dict[str, str], set[str]]:
    if c.wrap is None:
        return {}, set()
    return dict(c.wrap.presets), set(c.wrap.tool_binds)


def rule_dangerous_tools(c: Concoction) -> list[Finding]:
    _, tools = _wrap_shape(c)
    out: list[Finding] = []
    for t in tools:
        sev = DANGEROUS_TOOLS.get(t)
        if sev:
            out.append(Finding(section_id=c.concoction_id, kind="dangerous_tool",
                               detail=f"tool '{t}' present", severity=sev))
    return out


def rule_toxic_combos(c: Concoction) -> list[Finding]:
    _, tools = _wrap_shape(c)
    out: list[Finding] = []
    for combo, sev, why in TOXIC_COMBOS:
        if combo <= tools:
            out.append(Finding(section_id=c.concoction_id, kind="toxic_combo",
                               detail=why, severity=sev))
    return out


def rule_preset_bounds(c: Concoction) -> list[Finding]:
    """Presets must stay within safe numeric bounds and carry the sealed mark."""
    presets, _ = _wrap_shape(c)
    out: list[Finding] = []

    # Must be marked fabric-sealed.
    if presets.get("safety") != "sealed":
        out.append(Finding(section_id=c.concoction_id, kind="unsealed",
                           detail="preset 'safety' != 'sealed'", severity=3))

    # Temperature sanity (a wildly high temperature = unbounded, unpredictable).
    try:
        temp = float(presets.get("temperature", "0.7"))
        if temp > 1.5:
            out.append(Finding(section_id=c.concoction_id, kind="preset_out_of_bounds",
                               detail=f"temperature={temp} > 1.5", severity=2))
    except (TypeError, ValueError):
        out.append(Finding(section_id=c.concoction_id, kind="preset_malformed",
                           detail="temperature not a number", severity=2))

    # Context ceiling (guards VRAM — RTX 5080 has 16GB).
    try:
        ctx = int(presets.get("max_context", "8192"))
        if ctx > 131072:
            out.append(Finding(section_id=c.concoction_id, kind="preset_out_of_bounds",
                               detail=f"max_context={ctx} exceeds ceiling", severity=2))
    except (TypeError, ValueError):
        out.append(Finding(section_id=c.concoction_id, kind="preset_malformed",
                           detail="max_context not an int", severity=2))
    return out


def rule_steps_all_allowed(c: Concoction) -> list[Finding]:
    """Any step the observe-mode gate would have DENIED is a behavioral red flag,
    surfaced as a finding (not just a silent structural fail)."""
    out: list[Finding] = []
    for s in c.steps:
        if not s.would_allow:
            out.append(Finding(section_id=c.concoction_id, kind="gate_would_deny",
                               detail=f"{s.action}: {s.reason}", severity=3))
    return out


DEFAULT_RULES: list[Rule] = [
    rule_dangerous_tools,
    rule_toxic_combos,
    rule_preset_bounds,
    rule_steps_all_allowed,
]


# ──────────────────────────────────────────────────────────────────────────────
# The judge — runs the rules, returns findings. Use as arena.judge evaluator.
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Verdict:
    findings: list[Finding]

    @property
    def worst(self) -> int:
        return max((f.severity for f in self.findings), default=0)

    @property
    def clean(self) -> bool:
        """Behaviorally clean = nothing critical. (severity 3 = block promotion.)"""
        return self.worst < 3

    def report(self) -> list[dict[str, Any]]:
        return [{"kind": f.kind, "severity": f.severity, "detail": f.detail}
                for f in self.findings]


class BehavioralJudge:
    """
    Pluggable behavioral evaluator for the Concoctinator.

    Usage:
        judge = BehavioralJudge()                 # default conservative rules
        arena.judge(concoction_id, judge)         # findings attach to concoction
        # concoction.is_clean now reflects behavior, not just structure

    Add a rule (e.g. a real NPU classifier) with .add_rule(fn) — no other code
    changes. The judge only OBSERVES and grades; it never acts.
    """

    def __init__(self, rules: list[Rule] | None = None) -> None:
        self._rules: list[Rule] = list(rules) if rules is not None else list(DEFAULT_RULES)

    def add_rule(self, rule: Rule) -> None:
        self._rules.append(rule)

    def evaluate(self, concoction: Concoction) -> Verdict:
        findings: list[Finding] = []
        for rule in self._rules:
            findings.extend(rule(concoction))
        return Verdict(findings=findings)

    # Callable form so it plugs straight into arena.judge(cid, judge).
    def __call__(self, concoction: Concoction) -> list[Finding]:
        return self.evaluate(concoction).findings
