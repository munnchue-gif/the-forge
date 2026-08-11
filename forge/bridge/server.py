"""
THE FORGE BRIDGE — thin FastAPI over the kernel.

This is the ONLY thing the App talks to. It holds NO logic of its own: it exposes
the read-only Overseer tap and routes every action through the FabricGate. If the
gate refuses, the bridge refuses. The App is glass; the Forge decides.

Implements contract/FORGE_APP_CONTRACT.md v0.1.0.

Run (on the PC):
    cd forge
    pip install fastapi uvicorn pydantic
    python -m bridge.server         # serves http://127.0.0.1:8787

Then expose over a secured tunnel (Tailscale / Cloudflare Tunnel) — never bind
straight to a public interface.
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Any

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError as e:  # pragma: no cover - only on the PC
    raise SystemExit(
        "Bridge needs FastAPI: pip install fastapi uvicorn pydantic"
    ) from e

# Prefer the public boot helper. Fall back only if the module shape changes.
try:
    from fabric.kernel import boot_forge  # type: ignore
except Exception:  # pragma: no cover
    boot_forge = None  # type: ignore

CONTRACT_VERSION = "0.1.0"

app = FastAPI(title="The Forge Bridge", version=CONTRACT_VERSION)

# The App lives on a different origin. Lock this down to the app's real origin
# in production; "*" is only acceptable behind an authenticated tunnel.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Boot the Forge once, hold the handle ───────────────────────────────────
_kernel: Any = None
_booted_at: float = 0.0


def _boot():
    """Boot the living kernel. Always go through boot_forge so the required
    secret is supplied (dev default or FORGE_SECRET). Never call ForgeKernel()
    bare — it requires `secret`.
    """
    global _kernel, _booted_at
    if boot_forge is None:
        raise RuntimeError("fabric.kernel.boot_forge not importable")
    _kernel = boot_forge()  # uses FORGE_SECRET or safe dev default
    _booted_at = time.time()


@app.on_event("startup")
def _startup():
    try:
        _boot()
    except Exception as e:  # keep the server up so /health can report the failure
        print(f"[bridge] boot failed: {e}")


# ── READ endpoints (safe, read-only) ───────────────────────────────────────
@app.get("/health")
def health():
    booted = _kernel is not None
    return {
        "contract_version": CONTRACT_VERSION,
        "booted": booted,
        "uptime_s": int(time.time() - _booted_at) if booted else 0,
        "organs": getattr(_kernel, "organ_names", lambda: [])() if booted else [],
    }


@app.get("/sections")
def sections():
    _require_boot()
    return {"sections": _adapt(lambda: _kernel.overseer.section_status(), [])}


@app.get("/wraps")
def wraps():
    _require_boot()
    return {"wraps": _adapt(lambda: _kernel.wrapstore_summary(), [])}


@app.get("/ledger")
def ledger(since: int = 0):
    _require_boot()
    entries = _adapt(lambda: _kernel.ledger.entries_since(since), [])
    verified = _adapt(lambda: _kernel.ledger.verify(), None)
    return {"entries": entries, "verified": verified}


@app.get("/feed")
async def feed():
    """Server-Sent Events: the read-only Overseer tap piped to the App."""
    _require_boot()

    async def gen():
        cursor = 0
        while True:
            findings = _adapt(lambda: _kernel.overseer.drain_findings(cursor), [])
            for f in findings:
                cursor += 1
                yield f"data: {json.dumps(f, default=str)}\n\n"
            yield f"data: {json.dumps({'kind': 'heartbeat', 'ts': time.time()})}\n\n"
            await asyncio.sleep(1.0)

    return StreamingResponse(gen(), media_type="text/event-stream")


# ── ACT endpoint (privileged — always through the gate) ─────────────────────
class MintRequest(BaseModel):
    op: str
    target: str
    caveats: list[str] = []


@app.post("/mint")
def mint(req: MintRequest):
    """Ask the Forge to mint a NARROWED capability and run it through the gate.
    The App never receives a signing key — only the gate's decision."""
    _require_boot()
    try:
        decision = _kernel.request_action(
            op=req.op, target=req.target, caveats=req.caveats
        )
    except AttributeError:
        raise HTTPException(
            status_code=501,
            detail="kernel.request_action() not implemented yet — see contract §2",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "op": req.op,
        "target": req.target,
        "allowed": decision.get("allowed", False),
        "finding": decision.get("finding"),
    }


class ConcoctRequest(BaseModel):
    shape: dict


@app.post("/concoct/preview")
def concoct_preview(req: ConcoctRequest):
    """Fit + judge a drafted shape in the Concoctinator (observe-mode). Does NOT promote."""
    _require_boot()
    try:
        judgment = _kernel.arena.preview(req.shape)
    except AttributeError:
        raise HTTPException(
            status_code=501,
            detail="concoctinator.preview() not implemented yet — see contract §2",
        )
    return {"judgment": judgment, "promoted": False}


# ── helpers ─────────────────────────────────────────────────────────────────
def _require_boot():
    if _kernel is None:
        raise HTTPException(status_code=503, detail="Forge not booted")


def _adapt(fn, fallback):
    """Call an accessor that may not exist on the kernel yet. Returns fallback
    instead of 500ing, so the App can render a partial dashboard while the
    Forge side grows the accessor. Every gap is visible, never faked."""
    try:
        return fn()
    except AttributeError:
        return fallback


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="127.0.0.1", port=8787)
