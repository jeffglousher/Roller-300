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
cuts (native Extrude67/74 also hit caps 100/108 — caps chapter owns those cuts).

## input-cap-inner / input-cap-outer

| Item | Inner | Outer |
|------|-------|-------|
| Role | `input_cap_inner` | `input_cap_outer` |
| Native body | **100** | **108** |
| Chapter | `design/design_v0_1_input_caps.nbcad.jsonc` | same |
| Dump | `design/native-port/input_cap_inner-100.*` | `input_cap_outer-108.*` |
| Exports | `input-cap-inner.{3mf,stl}` | `input-cap-outer.{3mf,stl}` |
| AABB | X30–69 Y66–74 Z123.3–141 → **39×8×17.7** | X30–69 Y92–100 Z123.3–141 → **39×8×17.7** |
| Review STL | `shell-first-review/input-cap-inner-assembly-coordinates.stl` | `.../input-cap-outer-assembly-coordinates.stl` |

Shared Extrude67/74 M3: caps chapter cuts 100/108; carriage chapter cuts 97.
Extrude144 + Combine17/18 corner-limit; Extrude145 recessed heads (left-only).

See `_export_report.json` for the last export run.
