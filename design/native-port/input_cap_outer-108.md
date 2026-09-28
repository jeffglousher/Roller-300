# input_cap_outer (body 108) — native feature dump

Source: `Roller-300.nbcad` → `model.json` (schema 7). Structured twin: `input_cap_outer-108.json`.

## Creation
- **Extrude72** (`new_body`) from sketch **S02 R LEFT input cap Y96**
- Datum 72: offset **-92.0** from origin **XZ** (basis origin `[0.0, 92.0, 0.0]`, normal [0.0, -1.0, 0.0])
- Profile: rectangle UV **X 30.0–69.0 × Z 123.3–141.0** (39.0 × 17.700000000000003)
- Extent: **distance 8.0**, `flip: True` → body **108**
- Owning combine: **Combine18** intersect with Extrude144 tool body 234

## Feature sequence (fid order)

| fid | Feature | Op | Sketch / notes | Extent |
|-----|---------|----|----------------|--------|
| 238 | Extrude72 | new_body | S02 R LEFT input cap Y96 | 8.0 |
| 241 | Extrude73 | cut | S02 S cap bore Y96 | 8.0 |
| 244 | Extrude74 | cut | S02 T input cap M3 holes Y96 — also targets body **97** | 36.0 |
| 511 | Combine18 | intersect | tool Extrude144 / S02 input cap outside corner limit R70 for tension travel → body 234; keep_tools=True | 210.0 |
| 516 | Extrude145 | cut | S02 recessed M3 cap heads for hatch-ledge clearance — also targets 108/123/124 | 5.0 |
| 275 | Mirror2 | mirror | Sources **[97, 100, 108] → [122, 123, 124]**; **does not mutate 108** | — |

## AABB check

| Source | AABB (mm) |
|--------|-----------|
| Sketch envelope heuristic | X 30.0–69.0, Y 92.0–100.0, Z 123.3–141.0 → **39.0 × 8.0 × 17.700000000000003** |
| `shell-first-review/input-cap-outer-assembly-coordinates.stl` | **39×8×17.7** (30–69, 92–100, 123.3–141) |
| axle-vertical STL | extents **39×17.7×8** (reoriented) |
