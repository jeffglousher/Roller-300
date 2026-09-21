# Native → JSONC port tracking

Repo is the SoT for location and progress. CAD/MCP sessions are transitory.

## Native master
- File: `../../Roller-300.nbcad`
- Review meshes: `../../first-prints/shell-first-review/`
- Coupons: `../../first-prints/coupons/`
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
4. Blank-doc replay + export under `first-prints/` only after inspect matches native bounds.

## Status
- Inventory done (`body-inventory.json`).
- **Carriage dump done**: `left_input_carriage-97.json` + `left_input_carriage-97.md` (body 97 feature sequence, sketches, VERIFY gaps, AABB vs review STL).
- **Next**: JSONC rebuild of left_input_carriage from the dump (still no invented geometry).
