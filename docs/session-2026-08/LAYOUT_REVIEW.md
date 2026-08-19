# Review of the returned BUILD LAYOUT

**Verdict: sections A–C are usable with three corrections. Section E is wrong
and must be rejected. Section D contains one impossibility, one strong idea,
and one that needs a caveat.**

---

## ✅ What it got right

- **Bus first.** Correct. It is the nervous system, and Shift 5's
  Watcher/Commander wall is impossible without SubKernelBus namespaces.
- **Sandbox second.** Correct, and it closes M4 finding B (stripper isolation)
  as a side effect.
- **Gate third.** Correct — PathwayRegistry is the pre-declaration the whole
  proactive model rests on.
- **Every "DONE" is a real falsifiable test.** *"A process inside the sandbox
  cannot read FORGE_STATE.md on the host"* is exactly the right shape.
- **It respected the GAP instruction.** It marked blocks rather than inventing
  answers. That is the behaviour that prevents a fifth hopper.

---

## ❌ SECTION E IS WRONG — reject it

> *"Cut SubKernelBus and rely purely on the Gate for enforcement."*

Four reasons this fails:

### 1. It contradicts its own Brief 1

Two pages earlier the same document says:

> *"STAKES: Without this, the physical cryptographic deafness between the
> Overseer and Commander (Shift 5) is impossible."*
> *"DONE: Test proving a publisher on SubKernelBus A cannot be heard by a
> subscriber on SubKernelBus B."*

It built the case for the bus, then recommended cutting it. Internal
contradiction in one deliverable.

### 2. It breaks Shift 5 entirely

The Watcher/Commander wall **is** SubKernelBus deafness. Cut it and the
Overseer can hear the Commander's channel. Law 3 — *watching ≠ acting* —
degrades from a physical property back to a convention. That is the exact
regression the splice was built to prevent.

### 3. It confuses two different threats

The argument is *"a rogue twin still cannot act without the Gate."* True for
**acting**. Irrelevant for **hearing**.

The Gate stops unauthorized *action*. The bus stops unauthorized *observation*.
A twin that hears everything but acts on nothing is still a total
confidentiality failure — twins are deliberately compartmented so one cannot
learn what another is doing. Removing the wall means every twin sees every
other twin's work.

**And your own M4 reviewer flagged this exact surface as Risk #2:**

> *"SubstanceBus sharding + Overseer omnipresence = covert channel... a
> compromised organ could modulate its queue behavior (timing, padding) to
> signal another. With remote couplers, this becomes exfiltration path #1."*

The recommendation is to delete the mitigation for a risk that was
independently identified two months ago.

### 4. The complexity claim is measurably false

It calls the bus *"complexity cost on the internal hot path."* But your live
bus is **95 lines** and the recovered variant is **383** — and that 383
includes DLQ overflow and two-phase teardown, which fix the weakness *your own
Graded Master List* recorded: *"drops silently under load; not thread-safe."*

That is not cognitive weight. It is the fix for a known defect.

**Correct reading:** Gate = authority. Bus = confidentiality. Different
properties, both required. Defence-in-depth is not redundancy when the two
layers stop different things.

---

## ⚠️ SECTION D — one impossible, one strong, one caveated

### D1 · Hardware enclaves (SGX/TDX) — **not available to you**

