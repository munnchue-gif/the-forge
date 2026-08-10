"""
Forge-NG Fabric — the single-substance trust + runtime foundation.

One substance, one door. Every privileged action is a Capability that passes
through one FabricGate (crypto-verified, replay-exact, multi-tenant, policy-
pluggable). The substance can split itself into deaf sections (SubstanceBus),
and an omnipresent Overseer — split into a Watcher (observe) and a Commander
(act-through-the-gate) — is woven through all of them.

Public surface:
    gate:          FabricGate, GateDecision, Decision, GateDenied, SignedCapability
    capabilities:  Spawn/Mount/Egress/NpuEval/Conform/Splice/Reclaim
    bus:           SubstanceBus
    overseer:      Overseer, Watcher, Commander, Finding
"""

from __future__ import annotations

from fabric.gate import (
    FabricGate,
    GateDecision,
    GateDenied,
    Decision,
    SignedCapability,
    Capability,
    ReplayLedger,
)
from fabric.capabilities import (
    SpawnCapability,
    MountCapability,
    EgressCapability,
    NpuEvalCapability,
    ConformCapability,
    SpliceCapability,
    ReclaimCapability,
)
from fabric.bus import SubstanceBus
from fabric.wrap import Wrap, WrapStore
from fabric.overseer import Overseer, Watcher, Commander
from fabric.types import Finding
from fabric.conduit import (
    VectorConduit, VectorMemory, NpuSeat, HeuristicSeat,
)
from fabric.sandbox import Concoctinator, Concoction, ConcoctionStep
from fabric.tailor import (
    EmbeddedTailor, HeuristicTailor, TailorSeat, Draft, FitResult,
)
from fabric.ledger import AuditLedger, LedgerEntry
from fabric.judge import BehavioralJudge, Verdict
from fabric.kernel import ForgeKernel, boot_forge, KernelStats
from fabric.caveat import (
    AttenuatedGrant, Context, caveat_policy,
    expires_in, only_tenant, only_section, op_in, read_only,
)
from fabric.coupler import CouplerA, CouplerB, HomeBay, GrantRegistry

__version__ = "0.1.0"

__all__ = [
    "AttenuatedGrant", "Context", "caveat_policy",
    "expires_in", "only_tenant", "only_section", "op_in", "read_only",
    "CouplerA", "CouplerB", "HomeBay", "GrantRegistry",
    "ForgeKernel", "boot_forge", "KernelStats",
    "AuditLedger", "LedgerEntry", "BehavioralJudge", "Verdict",
    "EmbeddedTailor", "HeuristicTailor", "TailorSeat", "Draft", "FitResult",
    "FabricGate", "GateDecision", "GateDenied", "Decision",
    "SignedCapability", "Capability", "ReplayLedger",
    "SpawnCapability", "MountCapability", "EgressCapability",
    "NpuEvalCapability", "ConformCapability", "SpliceCapability",
    "ReclaimCapability",
    "SubstanceBus",
    "Wrap", "WrapStore",
    "Overseer", "Watcher", "Commander", "Finding",
    "VectorConduit", "VectorMemory", "NpuSeat", "HeuristicSeat",
    "Concoctinator", "Concoction", "ConcoctionStep",
    "__version__",
]
