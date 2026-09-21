# Native → JSONC port tracking

Repo is the SoT for location and progress. CAD/MCP sessions are transitory.

## Native master
- File: `../../Roller-300.nbcad`
- Review meshes: `../../first-prints/shell-first-review/`
- Coupons: `../../first-prints/coupons/`
- Native-port exports: `../../first-prints/native-port/` (dump-derived JSONC replay)
- Failed placeholder path: `../../first-prints/one-drive/DEPRECATED.md`

## Target bodies (left drive / shared)
| Role | Body ID |
|------|---------|
| main_shell | 32 |
| left_input_carriage | 97 |
| input_cap_inner | 100 |
| input_cap_outer | 108 |
| wheel_cap_inner | 56 |
| wheel_cap_outer | 65 |
| hatch | 141 |

## Method
1. Inventory native `model.json` (see `body-inventory.json`).
2. Dump one body at a time (features/sketches/datums) under `design/native-port/`.
3. Port from that dump into `design/design_v0_1_<role>.nbcad.jsonc` with Design Ops naming/refs — **no invented geometry**.
4. Blank-doc replay + export under `first-prints/native-port/` only after inspect matches native bounds.

## Status
- Inventory done (`body-inventory.json`).
- **Carriage dump + JSONC**: `left_input_carriage-97.{json,md}` → `design/design_v0_1_input_carriage.nbcad.jsonc` — AABB **39×100×35** @ 30/2/88. Exports: `first-prints/native-port/left-input-carriage.*`.
- **Caps dump + JSONC**: `input_cap_inner-100.{json,md}` + `input_cap_outer-108.{json,md}` → `design/design_v0_1_input_caps.nbcad.jsonc` — Extrude65/66/67 + Extrude72/73/74 + Extrude144/Combine17–18 + Extrude145 (skip Mirror2). Blank-doc AABB inner **39×8×17.7** @ 30/66/123.3; outer **39×8×17.7** @ 30/92/123.3. Exports: `first-prints/native-port/input-cap-{inner,outer}.*`.
- **Wheel caps dump + JSONC**: `wheel_cap_inner-56.{json,md}` + `wheel_cap_outer-65.{json,md}` → `design/design_v0_1_wheel_caps.nbcad.jsonc` — Extrude23/24/25 + Extrude31/32/33 (skip shell cuts). Blank-doc AABB inner **50×12×16.7** @ -25/45/123.3; outer **50×12×16.7** @ -25/93/123.3. Exports: `first-prints/native-port/wheel-cap-{inner,outer}.*`.
- **Next**: hatch 141 and/or main_shell 32.