Intel **deprecated SGX on consumer CPUs** starting with 11th/12th gen; it
survives only on Xeon for cloud and enterprise.
[[Wikipedia]](https://en.wikipedia.org/wiki/Software_Guard_Extensions)
[[Intel]](https://www.intel.com/content/www/us/en/support/articles/000089326/software/intel-security-products.html)
Your Core Ultra 9 275HX is a client part. **SGX is not there.** TDX is
Xeon-only.

Also worth knowing before anyone chases this: SGX's history is a long list of
breaks — Foreshadow, SGAxe, ÆPIC Leak, Plundervolt, and a Root Provisioning Key
extraction.

**Verdict: strike it.** Your `bwrap --unshare-all` + `systemd-run` cgroups is
the right isolation primitive for this hardware, and your M4 reviewer already
asked the same question — *"is splicing doing something namespaces + seccomp
couldn't do more simply?"* — which your `FabricSandbox` answers with: no, it
uses namespaces.

### D2 · Ephemeral tmpfs for rendered organs — **strong, take it**

This is genuinely good and fits Shift 1 exactly. Organs render into RAM, the
task runs, flatten zeroes the tmpfs. No forensic residue on the NVMe. Vectors
and snips still persist because those go to the keychain deliberately.

One correction to its cost note: it says *"RAM pressure, already tight with
16GB VRAM."* **You have 93 GB of system RAM.** VRAM and system RAM are separate
pools. tmpfs lives in system RAM, where you have enormous headroom. The cost is
close to zero on this machine.

### D3 · Verifiable snip provenance — **right instinct, wrong mechanism**

Zero-knowledge proof of inference is research-grade and would add minutes per
eject. But the underlying concern is real: a snip pulled from the boneyard
months later should be verifiable.

Cheaper answer that fits your existing house style: **hash-chain snips into the
AuditLedger** at splice time, exactly as `H_i = Hash(seq ‖ ts ‖ payload ‖
H_{i-1})` already does for gate decisions. Tamper-evident, effectively free,
and reuses an organ that already has 8 passing tests.

---

## 🔧 Three corrections to A–C

### Correction 1 · The capsule format is last. It should be first.

The layout puts it at **#12, blocked by G7**. But Shift 2 makes it the contract
everything conforms to:

> *"the capsule format is the most important contract in the system"*

Building Keychain (#6) before the capsule format means the Keychain's resume
records are designed against an undefined artifact. Same for Boneyard and
Sockets.

G7 is not a blocker that must clear before work starts — **it is the first
design decision.** It needs a specification, not an implementation, and
specifying it unblocks four other pieces.

**Move capsule format to position 1.** Spec only, no code.

### Correction 2 · Hopper is not blocked by G6

The layout blocks Hopper on *"what does the Copilot decide alone?"* That is a
false dependency.

The Hopper **sorts work; it never executes and never calls the Gate.** It does
not care who posts tasks or who decides organ composition. A copilot posting
tasks and a human posting tasks look identical to it.

Hopper is blocked by nothing. It can be built now, and it should be — it is the
piece that makes 50 agents possible.

### Correction 3 · Keychain's stakes are wrong

The layout says: *"necessary for the Forge to authenticate with external
services."* That is a credential store. That is not what you described.

Your definition:

> *"it's not the model that I need, it's plugging the model back in so it knows
> where it's at to do these tasks again or to finish something."*

The Keychain is the **resume point** — what to pull, in what shrunk form, to
put a capsule back exactly where it left off. Its stakes are *flatten-and-
recycle is impossible without it*, not *external auth*.

The layout is describing a keyring. You designed a bookmark.

---

## Corrected build order

| # | Piece | Change |
|---|---|---|
| 1 | **Capsule format spec** | ⬆ moved from #12 — the contract, spec only |
| 2 | bus.py + SubKernelBus | unchanged — and **not** cut |
| 3 | FabricSandbox | unchanged |
| 4 | gate.py PathwayRegistry | unchanged |
| 5 | **Hopper** | ⬆ moved from #8 — G6 was a false dependency |
| 6 | splicing_engine | still blocked by G1 (what is a snip) |
| 7 | Keychain | stakes rewritten: resume point, not keyring |
| 8 | security_guardian | review before port |
| 9 | Copilot | genuinely blocked by G6 |
| 10 | Toolchain | blocked by G3 |
| 11 | Boneyard | blocked by G5 |
| 12 | Sockets-with-memory | blocked by G2 |
| 13 | Surface | last, correct |

Plus **tmpfs organ rendering** folded into #3 as an implementation detail.

---

## The meta-lesson

Section E is a good example of the failure this whole project exists to
prevent. The model had Law 2 and Shift 5 in its context, wrote a correct brief
citing both, then two sections later recommended deleting the mechanism that
implements them — because in isolation the argument *"routing is not
authority"* sounds clean.

**It optimised a subsystem against a principle from a different subsystem.**

That is why `FORGE_STATE.md` §1 exists and why the pre-commit hook enforces it.
A locked decision is not advice. When a model proposes cutting one, the answer
is no unless *you* unlock it first — with a date and a reason.
