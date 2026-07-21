# 21 · The Embedded Tailor (the model ON the metal)

Parent: [[00_FORGE_CONCEPT_MAP]] · the missing organ of [[20_The_Wardrobe]]

## The idea (this is the big new one)
There needs to be an **actual model EMBEDDED on the system** whose whole job is
the wardrobe loop: **take suits apart, pull the data out, and tailor a new suit
for the next model** from those parts.

- Embedded = part of the bare metal, spawned AFTER the Forge itself is built.
- **Upgradeable** — Eugene expects to swap/upgrade this model over time; it's an
  important part, so it shouldn't be frozen.
- NOT trained in the normal way. Instead: **take the world's training data and
  "lose it in our own fashion"** — reshape it our way (see [[30_Our_Own_Data]]).

## Why embedded (vs a capsule model)
Because it operates ON the wardrobe/suits themselves — it's infrastructure, not
a workload. It's the tailor in the back of the shop, always there, cutting parts
into new suits. Ties to the NPU "shaping brain" (conduit Level 3): the brain that
pre-shapes new wraps from experience.

## Decisions to make (parked, not now)
- Spawn it after bare-metal Forge boots? (Eugene leans yes.)
- Which model to start with, and the upgrade path.
- Does it run on the NPU (bonded brain) or the RTX (workload)? Likely NPU-side,
  since it "knows everything and bridges memory of what goes where."
