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
- **Carriage dump done**: `left_input_carriage-97.json` + `left_input_carriage-97.md`.
- **Carriage JSONC rebuilt**: `design/design_v0_1_input_carriage.nbcad.jsonc` — Extrude62→86 (skip Mirror2), blank-doc replay AABB **39×100×35** @ mins 30/2/88. Exports: `first-prints/native-port/left-input-carriage.{3mf,stl}`.
- **Next**: input caps 100/108 (for shared M3 Extrude67/74) and/or next body from inventory.
