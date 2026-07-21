#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Forge-NG · bind/03 — capsule workhorse models on the RTX 5080 via Ollama
#
# Capsules = the doing models (they run tasks inside sealed sections). These go
# on the RTX 5080 (16GB) through Ollama, which you already have (v0.24.0). The
# NPU brain WATCHES them; it does not do their work.
#
# VRAM budget ~16GB — pick models that fit with headroom. SAFE: pulls models.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

command -v ollama >/dev/null || { echo "Ollama not found — install from ollama.com"; exit 1; }

echo "▶ Ollama version: $(ollama --version)"
echo "▶ Confirming GPU is visible to Ollama…"
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv 2>/dev/null || \
  echo "  ! nvidia-smi missing — check the 580 driver"

# Capsule workhorses that fit 16GB with room for the sealed runtime.
# Keep them modest so multiple capsules can coexist; the brain stays on the NPU.
CAPSULE_MODELS=(
  "qwen2.5:7b-instruct-q4_K_M"   # general capsule (~5GB)
  "llama3.1:8b-instruct-q4_K_M"  # alt general (~5GB)
)
echo "▶ Pulling capsule models (Ctrl-C to skip any)…"
for m in "${CAPSULE_MODELS[@]}"; do
  echo "  pulling $m"
  ollama pull "$m" || echo "  ! skipped $m"
done

echo "▶ Quick capsule smoke-test on the GPU…"
ollama run "${CAPSULE_MODELS[0]}" "Reply with the single word ONLINE." --verbose 2>/dev/null | head -5 || true

echo "✓ Capsule models ready on the RTX. The Forge will reach them through a"
echo "  sealed section — never bare — via the Ollama HTTP API (127.0.0.1:11434)."
echo "  Binding shim: fabric/bind/ollama_capsule.py (see bind/README.md)."
