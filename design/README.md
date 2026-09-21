# Roller-300 design/ — modular Design Ops (VERSION 0.1)

JSONC-first AI iterate tree. Native `../Roller-300.nbcad` remains the editable CAD master until chapters fully replace it; this directory is the **new SoT for AI iterate**.

## VERSION

- File: `VERSION` and `gen_meta.json` → **0.1** (first modular cut; keep until a proven cut).
- Filenames: `design_v0_1_<role-noun>.nbcad.jsonc`.
- Schema field `"version": 1` inside each JSONC is the **script schema** (INJS pattern), not the design VERSION.

## Modules (role-noun)

| File | PLAN stage | Role | Geometry status |
|------|------------|------|-----------------|
| `design_v0_1_hardware_refs.nbcad.jsonc` | S01 | Hardware / belt / bearing / shaft refs | **Coupon geometry**: 608 seat D22.2×7.2 trial + M4 nut AF7.3×3.5 |
| `design_v0_1_barrel_shell.nbcad.jsonc` | S02 | Barrel shell + saddles/rails/guards | **Saddle coupon** (one wheel seat); full OD160 barrel deferred |
| `design_v0_1_input_carriage.nbcad.jsonc` | S02 | Removable input carriage + caps | **one_drive_in_progress**: left_input_carriage + M3 input caps + M4 wheel caps (trial); rail coupon retained; full shell HOLD |
| `design_v0_1_structural_hatch.nbcad.jsonc` | S03 | Curved structural hatch | **Lap/M4 coupon** + **panel-arc** (R76→R80×35°); full 180 mm hatch deferred |
| `design_v0_1_electronics_mounts.nbcad.jsonc` | S04 | Battery / boards / sensors / harness | **Shelf/standoff + allowance coupons** (Pi / Pixracer / TOF / battery tray / thermal); shell-integrated mounts deferred |
| `design_v0_1_drive_stack.nbcad.jsonc` | S01/S05 | One-drive pulley/belt/hub stack | **Pitch envelopes** 24/48 + belt torus + Ø8 stubs |
| `design_v0_1_assemble.nbcad.jsonc` | orchestrator | Ordered chapter compose notes | Orchestrator only |

## Assemble + blank-doc replay

Product JSONC has **no include/compose** yet (Design Ops: chaptered includes when/if supported).

1. Open a **blank** document (`starting_state: empty`).
2. Replay chapters in the order listed in `design_v0_1_assemble.nbcad.jsonc` / `gen_meta.json` → `assemble.chapter_order`.
3. For **print-today coupons**, prefer replaying a **single** chapter (hardware_refs / barrel_shell saddle / input_carriage rail / structural_hatch lap / electronics_mounts shelves) rather than full assemble.
4. A runner (agent or Scripts UI) applies each chapter's `steps` onto the same doc; do not naive-concatenate JSON without remapping `$ref` / `let`.
5. After proven, prune older `design_v*` only intentionally.

Shared datums (comments in every chapter): mm; X forward, Y left, Z up; ground origin below axle midpoint; axle Z=123.

## Belt (cite only)

**D&D 210-3M-09 / Amazon B00ISC4PHG** — accepted; parent handles purchase messaging. Nominals from `parts-sources.json`: pitch 3 mm, pitch length 210 mm, width 9 mm, 70 teeth. CAD centers 49.6723 mm (`parameters.transmission`). Pitch-cylinder / torus solids in `drive_stack` are **envelopes ≠ tooth qualification**.

## Print today — mechanic fit coupons

Print **mechanic fit coupons / small articles** first — not full vehicle, not powered. Full shell orientations sliced but **HOLD**. See PLAN S05.

### New coupon scripts (Design Ops JSONC)

| Coupon | Script | Intent |
|--------|--------|--------|
| 608 bearing trial seat | `design_v0_1_hardware_refs.nbcad.jsonc` | Plate ~40×40×8; seat D22.2×7.2 trial; through D18 shoulder clear |
| M4 captive-nut hatch | same | Hex pocket AF 7.3 × depth 3.5 (PLAN hatch candidate) |
| Wheel-seat saddle | `design_v0_1_barrel_shell.nbcad.jsonc` | One saddle block matching D22.2×7.2; map to vehicle Y±51/±99 |
| Carriage rail slot (retained) | `design_v0_1_input_carriage.nbcad.jsonc` | Slot travel ±1.5 intent; size from parameters |
| Hatch lap + M4 nut | `design_v0_1_structural_hatch.nbcad.jsonc` | Developed lap_mm 8 + gap 0.3 + AF7.3×3.5; panel-arc envelope separate |
| Drive envelopes | `design_v0_1_drive_stack.nbcad.jsonc` | Visual/fit envelopes only — **not** a print-first article |
| Pi / Pixracer / TOF / battery / thermal | `design_v0_1_electronics_mounts.nbcad.jsonc` | Shelf/standoff + UNMEASURED allowance tray; footprint/envelope coupons — **not** claimed 3D fits |

Replay one coupon chapter on a blank doc in noBS CAD, then export STL/3MF to `../first-prints/coupons/` when export is available.

### Existing review STLs (still valid for print-today)

Under `../first-prints/`:

- `shell-first-review/` — shell, hatch, carriage, caps, wheels (REVIEW ONLY; not released)
- `drive-end-section/` — historical drive-fit-candidate-2026-09-19 (old carrier/spine; do not mix with shell-first)

See `../first-prints/shell-first-review/README.md` and `../first-prints/coupons/README.md`.

## One-drive printable set (in progress)

Status in `gen_meta.json`: **`one_drive_in_progress`**. Exports: `../first-prints/one-drive/` (prefer 3MF).

Includes left input carriage (rails/slots ±1.5 / 7.4×4.4, two D22.2×7.2 input seats, servo case lips 40.5×20×40.5 only), M3 recessed input caps, M4 wheel caps with trial seats. **Full OD160×L210 main-shell and full assembly remain HOLD** — not a print release of the barrel.

Open call to Jeff: measure servo ears/strap; coupon M3 shank + wheel-cap M4 pattern; VERIFY rail Y vs shell; then decide print of the service article.

## Filling geometry next

1. Prove hardware_refs + saddle coupons on printer (608 + M4 nut).
2. ~~Flesh carriage~~: one_drive left_input_carriage + caps exported under `../first-prints/one-drive/` (`one_drive_in_progress`). Still: add R1 to slots; Jeff open call for ears/strap/M3–M4 pattern; full shell HOLD.
3. ~~`structural_hatch`~~: coupons filled (lap/M4 + panel-arc); grow toward full 180 mm / ~120° after print feedback.
4. `barrel_shell`: grow from saddle coupons toward OD160/ID152/L210.
5. ~~`electronics_mounts`~~: shelf/standoff + allowance coupons filled from recorded nominals; positive retainers / sensor depth / optical aperture remain HOLD until measured parts.
