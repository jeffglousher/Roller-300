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

## wheel-cap-inner / wheel-cap-outer

| Item | Inner | Outer |
|------|-------|-------|
| Role | `wheel_cap_inner` | `wheel_cap_outer` |
| Native body | **56** | **65** |
| Chapter | `design/design_v0_1_wheel_caps.nbcad.jsonc` | same |
| Dump | `design/native-port/wheel_cap_inner-56.*` | `wheel_cap_outer-65.*` |
| Exports | `wheel-cap-inner.{3mf,stl}` | `wheel-cap-outer.{3mf,stl}` |
| AABB | X-25–25 Y45–57 Z123.3–140 → **50×12×16.7** | X-25–25 Y93–105 Z123.3–140 → **50×12×16.7** |
| Review STL | `shell-first-review/wheel-cap-inner-assembly-coordinates.stl` | `.../wheel-cap-outer-assembly-coordinates.stl` |

Extrude25/33 M4: wheel-caps chapter cuts 56/65; shell chapter owns body 32. No combine/recess/mirror on these bodies.

See `_export_report.json` for the last export run.

## main-shell

| Item | Value |
|------|--------|
| Role | `main_shell` |
| Native body | **32** |
| Chapter | `design/design_v0_1_barrel_shell.nbcad.jsonc` (VERSION 0.1) |
| Dump | `design/native-port/main_shell-32.md` + `.json` |
| Generator | `tools/dump_to_jsonc.py` |
| Exports | `main-shell.3mf`, `main-shell.stl` (body 1 only; Combine12 keep_tools leftovers omitted) |
| AABB (replay, w/ Combine16) | X[-79.926,80] Y[-105,105] Z[43.019,202.981] → **~159.93 × 210 × 159.96** |
| AABB review | **159.95 × 210 × 159.98** @ mins (-79.95, -105, 43.01) (`shell-first-review/main-shell-assembly-coordinates.stl`) |

Assemble-order blank-doc: shell through Combine3 → hatch → shell remainder + **Combine8** + **Combine16**. Outer envelope matches review (Combine5 already opens aperture; Combine16 keeps hatch tool). Standalone barrel_shell chapter still skips hatch-only ops.

## curved-hatch

| Item | Value |
|------|--------|
| Role | `hatch` |
| Native body | **141** |
| Chapter | `design/design_v0_1_structural_hatch.nbcad.jsonc` (VERSION 0.1) |
| Dump | `design/native-port/hatch-141.md` + `.json` |
| Generator | `tools/dump_to_jsonc.py --role hatch` |
| Exports | `curved-hatch.3mf`, `curved-hatch.stl` (body after Combine14) |
| AABB (replay / native) | X[-69,69] Y[-89.7,89.7] Z[123,202.932] → **138 × 179.4 × 79.932** |
| AABB review STL (trimmed) | X-69–69 Y-89.7–89.7 Z154.859–202.952 → **138 × 179.4 × 48.0928** (`shell-first-review/curved-hatch-assembly-coordinates.stl`) |

Replay (A): blank doc → barrel_shell through Combine3 → hatch chapter (or assemble-order with Combine16). XY match. **Z CLOSED**: native Extrude88 @ Z123 + Combine3 shoulders → tall solid matches dump; review STL zmin 154.859 is trimmed ID-R76 chord at |X|=69 (`123+sqrt(76²-69²)`) — do not invent cuts. Combine16 applied in assemble-order for main-shell opening.