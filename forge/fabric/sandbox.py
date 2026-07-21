"""
Forge-NG — Concoctinator: the sandbox kernel / testing grounds.

WHAT THIS IS (Eugene's "concoctinator... recycler concocter, backend, unlimited")
──────────────────────────────────────────────────────────────────────────────
A separate arena where the fabric can play with itself SAFELY. It speaks the
exact same substance language as the live Forge, but with the safeties turned
from REFUSAL into OBSERVATION. In production the gate refuses a replay; in the
sandbox it *records* "this would have been denied, here's why." That is what
makes free experimentation possible without weakening the real thing.

Isolation IS the freedom: the Concoctinator owns its OWN gate, bus, and wrap
store. Nothing it does can leak into a live Forge — it is literally a different
substance instance. Split a model a hundred ways, blow it up, remix it; the real
substance never feels it. Unlimited, because it's sealed off.

TWO VERBS (the ones Eugene named):
    concoct(...)  — splice snips + pour into a wrap + form the shape → see what
                    it becomes. Creation, mapping, "putting the pieces together."
    strip(...)    — the recycler: flatten a concoction, KEEP the vectors, strip
                    the suit off, hand the raw material back. Reclaim as a
                    creative act, not just cleanup.

THE PAYOFF — the sandbox is the ON-RAMP:
    Every concoction records a transcript (what was spliced, what the gate WOULD
    have said, what the brain judged). A concoction you like is PROMOTED: its
    exact shape is replayed against a REAL, strict gate to go live. Playground →
    production, same substance, no rewrite.

TRUST BOTH WAYS (the adapter spec's open question, answered here):
    A concoction's shape can come from the tool's own declaration (trust the
    method) OR be proposed by the NPU brain (`shaper`). The sandbox is exactly
    where you compare the two without risk.

Kept deliberately simple + modular — later we piece on: pull a copy of a live
capsule to remix, richer brain shapers, suit assembly. Each is a new wire, not
a rewrite.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Callable

from fabric.gate import FabricGate, Decision, SignedCapability
from fabric.bus import SubstanceBus
from fabric.overseer import Overseer, Finding
from fabric.wrap import WrapStore, Wrap
from fabric.capabilities import ConformCapability, SpliceCapability, ReclaimCapability

logger = logging.getLogger("forge_ng.sandbox")


# ──────────────────────────────────────────────────────────────────────────────
# Transcript — the record of a concoction, and its on-ramp to production
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ConcoctionStep:
    """One thing that happened during a concoction, and what the gate thought."""
    action: str                       # "splice" | "conform" | "strip" | ...
    kind: str                         # the capability kind
    would_allow: bool                 # what a STRICT gate would have decided
    reason: str                       # gate's reason (denial cause if any)
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class Concoction:
    """A thing built in the arena — snips spliced, poured into a wrap, formed.
    Carries its transcript so it can be judged and promoted to the live fabric.
    """
    concoction_id: str
    wrap: Wrap | None = None
    vectors: bytes = b""
    steps: list[ConcoctionStep] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    born_at: float = field(default_factory=time.time)

    @property
    def is_clean(self) -> bool:
        """A concoction is 'clean' (promotable) iff every step would have been
        allowed under strict production rules and the brain flagged nothing
        critical."""
        steps_ok = all(s.would_allow for s in self.steps)
        no_critical = all(f.severity < 3 for f in self.findings)
        return steps_ok and no_critical

    def transcript(self) -> list[dict[str, Any]]:
        return [{"action": s.action, "kind": s.kind, "would_allow": s.would_allow,
                 "reason": s.reason, **s.detail} for s in self.steps]


# ──────────────────────────────────────────────────────────────────────────────
# The Concoctinator — the sandbox kernel
# ──────────────────────────────────────────────────────────────────────────────

# A shaper is the NPU-brain proposing a shape instead of trusting the tool's.
# (presets, tool_binds) proposed from a raw intent dict. None = trust the method.
Shaper = Callable[[dict[str, Any]], tuple[dict[str, str], list[str]]]


class Concoctinator:
    """
    A sealed testing arena. Same substance language as live, but the gate runs
    in OBSERVE mode: instead of refusing, it records what a strict gate would
    have done. Own gate + bus + wrap store → nothing leaks to production.
    """

    def __init__(self, *, secret: bytes | None = None) -> None:
        # Its OWN substance instance — the isolation that makes it unlimited.
        self._secret = secret or sha256(b"sandbox-arena").digest()
        self._gate = FabricGate(self._secret)
        self._bus = SubstanceBus()
        self._store = WrapStore()
        self._overseer = Overseer(self._bus, self._gate)
        self._concoctions: dict[str, Concoction] = {}
        self._counter = 0

    # ── OBSERVE-mode gate check (records instead of refusing) ────────────────

    def _observe(self, signed: SignedCapability) -> tuple[bool, str]:
        """Ask the gate what it WOULD do, without letting a denial stop us.
        Returns (would_allow, reason). This is the safety-as-observation core."""
        decision = self._gate.authorize(signed)
        if decision.allowed:
            return True, "ok"
        return False, decision.reason or decision.decision.name

    # ── CONCOCT — build something from snips ─────────────────────────────────

    def concoct(
        self,
        *,
        intent: dict[str, Any],
        model_id: str,
        snips: list[str] | None = None,
        vectors: bytes = b"",
        shaper: Shaper | None = None,
    ) -> Concoction:
        """
        Put the pieces together. `intent` is the raw idea; `snips` are section
        names to splice; `shaper` (if given) = the NPU brain proposing the shape
        (trust the brain). If no shaper, we trust the declared method: intent's
        own 'presets'/'tool_binds'. Either way we SEE what it becomes, safely.
        """
        self._counter += 1
        cid = f"concoction-{self._counter}"
        c = Concoction(concoction_id=cid, vectors=vectors)

        # 1. Decide the shape — trust the method, or let the brain propose it.
        if shaper is not None:
            presets, tool_binds = shaper(intent)
            shape_origin = "npu_brain"
        else:
            presets = dict(intent.get("presets", {}))
            tool_binds = list(intent.get("tool_binds", []))
            shape_origin = "declared_method"

        # 2. Splice the snips (observe each — a bad splice is recorded, not fatal)
        for snip in (snips or []):
            cap = SpliceCapability(region_id=f"{cid}.{snip}", mode="split",
                                   sections=1, deaf=True)
            ok, reason = self._observe(self._gate.sign(cap))
            c.steps.append(ConcoctionStep(action="splice", kind=cap.kind,
                                          would_allow=ok, reason=reason,
                                          detail={"snip": snip}))
            if ok:
                self._bus.open_section(f"{cid}.{snip}.s0")

        # 3. Pour into a wrap — the mold. Seal it in the arena's own store.
        try:
            wrap, _audit = self._store.seal(
                self._gate, capsule_id=cid, model_id=model_id,
                presets=presets, tool_binds=tool_binds, vectors=vectors,
            )
            c.wrap = wrap
            c.steps.append(ConcoctionStep(action="conform", kind="fabric.conform",
                                          would_allow=True, reason="ok",
                                          detail={"wrap_sha": wrap.wrap_sha,
                                                  "shape_origin": shape_origin}))
        except Exception as e:  # gate refused even in-arena seal path
            c.steps.append(ConcoctionStep(action="conform", kind="fabric.conform",
                                          would_allow=False, reason=str(e),
                                          detail={"shape_origin": shape_origin}))

        self._concoctions[cid] = c
        logger.info("concocted %s (shape=%s, clean=%s)", cid, shape_origin, c.is_clean)
        return c

    # ── STRIP — the recycler: flatten, keep the material ─────────────────────

    def strip(self, concoction_id: str, *, keep_vectors: bool = True) -> Concoction:
        """
        Strip the suit off a concoction: flatten it, KEEP the vectors (the raw
        material), hand it back for remixing. The recycler half of the loop.
        """
        c = self._concoctions.get(concoction_id)
        if c is None:
            raise KeyError(f"no such concoction: {concoction_id!r}")

        wrap_sha = c.wrap.wrap_sha if c.wrap else ""
        cap = ReclaimCapability(capsule_id=concoction_id, keep_vectors=keep_vectors,
                                vector_sha=wrap_sha)
        ok, reason = self._observe(self._gate.sign(cap))
        c.steps.append(ConcoctionStep(action="strip", kind=cap.kind,
                                      would_allow=ok, reason=reason,
                                      detail={"kept_vectors": keep_vectors}))
        if c.wrap:
            self._store.reclaim(self._gate, capsule_id=concoction_id,
                                wrap_sha=c.wrap.wrap_sha, keep_vectors=keep_vectors)
        # The material (vectors) stays on `c` for remixing if kept.
        if not keep_vectors:
            c.vectors = b""
        return c

    # ── JUDGE — let the brain look at a concoction (trust-both-ways compare) ──

    def judge(self, concoction_id: str,
              evaluator: Callable[[Concoction], list[Finding]]) -> list[Finding]:
        """Run any evaluator (heuristic today, NPU brain later) over a
        concoction. Findings ride along so promotion can weigh them."""
        c = self._concoctions[concoction_id]
        findings = list(evaluator(c))
        c.findings.extend(findings)
        return findings

    # ── PROMOTE — the on-ramp to the live, strict fabric ─────────────────────

    def promote(self, concoction_id: str, live_gate: FabricGate,
                live_store: WrapStore, *, tenant_id: str = "default") -> tuple[bool, str]:
        """
        Take a concoction that behaved well in the arena and replay its exact
        shape against a REAL, strict production gate. Only a CLEAN concoction
        may attempt promotion — the arena's whole point is to catch the rest
        first. Returns (promoted, reason).
        """
        c = self._concoctions.get(concoction_id)
        if c is None or c.wrap is None:
            return False, "no such concoction or nothing to promote"
        if not c.is_clean:
            return False, "concoction is not clean — would fail strict rules"

        # Re-seal the identical shape against the LIVE gate + store.
        try:
            live_store.seal(
                live_gate, capsule_id=concoction_id, model_id=c.wrap.model_id,
                presets=dict(c.wrap.presets), tool_binds=list(c.wrap.tool_binds),
                vectors=c.vectors, tenant_id=tenant_id,
            )
            return True, "promoted to live fabric"
        except Exception as e:
            return False, f"live gate refused: {e}"

    # ── Introspection ─────────────────────────────────────────────────────────

    def preview(self, shape: dict[str, Any]) -> dict[str, Any]:
        """OBSERVE-MODE preview for the App /concoct/preview endpoint. Concoct the
        given shape in the arena, judge it with a BehavioralJudge, and return the
        transcript + verdict. NEVER promotes — this is the safe look-before-you-leap.

        `shape` = {"model_id": str, "presets": {...}, "tool_binds": [...],
                   "snips": [...]}"""
        from fabric.judge import BehavioralJudge
        c = self.concoct(
            intent={"presets": shape.get("presets", {}),
                    "tool_binds": shape.get("tool_binds", [])},
            model_id=shape.get("model_id", "unknown"),
            snips=shape.get("snips", []),
        )
        verdict = BehavioralJudge().evaluate(c)
        return {
            "concoction_id": c.concoction_id,
            "clean": bool(verdict.clean),
            "worst_severity": verdict.worst,
            "findings": verdict.report(),
            "transcript": c.transcript,
            "would_promote": bool(verdict.clean and c.is_clean),
        }

    def list_concoctions(self) -> list[str]:
        return sorted(self._concoctions)

    def get(self, concoction_id: str) -> Concoction:
        return self._concoctions[concoction_id]

    @property
    def arena(self) -> dict[str, Any]:
        """Handles to the arena's own substance, for tests/inspection."""
        return {"gate": self._gate, "bus": self._bus,
                "store": self._store, "overseer": self._overseer}
