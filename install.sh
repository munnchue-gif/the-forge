#!/usr/bin/env bash
# ============================================================
# THE FORGE — Complete Install Script
# Pop!_OS 24.04 + Intel Arrow Lake NPU + NVIDIA RTX
# Run once on a fresh install
# ============================================================
set -euo pipefail

FORGE_DIR="$HOME/the-forge"
FORGE_VENV="$FORGE_DIR/.venv"
MODELS_DIR="$HOME/.forge-models"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  THE FORGE — Install"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── 1. System packages ────────────────────────────────────
echo "▶ Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y \
    python3-venv python3-pip git wget curl \
    build-essential cmake pkg-config \
    intel-level-zero-npu intel-fw-npu \
    intel-driver-compiler-npu intel-opencl-icd \
    intel-level-zero-gpu libze-intel-gpu1 \
    libze1 strace

# ── 2. Pin libze1 (critical — must not be removed) ───────
echo "▶ Pinning libze1..."
sudo apt-mark hold libze1
echo "libze1 hold" | sudo dpkg --set-selections

# ── 3. Intel GPU apt repo ─────────────────────────────────
echo "▶ Adding Intel GPU repo..."
if [ ! -f /usr/share/keyrings/intel-graphics.gpg ]; then
    wget -qO - https://repositories.intel.com/gpu/intel-graphics.key | \
        sudo gpg --dearmor --output /usr/share/keyrings/intel-graphics.gpg
fi
if [ ! -f /etc/apt/sources.list.d/intel-gpu-jammy.list ]; then
    echo "deb [arch=amd64,i386 signed-by=/usr/share/keyrings/intel-graphics.gpg] https://repositories.intel.com/gpu/ubuntu jammy client" | \
        sudo tee /etc/apt/sources.list.d/intel-gpu-jammy.list
fi

# ── 4. NPU Level Zero ICD ────────────────────────────────
echo "▶ Configuring NPU ICD..."
sudo mkdir -p /etc/level_zero/icd.d
echo "/usr/lib/x86_64-linux-gnu/libze_intel_npu.so.1" | \
    sudo tee /etc/level_zero/icd.d/intel_npu.icd

# ── 5. udev rule for NPU device node ─────────────────────
echo "▶ Setting up NPU udev rule..."
echo 'KERNEL=="accel*", MODE="0660", GROUP="render"' | \
    sudo tee /etc/udev/rules.d/50-intel-npu.rules
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=accel

# ── 6. Groups ─────────────────────────────────────────────
echo "▶ Adding user to render and video groups..."
sudo usermod -aG render,video "$USER"

# ── 7. Clone or update the-forge ─────────────────────────
echo "▶ Setting up the-forge directory..."
mkdir -p "$FORGE_DIR"
mkdir -p "$MODELS_DIR"

# ── 8. Python venv ────────────────────────────────────────
echo "▶ Creating Python venv..."
python3 -m venv "$FORGE_VENV"
source "$FORGE_VENV/bin/activate"

pip install --upgrade pip -q
pip install -q \
    openvino openvino-genai openvino-tokenizers \
    intel-npu-acceleration-library \
    optimum[openvino] \
    requests aiohttp fastapi uvicorn \
    websockets pydantic

# ── 9. Write activate env vars ───────────────────────────
echo "▶ Writing environment variables..."
FORGE_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
cat >> "$FORGE_VENV/bin/activate" << ENVEOF

# ── The Forge environment ─────────────────────────────────
export ZE_ENABLE_NPU=1
export ZE_FLAT_DEVICE_HIERARCHY=COMPACT
export PYTHONPATH="$FORGE_DIR/forge:\${PYTHONPATH:-}"
export FORGE_SECRET="$FORGE_SECRET"
ENVEOF

# ── 10. Verify NPU ───────────────────────────────────────
echo ""
echo "▶ Verifying NPU..."
ZE_ENABLE_NPU=1 ZE_FLAT_DEVICE_HIERARCHY=COMPACT python3 -c "
import openvino as ov
devices = ov.Core().available_devices
print(f'  Devices: {devices}')
if 'NPU' in devices:
    print('  ✓ NPU ACTIVE')
else:
    print('  ✗ NPU not found — check libze1 and kernel')
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  INSTALL COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  To start The Forge:"
echo "    cd ~/the-forge"
echo "    source .venv/bin/activate"
echo "    python3 run_forge.py"
echo ""
echo "  NOTE: Log out and back in for render group to take effect"
echo "  NOTE: Keep kernel 7.0.0-28-generic — NPU verified working"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
