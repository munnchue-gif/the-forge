"""
Forge-NG — concrete Capabilities.

Every privileged action in the system is one of these. Adding a new
integration (NPU eval, GitHub, Todoist) = add a frozen dataclass here whose
canonical() names every security-relevant field. It automatically inherits
signing, replay protection, expiry, per-tenant keys, and policy hooks.

That is the whole point: the wall has exactly one door, and this file is the
list of who is allowed to knock.

─────────────────────────────────────────────────────────────────────────────
THE SUBSTANCE MODEL (Eugene's vision, 2026-07-16)
─────────────────────────────────────────────────────────────────────────────
The whole system is ONE substance. Suits, capsules, containers, bridges —
all the same material, reclaimed and re-formed on demand (the recycling yard).
Isolation is not a static wall; it is the substance CHOOSING to split itself
(SpliceCapability) so no piece can hear or seize another. A raw model does not
need pre-training because the WRAP is the training: ConformCapability seals
presets/tool-binds/vectors into the mold before the model runs, so it wakes up
already shaped. Reclaim flattens the model and keeps the wrap + learned vectors
to be re-poured later. Every one of these is just the substance passing through
the single FabricGate door.
"""

from __future__ import annotations

from dataclasses import dataclass, field


def _esc(value: object) -> str:
    """Escape the field delimiter so an attacker cannot smuggle a '|' inside a
    user-controlled string (e.g. agent_name, model_id, dest_host) to shift the
    canonical boundaries and forge a different-but-same-signature action.

    Backslash-escape '\\' first, then '|'. Every canonical() field that can
    contain caller-controlled text MUST pass through this. Fixed-format numeric
    / boolean fields don't need it, but wrapping them is harmless.
    """
    return str(value).replace("\\", "\\\\").replace("|", "\\|")


@dataclass(frozen=True, slots=True)
class SpawnCapability:
    """Replaces the ad-hoc gate on Hopper.acquire_slot()."""
    kind = "hopper.spawn"
    capsule_id: str
    script_sha: str          # sha256 of the exact script being run
    cpu_quota: str
    mem_limit: str
    network: bool

    def canonical(self) -> str:
        return (f"hopper.spawn|{_esc(self.capsule_id)}|{_esc(self.script_sha)}|"
                f"{_esc(self.cpu_quota)}|{_esc(self.mem_limit)}|net={int(self.network)}")


@dataclass(frozen=True, slots=True)
class MountCapability:
    """Replaces gate_slot_mount() — the SocketCoupler warm-bridge entry."""
    kind = "coupler.mount"
    capsule_id: str
    agent_name: str
    slot_cap_hash: str       # capability hash proving the identity is registered

    def canonical(self) -> str:
        return (f"coupler.mount|{_esc(self.capsule_id)}|{_esc(self.agent_name)}|"
                f"{_esc(self.slot_cap_hash)}")


@dataclass(frozen=True, slots=True)
class EgressCapability:
    """Replaces gate_network_egress() — the FabricAdapter second lock."""
    kind = "net.egress"
    capsule_id: str
    dest_host: str
    dest_port: int
    payload_sha: str         # sha256 of the exact bytes leaving the box

    def canonical(self) -> str:
        return (f"net.egress|{_esc(self.capsule_id)}|"
                f"{_esc(self.dest_host)}:{int(self.dest_port)}|{_esc(self.payload_sha)}")


@dataclass(frozen=True, slots=True)
class NpuEvalCapability:
    """The NPU-embedded evaluator, as a first-class door.

    In the original this would have been a whole new bespoke gate method.
    Here it's five lines and it inherits every protection automatically."""
    kind = "npu.eval"
    capsule_id: str
    model_id: str
    vector_sha: str          # sha256 of the input vector batch

    def canonical(self) -> str:
        return (f"npu.eval|{_esc(self.capsule_id)}|{_esc(self.model_id)}|"
                f"{_esc(self.vector_sha)}")


# ─────────────────────────────────────────────────────────────────────────────
# EUGENE'S VISION, MADE REAL — the substance shaping itself
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class ConformCapability:
    """
    THE WRAP THAT IS THE TRAINING.

    Seal a raw model into a pre-conformed mold. The presets, tool-binds, and
    memory vectors are hashed into the wrap BEFORE the model runs, so it boots
    already shaped — no separate fine-tune step. The wrap_sha binds the exact
    conformation: change one preset and the signature no longer verifies, so a
    model can never wake up in a shape it wasn't authorized to take.

    Fields:
        capsule_id:  The capsule (mold) the model is poured into.
        model_id:    The raw model being wrapped.
        wrap_sha:    sha256 over the full conformation manifest
                     (presets + tool_binds + vector_refs). This is the mold.
        seals_split: If True, this conformation includes an internal split
                     center (two models in one capsule that cannot hear each
                     other) — recorded here so the audit trail shows it.
    """
    kind = "fabric.conform"
    capsule_id: str
    model_id: str
    wrap_sha: str
    seals_split: bool = False

    def canonical(self) -> str:
        return (f"fabric.conform|{_esc(self.capsule_id)}|{_esc(self.model_id)}|"
                f"{_esc(self.wrap_sha)}|split={int(self.seals_split)}")


@dataclass(frozen=True, slots=True)
class SpliceCapability:
    """
    THE SUBSTANCE SPLITTING ITSELF — isolation as an action, not a wall.

    Authorizes the fabric to subdivide a region into sealed sections so no
    section can hear or seize another (or, in reverse, to dissolve a seam and
    flow two sections back into one — the recycling-yard reclaim direction).

    This is the ONLY thing that can create or destroy an isolation boundary,
    and because it rides the gate, every split/merge is signed, replay-proof,
    and written to the audit trail. Isolation can never be silently removed.

    Fields:
        region_id:   The substance region being spliced.
        mode:        "split" (create sealed sections) or "merge" (dissolve seam).
        sections:    Number of resulting sealed sections (>=2 for split).
        deaf:        If True, sections get independent SubKernelBus namespaces
                     so they are cryptographically deaf to each other's events.
    """
    kind = "fabric.splice"
    region_id: str
    mode: str                # "split" | "merge"
    sections: int
    deaf: bool = True

    def canonical(self) -> str:
        return (f"fabric.splice|{_esc(self.region_id)}|{_esc(self.mode)}|"
                f"n={int(self.sections)}|deaf={int(self.deaf)}")


@dataclass(frozen=True, slots=True)
class ReclaimCapability:
    """
    THE RECYCLING YARD.

    Flatten a model out of its capsule but KEEP the wrap and its learned
    vectors, so the same substance can be re-poured later. Nothing is thrown
    away — the suit and the container are the same material, reclaimed.

    Fields:
        capsule_id:   The capsule being reclaimed.
        keep_vectors: If True, learned vectors are preserved into the wrap
                      store before the model memory is flattened.
        vector_sha:   sha256 of the vector snapshot being preserved (or "" if
                      keep_vectors is False).
    """
    kind = "fabric.reclaim"
    capsule_id: str
    keep_vectors: bool
    vector_sha: str = ""

    def canonical(self) -> str:
        return (f"fabric.reclaim|{_esc(self.capsule_id)}|"
                f"keep={int(self.keep_vectors)}|{_esc(self.vector_sha)}")
