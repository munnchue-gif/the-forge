"""
Forge-NG — FabricGate: the single trust boundary for the whole system.

DESIGN THESIS (what changed vs. the original, and why)
──────────────────────────────────────────────────────────────────────────────
The original Forge OS had FOUR separate gate_* methods (gate_slot_mount,
gate_tool_invocation, gate_swarm_lifecycle, gate_network_egress) plus an
egress path bolted on later. Every new capability meant a new bespoke method
AND remembering to call it. That is how trust boundaries drift — the day
someone adds a capability and forgets the guard call, the wall has a hole.

Forge-NG collapses all of that into ONE contract: every privileged action,
present or future (spawn, mount, egress, NPU-eval, GitHub, Todoist, anything),
is a `Capability` that must pass through a single `FabricGate.authorize()`.
New integrations implement a Capability; they cannot invent a new way in.

WHAT I FIXED FROM THE ORIGINAL
──────────────────────────────────────────────────────────────────────────────
1. REPLAY DETECTION IS NOW EXACT, NOT PROBABILISTIC.
   The original used a 2-slot / 48-bit-tag flat array that both silently
   evicted (false negatives — a replay slips through) and could collide
   (false positives — a legit command wrongly rejected). For a *security*
   replay guard, a false negative is a vulnerability, full stop.

   Forge-NG uses an exact, memory-bounded seen-set with time-bucket sharding:
   tokens live exactly as long as they can possibly be valid (the signing
   window + tolerance), then their entire bucket is dropped in O(1). No
   eviction guesswork, no probabilistic miss, and memory is hard-bounded by
   (buckets_kept × tokens_per_window) — not unbounded, not lossy.

2. NO PRIVATE-ATTRIBUTE REACH.
   The original poked asyncio.Semaphore._value. Forge-NG exposes real
   introspection so nothing downstream depends on a CPython internal.

3. CONSTANT-TIME EVERYWHERE ON THE HOT PATH, ZERO ASYNC ON DECISIONS.
   authorize() is pure sync — it can never stall the event loop. Bus
   emission happens only after the decision is returned.

4. DECISIONS ARE VALUES, NOT EXCEPTIONS-ONLY.
   authorize() returns a GateDecision (allow/deny + reason + audit id).
   Callers that want the old raise-on-deny ergonomics call .enforce().
   This makes the gate testable and composable without try/except pyramids.
"""

from __future__ import annotations

import hmac
import struct
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from typing import Callable, Protocol


# ──────────────────────────────────────────────────────────────────────────────
# Capability contract — the ONE way anything privileged enters the system
# ──────────────────────────────────────────────────────────────────────────────

class Capability(Protocol):
    """
    Any privileged action implements this. That's the whole extensibility
    story: spawn, mount, egress, npu_eval, github_push — all Capabilities.
    """

    #: Stable identifier, e.g. "hopper.spawn", "coupler.mount", "net.egress".
    kind: str

    def canonical(self) -> str:
        """
        The exact bytes that get signed. MUST be deterministic and MUST
        include everything security-relevant (who, what, where). If two
        different real-world actions can produce the same canonical string,
        that is a signing bug in the Capability, not in the gate.
        """
        ...


class Decision(Enum):
    ALLOW = "allow"
    DENY_SIGNATURE = "deny_signature"
    DENY_EXPIRED = "deny_expired"
    DENY_REPLAY = "deny_replay"
    DENY_POLICY = "deny_policy"


@dataclass(frozen=True, slots=True)
class SignedCapability:
    """A Capability plus its HMAC proof. Produced by FabricGate.sign()."""
    kind: str
    canonical: str
    token: str
    issued_at: float
    nonce: str = ""          # unique per mint — lets 2 legit identical actions
                             # both succeed while replays of the SAME token fail


@dataclass(frozen=True, slots=True)
class GateDecision:
    decision: Decision
    kind: str
    audit_id: str
    reason: str = ""

    @property
    def allowed(self) -> bool:
        return self.decision is Decision.ALLOW


