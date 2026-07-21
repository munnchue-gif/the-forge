# Forge-NG · Model Binding (hands-on-the-PC step)

This folder is the **first step that runs on Eugene's actual machine** — the
sandbox can't touch the NPU or the RTX. Everything here is written to be run on
Pop!_OS, is re-runnable, and is SAFE (installs + verifies; touches no Forge code
until you wire the shims in).

## The split (why two paths)
- **The brain → the Intel NPU** (small, always-on, observe-and-judge). Path:
  Intel NPU driver + **OpenVINO GenAI** (the only viable Linux NPU LLM path —
  ipex-llm NPU is Windows-only; intel-npu-accel-lib is deprecated).
- **The capsules → the RTX 5080** (the doing models). Path: **Ollama** (already
  installed). The brain WATCHES the capsules; it never does their work.

## Run order (on the PC)
1. `bash bind/01_setup_npu_openvino.sh` — installs NPU driver bits + OpenVINO
   GenAI, then PROVES the NPU shows up as an inference device. If it doesn't,
   read `OS_NPU_NOTES.md` (kernel/firmware).
2. `bash bind/02_pull_and_convert_brain.sh` — pulls a small model
   (Qwen2.5-1.5B-Instruct by default), converts to OpenVINO INT4, and smoke-tests
   generation **on the NPU**.
3. `bash bind/03_setup_capsule_models_ollama.sh` — pulls capsule workhorse models
   onto the RTX via Ollama and smoke-tests one.

## Wiring into the fabric (after the scripts pass)
The shims are already written + unit-tested (with mocked hardware):
- `fabric/bind/openvino_seat.py` — `OpenVinoSeat(model_dir, "NPU")` satisfies the
  conduit's `NpuSeat` contract. Bind it at boot:
  ```python
  from fabric.kernel import boot_forge
  from fabric.bind.openvino_seat import OpenVinoSeat
  seat = OpenVinoSeat("~/.forge-models/brain-ov-int4", device="NPU")
  k = boot_forge(secret, seat=seat)   # the brain is now real silicon
  ```
- `fabric/bind/ollama_capsule.py` — `OllamaCapsule(model)` is a sealed section's
  handle to a GPU model. The section gates the egress; the shim just carries bytes.

## Safety notes
- Both shims **fail safe**: a broken NPU brain returns no findings (never fabricates
  an action, never crashes the heartbeat); an unreachable Ollama returns health=False.
- Nothing is bound bare — capsule calls still go through a sealed section + gate.
- Pin the NPU driver `.deb` version that matches your kernel (see `OS_NPU_NOTES.md`).

## Status
Scripts + shims written and unit-tested in the sandbox (11 bind tests green, suite
119 total). NOT yet run on real silicon — that's your move, ideally after the
mirror review.
