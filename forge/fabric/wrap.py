"""
Forge-NG — WrapSeal: the mold that IS the training. And Reclaim: the yard.

EFFICIENCY NOTE (why this file is thin on purpose)
──────────────────────────────────────────────────────────────────────────────
Eugene asked: instead of heavy code, can the fabric bridge this with the
material it already has? Yes. A wrap-seal is not a new subsystem — it is the
SAME hashing math the gate already runs, reused. The whole "training" is:

    wrap_sha = sha256(canonical(presets + tool_binds + vector_refs))

That hash IS the mold. The gate's existing HMAC then proves the mold wasn't
tampered with (ConformCapability.wrap_sha already carries it). So sealing a
model costs one hash, and unsealing costs one comparison. No fine-tune loop,
no heavy serialization framework — the substance conforms the model by
wrapping it in its own fingerprint. That is the lightweight bridge.

Reclaim is the mirror: flatten the model, but keep the wrap fingerprint and the
learned vectors so the same substance can be re-poured. Nothing is discarded.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

from fabric.gate import FabricGate
from fabric.capabilities import ConformCapability, ReclaimCapability


# ──────────────────────────────────────────────────────────────────────────────
# The wrap — a model's pre-conformed shape, expressed as one fingerprint
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class Wrap:
    """
    A sealed conformation. The model that wakes up inside this wrap is already
    shaped by it — presets, tool-binds, and vectors are fixed at seal time.

    wrap_sha is the identity of the mold. Two wraps with the same sha are the
    same shape; change one preset and the sha changes, so the model can never
    boot in an unauthorized shape (the gate refuses the mismatched signature).
    """
    model_id: str
    presets: tuple[tuple[str, str], ...]     # sorted (key, value) pairs
    tool_binds: tuple[str, ...]              # sorted tool names
    vector_ref: str                          # pointer/sha of the vector set
    wrap_sha: str
    sealed_at: float = field(default_factory=time.time)

    def manifest(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "presets": [list(p) for p in self.presets],
            "tool_binds": list(self.tool_binds),
            "vector_ref": self.vector_ref,
            "wrap_sha": self.wrap_sha,
            "sealed_at": self.sealed_at,
        }


def _canonical_manifest(model_id: str, presets: dict[str, str],
                        tool_binds: list[str], vector_ref: str) -> str:
    """Deterministic bytes for the mold. Sorting makes the sha order-independent
    so the same shape always yields the same fingerprint."""
    payload = {
        "model_id": model_id,
        "presets": sorted(presets.items()),
        "tool_binds": sorted(tool_binds),
        "vector_ref": vector_ref,
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


class WrapStore:
    """
    The recycling yard's shelf. Holds sealed wraps and preserved vectors so a
    reclaimed model can be re-poured. In-memory here; a real deployment points
    this at ZRAM/disk, but the interface stays identical — the fabric doesn't
    care where the shelf physically is.
    """

    def __init__(self) -> None:
        self._wraps: dict[str, Wrap] = {}            # wrap_sha -> Wrap
        self._vectors: dict[str, bytes] = {}         # vector_ref -> bytes

    # ── Seal (the training) ─────────────────────────────────────────────────

    def seal(
        self,
        gate: FabricGate,
        *,
        capsule_id: str,
        model_id: str,
        presets: dict[str, str],
        tool_binds: list[str],
        vectors: bytes = b"",
        seals_split: bool = False,
        tenant_id: str = "default",
    ) -> tuple[Wrap, str]:
        """
        Seal a model into a wrap and authorize it through the gate in one step.

        Returns (Wrap, audit_id). Raises GateDenied if the gate refuses.
        The wrap_sha is computed here and bound into the ConformCapability, so
        the same fingerprint the gate signs is the one stored — no drift.
        """
        vector_ref = "sha256:" + sha256(vectors).hexdigest() if vectors else "none"
        canonical = _canonical_manifest(model_id, presets, tool_binds, vector_ref)
        wrap_sha = sha256(canonical.encode()).hexdigest()

        cap = ConformCapability(
            capsule_id=capsule_id, model_id=model_id,
            wrap_sha=wrap_sha, seals_split=seals_split,
        )
        audit_id = gate.enforce(gate.sign(cap, tenant_id=tenant_id),
                                tenant_id=tenant_id)

        wrap = Wrap(
            model_id=model_id,
            presets=tuple(sorted(presets.items())),
            tool_binds=tuple(sorted(tool_binds)),
            vector_ref=vector_ref,
            wrap_sha=wrap_sha,
        )
        self._wraps[wrap_sha] = wrap
        if vectors:
            self._vectors[vector_ref] = vectors
        return wrap, audit_id

    # ── Verify (the mold checks itself) ─────────────────────────────────────

    def verify(self, wrap: Wrap) -> bool:
        """Recompute the fingerprint from the wrap's own contents. If it no
        longer matches wrap_sha, the mold was tampered with after sealing."""
        canonical = _canonical_manifest(
            wrap.model_id, dict(wrap.presets), list(wrap.tool_binds), wrap.vector_ref
        )
        return sha256(canonical.encode()).hexdigest() == wrap.wrap_sha

    # ── Reclaim (the recycling yard) ────────────────────────────────────────

    def reclaim(
        self,
        gate: FabricGate,
        *,
        capsule_id: str,
        wrap_sha: str,
        keep_vectors: bool = True,
        tenant_id: str = "default",
    ) -> tuple[bool, str]:
        """
        Flatten a model out of its capsule. Keep the wrap + learned vectors if
        keep_vectors (the yard preserves them for re-pouring). Authorized and
        audited by the gate like everything else.

        Returns (vectors_kept, audit_id).
        """
        wrap = self._wraps.get(wrap_sha)
        vector_sha = wrap.vector_ref if (wrap and keep_vectors) else ""

        cap = ReclaimCapability(capsule_id=capsule_id, keep_vectors=keep_vectors,
                                vector_sha=vector_sha)
        audit_id = gate.enforce(gate.sign(cap, tenant_id=tenant_id),
                                tenant_id=tenant_id)

        kept = False
        if keep_vectors and wrap is not None:
            # The wrap and its vectors stay on the shelf; only the live model
            # memory is considered flattened (the caller drops the runtime).
            kept = wrap.vector_ref in self._vectors or wrap.vector_ref == "none"
        else:
            # Not keeping: drop the wrap and its vectors from the yard.
            if wrap is not None:
                self._wraps.pop(wrap_sha, None)
                self._vectors.pop(wrap.vector_ref, None)
        return kept, audit_id

    # ── Re-pour (bring a reclaimed shape back) ──────────────────────────────

    def repour(self, wrap_sha: str) -> tuple[Wrap | None, bytes | None]:
        """Fetch a preserved wrap + its vectors to pour a fresh model back into
        the same shape. This is why nothing is thrown away."""
        wrap = self._wraps.get(wrap_sha)
        if wrap is None:
            return None, None
        vectors = self._vectors.get(wrap.vector_ref)
        return wrap, vectors

    # ── Introspection ───────────────────────────────────────────────────────

    def shelf_size(self) -> int:
        return len(self._wraps)