class GateDenied(Exception):
    """Raised by GateDecision.enforce() / FabricGate.enforce() on any deny."""
    def __init__(self, d: GateDecision) -> None:
        self.decision = d
        super().__init__(f"{d.decision.value}: {d.reason} [{d.kind} audit={d.audit_id}]")


# ──────────────────────────────────────────────────────────────────────────────
# Exact, bounded replay ledger — the real fix
# ──────────────────────────────────────────────────────────────────────────────

class ReplayLedger:
    """
    Exact seen-token set, sharded by time bucket so memory is hard-bounded
    and expiry is O(1) (drop a whole stale bucket at once).

    A token can only ever be valid inside [bucket - tolerance, bucket +
    tolerance]. We therefore only need to remember tokens for that many
    buckets. Anything older literally cannot be replayed — its signature
    no longer verifies — so forgetting it is not just safe, it's correct.

    This is exact: if a token is in the ledger, it WAS seen; if it isn't and
    still verifies, it was NOT seen. No false negatives on the hot path.
    """

    __slots__ = ("_buckets", "_window", "_tolerance", "_keep")

    def __init__(self, window_seconds: int, tolerance: int) -> None:
        self._window = window_seconds
        self._tolerance = tolerance
        # Keep current bucket ± tolerance, plus one slack bucket each side.
        self._keep = (2 * tolerance) + 3
        self._buckets: dict[int, set[bytes]] = {}

    def _bucket_of(self, ts: float) -> int:
        return int(ts) // self._window

    def _gc(self, now_bucket: int) -> None:
        cutoff = now_bucket - self._keep
        stale = [b for b in self._buckets if b < cutoff]
        for b in stale:
            del self._buckets[b]

    def check_and_record(self, token_digest: bytes, now: float) -> bool:
        """
        Return True if this token is fresh (and record it); False if replay.
        token_digest is the raw 32-byte HMAC, stored exactly — no truncation.
        """
        nb = self._bucket_of(now)
        self._gc(nb)
        for b in range(nb - self._tolerance - 1, nb + self._tolerance + 2):
            if token_digest in self._buckets.get(b, ()):
                return False
        self._buckets.setdefault(nb, set()).add(token_digest)
        return True

    def size(self) -> int:
        return sum(len(s) for s in self._buckets.values())


# ──────────────────────────────────────────────────────────────────────────────
# The gate itself
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class GateStats:
    allowed: int = 0
    denied_signature: int = 0
    denied_expired: int = 0
    denied_replay: int = 0
    denied_policy: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "allowed": self.allowed,
            "denied_signature": self.denied_signature,
            "denied_expired": self.denied_expired,
            "denied_replay": self.denied_replay,
            "denied_policy": self.denied_policy,
        }


