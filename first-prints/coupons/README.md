# first-prints/coupons/

STL/3MF exports from Design Ops coupon chapters under `design/`.

**Exported:** 2026-09-20 16:23 CT via headless `nbcad-mcp` (`cad_new_project` → `cad_interface` script path → `solid_export_preflight` → `solid_export_3mf` + `solid_export_stl`). Base commit for scripts: `3de1868`.

Prefer **3MF** for slicers; STL is the same geometry fallback. All seats are **TRIAL** — not released fits. See PLAN S05.

## Exports

| File | Source chapter | Replay | Notes |
|------|----------------|--------|-------|
| `608-seat-coupon.3mf` / `.stl` | `design/design_v0_1_hardware_refs.nbcad.jsonc` | OK (47 steps) | Body1 — plate ~40×40×8; trial D22.2×7.2 seat + D18 through |
| `m4-nut-coupon.3mf` / `.stl` | same | OK | Body4 — M4 captive-nut AF 7.3 × depth 3.5 trial |
| `wheel-seat-saddle-coupon.3mf` / `.stl` | `design/design_v0_1_barrel_shell.nbcad.jsonc` | OK (28 steps) | Single body saddle coupon |
| `carriage-rail-slot-coupon.3mf` / `.stl` | `design/design_v0_1_input_carriage.nbcad.jsonc` | OK (18 steps) | Rail slot travel coupon |

`design_v0_1_drive_stack.nbcad.jsonc` skipped for print export (envelope only).

## Replay notes

- Always blank document (`cad_new_project`); never replay over a non-blank doc.
- Attach writeback must stay false when driving a live desktop.
- Cursor MCP `user-nobs-cad` can replay via absolute Linux path under the agent workspace; Thunder Windows path was not readable from this MCP process. Local stdio binary: `/home/box/.local/share/nbcad/mcp/nbcad-mcp`.
