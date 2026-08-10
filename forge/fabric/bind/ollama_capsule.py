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
from typing import Any, Optional

# from fabric.overseer import Finding

logger = logging.getLogger("forge.bind.ollama_capsule")

_JUDGE_PROMPT = """You are the Forge overseer brain. You OBSERVE a local AI
fabric and report problems. You never act. Given the recent telemetry, list any
concerns as JSON: a list of objects with keys section, kind, detail, severity
(0=info,1=low,2=act,3=critical). If nothing is wrong, return [].

TELEMETRY:
{telemetry}

JSON:"""

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

    def judge(self, observations: list[dict[str, Any]]) -> list[Finding]:
        """Run the model to analyze observations and return findings."""
        if not observations:
            return []

        telemetry = json.dumps(observations, default=str)[:4000]
        prompt = _JUDGE_PROMPT.format(telemetry=telemetry)

        try:
            response = self.generate(prompt, max_tokens=256)
            return self._parse(response)
        except Exception:  # noqa: BLE001
            logger.exception("Ollama judge failed; no findings this tick")
            return []

    def health(self) -> bool:
        """Is the local Ollama server reachable and healthy?"""
        try:
            with urllib.request.urlopen(
                    f"http://{self.host}:{self.port}/api/tags", timeout=5) as r:
                return r.status == 200
        except Exception:  # noqa: BLE001
            return False

    @staticmethod
    def _parse(raw: str) -> list[Finding]:
        """Pull the JSON list out of the model's reply, defensively."""
        text = raw if isinstance(raw, str) else str(raw)
        start, end = text.find("["), text.rfind("]")
        if start == -1 or end == -1 or end < start:
            return []
        try:
            items = json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            return []
        findings: list[Finding] = []
        for it in items if isinstance(items, list) else []:
            if not isinstance(it, dict):
                continue
            try:
                sev = int(it.get("severity", 1))
            except (TypeError, ValueError):
                sev = 1
            from fabric.overseer import Finding
            findings.append(Finding(
                section_id=str(it.get("section", "unknown")),
                kind=str(it.get("kind", "ollama.concern")),
                detail=str(it.get("detail", ""))[:500],
                severity=max(0, min(3, sev)),
            ))
        return findings
