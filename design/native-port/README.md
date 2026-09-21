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
2. Port one body at a time into `design/design_v0_1_<role>.nbcad.jsonc` with Design Ops naming/refs.
3. Blank-doc replay + export under `first-prints/` only after inspect matches native bounds.
4. Never invent block geometry that is not derived from native feature params.

## Status
- Inventory generated from current native master.
- Next port target: **left_input_carriage (97)**.
