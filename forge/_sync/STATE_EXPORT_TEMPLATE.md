# STATE EXPORT TEMPLATE (both sides use this format)

> When either side finishes work, fill this out and paste it into the SYNC LOG of
> `FORGE_STATE_SYNC.md`. Keeping the shape identical lets us diff cleanly.

```json
{
  "state_export": {
    "generated_by": "Fable5 | Solene",
    "generated_utc": "<ISO timestamp>",
    "codebase": "forge_ng",
    "tests": { "passing": 0, "failing": 0 },
    "package": { "exports": 0, "version": "0.1.0" },

    "changed_since_last_sync": [
      { "component": "<name>", "what": "<what you did>", "files": ["path/one.py"], "tests_added": 0 }
    ],

    "capsule_map_updates": [
      { "id": "<organ/capsule>", "status": "GREEN|YELLOW|ORANGE|RED|PURPLE", "arch": "NPU|GPU|CPU", "note": "" }
    ],

    "gap_analysis": [
      { "component": "<name>", "grade": "RED|ORANGE|YELLOW", "severity": "", "snip": "<why it's unstable>", "owner": "" }
    ],

    "next": ["<next task 1>", "<next task 2>"],
    "needs_eugene": ["<any trust-boundary / core-concept decision that needs the human>"],
    "questions_for_other_side": ["<anything you want Solene/Fable5 to answer>"]
  }
}
```

**Grade key:** 🟢 GREEN solid · 🟡 YELLOW needs a look · 🟠 ORANGE needs custom work ·
🔴 RED weak/unstable · 🟣 PURPLE revolutionary/seed.
