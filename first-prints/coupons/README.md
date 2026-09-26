# first-prints/coupons/

STL and 3MF exports from the coupon chapters in `design/`.

Prefer 3MF for slicers. STL is the same geometry. Seats are trial dimensions, not released fits. See PLAN S05.

## Exports

| File | Source chapter | Notes |
|------|----------------|-------|
| `608-seat-coupon.3mf` / `.stl` | `design/design_v0_1_hardware_refs.nbcad.jsonc` | Plate about 40×40×8; trial D22.2×7.2 seat and D18 through |
| `m4-nut-coupon.3mf` / `.stl` | same | M4 captive-nut pocket AF 7.3 × depth 3.5 |
| `wheel-seat-saddle-coupon.3mf` / `.stl` | `design/design_v0_1_barrel_shell.nbcad.jsonc` | Single-body saddle coupon from the earlier coupon replay of that chapter |
| `carriage-rail-slot-coupon.3mf` / `.stl` | `design/design_v0_1_input_carriage.nbcad.jsonc` | Rail slot travel coupon |
| `hatch-lap-m4-coupon.3mf` / `.stl` | `design/design_v0_1_structural_hatch.nbcad.jsonc` | Lap 8 mm, gap 0.3 mm, M4 pocket AF 7.3×3.5 |
| `hatch-panel-arc-coupon.3mf` / `.stl` | same | R76 to R80, Y ±20, 35° skin. No fasteners |
| `pi-shelf-standoff-coupon.3mf` / `.stl` | `design/design_v0_1_electronics_mounts.nbcad.jsonc` | Pi Zero bare 65×30 shelf and corner standoffs |
| `pixracer-shelf-coupon.3mf` / `.stl` | same | 36×36 footprint recess. Height unmeasured |
| `tof-rail-coupon.3mf` / `.stl` | same | 20×12 locating channel. Depth unset |
| `battery-allowance-tray-coupon.3mf` / `.stl` | same | Open tray inner 85×30. Z=90 unmeasured |
| `thermal-envelope-shelf-coupon.3mf` / `.stl` | same | TOPDON TC002C Duo 71×42 nominal. Aperture unset |

`design_v0_1_drive_stack.nbcad.jsonc` is an envelope and has no coupon export. Shelf, tray, and lap coupons are fit coupons. They are not claimed 3D fits of the received parts.

Replay a coupon chapter on a blank document.
