"""
forge/fabric/codex_cli.py — Private Codex launcher + talk surface

Usage (local or over SSH):

  # Terminal 1 — start the organ + private socket
  cd ~/the-forge
  source .venv/bin/activate
  export PYTHONPATH=$HOME/the-forge/forge
  export FORGE_SECRET='dev-only-not-for-prod'
  python -m fabric.codex_cli serve

  # Terminal 2 (or SSH session) — talk to it
  python -m fabric.codex_cli ask "what is the current status of the fabric?"
  python -m fabric.codex_cli status
  python -m fabric.codex_cli feed
  python -m fabric.codex_cli interactive   # chat loop

No public listeners. Socket lives at ~/.forge/codex.sock (owner-only).
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path

# Ensure fabric is importable when run as python -m fabric.codex_cli
def _boot_paths() -> None:
    root = Path(__file__).resolve().parents[1]  # .../forge
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

_boot_paths()

from fabric.codex import Codex, SealedPathway  # noqa: E402
from fabric.codex_socket import CodexSocketServer, client_request, socket_path  # noqa: E402


def cmd_serve(_: argparse.Namespace) -> int:
    secret = os.environ.get("FORGE_SECRET", "dev-only-not-for-prod").encode()

    def ledger_append(entry: dict) -> None:
        # Lightweight local log so something is always recorded even without full Kernel
        log = Path.home() / ".forge" / "codex_ledger.jsonl"
        log.parent.mkdir(parents=True, exist_ok=True)
        with open(log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    codex = Codex(ledger_append=ledger_append)
    server = CodexSocketServer(codex)
    path = server.start()

    print(f"Codex vessel live  vessel_id={codex.status().vessel_id}")
    print(f"Private socket     {path}")
    print("Owner-only permissions. No TCP. No public bind.")
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
    data = resp["data"]
    print(data.get("content", ""))
    return 0


def cmd_feed(args: argparse.Namespace) -> int:
    resp = client_request("feed", since=args.since)
    print(json.dumps(resp, indent=2))
    return 0 if resp.get("ok") else 1


def cmd_interactive(_: argparse.Namespace) -> int:
    print("Codex interactive (private socket). Empty line or Ctrl+C to exit.")
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
    sub.add_parser("interactive", help="Chat loop over the private socket")

    args = p.parse_args(argv)
    if args.cmd == "serve":
        return cmd_serve(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "ask":
        return cmd_ask(args)
    if args.cmd == "feed":
        return cmd_feed(args)
    if args.cmd == "interactive":
        return cmd_interactive(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
