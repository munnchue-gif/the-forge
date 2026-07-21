"""
Forge-NG — Caveats: macaroon-style capability attenuation.

WHY (needed for couplers, even the trusted ones)
──────────────────────────────────────────────────────────────────────────────
When Coupler B (the away limb) or any delegate is handed a right, it must get a
NARROWED right, never the full one. Macaroons solve exactly this: the holder of
a capability can ADD caveats (restrictions) but can never REMOVE them, because
each caveat is chained into an HMAC. You can only ever weaken what you hold.

This stays true to Eugene's scope note — this is NOT the deep hostile-security
dive he parked. It's the one primitive a coupler genuinely needs: "hand a remote
limb a right that's read-only, valid 60s, capped to one section." Even a fully
trusted remote should hold the smallest possible key.

HOW IT PLUGS IN
──────────────────────────────────────────────────────────────────────────────
A Caveat is a predicate over a runtime Context (now, tenant, requested section,
op-kind). An AttenuatedGrant carries the base SignedCapability plus its caveats
and a chained proof. You register `caveat_policy(grant_lookup)` on the gate via
gate.add_policy(...) — then the gate refuses any action whose context violates a
caveat. Crypto core untouched; this rides the existing policy hook.
"""

from __future__ import annotations

import hmac
import time
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class Context:
    """What the gate knows about a request at authorize time."""
    now: float
    tenant_id: str
    section: str = ""
    op_kind: str = ""
    extra: tuple[tuple[str, Any], ...] = ()   # frozen key/vals for custom caveats


# A caveat: returns None if satisfied, or a string reason if it fails.
CaveatFn = Callable[[Context], str | None]


# ── Ready-made caveats (the common narrowings a coupler needs) ────────────────

def expires_in(seconds: float, issued_at: float | None = None) -> tuple[str, CaveatFn]:
    born = issued_at if issued_at is not None else time.time()
    deadline = born + seconds
    def _c(ctx: Context) -> str | None:
        return None if ctx.now <= deadline else f"expired (ttl {seconds}s)"
    return (f"ttl<={seconds}s", _c)


def only_tenant(tenant_id: str) -> tuple[str, CaveatFn]:
    def _c(ctx: Context) -> str | None:
        return None if ctx.tenant_id == tenant_id else f"tenant!={tenant_id}"
    return (f"tenant=={tenant_id}", _c)


def only_section(section: str) -> tuple[str, CaveatFn]:
    def _c(ctx: Context) -> str | None:
        return None if ctx.section == section else f"section!={section}"
    return (f"section=={section}", _c)


def op_in(*allowed: str) -> tuple[str, CaveatFn]:
    allow = frozenset(allowed)
    def _c(ctx: Context) -> str | None:
        return None if ctx.op_kind in allow else f"op {ctx.op_kind!r} not in {sorted(allow)}"
    return (f"op_in={sorted(allow)}", _c)


def read_only() -> tuple[str, CaveatFn]:
    """A coupler-friendly shorthand: refuse anything that isn't a read/observe."""
    def _c(ctx: Context) -> str | None:
        k = ctx.op_kind.lower()
        writing = any(w in k for w in ("write", "egress", "spawn", "splice",
                                       "reclaim", "mount", "shell"))
        return "read-only caveat: write op refused" if writing else None
    return ("read_only", _c)


# ── The attenuated grant (base right + chained caveats) ────────────────────────

@dataclass
class AttenuatedGrant:
    """
    A base right wrapped in caveats. `token` is the base capability's HMAC token
    (its identity). Each caveat's *label* is chained into a proof so the set of
    caveats can't be silently dropped without breaking the chain.

    You can only ATTENUATE (add caveats). There is no method to remove one.
    """
    base_token: str
    labels: list[str] = field(default_factory=list)
    _fns: list[CaveatFn] = field(default_factory=list)
    proof: str = ""

    @classmethod
    def over(cls, base_token: str, root_secret: bytes) -> "AttenuatedGrant":
        # proof seed = HMAC(secret, base_token); attenuation extends the chain.
        seed = hmac.new(root_secret, base_token.encode(), sha256).hexdigest()
        return cls(base_token=base_token, proof=seed)

    def add(self, caveat: tuple[str, CaveatFn]) -> "AttenuatedGrant":
        label, fn = caveat
        self.labels.append(label)
        self._fns.append(fn)
        # chain: new_proof = HMAC(prev_proof, label)
        self.proof = hmac.new(self.proof.encode(), label.encode(), sha256).hexdigest()
        return self

    def verify_chain(self, root_secret: bytes) -> bool:
        """Recompute the proof from scratch — any dropped/added/edited caveat
        label breaks it."""
        p = hmac.new(root_secret, self.base_token.encode(), sha256).hexdigest()
        for label in self.labels:
            p = hmac.new(p.encode(), label.encode(), sha256).hexdigest()
        return hmac.compare_digest(p, self.proof)

    def check(self, ctx: Context) -> str | None:
        """Return None if EVERY caveat is satisfied, else the first failure."""
        for fn in self._fns:
            reason = fn(ctx)
            if reason is not None:
                return reason
        return None


# ── Gate policy adapter — makes the gate honor caveats ─────────────────────────

def caveat_policy(
    lookup: Callable[[str], AttenuatedGrant | None],
    root_secret: bytes,
    context_of: Callable[[Any, str], Context],
) -> Callable[[Any, str], str | None]:
    """
    Build a policy hook for gate.add_policy(...). For each signed capability it:
      1. looks up any AttenuatedGrant registered for that token,
      2. verifies the caveat chain (tamper check),
      3. checks every caveat against the request context.
    No grant registered → no extra restriction (base gate rules still apply).
    """
    def _policy(signed: Any, tenant_id: str) -> str | None:
        grant = lookup(signed.token)
        if grant is None:
            return None                       # unattenuated → base rules only
        if not grant.verify_chain(root_secret):
            return "caveat chain tampered"
        ctx = context_of(signed, tenant_id)
        return grant.check(ctx)               # None=allow, str=deny reason
    return _policy