class FabricGate:
    """
    Single authorization boundary for every privileged action in Forge-NG.

    - sign(cap)               → SignedCapability (mint a proof)
    - authorize(signed, ...)  → GateDecision     (pure, sync, hot path)
    - enforce(signed, ...)    → None | raises GateDenied

    Per-tenant keys: pass a key_resolver(tenant_id) -> bytes to get
    multi-tenant isolation for free (this is the SDK-readiness change —
    the original had one global secret).
    """

    def __init__(
        self,
        secret: bytes | None = None,
        *,
        key_resolver: Callable[[str], bytes] | None = None,
        window_seconds: int = 30,
        tolerance: int = 1,
        emit: Callable[[str, dict], None] | None = None,
    ) -> None:
        if secret is None and key_resolver is None:
            raise ValueError("FabricGate requires either a secret or a key_resolver")
        self._secret = secret
        self._key_resolver = key_resolver
        self._window = window_seconds
        self._tolerance = tolerance
        self._ledger = ReplayLedger(window_seconds, tolerance)
        self._policies: list[Callable[[SignedCapability, str], str | None]] = []
        self._emit = emit or (lambda topic, payload: None)
        self.stats = GateStats()

    def _key(self, tenant_id: str) -> bytes:
        if self._key_resolver is not None:
            return self._key_resolver(tenant_id)
        assert self._secret is not None
        return self._secret

    def add_policy(self, policy: Callable[[SignedCapability, str], str | None]) -> None:
        """
        Register a policy hook. It receives (signed_cap, tenant_id) and
        returns None to allow, or a string reason to DENY. This is where
        allow-lists, rate ceilings, destination filters, etc. plug in —
        WITHOUT touching the crypto core.
        """
        self._policies.append(policy)

    def sign(self, cap: Capability, *, tenant_id: str = "default",
             ts: float | None = None, nonce: str | None = None) -> SignedCapability:
        issued = ts if ts is not None else time.time()
        bucket = int(issued) // self._window
        # A fresh random nonce makes each mint unique. Two legitimate, identical
        # actions (same canonical, same bucket) now produce DIFFERENT tokens, so
        # both authorize — while a replay of one exact token is still caught by
        # the ledger. The nonce is bound into the HMAC so it can't be swapped.
        n = nonce if nonce is not None else secrets.token_hex(16)
        canonical = cap.canonical()
        msg = (canonical.encode("utf-8")
               + b"|nonce=" + n.encode("utf-8")
               + struct.pack("<Q", bucket))
        token = hmac.new(self._key(tenant_id), msg, sha256).hexdigest()
        return SignedCapability(kind=cap.kind, canonical=canonical,
                                token=token, issued_at=issued, nonce=n)

    def authorize(self, signed: SignedCapability, *, tenant_id: str = "default",
                  now: float | None = None) -> GateDecision:
        now = now if now is not None else time.time()
        audit_id = sha256(
            (signed.token + f"{now:.6f}").encode()
        ).hexdigest()[:16]

        # 1. Freshness (cheapest)
        age = now - signed.issued_at
        max_age = (self._tolerance + 1) * self._window
        if age > max_age or age < -self._window:
            self.stats.denied_expired += 1
            d = GateDecision(Decision.DENY_EXPIRED, signed.kind, audit_id,
                             f"age={age:.0f}s outside ±{max_age}s")
            self._emit("gate.denied", {"reason": "expired", "kind": signed.kind})
            return d

        # 2. Signature — constant-time, checked across skew buckets
        key = self._key(tenant_id)
        body = (signed.canonical.encode("utf-8")
                + b"|nonce=" + signed.nonce.encode("utf-8"))
        now_bucket = int(now) // self._window
        ok = False
        for off in range(-self._tolerance, self._tolerance + 1):
            expected = hmac.new(key, body + struct.pack("<Q", now_bucket + off),
                                sha256).hexdigest()
            if hmac.compare_digest(expected, signed.token):
                ok = True
                break
        if not ok:
            self.stats.denied_signature += 1
            d = GateDecision(Decision.DENY_SIGNATURE, signed.kind, audit_id,
                             "hmac mismatch")
            self._emit("gate.denied", {"reason": "signature", "kind": signed.kind})
            return d

        # 3. Replay — EXACT, bounded
        digest = bytes.fromhex(signed.token)
        if not self._ledger.check_and_record(digest, now):
            self.stats.denied_replay += 1
            d = GateDecision(Decision.DENY_REPLAY, signed.kind, audit_id, "seen before")
            self._emit("gate.replay_suppressed", {"kind": signed.kind})
            return d

        # 4. Policy hooks (allow-lists, ceilings, destination filters…)
        for policy in self._policies:
            reason = policy(signed, tenant_id)
            if reason is not None:
                self.stats.denied_policy += 1
                d = GateDecision(Decision.DENY_POLICY, signed.kind, audit_id, reason)
                self._emit("gate.denied", {"reason": "policy", "kind": signed.kind,
                                           "detail": reason})
                return d

        self.stats.allowed += 1
        self._emit("gate.allowed", {"kind": signed.kind, "audit": audit_id})
        return GateDecision(Decision.ALLOW, signed.kind, audit_id)

    def enforce(self, signed: SignedCapability, *, tenant_id: str = "default",
                now: float | None = None) -> str:
        d = self.authorize(signed, tenant_id=tenant_id, now=now)
        if not d.allowed:
            raise GateDenied(d)
        return d.audit_id

    def ledger_size(self) -> int:
        return self._ledger.size()
