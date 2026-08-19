# Verdict on the Gemini stack advice

## The one that doesn't work: Cursor + local Ollama

Gemini (Choice A) says:

> *"Disable all cloud providers. Add your local Ollama endpoint. Set the API
> Base URL to http://127.0.0.1:11434/v1"*

**This cannot work.** Cursor does not call your Base URL from your machine —
it routes every request through its own cloud backend, so `127.0.0.1` resolves
to *Cursor's server's* loopback, not yours. The chat just hangs and your Ollama
logs stay empty.
[[dev.to]](https://dev.to/orchidfiles/why-localhost-doesnt-work-as-openai-base-url-in-cursor-and-how-to-fix-it-589e)

To make it work you must expose Ollama on a **public HTTPS tunnel**
(Cloudflare Tunnel / ngrok). Which means:

- your "local, private, isolated" model is now reachable from the internet
- you still need an active internet connection — local inference ≠ offline
  [[60minuteapps]](https://60minuteapps.com/blog/cursor-with-local-llm/)

And even then, per Cursor's own docs and forum staff:

| Feature | Works with local model? |
|---|---|
| Chat / Cmd+K | yes |
| **Tab autocomplete** | **no — always cloud** |
| **Composer models** | **no — "Composer models don't work with BYOK keys"** [[forum.cursor.com]](https://forum.cursor.com/t/composer-2-5-error-this-model-does-not-support-custom-api-keys/163374) |
| Embeddings / code indexing | no — Cursor's own pipeline |

There was also a live bug where the model field got dropped on the
OpenAI-compatible path, breaking agent mode with Ollama entirely; Cursor staff
confirmed it and it took ~2 months to fix.
[[forum.cursor.com]](https://forum.cursor.com/t/gent-mode-with-openai-base-url-override-sends-request-without-model-model-is-required/160070)

**For your project this is disqualifying.** The entire point is isolation and
not leaking your architecture. Tunnelling your model to the public internet so
a third-party cloud can proxy into it is the opposite.

**Use instead: VS Code + Continue.dev.** Continue calls `localhost:11434`
directly from your machine. No tunnel, no cloud hop, genuinely offline.
Gemini's Choice B lists this as the "100% open-source" option — it's actually
the *only* one that satisfies your requirement.

---

## The dangerous one: rclone bisync over git

Gemini says run a daily `rclone bisync` of your local git directories to Drive.

**Do not sync `.git` directories with any cloud sync tool.** This is a
well-known corruption source across Proton/OneDrive/Dropbox/Drive — git's
object store is many small files written in a specific order, and sync tools
interleave them.
[[reddit]](https://www.reddit.com/r/ProtonDrive/comments/1smpouf/i_spent_hours_repairing_a_git_repository_that/)

rclone's own bisync docs are blunt: *"Bisync is considered an advanced
command... make sure you have read and understood the entire manual (especially
Limitations) before using, or data loss can result."* Files that change during
a run may be lost, and critical errors lock out future runs until you `--resync`.
[[rclone docs]](https://github.com/rclone/rclone/blob/master/docs/content/bisync.md)

**Correct pattern — and Gemini half-said this:**

- **GitHub is the sync mechanism for anything in git.** `push`/`pull` *is* the
  sync. Don't add a second one.
- Use Drive only for things git is bad at: `06_ARCHIVE_RAW`, big binaries,
  model files, PDFs.
- If you must sync a repo folder, exclude the git internals:
  `--exclude '.git/**'` — or better, `git bundle` it into one file and sync that.

---

## The honest one: seL4

Gemini's two answers contradict each other. **Choice B is correct:**

> *"using it as a daily-driver desktop hypervisor to pass through hardware for
> local LLMs and run modern GUIs is a massive bare-metal engineering
> undertaking"*

Choice A's Genode/Sculpt suggestion is real software, but it won't give you
NVIDIA CUDA passthrough for Ollama on a 5080. That's the blocker, and no
prompt-generated installer guide will produce it.

Matches what your own Kimi review already told you: **don't distro-hop, the
5080 friction is distro-agnostic.** Your NPU works now. Leave the kernel alone.

---

## The model pick

Gemini says `ollama pull deepseek-coder-v2` without noting there are two:
the **16B lite** (fits your 16 GB) and the **236B** (does not, by a factor of
~10). If you pull the wrong tag you'll spend an hour wondering why it's on CPU.

Stick with what fits: `gpt-oss:20b` or `qwen2.5-coder:7b` (which you already
have loaded in codex). And set the context window — Ollama defaults to 4k–8k,
and silently drops earlier context, producing confident garbage:

```bash
OLLAMA_CONTEXT_LENGTH=16384
```

---

## The corrected stack

| Layer | Use | Not |
|---|---|---|
| Editor | **VS Code + Remote-SSH** | Cursor (cloud-routed) |
| AI in editor | **Continue.dev** → `localhost:11434` | Cursor Composer |
| Model | `gpt-oss:20b`, ctx 16384 | `deepseek-coder-v2` (ambiguous tag) |
| Isolation | **`grid.py`** (built, tested) + optional `systemd-run --scope` | seL4/Genode |
| Code sync | **git push/pull** | rclone bisync of `.git` |
| Notes | Obsidian + Obsidian Git → private repo | vault inside a mounted Drive |
| Bulk/archive | rclone to Drive, `--exclude '.git/**'` | bisync |

---

## What Gemini got right

- Obsidian vault in a **local git repo**, not inside the mounted Drive — correct
- Obsidian Git plugin auto-commit — correct
- Hub-and-spoke, one source of truth — correct, and it's what `FORGE_STATE.md` does
- Ollama as the local daemon — correct
- rclone as *the* Linux Drive tool — correct (just not bisync over git)
- **Choice B's honesty about seL4** — correct, and worth more than Choice A's enthusiasm

The structure of its advice is good. The two specific instructions that would
have cost you a weekend are the Cursor localhost setup and bisync over git.
