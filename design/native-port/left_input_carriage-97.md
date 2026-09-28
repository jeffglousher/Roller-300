# left_input_carriage (body 97) — native feature dump

Source: `Roller-300.nbcad` → `model.json` (schema 7). Structured twin: `left_input_carriage-97.json`.

## Creation
- **Extrude62** (`new_body`) from sketch **S02 O LEFT adjustable input carriage**
- Datum 62: offset **−2** from origin **XZ** (basis origin `[0, 2, 0]`, normal −Y)
- Profile: rectangle UV **X 30–65 × Z 88–92** (35 × 4)
- Extent: **distance 100**, `flip: true` → body **97**
- No owning `combine`; body is native extrude chain only

## Feature sequence (fid order)

| fid | Feature | Op | Sketch / notes | Extent |
|-----|---------|----|----------------|--------|
| 208 | Extrude62 | new_body | S02 O LEFT adjustable input carriage | 100 |
| 211 | Extrude63 | join | S02 P supported input post Y70 (datum Y66) | 8 |
| 214 | Extrude64 | cut | S02 Q bearing seat Y70 — Ø22.2 @ (49.6723, 123) | 8 |
| 223 | Extrude67 | cut | S02 T M3 holes Y70 — also targets body **100** | 36 |
| 226 | Extrude68 | cut | S02 U nut pocket (34.6723, 70) | 7 |
| 229 | Extrude69 | cut | S02 U nut pocket (64.6723, 70) | 7 |
| 232 | Extrude70 | join | S02 P supported input post Y96 (datum Y92) | 8 |
| 235 | Extrude71 | cut | S02 Q bearing seat Y96 | 8 |
| 244 | Extrude74 | cut | S02 T M3 holes Y96 — also targets body **108** | 36 |
| 247 | Extrude75 | cut | S02 U nut pocket (34.6723, 96) | 7 |
| 250 | Extrude76 | cut | S02 U nut pocket (64.6723, 96) | 7 |
| 253 | Extrude77 | cut | S02 V tension slot (34, 56) on Z=87 | 6 |
| 256 | Extrude78 | cut | S02 V tension slot (61, 56) | 6 |
| 259 | Extrude79 | cut | S02 V tension slot (34, 84) | 6 |
| 262 | Extrude80 | cut | S02 V tension slot (61, 84) | 6 |
| 265 | Extrude81 | join | S02 W servo lip X37.6723 | 40.5 |
| 268 | Extrude82 | join | S02 W servo lip X60.1723 | 40.5 |
| 271 | Extrude83 | join | S02 X end stop Y3.5 | 1 |
| 274 | Extrude84 | join | S02 X end stop Y46 | 1 |
| 275 | Mirror2 | mirror | Sources **[97,100,108] → [122,123,124]** about origin XZ; **does not mutate 97** | — |
| 287 | Extrude86 | cut | S02 Z L removable servo strap passages (4 rects) | 6 |

Between these, same S02 block also builds caps (Extrude65/66 → 100, Extrude72/73 → 108) — see JSON `timeline_context_extrudes_not_targeting_97`.

## AABB check (optional)
| Source | AABB (mm) |
|--------|-----------|
| Sketch envelope heuristic | X 30–69, Y 2–102, Z 88–123 → **39 × 100 × 35** |
| `shell-first-review/left-input-carriage-assembly-coordinates.stl` | **exact match** (30–69, 2–102, 88–123) |
| `.../left-input-carriage-floor-down.stl` | −19.5–19.5, −50–50, 0–35 → same extents **39 × 100 × 35** (reoriented) |
