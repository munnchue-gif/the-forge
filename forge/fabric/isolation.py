"""
Forge-NG — OS-level process isolation for the Concoctinator (D1).

COLLAB decision T3 (approved by @Eugene 2026-07-21): bubblewrap inside a
systemd-run --user scope. bwrap gives the unprivileged namespace sandbox
(fs / pid / net isolation, no daemon, no root); the systemd scope layers
cgroup v2 resource limits (CPUQuota, MemoryMax, TasksMax) on top.

This module does NOT replace fabric/sandbox.py — that is the logical arena
(gate-in-observe-mode). This is the OS wall around any *process* the arena
spawns: when a concoction needs to actually execute something, it runs here,
where it cannot touch the host, the network, or the real Forge state.

Design:
    - build_isolated_argv(argv, policy) is a PURE function — fully unit-testable
      on any machine, no bwrap/systemd needed.
    - run_isolated(argv, policy) executes it (Pop!_OS host only).
    - Deny by default: no network, read-only /usr toolchain, tmpfs scratch,
      cleared environment, dies with parent.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field


class IsolationError(Exception):
    """Raised when an isolated run cannot be composed or launched."""


@dataclass(frozen=True)
class IsolationPolicy:
    """Resource + reach limits for one isolated process."""
    cpu_quota_pct: int = 50          # CPUQuota= (percent of one core)
    memory_max: str = "512M"         # MemoryMax=
    tasks_max: int = 64              # TasksMax= (fork-bomb wall)
    timeout_s: float = 30.0          # hard wall-clock kill
    allow_network: bool = False      # keep False: concoctions have no net
    ro_binds: tuple = ("/usr", "/lib", "/lib64", "/bin", "/etc/alternatives")
    extra_ro_binds: tuple = ()       # e.g. a snip staging dir, read-only
    scratch_dir: str = "/tmp"        # tmpfs inside the sandbox


@dataclass
class IsolationResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
    argv: list = field(default_factory=list)


def build_isolated_argv(argv: list[str], policy: IsolationPolicy | None = None) -> list[str]:
    """Compose the full systemd-run + bwrap command line. Pure — no side effects."""
    if not argv:
        raise IsolationError("empty argv — nothing to isolate")
    p = policy or IsolationPolicy()

    cmd = [
        "systemd-run", "--user", "--scope", "--quiet",
        "--property", f"CPUQuota={p.cpu_quota_pct}%",
        "--property", f"MemoryMax={p.memory_max}",
        "--property", f"TasksMax={p.tasks_max}",
        "--",
        "bwrap",
        "--die-with-parent",
        "--new-session",
        "--clearenv",
        "--setenv", "PATH", "/usr/bin:/bin",
        "--unshare-user",
        "--unshare-pid",
        "--unshare-ipc",
        "--unshare-uts",
        "--unshare-cgroup",
    ]
    if not p.allow_network:
        cmd.append("--unshare-net")
    for path in tuple(p.ro_binds) + tuple(p.extra_ro_binds):
        cmd += ["--ro-bind-try", path, path]
    cmd += [
        "--proc", "/proc",
        "--dev", "/dev",
        "--tmpfs", p.scratch_dir,
        "--chdir", p.scratch_dir,
        "--",
    ]
    return cmd + list(argv)


def isolation_available() -> tuple[bool, str]:
    """Check the host has both walls. Returns (ok, reason)."""
    missing = [t for t in ("systemd-run", "bwrap") if shutil.which(t) is None]
    if missing:
        return False, f"missing on host: {', '.join(missing)} (apt install bubblewrap)"
    return True, "ok"


def run_isolated(argv: list[str], policy: IsolationPolicy | None = None) -> IsolationResult:
    """Run argv inside the bwrap+scope wall. Host-only; only the Concoctinator
    invokes this, and only for draft execution — never the App path directly."""
    p = policy or IsolationPolicy()
    ok, reason = isolation_available()
    if not ok:
        raise IsolationError(reason)
    full = build_isolated_argv(argv, p)
    try:
        proc = subprocess.run(
            full, capture_output=True, text=True, timeout=p.timeout_s, check=False
        )
        return IsolationResult(proc.returncode, proc.stdout, proc.stderr, False, full)
    except subprocess.TimeoutExpired as e:
        def _s(v):
            return v.decode() if isinstance(v, bytes) else (v or "")
        return IsolationResult(-1, _s(e.stdout), _s(e.stderr), True, full)
