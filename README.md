# Roller-300

Indoor-first two-wheel roller with a round barrel exoskeleton. No caster. Mechanical development. Not physically validated. No print or powered-test release.

- [PLAN.md](PLAN.md): mechanical decisions, assembly sequence, and release gates.
- [parameters.json](parameters.json): dimensions and measurement gates.
- [parts-sources.json](parts-sources.json) and [BOM.xlsx](BOM.xlsx): source record and purchase workbook, one populated drive first.
- [test-record.json](test-record.json): CAD and slicer observations. Physical tests are recorded separately and none have been run.
- [design/](design/README.md): VERSION 0.1 chapters, `design/design_v0_1_*.nbcad.jsonc`.
- [Roller-300.nbcad](Roller-300.nbcad): native desktop model.
- [checks/shell-first-checks.json](checks/shell-first-checks.json): preflight and exported mesh topology.
- [checks/shell-slice-review.json](checks/shell-slice-review.json): offline X2D orientation comparison.
- `first-prints/shell-first-review/`: review meshes from the native model.
- `first-prints/coupons/`: fit coupons.
- `first-prints/native-port/`: meshes replayed from the design chapters.

The first complete bench article is the barrel and hatch with one supported drive and wheel. Servo and horn mounting, input axial retention, clutch interfaces, measured battery, sensor, and cable sizes, positive electronics restraints, joint preload, and service access remain release gates. Nominal envelopes do not prove received-component fit or structural capacity.

No print has been sent. Offline slices use the installed X2D profiles and do not send a print:

```
python tools/slice_fit.py main-shell-axle-vertical
python tools/slice_fit.py main-shell-opening-down
python tools/slice_fit.py curved-hatch-axle-vertical
```

The default print set is `shell-first-review`.

The public repository is https://github.com/jeffglousher/Roller-300. No hardware or source license has been assigned; linked third-party material retains its own terms.
