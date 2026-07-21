# OS ↔ NPU Fit — research verdict (2026-07-19)

## Hardware correction (important)
Your **Core Ultra 9 275HX** (Arrow Lake-HX) carries **Intel NPU 3 (NPU 3720), ~13 TOPS** —
NOT the NPU 4 (48 TOPS) that's in Lunar Lake / Arrow Lake-H.
- Driver loads firmware **`vpu_37xx.bin`** (NOT `vpu_40xx.bin`). Don't force NPU4 firmware.
- Practical impact: keep the NPU brain SMALL (1.5B–3B, INT4). 13 TOPS is fine for the
  always-on observe-and-judge role; heavy work stays on the RTX. This matches our design —
  the brain watches, the capsules do.

## VERDICT: stay on Pop!_OS 24.04 (COSMIC/Wayland). Do NOT distro-hop.
For this exact dual-hardware combo (Intel NPU + NVIDIA RTX 5080), Pop!_OS is the best
Linux platform available. Reasons, itemized:

| Why stay | Detail |
|----------|--------|
| Kernel is already fresh enough | NPU driver (`intel_vpu`) wants Linux 6.8 min / **6.11+ recommended**. Pop!_OS 24.04 rolls kernels aggressively (7.0.x as of early 2026) — **more than ready out of the box**, ahead of stock Ubuntu (6.8). |
| Debian base = Intel's `.deb` packages "just work" | Intel ships official **`.deb`** NPU driver + firmware for Ubuntu 24.04. Pop!_OS runs them natively. Fedora needs unofficial COPR RPMs; Arch needs AUR builds that break on lib bumps. |
| Firmware lag is a non-issue | Even if Pop's `linux-firmware` lags, Intel's **`intel-fw-npu` .deb** drops the exact `vpu_37xx.bin` straight into `/lib/firmware/intel/vpu/`. Zero wait. |
| Best NVIDIA + Wayland story | COSMIC (Rust, native Wayland) handles Intel-NPU / NVIDIA-RTX hybrid with explicit sync, out of the box. Arch/Fedora need manual tuning to avoid flicker/power issues. Pop's ISO pre-installs the 580.x proprietary driver. |
| Lowest hassle, high stability | LTS Debian base + rolling kernel + COSMIC = the freshness of Arch with the stability/compat of Ubuntu. |

### Side-by-side (the short version)
| Distro | Kernel | NPU driver install | NVIDIA | Verdict |
|--------|--------|--------------------|--------|---------|
| **Pop!_OS 24.04 (COSMIC)** | 7.0.x — freshest | Easy (native .deb) | Pre-installed 580.x | **✅ stay** |
| Ubuntu 24.04/24.10 | 6.8 / 6.11 | Easy (Intel's target) | GUI installer | ok, older kernel |
| Fedora 41/42 | 6.12/6.13 | COPR (unofficial) | RPM Fusion | more hassle |
| Arch / CachyOS | 7.0.x+ | AUR (breaks on lib bumps) | DKMS risk | high hassle |

**Bottom line:** there is **no reason to switch off Pop!_OS COSMIC/Wayland**. You'd trade
zero NPU benefit for real dual-GPU hassle. Just update kernel/firmware/driver on Pop.

## The exact path on Pop!_OS (folded into bind/01)
1. `lsmod | grep intel_vpu` and `ls -l /dev/accel/accel0` — confirm the driver + node.
2. Grab the **Ubuntu 24.04** `.deb` set from github.com/intel/linux-npu-driver/releases
   (validated release, e.g. v1.33.0+): `intel-driver-compiler-npu`, `intel-fw-npu`,
   `intel-level-zero-npu`. Deps: `sudo apt install libtbb12 libze-loader1`.
3. `sudo dpkg -i intel-*npu*_ubuntu24.04_amd64.deb`
4. Permissions: `sudo usermod -aG render $USER`, apply Intel's `10-intel-vpu.rules`,
   `sudo rmmod intel_vpu && sudo modprobe intel_vpu`.
5. Confirm: `sudo dmesg | grep intel_vpu` should show **`vpu_37xx_v0.0.bin`** loaded.
6. `python3 -c "import openvino as ov; print(ov.Core().available_devices)"` →
   should list **`NPU`**.

## Sources
- github.com/intel/linux-npu-driver (+ /releases)
- docs.openvino.ai/2025/get-started/install-openvino/configurations/configurations-intel-npu.html
- docs.openvino.ai/nightly/openvino-workflow-generative/inference-with-genai/inference-with-genai-on-npu.html
