#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Forge-NG · bind/01 — set up the Intel Arrow Lake NPU for LLM inference (Linux)
#
# Runs on Eugene's PC (Pop!_OS 24.04, Intel Core Ultra 9 275HX + Arrow Lake NPU).
# Installs the ONLY viable Linux NPU LLM path: intel/linux-npu-driver + OpenVINO
# GenAI. (ipex-llm NPU is Windows-only; intel-npu-accel-lib is deprecated.)
#
# SAFE: this only INSTALLS + VERIFIES. It touches no Forge code and no models yet.
# Read the echoed steps; nothing here is destructive. Re-runnable.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

say() { printf "\n\033[1;36m▶ %s\033[0m\n" "$*"; }
ok()  { printf "  \033[1;32m✓ %s\033[0m\n" "$*"; }
warn(){ printf "  \033[1;33m! %s\033[0m\n" "$*"; }

say "0/6  Environment check"
uname -a
echo "kernel: $(uname -r)"
KVER=$(uname -r | cut -d. -f1-2)
warn "Arrow Lake NPU wants a recent kernel. If this is < 6.10, see bind/OS_NPU_NOTES.md"

say "1/6  Confirm the NPU device is present"
if lspci | grep -i "npu\|neural\|00:0b.0" ; then ok "NPU visible on PCI bus"; else
  warn "NPU not seen via lspci — check BIOS (NPU enabled?) and kernel version"; fi
ls -l /dev/accel/ 2>/dev/null && ok "/dev/accel present" || warn "/dev/accel missing — driver not loaded yet"

say "2/6  Intel NPU kernel driver + firmware"
# The intel_vpu kernel module drives the NPU. Recent kernels ship it; older need it added.
if lsmod | grep -q intel_vpu; then ok "intel_vpu module loaded"; else
  warn "intel_vpu not loaded — updating linux-firmware + trying modprobe"
  sudo apt-get update -y
  sudo apt-get install -y linux-firmware libtbb12 libze-loader1 || true
  sudo modprobe intel_vpu || warn "modprobe failed — likely needs newer kernel (see notes)"
fi

say "3/6  Intel NPU user-mode driver (from intel/linux-npu-driver releases)"
# These .deb releases match a driver version to your kernel; pin the version you tested.
NPU_DRV_VER="${NPU_DRV_VER:-1.33.0}"   # override with env if you pick a newer release
echo "Target user-mode NPU driver: v${NPU_DRV_VER}"
echo "Download the matching .deb set from:"
echo "   https://github.com/intel/linux-npu-driver/releases"
echo "Then: sudo dpkg -i intel-driver-compiler-npu_*.deb intel-fw-npu_*.deb intel-level-zero-npu_*.deb"
warn "Kept manual on purpose — you pick the release that matches your kernel. Notes in bind/OS_NPU_NOTES.md"

say "4/6  OpenVINO GenAI runtime (Python)"
python3 -m venv ~/.forge-npu 2>/dev/null || true
# shellcheck disable=SC1090
source ~/.forge-npu/bin/activate
pip install --upgrade pip
pip install "openvino-genai>=2025.0.0" "openvino>=2025.0.0" "optimum[openvino]" huggingface_hub
ok "OpenVINO GenAI installed in ~/.forge-npu"

say "4b  Confirm the CORRECT firmware loaded (NPU 3 = vpu_37xx, NOT vpu_40xx)"
sudo dmesg | grep -i intel_vpu | tail -5 || true
warn "Your 275HX is NPU 3 (13 TOPS) — expect vpu_37xx_v0.0.bin. Do NOT force NPU4 fw."

say "5/6  Prove the NPU is a usable inference device"
python3 - <<'PY'
try:
    import openvino as ov
    core = ov.Core()
    devs = core.available_devices
    print("  OpenVINO devices:", devs)
    if "NPU" in devs:
        print("  ✓ NPU is available to OpenVINO — the brain has a seat.")
        print("  NPU name:", core.get_property("NPU", "FULL_DEVICE_NAME"))
    else:
        print("  ! NPU not listed. GPU/CPU still usable. Check driver+kernel (notes).")
except Exception as e:
    print("  ! OpenVINO probe failed:", e)
PY

say "6/6  Done"
ok "If NPU showed up above, run bind/02_pull_and_convert_brain.sh next."
echo "Leave the venv active or: source ~/.forge-npu/bin/activate"
