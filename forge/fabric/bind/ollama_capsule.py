"""
Forge-NG · bind — OllamaCapsule: reach a capsule workhorse model on the RTX.

Capsule models (the doing models) run on the RTX 5080 via Ollama. The fabric
NEVER touches them bare — a call goes out only inside a sealed section, and every
egress is a gate-signed EgressCapability. This shim is the thin HTTP client; the
sealing/gating happens in the section that owns it.

No hard dependency on the `ollama` package — uses urllib so it imports anywhere.
The Ollama server default is 127.0.0.1:11434 (local only — that's the point).
"""

from __future__ import annotations

import json
import logging
import urllib.request
from dataclasses import dataclass

logger = logging.getLogger("forge.bind.ollama_capsule")


@dataclass
class OllamaCapsule:
    """A sealed capsule's handle to one GPU model. Local-only by design."""
    model: str
    host: str = "127.0.0.1"
    port: int = 11434
    timeout: float = 120.0

    @property
    def _url(self) -> str:
        return f"http://{self.host}:{self.port}/api/generate"

    def generate(self, prompt: str, *, max_tokens: int = 512) -> str:
        """Run the capsule model. Returns text, or raises on transport failure so
        the owning section can decide (retry / quarantine / reclaim)."""
        payload = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }).encode()
        req = urllib.request.Request(
            self._url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            body = json.loads(r.read().decode())
        return body.get("response", "")

    def health(self) -> bool:
        """Is the local Ollama server reachable?"""
        try:
            with urllib.request.urlopen(
                    f"http://{self.host}:{self.port}/api/tags", timeout=5) as r:
                return r.status == 200
        except Exception:  # noqa: BLE001
            return False
