# hatch (body 141) — native feature dump

Source: `Roller-300.nbcad` → `model.json` (schema 7). Structured twin: `hatch-141.json`.

**This pass: dump complete + partial JSONC.** Full blank-doc AABB port is **BLOCKED** on shell body **32** (MoveCopy5 identity copy). No invented geometry.

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
| Blank-doc JSONC replay | **PENDING** — `pending_shell_dependency` |

## VERIFY gaps (before full JSONC rebuild)
1. **shell_copy_dependency** (MoveCopy5): Hatch starts as identity copy of body **32** at fid 291. Full blank-doc port needs shell history through that fid (or retained solid). **Do not invent OD160/ID152 tube.**
2. **stale_sketch_plane_datum_id** (S03 I): `plane.datum_id=96` but `basis.origin z=190` matches datum **330**. Port Z=190.
3. **stale_sketch_plane_datum_id** (S03 J): prefer chain datum **338** / sketch.basis over plane.datum_id=97.
4. **quat_rotation_movecopy** (MoveCopy8/9): Port exact quat `[0, 0.4617486132350339, 0, 0.8870108331782217]` — do not invent angle.
5. **revolve_countersink** (Revolve1): Only revolve in document; axis_origin (0,123), axis_dir (0,1), 360°.
6. **shell_side_s03**: Extrude89–95 / Combine5,9–12 modify shell 32 / lap 144 — not hatch chapter.
7. **coupon_partial**: Prior lap/M4 + panel-arc coupons remain print-today until shell dependency clears.

## How the JSONC chapter should be rebuilt
1. **BLOCKER**: Shell body 32 through fid < 291 (barrel_shell chapter) — or retained solid ≡ native body 32 at MoveCopy5.
2. MoveCopy5 copy → hatch (identity).
3. Extrude88 new_body from S03 A (datum Z123, extent 110) → Combine4 intersect.
4. Extrude96 → MoveCopy8 → RectangularPattern5 → Mirror6 → Combine13 cut.
5. Revolve1 → MoveCopy9 → RectangularPattern6 → Mirror7 → Combine14 cut.
6. Blank-doc replay; AABB vs review STL **138.0000×179.4000×48.0928** @ (-69.0000, -89.7000, 154.8591).

See `hatch-141.json` for full sketch entities, datums, and payloads.
