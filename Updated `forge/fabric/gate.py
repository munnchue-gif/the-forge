"""
Forge-NG — Gate: the authorization and isolation layer.

The gate is the only point of contact between the skeleton (kernel) and the
outside world. It authorizes actions, isolates sections, and enforces security
policies. The gate is also responsible for auditing all decisions.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from fabric.capabilities import Capability
from fabric.overseer import Finding
from fabric.ledger import AuditLedger


logger = logging.getLogger("forge_ng.gate")


@dataclass(frozen=True, slots=True)
class GateDecision:
    allowed: bool
    audit_id: str
    reason: str


class FabricGate:
    """
    The gate is the authorization and isolation layer.

    It authorizes actions, isolates sections, and enforces security policies.
    The gate is also responsible for auditing all decisions.
    """

    def __init__(self, ledger: AuditLedger) -> None:
        self._ledger = ledger
        self.stats = GateStats()

    async def authorize(self, cap: Capability, *, tenant_id: str = "default") -> GateDecision:
        """Authorize a capability."""
        # Placeholder for actual authorization logic
        decision = GateDecision(allowed=True, audit_id="audit-123", reason="Authorized")
        self.stats.authorizations += 1
        await self._ledger.record("gate.authorize", {
            "cap": cap,
            "tenant_id": tenant_id,
            "decision": decision,
        })
        return decision

    async def sign(self, cap: Capability) -> Capability:
        """Sign a capability."""
        # Placeholder for actual signing logic
        signed_cap = Capability(**cap.dict())
        self.stats.signatures += 1
        await self._ledger.record("gate.sign", {
            "cap": cap,
            "signed_cap": signed_cap,
        })
        return signed_cap


@dataclass
class GateStats:
    authorizations: int = 0
    signatures: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "authorizations": self.authorizations,
            "signatures": self.signatures,
        }
