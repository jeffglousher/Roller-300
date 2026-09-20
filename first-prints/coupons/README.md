# first-prints/coupons/

Target folder for STL/3MF exports from Design Ops coupon chapters under `design/`.

## Scripts → expected exports

| Export name (suggested) | Source chapter |
|-------------------------|----------------|
| `608-bearing-seat-trial.stl` | `design/design_v0_1_hardware_refs.nbcad.jsonc` |
| `m4-captive-nut-af73.stl` | same (isolate nut plate body if multi-body) |
| `wheel-seat-saddle-trial.stl` | `design/design_v0_1_barrel_shell.nbcad.jsonc` |
| `carriage-rail-slot-travel.stl` | `design/design_v0_1_input_carriage.nbcad.jsonc` |

Until MCP/desktop export lands files here, print from:

1. Replay the chapter on a **blank** noBS CAD document, or
2. Existing review meshes in `../shell-first-review/` and `../drive-end-section/`.

All coupon seats are **TRIAL** — not released fits. See PLAN S05.
