# Whole-chassis fit review — 2026-10-07

The small unpowered drivetrain fit test remains the first print. The complete chassis is **not yet a fit release**. This review found and corrected two assembly/print-access defects, and exposed unfinished hatch and electronics interfaces. Strength optimization is deferred.

## Native fit corrections

- Two D4.4 service bores through the full shell's belt guards give a straight 3 mm driver access to the rear carrier screws. Previously each guard obstructed the driver through Z156..164. Bearing seats and the roof-open fixture are unchanged.
- Both wheel faces are opened inside D216. The D230 rim, 40 mm wheel width, 4 mm hub web and its bolt/pilot geometry remain. The former outer plate blocked all four hub-screw drivers; the two closed cavities also trapped approximately 148 g of support paths in the historical wheel slice. The open faces permit screw installation and support cleanup.
- Corrected the current register's old collar/spacer positions and servo case datum. The BOM now separates four M3x10 servo-ear screws from sixteen M3x12 bearing-retainer screws per drive. Exact M3x10 source/price remains open.

S21 adds eighteen native history features to S20, reaching 2,033. Installed Limo CAD replays and exports every changed shape. All ten existing smaller fit-part STL hashes remain identical. Native changes affect full shell32 and wheels13/30; the older closed-wheel print projects are superseded.

## Whole-chassis findings

The historical curved hatch141 and its closure features are suppressed. A separate native restoration candidate had no history errors, but exact inspection found **1,334.910 mm³ of hatch/shell overlap**, plus new input-retainer/carrier interference. Simply enabling the old features does not make a fitting hatch. The failed restoration remains separate from the canonical design.

Battery, Pi/controller, thermal camera, ToF, optical and harness mounting features are also inactive. Their old locating shelves and footprint registers do not constitute a current fitting assembly. Complete received component contours, connector exits, cable bends, positive restraints and service sweeps still need to be incorporated.

The wheels span 300 mm, but the uncut stock shafts end at Y±158: **316 mm actual shaft width**, exceeding the 300 mm target. Bare printed wheel diameter is230 mm; D246 is the tread allowance. Nominal belly clearance is35 mm on bare wheels and43 mm with the8 mm radial tread allowance. The width target and tread interface remain unresolved.

The old closed wheel's 5 mm shell-end gap concealed a smaller0.5 mm clearance to its protruding bearing-retainer bosses. S21 removes that surface: wheel/retainer clearance is24.0 mm nominal,23.8 mm at inward axial travel; minimum wheel/shell clearance is28.3 mm. Physical runout, endplay and hand rotation remain receiving tests.

The metal wheel hub/collar reference envelopes do not include a qualified clamp-screw/tool model. Clamp access and included hardware must be checked on receipt. The wheel bolts use the retained4 mm web, giving6 mm nominal engagement for M4x10 in8 mm deep metal threads; verify actual head/length/pilot seating.

## Printing and assembly gates

1. Print the [five small interfaces](../../first-prints/receiving-fit-gate-2026-10-06/Roller-300-small-fit-gate.3mf): PETG,0.4 mm, approximately25.48 g /1 h16 min. Test the received horn, REX key, center-screw clearance, clip insertion and nut/head fits.
2. Print the [carrier trial](../../first-prints/carrier-roof-trial-2026-10-06/Roller-300-carrier-roof-trial.3mf): approximately55.05 g /2 h22 min. Test both unsupported nut-channel roofs, actual608 seats, alignment, accessible nuts and screw lengths. Its9.116/16.372 mm roof runs are still physically unqualified.
3. Use the existing corrected fixture project and the [S21 open-face wheel project](../../first-prints/chassis-fit-2026-10-07/outboard-down/Roller-300-wheel-open-fit.3mf) after the receiving tests pass. The wheel is outboard-face down, approximately336.71 g /8 h38 min, with a connected annular first layer and at least10.137 mm bed margin. Supports lie below the hub web and are accessible through theD216 opening; pilot and four screw bores contain no support paths. Bench-assemble hub/pulley and input shaft/clip first. Install the E-clip before mounting its carrier; install the wheel through its open face. Check free rotation with axial travel at both ends, then belt seating/tracking.
4. Refit the hatch and active electronics/connector/restraint interfaces before a complete-chassis fit test. Full barrel slicing and support cleanup still require review after those geometry changes.

Do not force shafts through misaligned bearings, clamp bearing outer races with the shaft stops, or use screws that bottom in the metal threads. Record actual hardware, fit, support removal and endplay. No print, order or powered test was submitted.

## Evidence

- `independent/`: fresh S20 native replay, exact access/envelope probes and the failed hatch restoration.
- `fresh-native-wheel-clearances.json`: pre-correction native wheel/shell/cap interference query; explicitly S20 evidence.
- `register-and-bom-audit.json`: active/suppressed feature and record/BOM review.
- `s21-access/`: new native replay/export and exact correction checks.
- `s21-access/native-replay.nbcad` preserves the exact native replay candidate used by the wheel slice, independently of ignored local scratch files. Use `tools/record_chassis_review.py` to verify it against the saved canonical and print projects.
- [Current native CAD overall view](s21-overall-native.png) and [wheel access view](s21-wheel-access-native.png).
- `fresh-native-replay.json`, `print-project-validation.json`, `validation-summary.json`: saved canonical/provenance checks and current fit-project compatibility.
- `wheel-project-validation.json` reconciles the wheel's native replay source to the saved canonical geometry. `bambu-native-gui-verification.json` records reopened settings and a fresh native GUI slice matching336.71 g /8 h38 min.
- [Print and tolerance notes](tolerance-and-print-fit.md): actual fits to measure and historical support/toolpath findings.

The connector, spline/thread, PETG fit and physical support-removal tests are not replaced by nominal CAD or a warning-free slice.
