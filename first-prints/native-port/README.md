# Native-port first prints

Meshes here are **replayed from Design Ops JSONC chapters that were ported from
`design/native-port/` dumps** of `Roller-300.nbcad` — **not** from the deprecated
`first-prints/one-drive/` placeholder blocks.

## left-input-carriage

| Item | Value |
|------|--------|
| Role | `left_input_carriage` |
| Native body | **97** |
| Chapter | `design/design_v0_1_input_carriage.nbcad.jsonc` (VERSION 0.1) |
| Dump | `design/native-port/left_input_carriage-97.md` + `.json` |
| Exports | `left-input-carriage.3mf`, `left-input-carriage.stl` |
| AABB | X 30–69, Y 2–102, Z 88–123 → **39 × 100 × 35** (matches `shell-first-review/left-input-carriage-assembly-coordinates.stl`) |

Blank-doc replay via nbcad-mcp; Mirror2 skipped (left-only). Carriage-only M3
cuts (native Extrude67/74 also hit caps 100/108 — deferred).

See `_export_report.json` for the last export run.
