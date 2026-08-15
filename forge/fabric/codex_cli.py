"""
forge/fabric/codex_cli.py — Private Codex launcher + talk surface

Usage (local or over SSH):

  # Terminal 1 — start the organ + private socket
  python -m fabric.codex_cli serve

  # Terminal 2
  python -m fabric.codex_cli status
  python -m fabric.codex_cli load-model qwen2.5-coder:7b
  python -m fabric.codex_cli ask "explain the Gate organ"
  python -m fabric.codex_cli unload-model
  python -m fabric.codex_cli interactive

No public listeners. Socket: ~/.forge/codex.sock
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path


def _boot_paths() -> None:
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_boot_paths()

from fabric.codex import Codex  # noqa: E402
from fabric.codex_socket import CodexSocketServer, client_request, socket_path  # noqa: E402


def cmd_serve(_: argparse.Namespace) -> int:
    def ledger_append(entry: dict) -> None:
        log = Path.home() / ".forge" / "codex_ledger.jsonl"
        log.parent.mkdir(parents=True, exist_ok=True)
        with open(log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    codex = Codex(ledger_append=ledger_append)
    server = CodexSocketServer(codex)
    path = server.start()

    s = codex.status()
    print(f"Codex vessel live  vessel_id={s.vessel_id}")
    print(f"Private socket     {path}")
    print("Owner-only. No TCP. No public bind.")
    print("Commands from other terminal: status | load-model | unload-model | ask | interactive")
    print("Ctrl+C to scrap and exit.")

    def _shutdown(*_a: object) -> None:
        print("\nScrapping Codex…")
        try:
            codex.scrap()
        except Exception:
            pass
        server.stop()
        print("Socket removed. Done.")
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    while True:
        time.sleep(1.0)


def cmd_status(_: argparse.Namespace) -> int:
    resp = client_request("status")
    print(json.dumps(resp, indent=2))
    return 0 if resp.get("ok") else 1


def cmd_ask(args: argparse.Namespace) -> int:
    prompt = args.prompt or " "
    resp = client_request("ask", prompt=prompt)
    if not resp.get("ok"):
        print(json.dumps(resp, indent=2))
        return 1
    print(resp["data"].get("content", ""))
    return 0


def cmd_feed(args: argparse.Namespace) -> int:
    resp = client_request("feed", since=args.since)
    print(json.dumps(resp, indent=2))
    return 0 if resp.get("ok") else 1


def cmd_load_model(args: argparse.Namespace) -> int:
    mid = args.model or "qwen2.5-coder:7b"
    resp = client_request("load_model", model_id=mid)
    print(json.dumps(resp, indent=2))
    return 0 if resp.get("ok") else 1


def cmd_unload_model(_: argparse.Namespace) -> int:
    resp = client_request("unload_model")
    print(json.dumps(resp, indent=2))
    return 0 if resp.get("ok") else 1


def cmd_interactive(_: argparse.Namespace) -> int:
    print("Codex interactive. Empty line or Ctrl+C to exit.")
    print(f"Socket: {socket_path()}")
    while True:
        try:
            line = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            break
        resp = client_request("ask", prompt=line)
        if not resp.get("ok"):
            print(f"error: {resp.get('error')}")
            continue
        print(resp["data"].get("content", ""))
        print()
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="codex", description="Private Codex organ control")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("serve", help="Start Codex + private Unix socket")
    sub.add_parser("status", help="Show vessel status")
    sub.add_parser("feed", help="Show feed").add_argument("--since", type=float, default=0.0)
    ask_p = sub.add_parser("ask", help="Single question")
    ask_p.add_argument("prompt", nargs="?", default="")
    load_p = sub.add_parser("load-model", help="Hot-load a local Ollama model")
    load_p.add_argument("model", nargs="?", default="qwen2.5-coder:7b")
    sub.add_parser("unload-model", help="Unload model and free VRAM")
    sub.add_parser("interactive", help="Chat loop")

    args = p.parse_args(argv)
    if args.cmd == "serve":
        return cmd_serve(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "ask":
        return cmd_ask(args)
    if args.cmd == "feed":
        return cmd_feed(args)
    if args.cmd == "load-model":
        return cmd_load_model(args)
    if args.cmd == "unload-model":
        return cmd_unload_model(args)
    if args.cmd == "interactive":
        return cmd_interactive(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
