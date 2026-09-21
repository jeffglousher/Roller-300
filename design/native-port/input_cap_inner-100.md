# input_cap_inner (body 100) — native feature dump

Source: `Roller-300.nbcad` → `model.json` (schema 7). Structured twin: `input_cap_inner-100.json`.
**This pass is dump-only — no invented JSONC geometry.**

## Creation
- **Extrude65** (`new_body`) from sketch **S02 R LEFT input cap Y70**
- Datum 65: offset **-66.0** from origin **XZ** (basis origin `[0.0, 66.0, 0.0]`, normal [0.0, -1.0, 0.0])
- Profile: rectangle UV **X 30.0–69.0 × Z 123.3–141.0** (39.0 × 17.700000000000003)
- Extent: **distance 8.0**, `flip: True` → body **100**
- Owning combine: **Combine17** intersect with Extrude144 tool body 234

## Feature sequence (fid order)

| fid | Feature | Op | Sketch / notes | Extent |
|-----|---------|----|----------------|--------|
| 217 | Extrude65 | new_body | S02 R LEFT input cap Y70 | 8.0 |
| 220 | Extrude66 | cut | S02 S cap bore Y70 | 8.0 |
| 223 | Extrude67 | cut | S02 T input cap M3 holes Y70 — also targets body **97** | 36.0 |
| 510 | Combine17 | intersect | tool Extrude144 / S02 input cap outside corner limit R70 for tension travel → body 234; keep_tools=True | 210.0 |
| 516 | Extrude145 | cut | S02 recessed M3 cap heads for hatch-ledge clearance — also targets 108/123/124 | 5.0 |
| 275 | Mirror2 | mirror | Sources **[97, 100, 108] → [122, 123, 124]**; **does not mutate 100** | — |

## AABB check

| Source | AABB (mm) |
|--------|-----------|
| Sketch envelope heuristic | X 30.0–69.0, Y 66.0–74.0, Z 123.3–141.0 → **39.0 × 8.0 × 17.700000000000003** |
| `shell-first-review/input-cap-inner-assembly-coordinates.stl` | **39×8×17.7** (30–69, 66–74, 123.3–141) |
| axle-vertical STL | extents **39×17.7×8** (reoriented) |

## VERIFY gaps (before JSONC rebuild)
1. **multi_body_m3** (Extrude67): Also targets body 97 (carriage). Caps chapter should cut this cap; carriage chapter already cuts 97.
2. **combine_tool** (Extrude144): Tool body 234 kept (keep_tools True on Combine17/18). Need tool solid in chapter then intersect.
3. **extrude145** (Extrude145): Cuts all four caps (L/R inner/outer). Left-only chapter: target this body only (or both left caps).
4. **mirror2** (Mirror2): Skip for left-only; right bodies 123/124 later.
5. **datum_offset_sign** (datums): XZ offsets negative → +Y origin (same as carriage). Extrude144 datum distance +105 → origin Y=-105 (unusual).

## How the JSONC chapter should be rebuilt
1. Extrude65 new_body blank
2. Extrude66 cut bore
3. Extrude67 cut M3 (cap target; carriage already has carriage-only cut)
4. Extrude144 new_body corner-limit tool
5. Combine17 intersect cap with tool
6. Extrude145 cut recessed M3 heads on this cap (and optionally sibling)
7. Skip Mirror2
8. Blank-doc replay; AABB vs shell-first-review assembly-coordinates STL

Assemble: Caps chapter after carriage blank/chapter. Extrude67/74: carriage chapter cuts 97 only; caps chapter cuts 100/108 only with same sketches. Extrude145 left-only targets 100+108.

See `input_cap_inner-100.json` for full sketch entity lists, datum sources, and per-feature payloads.
