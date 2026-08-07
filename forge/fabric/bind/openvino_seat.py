"""
Forge-NG · bind — OpenVinoSeat: a real NPU brain that satisfies NpuSeat.

This is the ONE method the conduit needs: judge(observations, memory) -> Findings.
It runs a small OpenVINO-GenAI model on the Intel NPU to look at what the body is
doing and raise Findings. It cannot act or mutate the skeleton — advisory only,
exactly like HeuristicSeat, just with a real model behind the judgment.

Import of openvino_genai is LAZY so this module imports fine in the sandbox (no
NPU here); the heavy dep only loads when you actually construct the seat on the PC.
Falls back to CPU device if the NPU isn't available, so it degrades instead of
crashing.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from fabric.overseer import Finding

logger = logging.getLogger("forge.bind.openvino_seat")

_JUDGE_PROMPT = """You are the Forge overseer brain. You OBSERVE a local AI
fabric and report problems. You never act. Given the recent telemetry, list any
concerns as JSON: a list of objects with keys section, kind, detail, severity
(0=info,1=low,2=act,3=critical). If nothing is wrong, return [].

TELEMETRY:
{telemetry}

JSON:"""

class OpenVinoSeat:
    """A small model on the Intel NPU acting as the observe-and-judge brain."""

    def __init__(self, model_dir: str, device: str = "NPU",
                 max_new_tokens: int = 256, batch_cap: int = 32) -> None:
        self.model_dir = model_dir
        self.device = device
        self.max_new_tokens = max_new_tokens
        self.batch_cap = batch_cap
        self._pipe = None  # lazily built on first judge()
        self._openvino_available = False
        self._check_openvino()

    def _check_openvino(self):
        """Check if OpenVINO is available in the environment."""
        try:
            from openvino.runtime import Core
            self._openvino_available = True
            logger.info("OpenVINO is available")
        except ImportError:
            logger.warning("OpenVINO not available - NPU functionality disabled")
            self._openvino_available = False

    def _ensure_pipe(self):
        if self._pipe is not None:
            return

        if not self._openvino_available:
            raise RuntimeError("OpenVINO not available - cannot initialize NPU pipeline")

        try:
            import openvino_genai as ov_genai
        except ImportError as e:
            raise RuntimeError(
                "openvino_genai not installed — run bind/01_setup_npu_openvino.sh"
            ) from e

        try:
            self._pipe = ov_genai.LLMPipeline(self.model_dir, self.device)
            logger.info("OpenVinoSeat bound on %s", self.device)
        except Exception as e:  # NPU busy/unavailable → degrade to CPU
            logger.warning("NPU pipeline failed (%s); falling back to CPU", str(e))
            try:
                self._pipe = ov_genai.LLMPipeline(self.model_dir, "CPU")
                self.device = "CPU"
                logger.info("OpenVinoSeat bound on CPU as fallback")
            except Exception as cpu_e:
                logger.error("CPU fallback also failed: %s", str(cpu_e))
                raise

    def judge(self, observations: list[dict[str, Any]]) -> list[Finding]:
        """Run the NPU model over recent telemetry, parse Findings. On any model
        or parse failure, return [] — a broken brain must never fabricate an
        action, and must never take down the heartbeat."""
        if not observations or not self._openvino_available:
            return []

        try:
            self._ensure_pipe()
            batch = observations[-self.batch_cap:]
            telemetry = json.dumps(batch, default=str)[:4000]
            prompt = _JUDGE_PROMPT.format(telemetry=telemetry)
            raw = self._pipe.generate(prompt, max_new_tokens=self.max_new_tokens)
            return self._parse(raw)
        except Exception as e:
            logger.exception("NPU generate failed; no findings this tick: %s", str(e))
            return []

    def health(self) -> bool:
        """Check if the model is loaded and ready for inference."""
        if not self._openvino_available:
            return False

        try:
            self._ensure_pipe()
            return True
        except Exception as e:
            logger.debug("Health check failed: %s", str(e))
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
            findings.append(Finding(
                section_id=str(it.get("section", "unknown")),
                kind=str(it.get("kind", "npu.concern")),
                detail=str(it.get("detail", ""))[:500],
                severity=max(0, min(3, sev)),
            ))
        return findings
