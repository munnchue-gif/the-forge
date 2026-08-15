"""
forge/fabric/codex_socket.py — Private transport for Codex

Unix domain socket only. No TCP. No public bind. No Cloudflare.
Default path: ~/.forge/codex.sock

Protocol (newline-delimited JSON):
    → {"cmd": "status"}
    → {"cmd": "ask", "prompt": "..."}
    → {"cmd": "load_model", "model_id": "qwen2.5-coder:7b"}
    → {"cmd": "unload_model"}
    → {"cmd": "propose_tool", ...}
    → {"cmd": "request_sear", ...}
    → {"cmd": "invoke_seared", ...}
    → {"cmd": "feed", "since": 0.0}
    → {"cmd": "scrap"}
    → {"cmd": "ping"}

    ← {"ok": true, "data": ...}  or  {"ok": false, "error": "..."}
"""

from __future__ import annotations

import json
import os
import socket
import stat
import threading
import time
from pathlib import Path
from typing import Any

from fabric.codex import Codex


DEFAULT_SOCK = Path.home() / ".forge" / "codex.sock"


def socket_path() -> Path:
    raw = os.environ.get("FORGE_CODEX_SOCK")
    return Path(raw) if raw else DEFAULT_SOCK


class CodexSocketServer:
    def __init__(self, codex: Codex, path: Path | None = None) -> None:
        self.codex = codex
        self.path = path or socket_path()
        self._sock: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def start(self) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            self.path.unlink()

        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.bind(str(self.path))
        os.chmod(self.path, stat.S_IRUSR | stat.S_IWUSR)
        self._sock.listen(1)
        self._sock.settimeout(1.0)

        self._stop.clear()
        self._thread = threading.Thread(
            target=self._serve, name="codex-socket", daemon=True
        )
        self._thread.start()
        return self.path

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        if self.path.exists():
            try:
                self.path.unlink()
            except OSError:
                pass

    def _serve(self) -> None:
        assert self._sock is not None
        while not self._stop.is_set():
            try:
                conn, _ = self._sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            try:
                self._handle(conn)
            finally:
                try:
                    conn.close()
                except OSError:
                    pass

    def _handle(self, conn: socket.socket) -> None:
        buf = b""
        conn.settimeout(120.0)  # allow model generate
        while True:
            try:
                chunk = conn.recv(65536)
            except (socket.timeout, OSError):
                break
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    req = json.loads(line.decode("utf-8"))
                    resp = self._dispatch(req)
                except Exception as e:
                    resp = {"ok": False, "error": str(e)}
                out = (json.dumps(resp, default=str) + "\n").encode("utf-8")
                try:
                    conn.sendall(out)
                except OSError:
                    return

    def _status_dict(self) -> dict[str, Any]:
        s = self.codex.status()
        return {
            "vessel_id": s.vessel_id,
            "organ": s.organ,
            "live": s.live,
            "seared_pathways": list(s.seared_pathways),
            "open_results": s.open_results,
            "feed_length": s.feed_length,
            "isolation_state": s.isolation_state,
            "model_id": s.model_id,
            "model_loaded": s.model_loaded,
            "timestamp": s.timestamp,
        }

    def _dispatch(self, req: dict[str, Any]) -> dict[str, Any]:
        cmd = req.get("cmd")
        if cmd == "ping":
            return {"ok": True, "data": {"pong": True, "ts": time.time()}}

        if cmd == "status":
            return {"ok": True, "data": self._status_dict()}

        if cmd == "load_model":
            mid = req.get("model_id") or "qwen2.5-coder:7b"
            self.codex.load_model(str(mid))
            return {"ok": True, "data": self._status_dict()}

        if cmd == "unload_model":
            self.codex.unload_model()
            return {"ok": True, "data": self._status_dict()}

        if cmd == "ask":
            prompt = str(req.get("prompt", ""))
            result = self.codex.ask(prompt)
            return {"ok": True, "data": self._result_dict(result)}

        if cmd == "propose_tool":
            result = self.codex.propose_tool(
                name=str(req.get("name", "")),
                description=str(req.get("description", "")),
                interface=req.get("interface") or {},
            )
            return {"ok": True, "data": self._result_dict(result)}

        if cmd == "request_sear":
            result = self.codex.request_sear(
                kind=str(req.get("kind", "")),
                description=str(req.get("description", "")),
                clearance=str(req.get("clearance", "PRIVILEGED")),
                metadata=req.get("metadata") or {},
            )
            return {"ok": True, "data": self._result_dict(result)}

        if cmd == "invoke_seared":
            result = self.codex.invoke_seared(
                kind=str(req.get("kind", "")),
                payload=req.get("payload") or {},
            )
            return {"ok": True, "data": self._result_dict(result)}

        if cmd == "feed":
            since = float(req.get("since", 0.0))
            entries = [
                {
                    "entry_id": e.entry_id,
                    "ts": e.ts,
                    "event": e.event,
                    "detail": e.detail,
                    "result_id": e.result_id,
                }
                for e in self.codex.feed(since=since)
            ]
            return {"ok": True, "data": entries}

        if cmd == "scrap":
            s = self.codex.scrap()
            return {"ok": True, "data": {
                "vessel_id": s.vessel_id,
                "live": s.live,
                "isolation_state": s.isolation_state,
                "model_loaded": s.model_loaded,
            }}

        if cmd == "list_seared":
            paths = [
                {
                    "kind": p.kind,
                    "description": p.description,
                    "clearance": p.clearance,
                    "seared_at": p.seared_at,
                    "seared_by": p.seared_by,
                }
                for p in self.codex.list_seared()
            ]
            return {"ok": True, "data": paths}

        return {"ok": False, "error": f"unknown cmd: {cmd!r}"}

    @staticmethod
    def _result_dict(r: Any) -> dict[str, Any]:
        return {
            "result_id": r.result_id,
            "kind": r.kind,
            "content": r.content,
            "created_at": r.created_at,
            "vessel_id": r.vessel_id,
            "pathway_kind": r.pathway_kind,
            "content_hash": r.content_hash,
            "metadata": dict(r.metadata),
        }


def client_request(cmd: str, path: Path | None = None, **kwargs: Any) -> dict[str, Any]:
    sock_path = path or socket_path()
    if not sock_path.exists():
        return {"ok": False, "error": f"socket not found: {sock_path}"}

    req = {"cmd": cmd, **kwargs}
    data = (json.dumps(req) + "\n").encode("utf-8")

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.settimeout(120.0)
        s.connect(str(sock_path))
        s.sendall(data)
        buf = b""
        while b"\n" not in buf:
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
        line = buf.split(b"\n", 1)[0]
        return json.loads(line.decode("utf-8"))
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        try:
            s.close()
        except OSError:
            pass
