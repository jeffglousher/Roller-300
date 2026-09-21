# first-prints/one-drive/

One-drive **service article** meshes from Design Ops chapter `design/design_v0_1_input_carriage.nbcad.jsonc` (VERSION 0.1).

**Not** a print release of the full OD160×L210 main-shell. Status: `one_drive_in_progress` — Jeff open call for fit coupons before locking.

**Exported:** 2026-09-20 ~22:20 CT via headless `nbcad-mcp` (`cad_new_project` → `cad_interface` script path → `solid_export_preflight` → `solid_export_3mf` + `solid_export_stl`). Prefer **3MF**.

## Bodies

| File | Body (replay) | Nominal intent (PLAN / parameters only) |
|------|---------------|-------------------------------------------|
| `left-input-carriage.3mf` / `.stl` | Body3 — ~39×100×35 | Rails/slots ±1.5 travel, window 7.4×4.4 (cut 10.4×4.4); two input bearing seats D22.2×7.2 trial + D18 shoulder; servo locating pocket from case 40.5×20×40.5 / `layout.servo_case_size` [20,40.5,40.5]. Ears/horn HOLD. Strap passages VERIFY (no dims). |
| `input-cap-inner.3mf` / `.stl` | Body11 | M3 recessed trial: CB D6 × 3.0 (`input_cap_travel_detail`); shank through D3.2 **TRIAL/VERIFY** (not in parameters). |
| `input-cap-outer.3mf` / `.stl` | Body14 | Copy of inner (left-side pair). Outer limit R70 is clearance bound — not modeled as disc here. |
| `wheel-cap-inner.3mf` / `.stl` | Body15 | M4 clearance D4.4 (`wheel_holes`); trial 608 seat D22.2×7.2 + D18; two M4 holes at ±18 mm X **pattern VERIFY**. |
| `wheel-cap-outer.3mf` / `.stl` | Body20 | Copy of inner. |
| `carriage-rail-slot-coupon.3mf` / `.stl` | Body1 | Retained S02 rail/slot coupon (±1.5 / 7.4×4.4). |

## Replay

1. Blank document only (`starting_state: empty` / `cad_new_project`).
2. Replay `design/design_v0_1_input_carriage.nbcad.jsonc` alone (do not concatenate with other chapters without remapping `$ref`).
3. Export selected bodies; do not claim main-shell print release.

## Still HOLD / open call to Jeff

- Full OD160×L210 barrel shell + hatch integration
- Servo **ears** / horn / mount pattern (case nominal only used)
- Strap passage dimensions (none in parameters)
- Slot corner R1 (`slot_corner_radius`)
- M3 shank clearance lock; wheel-cap screw count/pattern lock
- Input axial retention; clutch; powered assembly
- Native rail Y locations on shell vs service-article slot Y (−35 / −15) — VERIFY

See `design/README.md` and `design/gen_meta.json` (`one_drive_in_progress`).
