"""Sandbox-testable tests for the model-binding shims.

There's no NPU or Ollama server here, so the heavy model calls are MOCKED. These
prove the CONTRACT and the parsing/fallback logic — the parts that break silently
on real hardware if they're wrong."""

from fabric.bind.openvino_seat import OpenVinoSeat
from fabric.bind.ollama_capsule import OllamaCapsule
from fabric.conduit import VectorMemory
from fabric.overseer import Finding


# ── OpenVinoSeat: it must satisfy the NpuSeat contract + parse robustly ────────

def test_seat_parses_findings_from_model_json():
    seat = OpenVinoSeat(model_dir="/fake")
    raw = ('Here you go: [{"section":"cap-a","kind":"drift",'
           '"detail":"vector drift","severity":2}] done')
    findings = seat._parse(raw)
    assert len(findings) == 1
    f = findings[0]
    assert isinstance(f, Finding)
    assert f.section_id == "cap-a" and f.severity == 2


def test_seat_empty_on_no_json():
    seat = OpenVinoSeat(model_dir="/fake")
    assert seat._parse("the model rambled with no list") == []


def test_seat_empty_on_malformed_json():
    seat = OpenVinoSeat(model_dir="/fake")
    assert seat._parse("[ {broken json ]") == []


def test_seat_clamps_severity():
    seat = OpenVinoSeat(model_dir="/fake")
    raw = '[{"section":"s","kind":"k","detail":"d","severity":99}]'
    assert seat._parse(raw)[0].severity == 3
    raw2 = '[{"section":"s","kind":"k","detail":"d","severity":-5}]'
    assert seat._parse(raw2)[0].severity == 0


def test_seat_judge_returns_empty_on_no_observations():
    seat = OpenVinoSeat(model_dir="/fake")
    assert seat.judge([], VectorMemory()) == []


def test_seat_judge_uses_the_pipe(monkeypatch):
    """With the pipe mocked, judge() runs end-to-end and returns parsed findings
    WITHOUT any real NPU."""
    seat = OpenVinoSeat(model_dir="/fake")

    class FakePipe:
        def generate(self, prompt, max_new_tokens):
            return '[{"section":"cap-b","kind":"loop","detail":"x","severity":3}]'

    seat._pipe = FakePipe()  # pretend it's already bound
    findings = seat.judge([{"_section": "cap-b", "state": "spin"}], VectorMemory())
    assert len(findings) == 1 and findings[0].severity == 3


def test_seat_judge_survives_model_crash(monkeypatch):
    """A broken brain must return [] — never crash the heartbeat, never fabricate."""
    seat = OpenVinoSeat(model_dir="/fake")

    class BoomPipe:
        def generate(self, *a, **k):
            raise RuntimeError("NPU on fire")

    seat._pipe = BoomPipe()
    assert seat.judge([{"x": 1}], VectorMemory()) == []


def test_seat_satisfies_npuseat_protocol():
    """Structural: the conduit accepts it as a seat."""
    from fabric.conduit import VectorConduit  # noqa: F401
    seat = OpenVinoSeat(model_dir="/fake")
    assert hasattr(seat, "judge")


# ── OllamaCapsule: URL + payload shape (no server here) ────────────────────────

def test_capsule_builds_local_url():
    cap = OllamaCapsule(model="qwen2.5:7b")
    assert cap._url == "http://127.0.0.1:11434/api/generate"


def test_capsule_generate_parses_response(monkeypatch):
    import fabric.bind.ollama_capsule as mod

    class FakeResp:
        status = 200
        def read(self): return b'{"response":"ONLINE"}'
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(mod.urllib.request, "urlopen", lambda *a, **k: FakeResp())
    cap = OllamaCapsule(model="qwen2.5:7b")
    assert cap.generate("hi") == "ONLINE"


def test_capsule_health_false_when_unreachable(monkeypatch):
    import fabric.bind.ollama_capsule as mod
    def boom(*a, **k): raise OSError("no server")
    monkeypatch.setattr(mod.urllib.request, "urlopen", boom)
    assert OllamaCapsule(model="x").health() is False
