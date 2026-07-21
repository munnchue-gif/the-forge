"""Run the Forge: `python -m forge_ng` boots the kernel and beats a few times.

This is the BOOT proof — the fabric coming alive as a process, not an import.
In production this becomes the long-running daemon the DJ booth connects to.
"""
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")

from fabric.kernel import boot_forge


def main() -> None:
    k = boot_forge()
    print("\n=== FORGE BOOTED ===")
    print("organs:", k.organ_names())

    # Open a couple of deaf sections and beat the heartbeat.
    k.overseer.split_region("capsule-a", sections=1)
    k.overseer.split_region("capsule-b", sections=1)
    for i in range(3):
        k.bus.publish("capsule-a.s0", "telemetry", {"state": "ok", "beat": i})
        findings = k.tick()
        print(f"tick {i}: {len(findings)} findings")
        time.sleep(0.05)

    print("\n=== HEALTH ===")
    for key, val in k.health().items():
        print(f"  {key}: {val}")

    ok, bad = k.shutdown()
    print(f"\n=== SHUTDOWN === audit_intact={ok}")


if __name__ == "__main__":
    main()
