# Forge Build — Review of the Plan, and What I'd Change

You asked for my take on the baseline you were given, how to wire Obsidian +
GitHub as a memory layer, and how to run all of this on the GPU of the MSI
Vector HX 16 (i9-275HX, 96 GB DDR5, RTX 5080 Laptop 16 GB, 13 TOPS NPU).

---

## 1. Verdict on the plan you were handed

It is **structurally sound** — better than most. Keep these four things:

1. **Copy-only, deletes never.** This is the single decision that makes the
   whole project safe to attempt.
2. **One spine as source of truth** (`the-forge`), everything else demoted to
   "candidate material." Without this you get five half-alive repos again.
3. **Phased rollout, one root first.** Correct instinct.
4. **seL4 deferred.** Right call. See §6.

Five things I would change:

| # | Issue in the plan | Fix |
|---|---|---|
| 1 | Paths were unverified `/home/mancier/...`. Confirmed correct — you're on **Pop!_OS**, so these are real paths. But a hardcoded username in a coder prompt is still fragile. | Config uses `~` expansion throughout; no username is baked into any script. |
| 2 | "Grade GOLD if it matches or beats live the-forge" is not automatable as written — "beats" is a judgement call. A blind coder will implement it as a filename match and mislabel everything. | Replaced with an explicit weighted score (AST substance + concept density + path signal + spine relationship). Thresholds are config, not code. |
| 3 | The plan grades *files*. Your actual goal — you said it yourself — is keeping **good ideas**, some of which live in bad files. A low-scoring doc can hold your best Overseer design. | Added `concepts.csv`, a concept→file ledger written for every file at every grade. Ideas survive independent of their file's score. |
| 4 | Phase 4 (diff vs spine) is described but has no output format, so nothing reaches Obsidian. | `diff_spine.py` emits `REPORT.md` with YAML frontmatter, written straight into the vault. Drift becomes a note, automatically. |
| 5 | The "first coder prompt" outsources Phase 1 to a model that, in your words, can't see the path. That's the failure you already had. | Phase 1–4 are written and tested. No coder bot needed until Phase 6. |

**Also:** `06_ARCHIVE_RAW` is marked "(optional)" in the plan. It is not
optional. It is the thing that lets you wipe the drive. Run it first.

---

## 2. What I built for you

Tested end-to-end against a synthetic messy tree. In that test it correctly:
promoted the richer `gate.py` to GOLD and flagged it as a **conflict** with the
spine version; marked a byte-identical copy DUP; quarantined a binary blob;
scored a stub file down to BRONZE; and left the spine and all originals
untouched (verified by mtime and file count).

```
sorter/
  config.yaml            paths, denylists, concept vocabulary, thresholds
  forgelib.py            Config, Record, SHA256, and the write-safety guard
  scan.py                Phase 1  — walk + hash → scan.jsonl
  archive_copy.py        Phase 1b — verbatim mirror → 06_ARCHIVE_RAW
  grade.py               Phase 2  — score → grades.csv + concepts.csv
  file_into_cabinet.py   Phase 3  — shelve copies + .grade.json sidecars
  diff_spine.py          Phase 4  — spine_diff.csv + Obsidian REPORT.md
  README.md              run order, threshold tuning, safety notes
```

The safety guard is the important part. Every write goes through
`assert_writable()`, which raises unless the target resolves inside the
cabinet, and raises again if it resolves inside the spine. Verified: it blocks
`the-forge/x.py` and blocks a home-directory path, allows only cabinet paths.

Copy them to `FORGE_CABINET/_WORK/sorter/` and follow the README.

---

## 3. Running the model on the GPU, not the CPU

Your current local model is on CPU. That's why it feels useless. Fix:

**The 16 GB VRAM constraint is the whole story.** An RTX 5080 Laptop has 16 GB
regardless of your 96 GB of system RAM — Ollama will happily spill a too-big
model into RAM and you're back on CPU speed. Pick a model that *fits*.

