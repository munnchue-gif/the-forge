#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Forge-NG · bind/02 — pull a small "brain" model and convert it for the NPU
#
# The brain = the small observe-and-judge model that sits on the NPU (the seat).
# It stays home, small, and always-on — NOT a capsule workhorse (those go on the
# RTX via Ollama, see bind/03). NPUs like small, INT4/INT8-quantized models.
#
# SAFE: downloads + converts into ~/.forge-models/. Touches no Forge code.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
source ~/.forge-npu/bin/activate 2>/dev/null || { echo "run bind/01 first"; exit 1; }

# A small instruct model is ideal for the judge role. Swap freely.
BRAIN_ID="${BRAIN_ID:-Qwen/Qwen2.5-1.5B-Instruct}"
OUT="${OUT:-$HOME/.forge-models/brain-ov-int4}"
mkdir -p "$OUT"

echo "▶ Converting $BRAIN_ID to OpenVINO INT4 for the NPU seat…"
# optimum-cli exports HF → OpenVINO IR with weight compression the NPU wants.
optimum-cli export openvino \
  --model "$BRAIN_ID" \
  --weight-format int4 \
  --task text-generation-with-past \
  "$OUT"

echo "▶ Smoke-test the brain ON THE NPU…"
python3 - "$OUT" <<'PY'
import sys, openvino_genai as ov_genai
model_dir = sys.argv[1]
try:
    pipe = ov_genai.LLMPipeline(model_dir, "NPU")
    out = pipe.generate("Say READY in one word.", max_new_tokens=8)
    print("  NPU brain says:", out)
    print("  ✓ Brain runs on the NPU.")
except Exception as e:
    print("  ! NPU generate failed:", e)
    print("  Falling back to CPU to prove the model itself is fine…")
    pipe = ov_genai.LLMPipeline(model_dir, "CPU")
    print("  CPU:", pipe.generate("Say READY.", max_new_tokens=8))
PY
echo "✓ Brain converted at: $OUT"
echo "Next: wire it into the conduit via fabric/bind/openvino_seat.py (see bind/README.md)."
