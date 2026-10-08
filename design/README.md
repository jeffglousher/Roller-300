# design/

## Current S20 drivetrain

[Adversarial review](adversarial-review-2026-10-06/README.md) contains the current native captures, exact interference and geometry checks. [Canonical CAD](../Roller-300.nbcad) and [PLAN.md](../PLAN.md) define the current assembly. The chapter files below are historical baselines and do not regenerate S20.

VERSION 0.1 chapters (`VERSION`, `gen_meta.json`). Filenames are `design_v0_1_<role>.nbcad.jsonc`. The `"version": 1` field inside each file is the script schema.

Mechanical decisions are in [`../PLAN.md`](../PLAN.md). Dimensions are in [`../parameters.json`](../parameters.json). The native desktop model is [`../Roller-300.nbcad`](../Roller-300.nbcad).

## Chapters

| File | Stage | Role | Contents |
|------|-------|------|----------|
| `design_v0_1_hardware_refs.nbcad.jsonc` | S01 | Bearing and nut coupons | Trial 608 seat D22.2×7.2 and M4 nut pocket AF 7.3×3.5 |
| `design_v0_1_barrel_shell.nbcad.jsonc` | S02 | `main_shell` (body 32) | Shell chapter. Standalone file skips MoveCopy5, Combine8, and Combine16. Assemble-order AABB about 159.93×210×159.96. Meshes: `../first-prints/native-port/main-shell.*` |
| `design_v0_1_input_carriage.nbcad.jsonc` | S02 | `left_input_carriage` (body 97) | Left carriage. AABB 39×100×35. Meshes: `../first-prints/native-port/left-input-carriage.*` |
| `design_v0_1_input_caps.nbcad.jsonc` | S02 | Input caps (bodies 100, 108) | Inner and outer. AABB 39×8×17.7. Meshes: `../first-prints/native-port/input-cap-{inner,outer}.*` |
| `design_v0_1_wheel_caps.nbcad.jsonc` | S02 | Wheel caps (bodies 56, 65) | Inner and outer. AABB 50×12×16.7. Meshes: `../first-prints/native-port/wheel-cap-{inner,outer}.*` |
| `design_v0_1_structural_hatch.nbcad.jsonc` | S03 | `hatch` (body 141) | Replay after the shell chapter through Combine3. AABB 138×179.4×79.932. The review STL in `shell-first-review/` is the trimmed export (zmin 154.859). Meshes: `../first-prints/native-port/curved-hatch.*` |
| `design_v0_1_electronics_mounts.nbcad.jsonc` | S04 | Shelf and allowance coupons | Pi, Pixracer, TOF, battery tray, and thermal shelf from recorded nominals. Positive retainers, sensor depth, and the optical aperture stay open until the parts are measured |
| `design_v0_1_drive_stack.nbcad.jsonc` | S01/S05 | Drive envelopes | 24/48 pitch circles, belt torus, and Ø8 stubs. These are envelopes, not tooth geometry |
| `design_v0_1_assemble.nbcad.jsonc` | orchestrator | Chapter order | Empty steps. Order is listed in that file and in `gen_meta.json` → `assemble.chapter_order` |

## Replay

Open a blank document and apply the chapters in `assemble.chapter_order`. These files have no include. A runner has to apply each chapter's steps and remap `$ref` / `let` bindings.

Frame: millimeters; X forward, Y left, Z up; axle Z=123.

Belt cited on the drive chapter: D&D 210-3M-09, pitch 3 mm, pitch length 210 mm, width 9 mm, 70 teeth.

## Meshes

- [`../first-prints/coupons/`](../first-prints/coupons/README.md) — fit coupons
- [`../first-prints/shell-first-review/`](../first-prints/shell-first-review/README.md) — review meshes from the native model
- [`../first-prints/native-port/`](../first-prints/native-port/README.md) — meshes replayed from these chapters

Feature dumps of the native bodies are in [`native-port/`](native-port/README.md).
