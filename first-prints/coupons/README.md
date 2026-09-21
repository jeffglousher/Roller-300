# first-prints/coupons/

STL/3MF exports from Design Ops coupon chapters under `design/`.

**Exported:** 2026-09-20 16:23 CT (S01/S02 coupons), 16:26 CT (structural_hatch), and 16:30 CT (electronics_mounts) via headless `nbcad-mcp` (`cad_new_project` → `cad_interface` script path → `solid_export_preflight` → `solid_export_3mf` + `solid_export_stl`). Base commit for scripts: `3de1868`.

Prefer **3MF** for slicers; STL is the same geometry fallback. All seats are **TRIAL** — not released fits. See PLAN S05.

## Exports

| File | Source chapter | Replay | Notes |
|------|----------------|--------|-------|
| `608-seat-coupon.3mf` / `.stl` | `design/design_v0_1_hardware_refs.nbcad.jsonc` | OK (47 steps) | Body1 — plate ~40×40×8; trial D22.2×7.2 seat + D18 through |
| `m4-nut-coupon.3mf` / `.stl` | same | OK | Body4 — M4 captive-nut AF 7.3 × depth 3.5 trial |
| `wheel-seat-saddle-coupon.3mf` / `.stl` | `design/design_v0_1_barrel_shell.nbcad.jsonc` | OK (28 steps) | Single body saddle coupon |
| `carriage-rail-slot-coupon.3mf` / `.stl` | `design/design_v0_1_input_carriage.nbcad.jsonc` | OK (18 steps) | Rail slot travel coupon |
| `hatch-lap-m4-coupon.3mf` / `.stl` | `design/design_v0_1_structural_hatch.nbcad.jsonc` | OK (62 steps) | Developed lap_mm 8 + gap 0.3 + M4 AF7.3×3.5 trial |
| `hatch-panel-arc-coupon.3mf` / `.stl` | same | OK | R76→R80 × Y±20 × 35° skin envelope (no fasteners) |
| `pi-shelf-standoff-coupon.3mf` / `.stl` | `design/design_v0_1_electronics_mounts.nbcad.jsonc` | OK (91 steps) | Body1 — Pi Zero bare 65×30 shelf + corner standoffs (nominal) |
| `pixracer-shelf-coupon.3mf` / `.stl` | same | OK | Body6 — 36×36 footprint recess (height UNMEASURED) |
| `tof-rail-coupon.3mf` / `.stl` | same | OK | Body8 — 20×12 locating channel (depth null) |
| `battery-allowance-tray-coupon.3mf` / `.stl` | same | OK | Body10 — open tray inner 85×30; Z=90 UNMEASURED |
| `thermal-envelope-shelf-coupon.3mf` / `.stl` | same | OK | Body12 — TOPDON TC002C Duo 71×42 nominal; aperture HOLD |

`design_v0_1_drive_stack.nbcad.jsonc` skipped for print export (envelope only). `design_v0_1_structural_hatch.nbcad.jsonc` lap coupon is print-today TRIAL; panel-arc is envelope-only. `design_v0_1_electronics_mounts.nbcad.jsonc` shelves/tray are print-today TRIAL/allowance coupons — not claimed 3D fits.

## Replay notes

- Always blank document (`cad_new_project`); never replay over a non-blank doc.
- Attach writeback must stay false when driving a live desktop.
- Cursor MCP `user-nobs-cad` can replay via absolute Linux path under the agent workspace; Thunder Windows path was not readable from this MCP process. Local stdio binary: `/home/box/.local/share/nbcad/mcp/nbcad-mcp`.
