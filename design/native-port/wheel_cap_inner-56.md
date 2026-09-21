# wheel_cap_inner (body 56) — native feature dump

Source: `Roller-300.nbcad` → `model.json` (schema 7). Structured twin: `wheel_cap_inner-56.json`.
**This pass is dump-only — no invented JSONC geometry.**

## Creation
- **Extrude23** (`new_body`) from sketch **S02 F removable wheel cap Y51**
- Datum 23: offset **-45.0** from origin **XZ** (basis origin `[0.0, 45.0, 0.0]`, normal [0.0, -1.0, 0.0])
- Profile: rectangle UV **X -25.0–25.0 × Z 123.3–140.0** (50.0 × 16.700000000000003)
- Extent: **distance 12.0**, `flip: True` → body **56**
- Owning combine: **none** (no later intersect/recess on this body)

## Feature sequence (fid order)

| fid | Feature | Op | Sketch / notes | Extent |
|-----|---------|----|----------------|--------|
| 89 | Extrude23 | new_body | S02 F removable wheel cap Y51 | 12.0 |
| 92 | Extrude24 | cut | S02 G cap seat Y51 — targets [56] | 12.0 |
| 95 | Extrude25 | cut | S02 H M4 cap holes Y51 — targets [32, 56] | 40.0 |

## AABB check

| Source | AABB (mm) |
|--------|-----------|
| Sketch envelope heuristic | X -25.0–25.0, Y 45.0–57.0, Z 123.3–140.0 → **50.0 × 12.0 × 16.700000000000003** |
| `first-prints/shell-first-review/wheel-cap-inner-assembly-coordinates.stl` | **50×12×16.7** (-25–25, 45–57, 123.3–140) |
| axle-vertical STL | extents **50×16.7×12** (reoriented) |

## VERIFY gaps (before JSONC rebuild)
1. **multi_body_m4** (Extrude25): Also targets body 32 (main_shell). Wheel-caps chapter should cut this cap only; shell chapter owns shell cuts.
2. **no_mirror** (mirrors): No mirror copies wheel caps 56/65 in native history — left-only bodies as-is.
3. **datum_offset_sign** (datums): XZ offsets negative → +Y origin (same as carriage/input caps). M4 hole datums offset +104 from origin XY.
4. **m4_radius_asymmetry** (Extrude25): Native dump radii differ slightly: [2.1999999999999993, 2.23606797749979]. Port exact values; do not invent nominal M4=2.0.

## How the JSONC chapter should be rebuilt
1. Extrude23 new_body blank
2. Extrude24 cut seat bore Ø22.2
3. Extrude25 cut M4 (cap target only; shell chapter owns body 32)
4. Blank-doc replay; AABB vs shell-first-review assembly-coordinates STL

Wheel-caps chapter after input_caps (or alone for cap exports). Extrude25: chapter cuts this/sibling wheel cap only; do not cut shell 32 here.

See `wheel_cap_inner-56.json` for full sketch entity lists, datum sources, and per-feature payloads.
