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
- **Hatch dump + JSONC**: `hatch-141.{json,md}` → `design/design_v0_1_structural_hatch.nbcad.jsonc` (via `tools/dump_to_jsonc.py --role hatch`). MoveCopy5→Extrude88∩Combine4→Extrude96/pattern/mirror/Combine13→Revolve1/pattern/mirror/Combine14. Replay (A): shell chapter `--max-fid 290` then hatch (or `--embed-shell`). Blank-doc AABB **138×179.4×79.932** @ mins (-69,-89.7,123) — **XY match**; **Z CLOSED** (native tall matches Extrude88@Z123; review **138×179.4×48.0928** @ zmin 154.859 is trimmed ID-chord export). Legacy coupons removed from steps (README only). Exports: `first-prints/native-port/curved-hatch.*`.
- **main_shell dump + JSONC**: `main_shell-32.{json,md}` → `design/design_v0_1_barrel_shell.nbcad.jsonc` (via `tools/dump_to_jsonc.py`). Skip MoveCopy5/Combine8/Combine16 (hatch 141). Assemble-order AABB **~159.93×210×159.96** @ mins (-79.93, -105, 43.02) with Combine16 applied. Review: **159.95×210×159.98** @ (-79.95, -105, 43.01). Exports: `first-prints/native-port/main-shell.*`. Saddle coupon chapter replaced; coupons under `first-prints/coupons/`.

- **Next**: electronics_mounts / drive_stack native-port (hatch Z + Combine16 VERIFYs closed).
