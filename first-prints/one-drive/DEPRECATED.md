# DEPRECATED — do not print

`first-prints/one-drive/` held crude JSONC block placeholders (2026-09-20 `7a8e6d9`).
They are **not** vehicle parts and must not be used for fit or assembly.

## Tracking SoT (repo, not sessions)

| Role | Location |
|------|----------|
| Native CAD master | `Roller-300.nbcad` |
| Shell-first review meshes (from native) | `first-prints/shell-first-review/` |
| Mechanic coupons (608 / M4 / slots / electronics) | `first-prints/coupons/` |
| Design Ops JSONC chapters | `design/*.nbcad.jsonc` (VERSION 0.1) |
| Plan / dims | `PLAN.md`, `parameters.json` |

Print carriage/caps from **`shell-first-review/`** (`left-input-carriage-floor-down`, `input-cap-*-axle-vertical`, `wheel-cap-*-axle-vertical`). Full `main-shell-*` remains HOLD.

JSONC will be re-driven from native body IDs (shell 32, carriage 97, caps 100/108/56/65, hatch 141) — not reinvented as toy blocks.
