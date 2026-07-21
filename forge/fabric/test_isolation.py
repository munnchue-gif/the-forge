"""Unit tests for fabric.isolation (D1) — pure command composition, no bwrap needed."""

import pytest

from fabric.isolation import (
    IsolationError,
    IsolationPolicy,
    build_isolated_argv,
)


def test_empty_argv_refused():
    with pytest.raises(IsolationError):
        build_isolated_argv([])


def test_default_policy_composes_both_walls():
    cmd = build_isolated_argv(["echo", "hi"])
    assert cmd[0] == "systemd-run"
    assert "bwrap" in cmd
    assert cmd[-2:] == ["echo", "hi"]


def test_network_denied_by_default():
    cmd = build_isolated_argv(["true"])
    assert "--unshare-net" in cmd


def test_network_opt_in():
    cmd = build_isolated_argv(["true"], IsolationPolicy(allow_network=True))
    assert "--unshare-net" not in cmd


def test_cgroup_limits_rendered():
    p = IsolationPolicy(cpu_quota_pct=25, memory_max="128M", tasks_max=16)
    cmd = build_isolated_argv(["true"], p)
    assert "CPUQuota=25%" in cmd
    assert "MemoryMax=128M" in cmd
    assert "TasksMax=16" in cmd


def test_env_cleared_and_session_new():
    cmd = build_isolated_argv(["true"])
    assert "--clearenv" in cmd
    assert "--new-session" in cmd
    assert "--die-with-parent" in cmd


def test_extra_ro_binds_included():
    p = IsolationPolicy(extra_ro_binds=("/opt/snips",))
    cmd = build_isolated_argv(["true"], p)
    i = cmd.index("/opt/snips")
    assert cmd[i - 1] == "--ro-bind-try" and cmd[i + 1] == "/opt/snips"