Current sensible picks for a 16 GB card, agentic-coding oriented
([ranking sources](https://localaimaster.com/blog/best-ollama-models),
[16 GB analysis](https://blog.laozhang.ai/en/posts/best-local-coding-llm-16gb-vram)):

| Model | Why | Pull |
|---|---|---|
| **gpt-oss:20b** | The community default for 16 GB; MoE, ~3.6 B active, adjustable reasoning effort. Start here. | `ollama pull gpt-oss:20b` |
| **qwen3-coder:30b** | Stronger at agentic multi-file work, 256 K context — but ~18 GB at Q4, so it will partially offload. Try it *second* and measure. | `ollama pull qwen3-coder:30b` |
| **devstral:24b** | Agent-first training, good at multi-file edits, ~15 GB. Good middle option. | `ollama pull devstral:24b` |

Verify it's actually on the GPU — this is the step people skip:

```powershell
ollama run gpt-oss:20b "hello"
ollama ps        # PROCESSOR column must read 100% GPU, not "45%/55% CPU"
nvidia-smi       # VRAM should jump ~12-14 GB
```

If `ollama ps` shows any CPU split, the model is too big. Drop to a smaller
quant or a smaller model. On Pop!_OS, set the knobs as a systemd drop-in — this
is the step that makes it stick across reboots:

```bash
sudo systemctl edit ollama
```

Add:

```ini
[Service]
Environment="OLLAMA_KEEP_ALIVE=30m"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_CONTEXT_LENGTH=16384"
Environment="OLLAMA_SCHED_SPREAD=0"
```

Then `sudo systemctl daemon-reload && sudo systemctl restart ollama`.

`OLLAMA_CONTEXT_LENGTH` matters more than the model choice. Asking for 128 K
context on a 16 GB card blows the KV cache into system RAM and silently drops
you back to CPU speed — that is the usual cause of "it was on GPU yesterday."
Start at 16384 and only raise it while watching `nvidia-smi`.

Pop!_OS specifics worth checking before you blame Ollama:

```bash
nvidia-smi                    # driver present? 5080 needs a recent one
ollama --version
sudo systemctl status ollama  # running as a service, not a stray terminal
```

If you're on the NVIDIA ISO of Pop!_OS the driver is already there. If you see
no GPU in `nvidia-smi`, that's the real problem and no Ollama setting fixes it.

You said keep the old model — fine, it costs only disk. Just make sure the new
one is the default you actually invoke, and confirm with `ollama ps` that the
old one isn't still resident eating VRAM (`ollama stop <oldmodel>` if it is).
A realistic expectation: a 16 GB local model is
good for scanning, grading, summarising, writing config and small modules. For
the Frankenstein merges in Phase 6, use a frontier model. Local for volume,
cloud for judgement.

**The 13 TOPS NPU:** ignore it entirely. Its tooling is Windows-oriented and
Linux NPU support for Intel's Meteor/Arrow Lake NPU is early and not useful for
LLM inference. On Pop!_OS it is effectively idle silicon. Not a loss — the 5080
is doing the work.

---

## 4. Obsidian as MCP + GitHub — how to actually wire it

Your instinct is right, but be precise about which repo holds what.

**Two repos, never one:**
- `the-forge` — code spine. Human commits only. Never let a plugin auto-commit here.
- `forge-vault` (new, **private**) — the Obsidian vault. Auto-commit welcome.

Mixing them means an Obsidian autosave every 10 minutes pollutes your code
history and destroys the "GitHub wins" rule.

**Vault git sync:** install the **Obsidian Git** community plugin, set
auto-commit to 10 minutes, auto-push on, auto-pull on start
([setup](https://studio-obsidian.com/backup-obsidian-vault/)). Add a
`.gitignore` with `.obsidian/workspace.json` and
`.obsidian/workspace-mobile.json` or you'll get noise commits forever.

**MCP:** install the **Local REST API** community plugin in Obsidian, copy its
API key, then register an Obsidian MCP server with your client
([mcp-obsidian](https://pypi.org/project/mcp-obsidian/)):

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": ["mcp-obsidian"],
      "env": { "OBSIDIAN_API_KEY": "<from the plugin>",
               "OBSIDIAN_HOST": "127.0.0.1" }
    }
  }
}
```

Pair it with a **filesystem MCP scoped to the cabinet only** and a **GitHub
MCP** for the four repos. Three servers, each narrow. Do not give a filesystem
MCP your whole drive — that is precisely how the mess happened.

**Vault structure that stays useful:**

```
forge-vault/
  00 Inbox/            unsorted capture
  10 Spine/            STATUS, LOCKED decisions, architecture (mirrors forge-os-core)
  20 Cabinet/          auto-dropped REPORT.md from diff_spine.py
  30 Concepts/         one note per concept: Gate, Overseer, Kernel, Codex, Finding
  40 Daily/            daily notes
  90 Archive/
```

`30 Concepts/` is the payoff. Each concept note links to the GOLD/SILVER files
in `concepts.csv` that implement it. That's your "keep the very good ideas even
if the code is worse than what's built" requirement, made navigable.

**Automation (Pop!_OS, systemd user timer — no root, no cron):**

`~/.config/systemd/user/forge-sweep.service`:

```ini
[Unit]
Description=Forge cabinet weekly sweep

[Service]
Type=oneshot
WorkingDirectory=%h/FORGE_CABINET/_WORK/sorter
ExecStart=/usr/bin/python3 scan.py --config config.yaml
ExecStart=/usr/bin/python3 grade.py --config config.yaml
ExecStart=/usr/bin/python3 diff_spine.py --config config.yaml --vault %h/Obsidian/ForgeOS
```

`~/.config/systemd/user/forge-sweep.timer`:

```ini
[Unit]
Description=Run Forge cabinet sweep weekly

[Timer]
OnCalendar=Sun 09:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable it:

```bash
systemctl --user daemon-reload
systemctl --user enable --now forge-sweep.timer
systemctl --user list-timers forge-sweep.timer   # confirm next run
loginctl enable-linger $USER                     # runs even when logged out
```

Note the sweep deliberately omits `archive_copy.py` and
`file_into_cabinet.py` — automated *reporting* is safe, automated *copying* of
a drive you're still reorganising is not. Run those two by hand.

Obsidian Git commits the new report on its next cycle. Drift becomes visible
without you doing anything.

---

## 5. Sources of truth — my ranking

The ranking you were given is correct in shape. One correction and one addition:

| Rank | Source | Role | Note |
|---|---|---|---|
| 1 | `github.com/munnchue-gif/the-forge` (`master`) | **Code spine** | Only living fabric. GitHub wins over local, always. |
| 2 | `github.com/munnchue-gif/forge-os-core` | STATUS / LOCKED decisions | *Mirror these into the vault `10 Spine/`, don't retype them.* |
| 3 | `github.com/munnchue-gif/forge-copilot` | Handoff / continuity protocol | |
| 4 | `github.com/munnchue-gif/coder-context` | Creation blocks / prompts (private) | |
| 5 | `~/the-forge` | Local checkout of #1 | Must equal #1 after `git pull`. |
| 6 | `~/.forge/` | Runtime only | Socket + local state. Not source. Never graded. |
| — | **`FORGE_CABINET/00_MANIFEST/`** | **Source of truth about *the mess*** | Added. The manifests are authoritative for "what existed on this drive." Once they're committed to the vault repo, the raw folders are disposable. |

The conflict rule you need in writing, because it's what actually protects you:

> If GitHub `the-forge` and `~/the-forge` disagree → GitHub wins until you
> intentionally commit. If the cabinet and `the-forge` disagree → `the-forge`
> wins, and the cabinet file is a *recovery candidate*, never an auto-merge.

Nothing is ever promoted from cabinet to spine by a script. Human-led, one
module at a time, through Creation Blocks in `coder-context`.

---

## 6. seL4

Right to defer, and here's the honest framing: seL4 is a **formally verified
microkernel**, not a distro. Adopting it means building a userland — drivers,
init, IPC plumbing — on CAmkES or Microkit. It is a months-of-work substrate
project, and it is not going to host Ollama or Obsidian.

The realistic path: keep Pop!_OS as your workstation, and treat seL4 as the
**future isolation target** you design *toward*. Concretely, that means your
Gate/Overseer/capability model should map onto seL4 capabilities cleanly — so
when you get there, the architecture ports instead of being rewritten. Write
that as a LOCKED decision in `forge-os-core` now; build nothing on it yet.

---

## 7. Your next three moves

Confirmed: **Pop!_OS**, first root **`~/forge-spine`**, new model straight onto
GPU VRAM. Run `bootstrap.sh` — it does steps 1 and 2 for you.

1. **Freeze the spine:**
   `git -C ~/the-forge pull origin master && git -C ~/the-forge status`
   Working tree clean = good. Do not proceed if it's dirty.
2. **Build the cabinet and install the sorter:**
   ```bash
   bash bootstrap.sh
   ```
   Creates all eight shelves, copies `sorter/` into `_WORK/sorter/`, installs
   pyyaml if missing, and verifies the write-safety guard actually blocks.
3. **First scan, one root, nothing filed:**
   ```bash
   cd ~/FORGE_CABINET/_WORK/sorter
   python3 scan.py --config config.yaml --root ~/forge-spine
   head -n 10 ~/FORGE_CABINET/00_MANIFEST/scan.jsonl
   python3 archive_copy.py --config config.yaml --dry-run
   ```
   Bring me the summary lines and those ten JSONL lines. We tune thresholds on
   real data before a single file is shelved in bulk.

Do not wipe a single folder until `06_ARCHIVE_RAW` exists and `grades.csv` has
been read by a human. The archive is the permission slip for the wipe.
