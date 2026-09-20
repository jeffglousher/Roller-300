# Roller-300

Indoor-first two-wheel roller with a round barrel exoskeleton. No caster. Mechanical development in the local NoBS CAD desktop. **Not physically validated; no print or powered-test release.**

Open [Roller-300.nbcad](Roller-300.nbcad), the only editable CAD master. The inherited frame has been removed from this master and preserved in Git. Fresh native shell, bearing supports, structural hatch and direct mounting features follow the named S01–S05 stages. Purchased-part references and incomplete envelopes are labeled separately.

- [PLAN.md](PLAN.md): concise canonical mechanical decisions, assembly sequence and release gates.
- [parameters.json](parameters.json): current dimensions, native feature/stage IDs and measurement gates; manually synchronized with CAD.
- [parts-sources.json](parts-sources.json) and [BOM.xlsx](BOM.xlsx): source record and generated purchase workbook, with one populated drive first.
- [test-record.json](test-record.json): current CAD/slicer observations and historical results, distinguished from physical tests.
- [checks/shell-first-checks.json](checks/shell-first-checks.json): native preflight and selected exported mesh topology.
- [checks/shell-slice-review.json](checks/shell-slice-review.json): offline X2D orientation comparison and toolpath statistics.
- `first-prints/shell-first-review/`: current derived review exports. These are not alternate working models or released prints.
- `first-prints/drive-end-section/`: unchanged historical carrier/spine fit exports, pinned to tag `drive-fit-candidate-2026-09-19` and commit `80f06f3`.

Use native visibility and sections in the master; use history to edit features. Export selected body IDs explicitly. Automatic operation names remain app-generated; named sketches, datums/components and the recorded feature IDs identify stages. Do not hand-edit the generated `checks/model-review.json` snapshot. Refresh it after saving with `python tools/cad_snapshot.py --write`.

The first complete bench article is the whole barrel and hatch with one supported drive and wheel. Servo/horn mounting, input axial retention, clutch interfaces, measured battery/sensor/cable sizes, positive electronics restraints, joint preload and service/tool access remain release gates. Nominal envelopes do not prove received-component fit or structural capacity.

No print has been sent. The current desktop security prompt prevents final CAD screenshots and visual slicer/toolpath review; this does not invalidate the saved CAD but leaves those deliverables open. Earlier root-level CAD screenshots show earlier revisions and are not evidence for this shell-first design.

On this installation, reproduce current offline slices by setting `ROLLER_PRINT_SET=shell-first-review`, then running `python tools/slice_fit.py main-shell-axle-vertical`, `python tools/slice_fit.py main-shell-opening-down` or `python tools/slice_fit.py curved-hatch-axle-vertical`. The utility uses the installed X2D profiles and never sends a print. The default print set remains the historical carrier/spine folder.

The public repository is https://github.com/jeffglousher/Roller-300. No hardware/source license has been assigned; linked third-party material retains its own terms.
