# Unpowered native fit parts — 2026-10-03

Source: `Roller-300.nbcad`, 1,208 native features. PETG, X2D, 0.4 mm nozzle. No physical print has been performed or sent. These files supersede older print candidates.

Start with `outer-wheel-bearing-coupon.stl` and `wheel-bearing-retainer.stl`: approximately **24 g / 58 minutes** when sliced separately. This tests the 22.2 mm trial608 seat,18 mm shoulder clearance, M3 captive nuts and recessed heads before larger prints. Use four M3x16 bolts and M3 nuts; verify engagement and free bearing rotation. This coupon represents the outer bearing mount, not a complete wheel.

Then test `servo-shaft-clamp-trial.stl` and `input-pulley-clamp-trial.stl` on the uncut8 mm shaft, using M3x10 bolts/nuts. The purchased servo horn interface is excluded until its actual mounting pattern, boss and screw engagement are measured.

The one-drive shell section preserves the left servo mount, both input bearings, and center/mouth wheel-shaft supports. Print `one-drive-fit-section.stl` after small fits pass: **231 g / 6.4 hours**. Add the upper bridge and center, mouth and two input bearing retainers. Use nominal608 bearings, uncut150 mm wheel and50 mm input shafts, an8x25x6 metal input stop collar and2 mm of metal inner-race shims. Retainers must seat freely; set measured endplay without bearing preload. `test-record.json` lists trial hardware and observations.

The full left wheel candidate slices at **613 g / 15.9 hours**, including support. Review its print strategy/mass before that expenditure. A complete wheel/tyre is required later to assess stiffness, clearance and loads; small coupons do not establish those results.

All eleven current candidates slice without warnings with installed Bambu Studio X2D/Generic PETG settings:0.2 mm layers, five walls,15% gyroid, supports where enabled. Native CAD STEP/STL connectivity checks pass. Preparation changes only orientation, placement and serialization; the placement3MF shares vertex references. No custom renderer is used. Review toolpaths in `slicer-check/<part>/<part>-estimate.3mf`; estimates are in `slice-estimates.json`, source hash in `source.json`.

Inspect support removal at bores, nut pockets and servo walls, then record received fits. The supplied drawing labels the270-degree variant; the owned360-degree case, ears and cable boot still need physical confirmation. The shaft-driven clutch and its preload remain unresolved for powered operation. This package is for unpowered fit work.

Assembly: load captive nuts while accessible; install bearings against outer-race shoulders; close retainers and confirm free rotation; insert servo with its bridge removed; fit ear/bridge bolts; install shaft clamps, pulleys and belt; set metal stop and measured endplay. Add the measured horn adapter later. Check driver and cable access physically.
