# left_input_carriage (body 97) — native feature dump

Source: `Roller-300.nbcad` → `model.json` (schema 7). Structured twin: `left_input_carriage-97.json`.
**This pass is dump-only — no invented JSONC geometry.**

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

## VERIFY gaps (before JSONC rebuild)
1. **Join/cut `new_body_ids`**: every join/cut also lists transient `new_body_ids` (98, 99, …). Treat as tool solids auto-booleaned into 97 — do **not** keep as SoT bodies unless visibility says otherwise.
2. **Multi-body cuts**: Extrude67 (97+100) and Extrude74 (97+108). Carriage-only chapter must either stub-include caps or defer shared M3 hole cuts until caps exist.
3. **Mirror2 timing**: right copies mirrored **before** Extrude86 strap cuts on left 97 — confirm whether body 122 needs a mirrored Extrude86 or was intentionally pre-cut-free.
4. **Datum offset sign**: native uses negative offset from XZ with positive Y origin (e.g. −2 → Y=2). Match Design Ops plane convention before replaying flip extrudes.
5. **Profiles**: only `profile_indices` stored; recover closed loops from sketch entities (rects/circles). Bearing seats are single circles; M3 sketches are two circles; strap passages are four rectangles.
6. **No fillet/chamfer/hole features** in the whole native file — all detail is sketch+extrude.

## How the JSONC chapter should be rebuilt
1. Port **in fid order** from this dump — datums → sketches (entities + constraints) → extrudes with exact operation / extent / flip / profile_indices.
2. Name the body `left_input_carriage` (Design Ops); map native id 97 only in comments/meta.
3. Skip Mirror2 for a left-only chapter; note right-side bodies 122–124 for a later assembly pass.
4. Do **not** invent blocks, lips, or holes that are not in the dump.
5. Blank-doc replay → compare AABB to assembly-coordinates STL (**39×100×35** at mins 30/2/88) before any `first-prints/` export.
6. Next status after rebuild: inspect match, then export.

See `left_input_carriage-97.json` for full sketch entity lists, datum sources, and per-feature payloads.
