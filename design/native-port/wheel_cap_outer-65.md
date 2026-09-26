# wheel_cap_outer (body 65) — native feature dump

Source: `Roller-300.nbcad` → `model.json` (schema 7). Structured twin: `wheel_cap_outer-65.json`.

## Creation
- **Extrude31** (`new_body`) from sketch **S02 F removable wheel cap Y99**
- Datum 31: offset **-93.0** from origin **XZ** (basis origin `[0.0, 93.0, 0.0]`, normal [0.0, -1.0, 0.0])
- Profile: rectangle UV **X -25.0–25.0 × Z 123.3–140.0** (50.0 × 16.700000000000003)
- Extent: **distance 12.0**, `flip: True` → body **65**
- Owning combine: **none** (no later intersect/recess on this body)

## Feature sequence (fid order)

| fid | Feature | Op | Sketch / notes | Extent |
|-----|---------|----|----------------|--------|
| 113 | Extrude31 | new_body | S02 F removable wheel cap Y99 | 12.0 |
| 116 | Extrude32 | cut | S02 G cap seat Y99 — targets [65] | 12.0 |
| 119 | Extrude33 | cut | S02 H M4 cap holes Y99 — targets [32, 65] | 40.0 |

## AABB check

| Source | AABB (mm) |
|--------|-----------|
| Sketch envelope heuristic | X -25.0–25.0, Y 93.0–105.0, Z 123.3–140.0 → **50.0 × 12.0 × 16.700000000000003** |
| `first-prints/shell-first-review/wheel-cap-outer-assembly-coordinates.stl` | **50×12×16.7** (-25–25, 93–105, 123.3–140) |
| axle-vertical STL | extents **50×16.7×12** (reoriented) |
