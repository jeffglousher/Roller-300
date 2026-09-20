# Roller-300 design/ — modular Design Ops (VERSION 0.1)

JSONC-first AI iterate tree. Native `../Roller-300.nbcad` remains the editable CAD master until chapters carry geometry; this directory is the **new SoT for AI iterate**.

## VERSION

- File: `VERSION` and `gen_meta.json` → **0.1** (first modular cut).
- Filenames: `design_v0_1_<role-noun>.nbcad.jsonc`.
- Schema field `"version": 1` inside each JSONC is the **script schema** (INJS pattern), not the design VERSION.

## Modules (role-noun)

| File | PLAN stage | Role |
|------|------------|------|
| `design_v0_1_hardware_refs.nbcad.jsonc` | S01 | Hardware / belt / bearing / shaft references |
| `design_v0_1_barrel_shell.nbcad.jsonc` | S02 | Primary barrel shell + saddles/rails/guards |
| `design_v0_1_input_carriage.nbcad.jsonc` | S02 | Removable input carriage + caps |
| `design_v0_1_structural_hatch.nbcad.jsonc` | S03 | Curved structural hatch |
| `design_v0_1_electronics_mounts.nbcad.jsonc` | S04 | Battery / boards / sensors / harness |
| `design_v0_1_drive_stack.nbcad.jsonc` | S01/S05 | One-drive pulley/belt/hub stack |
| `design_v0_1_assemble.nbcad.jsonc` | orchestrator | Ordered chapter compose notes |

## Assemble + blank-doc replay

Product JSONC has **no include/compose** yet (Design Ops: chaptered includes when/if supported).

1. Open a **blank** document (`starting_state: empty`).
2. Replay chapters in the order listed in `design_v0_1_assemble.nbcad.jsonc` / `gen_meta.json` → `assemble.chapter_order`.
3. A runner (agent or Scripts UI) applies each chapter's `steps` onto the same doc; do not naive-concatenate JSON without remapping `$ref` / `let`.
4. After proven, prune older `design_v*` only intentionally — this cut is scaffold-only.

Shared datums (comments in every chapter): mm; X forward, Y left, Z up; ground origin below axle midpoint; axle Z=123.

## Belt (cite only)

**D&D 210-3M-09 / Amazon B00ISC4PHG** — accepted; parent handles purchase messaging. Nominals from `parts-sources.json`: pitch 3 mm, pitch length 210 mm, width 9 mm, 70 teeth. CAD centers 49.6723 mm (`parameters.transmission`).

## Print policy (today)

Print **mechanic fit coupons / small articles** first — not full vehicle, not powered. Prefer existing `../first-prints/` exports when valid; full shell orientations sliced but **HOLD**. See PLAN S05.

## Filling geometry next

1. `barrel_shell`: port shell OD/ID/length, wheel seats D22.2×7.2, carriage rails from native master / `parameters.body` + `parameters.bearings`.
2. `drive_stack`: pulley envelopes at nominal centers; belt path as reference solid only until tooth geometry verified.
