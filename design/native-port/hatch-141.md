# hatch (body 141) — native feature dump

Source: `Roller-300.nbcad` → `model.json` (schema 7). Structured twin: `hatch-141.json`.

## Creation
- **MoveCopy5** (`copy: true`) of **body 32** (main_shell) → **body 141**, identity transform
- Owning combines: **Combine4** intersect tool 142; **Combine13** cut tools 164–171; **Combine14** cut tools 172–179
- Used as tool (keep_tools): Combine8→144, Combine16→32 — **shell chapter** owns those

## Feature sequence (hatch create/modify + required tools)

| fid | Feature | Kind | Notes |
|-----|---------|------|-------|
| 291 | MoveCopy5 | move_copy | new [141] · from [32] result [141] · T {'x': 0.0, 'y': 0.0, 'z': 0.0} |
| 292 | S03 A rounded curved hatch boundary 180L 120deg datum | datum_plane |  |
| 293 | S03 A rounded curved hatch boundary 180L 120deg | sketch | S03 A rounded curved hatch boundary 180L |
| 294 | Extrude88 | extrude | new_body · extent {'distance': 110.0, 'type': 'distance'} · S03 A rounded curved hatch boundary 180L · new [142] |
| 295 | Combine4 | combine | intersect · tgt [141] · tools [142] |
| 330 | S03 I radial screw clearance master datum | datum_plane |  |
| 331 | S03 I radial screw clearance master | sketch | S03 I radial screw clearance master |
| 332 | Extrude96 | extrude | new_body · extent {'distance': 18.0, 'type': 'distance'} · S03 I radial screw clearance master · new [164] |
| 333 | MoveCopy8 | move_copy | new [164] · from [164] result [164] · T {'x': 0.0, 'y': -75.0, 'z': 0.0} · quat [0.0, 0.4617486132350339, 0.0, 0.8870108331782217] |
| 334 | RectangularPattern5 | rectangular_pattern | new [165, 166, 167] · count 4 spacing 50.0 |
| 335 | Mirror6 | mirror | new [168, 169, 170, 171] |
| 337 | Combine13 | combine | cut · tgt [141] · tools [164, 165, 166, 167, 168, 169, 170, 171] |
| 338 | S03 J 90 degree countersink master datum | datum_plane |  |
| 339 | S03 J 90 degree countersink master | sketch | S03 J 90 degree countersink master |
| 340 | Revolve1 | revolve | new_body · angle 360.0 · S03 J 90 degree countersink master · new [172] |
| 341 | MoveCopy9 | move_copy | new [172] · from [172] result [172] · T {'x': 0.0, 'y': -75.0, 'z': 0.0} · quat [0.0, 0.4617486132350339, 0.0, 0.8870108331782217] |
| 342 | RectangularPattern6 | rectangular_pattern | new [173, 174, 175] · count 4 spacing 50.0 |
| 343 | Mirror7 | mirror | new [176, 177, 178, 179] |
| 344 | Combine14 | combine | cut · tgt [141] · tools [172, 173, 174, 175, 176, 177, 178, 179] |

## AABB check

| Source | AABB (mm) |
|--------|-----------|
| S03 A sketch UV envelope | X ±69 × Y ±89.7 → **138 × 179.4** (2D only; Extrude88 alone ≠ final hatch) |
| `first-prints/shell-first-review/curved-hatch-assembly-coordinates.stl` | X[-69.0000,69.0000] Y[-89.7000,89.7000] Z[154.8591,202.9519] → **138.0000 × 179.4000 × 48.0928** (tris 4296) |
| Blank-doc JSONC replay (shell@fid≤290 → hatch) | X[-69,69] Y[-89.7,89.7] Z[123,202.932] → **138 × 179.4 × 79.932** (tris 3068). XY match. **Z CLOSED**: native matches tall replay; review zmin 154.859 = ID R76 chord at |X|=69 (trimmed export). |X|=69); replay includes Extrude88 plane / Combine3 shoulder material down to Z123. |
