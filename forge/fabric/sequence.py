"""
Forge-NG — Concoct Engine sequencing DSL (D2).

Assembly sequences as data: a spec (YAML text or plain dict) describing an
ordered set of steps run against a Concoctinator arena, with a small state
machine, rollback on failure, and per-snip provenance.

Spec shape (YAML or dict):

    name: remix-attempt-1
    steps:
      - id: build
        action: concoct
        model_id: capsule-7b
        snips: [attn.0, mlp.3]
        presets: {temp: "0.7"}
        tool_binds: [browser]
      - id: verdict
        action: judge          # BehavioralJudge over the concoction from `use`
        use: build
      - id: reclaim
        action: strip          # optional explicit reclaim
        use: build
        keep_vectors: true

State machine per step: PENDING → RUNNING → DONE | FAILED.
Run outcome: DONE, or FAILED → automatic rollback (strip every concoction this
run created, reverse order, vectors reclaimed) → ROLLED_BACK.

Provenance: every snip spliced during the run gets a record
{snip, step_id, concoction_id, would_allow, reason, sequence, ts} — the
per-snip paper trail both reviewers asked for.

Deliberately decoupled: the runner only touches the public Concoctinator verbs
(concoct / judge / strip / promote). PyYAML is optional — dict specs need no deps.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from fabric.sandbox import Concoctinator

_ACTIONS = ("concoct", "judge", "strip", "promote")


class SequenceError(Exception):
    """Bad spec, or a step referenced something that doesn't exist."""


# ── Spec ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SeqStep:
    step_id: str
    action: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SequenceSpec:
    name: str
    steps: tuple[SeqStep, ...]


def parse_spec(source: dict[str, Any] | str) -> SequenceSpec:
    """Parse a dict or YAML text into a validated SequenceSpec."""
    if isinstance(source, str):
        try:
            import yaml  # optional dep — only needed for YAML text specs
        except ImportError as e:
            raise SequenceError("YAML text spec given but PyYAML not installed "
                                "(pip install pyyaml), or pass a dict") from e
        source = yaml.safe_load(source)
    if not isinstance(source, dict):
        raise SequenceError("spec must be a mapping")
    name = source.get("name")
    raw_steps = source.get("steps")
    if not name or not isinstance(raw_steps, list) or not raw_steps:
        raise SequenceError("spec needs a name and a non-empty steps list")

    steps, seen = [], set()
    for i, s in enumerate(raw_steps):
        if not isinstance(s, dict):
            raise SequenceError(f"step {i} is not a mapping")
        sid = s.get("id") or f"step-{i}"
        action = s.get("action")
        if sid in seen:
            raise SequenceError(f"duplicate step id: {sid!r}")
        if action not in _ACTIONS:
            raise SequenceError(f"step {sid!r}: unknown action {action!r} "
                                f"(one of {', '.join(_ACTIONS)})")
        seen.add(sid)
        params = {k: v for k, v in s.items() if k not in ("id", "action")}
        steps.append(SeqStep(step_id=sid, action=action, params=params))
    return SequenceSpec(name=str(name), steps=tuple(steps))


# ── Run records ─────────────────────────────────────────────────────────

@dataclass
class StepRecord:
    step_id: str
    action: str
    status: str = "pending"          # pending | running | done | failed
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class SequenceRun:
    sequence: str
    status: str = "running"          # running | done | failed | rolled_back
    records: list[StepRecord] = field(default_factory=list)
    provenance: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


# ── Runner ────────────────────────────────────────────────────────────────

class SequenceRunner:
    """Drives one spec against one arena. Fail → strip everything this run made."""

    def __init__(self, arena: Concoctinator) -> None:
        self._arena = arena

    def run(self, source: dict[str, Any] | str) -> SequenceRun:
        spec = parse_spec(source)
        run = SequenceRun(sequence=spec.name)
        made: list[str] = []                 # concoction ids created by THIS run
        named: dict[str, str] = {}           # step_id -> concoction_id

        for step in spec.steps:
            rec = StepRecord(step_id=step.step_id, action=step.action, status="running")
            run.records.append(rec)
            try:
                self._exec(step, run, made, named, rec)
                rec.status = "done"
            except Exception as e:           # any step failure triggers rollback
                rec.status = "failed"
                rec.detail["error"] = str(e)
                run.error = f"{step.step_id}: {e}"
                run.status = "failed"
                self._rollback(run, made)
                return run
        run.status = "done"
        return run

    # ── steps ──

    def _exec(self, step: SeqStep, run: SequenceRun, made: list[str],
              named: dict[str, str], rec: StepRecord) -> None:
        p = step.params
        if step.action == "concoct":
            snips = list(p.get("snips", []))
            c = self._arena.concoct(
                intent={"presets": p.get("presets", {}),
                        "tool_binds": p.get("tool_binds", [])},
                model_id=p.get("model_id", "unknown"),
                snips=snips,
                vectors=p.get("vectors", b""),
            )
            made.append(c.concoction_id)
            named[step.step_id] = c.concoction_id
            rec.detail["concoction_id"] = c.concoction_id
            now = time.time()
            for s in c.steps:
                if s.action == "splice":
                    run.provenance.append({
                        "snip": s.detail.get("snip"), "step_id": step.step_id,
                        "concoction_id": c.concoction_id,
                        "would_allow": s.would_allow, "reason": s.reason,
                        "sequence": run.sequence, "ts": now,
                    })
        elif step.action == "judge":
            from fabric.judge import BehavioralJudge
            c = self._arena.get(self._ref(step, named))
            verdict = BehavioralJudge().evaluate(c)
            rec.detail.update(clean=bool(verdict.clean), worst=verdict.worst)
            if not verdict.clean:
                raise SequenceError(f"judge verdict not clean (worst={verdict.worst})")
        elif step.action == "strip":
            cid = self._ref(step, named)
            self._arena.strip(cid, keep_vectors=bool(p.get("keep_vectors", True)))
            rec.detail["stripped"] = cid
        elif step.action == "promote":
            cid = self._ref(step, named)
            ok, reason = self._arena.promote(cid, p["live_gate"], p["live_store"])
            rec.detail["reason"] = reason
            if not ok:
                raise SequenceError(f"promotion refused: {reason}")

    def _ref(self, step: SeqStep, named: dict[str, str]) -> str:
        use = step.params.get("use")
        if not use or use not in named:
            raise SequenceError(f"step {step.step_id!r}: 'use' must name an "
                                f"earlier concoct step (got {use!r})")
        return named[use]

    # ── rollback ──

    def _rollback(self, run: SequenceRun, made: list[str]) -> None:
        for cid in reversed(made):
            try:
                self._arena.strip(cid, keep_vectors=False)
                run.records.append(StepRecord(step_id=f"rollback:{cid}",
                                              action="strip", status="done"))
            except Exception as e:
                run.records.append(StepRecord(step_id=f"rollback:{cid}",
                                              action="strip", status="failed",
                                              detail={"error": str(e)}))
        run.status = "rolled_back"
