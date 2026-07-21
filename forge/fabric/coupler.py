"""
Forge-NG — Couplers: the sockets the outside world plugs into.

SCOPE (Eugene's note, 2026-07-17)
──────────────────────────────────────────────────────────────────────────────
This is the SIMPLE, TRUSTED-PEOPLE-ONLY version. The deep hostile-security dive
(public/enterprise exposure) is deliberately PARKED. What's here is the honest
minimum that's still correct: every coupler speaks ONLY through the one gate,
and a remote coupler holds an ATTENUATED (narrowed) grant — never a full right.

TWO COUPLERS
──────────────────────────────────────────────────────────────────────────────
  • CouplerA (native)  — on Eugene's PC. Full local reach through the gate.
    Direct, trusted. Mints capabilities and authorizes them locally.
  • CouplerB (away)    — a tiny limb on another machine. Has NO brain. It cannot
    mint its own rights — it can only PRESENT a pre-issued AttenuatedGrant that
    Home stamped for it, and Home's gate decides. The brain stays home; the limb
    borrows it. B holding no minting key is the security feature.

Both couplers are REMOTE TENANTS through the same FabricGate. Nothing here binds
a real transport (SSH/phone/CLI) yet — those are separate adapter shapes for
later. This is the seam they'll all plug into.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from fabric.gate import FabricGate, SignedCapability, Capability
from fabric.caveat import (
    AttenuatedGrant, Context, caveat_policy,
    expires_in, only_tenant, read_only,
)

logger = logging.getLogger("forge.coupler")


@dataclass
class CouplerA:
    """Native, trusted socket on the home machine. Mints + authorizes locally."""
    gate: FabricGate
    tenant_id: str = "home"

    def request(self, cap: Capability) -> tuple[bool, str]:
        signed = self.gate.sign(cap, tenant_id=self.tenant_id)
        d = self.gate.authorize(signed, tenant_id=self.tenant_id)
        return d.allowed, d.reason


@dataclass
class GrantRegistry:
    """Home's record of the attenuated grants it has stamped for away-limbs.
    The gate's caveat policy reads this to decide."""
    root_secret: bytes
    _grants: dict[str, AttenuatedGrant] = field(default_factory=dict)

    def issue(self, signed: SignedCapability,
              caveats: list[tuple[str, Any]]) -> AttenuatedGrant:
        grant = AttenuatedGrant.over(signed.token, self.root_secret)
        for c in caveats:
            grant.add(c)
        self._grants[signed.token] = grant
        return grant

    def lookup(self, token: str) -> AttenuatedGrant | None:
        return self._grants.get(token)

    def revoke(self, token: str) -> bool:
        return self._grants.pop(token, None) is not None


@dataclass
class HomeBay:
    """
    The home side that away-limbs phone into. Wires the caveat policy onto the
    gate so every away request is checked against its narrowed grant. This is
    where CouplerB's requests actually get judged.
    """
    gate: FabricGate
    registry: GrantRegistry
    tenant_id: str = "away"

    def __post_init__(self) -> None:
        # Bind caveat enforcement to the gate (rides the policy hook; crypto
        # core untouched).
        self.gate.add_policy(
            caveat_policy(
                self.registry.lookup,
                self.registry.root_secret,
                lambda s, tn: Context(now=time.time(), tenant_id=tn,
                                      section=getattr(s, "section", ""),
                                      op_kind=s.kind),
            )
        )

    def stamp_for_away(self, cap: Capability, *, ttl: float = 60.0,
                       readonly: bool = True) -> tuple[SignedCapability, AttenuatedGrant]:
        """Home mints a right AND narrows it for a remote limb. The limb receives
        only the signed cap + the grant handle — never a minting key."""
        signed = self.gate.sign(cap, tenant_id=self.tenant_id)
        caveats: list[tuple[str, Any]] = [
            expires_in(ttl, issued_at=signed.issued_at),
            only_tenant(self.tenant_id),
        ]
        if readonly:
            caveats.append(read_only())
        grant = self.registry.issue(signed, caveats)
        logger.info("stamped away grant token=%s caveats=%s",
                    signed.token[:12], grant.labels)
        return signed, grant


@dataclass
class CouplerB:
    """
    The away limb. Brainless: it holds NO minting key and cannot widen anything.
    It can only present a home-stamped SignedCapability back to HomeBay's gate.
    """
    home: HomeBay
    held: SignedCapability | None = None
    tenant_id: str = "away"

    def receive(self, signed: SignedCapability) -> None:
        """Home hands the limb a pre-stamped, narrowed right."""
        self.held = signed

    def present(self) -> tuple[bool, str]:
        """Present the held right back home. Home's gate + caveats decide."""
        if self.held is None:
            return False, "no grant held"
        d = self.home.gate.authorize(self.held, tenant_id=self.tenant_id)
        return d.allowed, d.reason
