"""
Forge-NG — The Embedded Tailor: the hands of the Wardrobe.

WHAT THIS ORGAN IS (Eugene's words, mapped to code)
──────────────────────────────────────────────────────────────────────────────
Everything below the Tailor can HOLD a shape (Wrap), SEAL it (gate), and
RECYCLE it (WrapStore.reclaim). But nothing could decide a *new* shape on its
own — the fabric was "dumb cloth." The Tailor is the small brain that:

    1. STRIPS an old suit  — reads a worn wrap, reclaims it, keeps the vectors.
    2. DRAFTS the next one — proposes a fresh wrap SHAPE for a raw model.
    3. FITS it safely      — sends the draft through the Concoctinator (the
                             proving ground) so a bad shape is caught in the
                             sandbox, never on the live body.
    4. HANDS it over       — a CLEAN draft is promoted to the live gate+store.

CRUCIAL SEPARATION (the standing rule: bonded, not fused)
──────────────────────────────────────────────────────────────────────────────
The Tailor NEVER acts on the live fabric directly. It only:
  • proposes shapes (pure data — a Draft), and
  • asks the Concoctinator to try them (observe-mode, isolated).
The live gate is the only thing that can make a draft real, and only for a
draft that proved CLEAN. So even though the Tailor "thinks," it cannot push an
unproven shape onto the body. The brain drafts; the door decides.

THE BRAIN SEAT (why it's thin + swappable)
──────────────────────────────────────────────────────────────────────────────
The actual "intelligence" is a TailorSeat protocol — one method, `draft()`.
Today a HeuristicTailor fills it (dependency-free, works on your metal right
now). When the Intel Arrow Lake NPU is wired, a real small-LLM seat drops into
the exact same slot with `bind_seat()` — no other code changes. Same pattern
as the VectorConduit's NpuSeat: the organ is alive out of the box, and gets
smarter by swapping one part.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol, runtime_checkable

from fabric.gate import FabricGate
from fabric.wrap import Wrap, WrapStore
from fabric.sandbox import Concoctinator, Concoction


# ──────────────────────────────────────────────────────────────────────────────
# A Draft — the Tailor's proposed shape. Pure data, harmless until proven.
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class Draft:
    """A proposed conformation for a model. This is only a PLAN — it carries no
    authority. It becomes real only if the Concoctinator says it's clean AND the
    live gate seals it."""
    model_id: str
    presets: dict[str, str]
    tool_binds: tuple[str, ...]
    reason: str                       # why the Tailor chose this shape (audit trail)
    reclaimed_from: str | None = None  # wrap_sha of the suit this recycles, if any
    drafted_at: float = field(default_factory=time.time)

    def manifest(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "presets": dict(sorted(self.presets.items())),
            "tool_binds": list(self.tool_binds),
            "reason": self.reason,
            "reclaimed_from": self.reclaimed_from,
            "drafted_at": self.drafted_at,
        }


# ──────────────────────────────────────────────────────────────────────────────
# The brain seat — the ONE place real NPU intelligence binds later.
# ──────────────────────────────────────────────────────────────────────────────

@runtime_checkable
class TailorSeat(Protocol):
    """Observe-and-propose only. A seat NEVER touches the gate, store, or fabric
    — it just returns a Draft. That keeps the thinking part unable to act."""
    def draft(self, model_id: str, *, goal: str,
              recycled: Wrap | None) -> Draft: ...


class HeuristicTailor:
    """
    The default brain — no NPU, no LLM, works on bare metal today.

    It drafts a sane, conservative shape from the goal string and (if we're
    recycling) the old wrap's proven presets. Deliberately simple: the point is
    that the Tailor ORGAN is alive and correct now; the smart seat swaps in
    later without touching anything else.
    """

    # goal keyword -> extra tool binds the shape should carry
    _GOAL_TOOLS = {
        "code": ("fs.read", "fs.write", "shell.run"),
        "research": ("web.search", "web.read"),
        "chat": ("memory.read",),
        "vision": ("image.read",),
    }

    def draft(self, model_id: str, *, goal: str,
              recycled: Wrap | None) -> Draft:
        goal_l = goal.lower()

        # Start from recycled proven presets when re-pouring an old suit.
        presets: dict[str, str] = {}
        reclaimed_from = None
        if recycled is not None:
            presets.update(dict(recycled.presets))
            reclaimed_from = recycled.wrap_sha

        # Conservative baseline the gate will always accept.
        presets.setdefault("temperature", "0.7")
        presets.setdefault("max_context", "8192")
        presets.setdefault("safety", "sealed")   # marks it as fabric-conformed

        # Pick tool binds from the goal.
        tools: set[str] = set(recycled.tool_binds) if recycled else set()
        for key, extra in self._GOAL_TOOLS.items():
            if key in goal_l:
                tools.update(extra)

        reason = (f"heuristic draft for goal={goal!r}"
                  + (f"; recycled {reclaimed_from[:12]}…" if reclaimed_from else ""))
        return Draft(
            model_id=model_id,
            presets=presets,
            tool_binds=tuple(sorted(tools)),
            reason=reason,
            reclaimed_from=reclaimed_from,
        )


# ──────────────────────────────────────────────────────────────────────────────
# The Embedded Tailor — the organ.
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class FitResult:
    """The outcome of trying a draft in the proving ground."""
    draft: Draft
    concoction: Concoction
    clean: bool
    promoted_wrap_sha: str | None = None
    audit_id: str | None = None


class EmbeddedTailor:
    """
    Strips old suits, drafts new ones, and fits them in the sandbox before the
    live body ever sees them.

    It owns NOTHING privileged. It borrows:
      • a TailorSeat  — to think (swap for the NPU later)
      • a Concoctinator — the isolated proving ground to try shapes in
    and it is HANDED, per call, the live gate + store it may promote into.
    """

    def __init__(self, arena: Concoctinator, *, seat: TailorSeat | None = None) -> None:
        self._arena = arena
        self._seat: TailorSeat = seat or HeuristicTailor()

    # The seat is hot-swappable — this is the NPU upgrade path (Level 2+).
    def bind_seat(self, seat: TailorSeat) -> None:
        if not isinstance(seat, TailorSeat):
            raise TypeError("seat must implement TailorSeat.draft()")
        self._seat = seat

    # ── 1+2. STRIP the old suit (optional) and DRAFT the next ────────────────

    def draft_shape(
        self,
        model_id: str,
        *,
        goal: str,
        recycle_wrap_sha: str | None = None,
        live_store: WrapStore | None = None,
    ) -> Draft:
        """
        Ask the brain for a new shape. If recycle_wrap_sha + live_store are
        given, the Tailor first pulls the old suit's proven shape so the draft
        RE-POURS it (nothing thrown away) instead of starting from scratch.
        Pure planning — produces a Draft, touches no live state.
        """
        recycled: Wrap | None = None
        if recycle_wrap_sha and live_store is not None:
            recycled, _ = live_store.repour(recycle_wrap_sha)
        return self._seat.draft(model_id, goal=goal, recycled=recycled)

    # ── 3. FIT the draft in the proving ground ───────────────────────────────

    def fit(
        self,
        draft: Draft,
        *,
        snips: list[str] | None = None,
        vectors: bytes = b"",
        evaluator: Callable[[Concoction], list] | None = None,
    ) -> FitResult:
        """
        Try the draft inside the Concoctinator (isolated, observe-mode). The
        draft's shape becomes the concoct intent; the arena records whether
        every step WOULD be allowed under strict rules. Nothing here can reach
        the live body — that's the whole point of fitting first.
        """
        intent = {
            "model_id": draft.model_id,
            "presets": draft.presets,
            "tool_binds": list(draft.tool_binds),
        }
        concoction = self._arena.concoct(
            intent=intent,
            model_id=draft.model_id,
            snips=snips or [],
            vectors=vectors,
            shaper=None,   # trust the Tailor's declared draft; NPU shaper optional
        )
        if evaluator is not None:
            self._arena.judge(concoction.concoction_id, evaluator)
        return FitResult(draft=draft, concoction=concoction,
                         clean=concoction.is_clean)

    # ── 4. HAND a clean draft to the live body ───────────────────────────────

    def hand_over(
        self,
        fit: FitResult,
        *,
        live_gate: FabricGate,
        live_store: WrapStore,
        tenant_id: str = "default",
    ) -> FitResult:
        """
        Promote a CLEAN fitted draft onto the live fabric: the exact shape is
        re-sealed against the REAL strict gate and lands in the live store. A
        dirty fit is refused here — the sandbox already flagged it, and the
        Tailor will not push it onto the body.
        """
        if not fit.clean:
            raise PermissionError(
                "Tailor refuses to hand over a draft that did not fit clean "
                f"(concoction {fit.concoction.concoction_id})"
            )
        promoted, reason = self._arena.promote(
            fit.concoction.concoction_id, live_gate, live_store,
            tenant_id=tenant_id,
        )
        if not promoted:
            raise PermissionError(f"live gate refused promotion: {reason}")
        # The live store now holds the sealed shape; record its fingerprint.
        fit.promoted_wrap_sha = fit.concoction.wrap.wrap_sha if fit.concoction.wrap else None
        fit.audit_id = reason
        return fit

    # ── Convenience: the full loop in one call ───────────────────────────────

    def tailor(
        self,
        model_id: str,
        *,
        goal: str,
        live_gate: FabricGate,
        live_store: WrapStore,
        recycle_wrap_sha: str | None = None,
        snips: list[str] | None = None,
        vectors: bytes = b"",
        tenant_id: str = "default",
    ) -> FitResult:
        """
        Strip → draft → fit → (if clean) hand over, in one shot. Returns the
        FitResult; if clean it carries the live wrap_sha + audit_id, if not it
        carries the transcript of why it was refused. Never raises on a dirty
        draft here — it just comes back clean=False so the caller can inspect.
        """
        draft = self.draft_shape(
            model_id, goal=goal,
            recycle_wrap_sha=recycle_wrap_sha, live_store=live_store,
        )
        result = self.fit(draft, snips=snips, vectors=vectors)
        if result.clean:
            self.hand_over(result, live_gate=live_gate,
                           live_store=live_store, tenant_id=tenant_id)
        return result
