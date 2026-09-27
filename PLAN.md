# Roller-300 — shell-first mechanical master

## Source and status

`Roller-300.nbcad` is the only editable CAD master. Use native visibility, sections and history within it. `parameters.json` is the manually synchronized dimension/measurement record, not another geometry generator. The active model is the barrel skin plus the load-path hardware. Saddles, caps, carriage, rails, hatch, and electronics mounts stay in history and are suppressed until a structure is designed around these positions.

This is a mechanical development model, not a print release, structural qualification or powered-test release. No physical tests have been performed. Electrical/software compatibility is outside this revision. Two wheels without a caster remain the accepted architecture; active pitch control is a separate unimplemented requirement.

Sketches, datums and components use S01–S05 names. The app's automatically generated operation names remain unchanged; the feature-ID map identifies their stages honestly.

## Datum and envelope

Millimeters; X forward, Y left, Z up. Ground origin below axle midpoint; axle Z=123. Wheel OD246, width40; outside Y=±150. Barrel D160, ID152, length210, ends Y=±105. Tire inner faces Y=±110 give a nominal5 mm gap; deformation, runout, bearing play and manufacturing variation consume it. It is not a safe finger clearance. Nominal belly clearance43 mm is an unloaded geometric value.

## S01 — Hardware references and load paths

Owned INJORA INJS035-360, the 210-3M-09 belt, 24/48 pulleys, 8 mm shafts, 608 bearings, and the wheel hub stay. The ComInTec 00.25 limiter is retired: about $80 each before plates and bushes, and the installed pair was never quoted. Slip is a collar-adjusted stack of ordinary metal washers on the wheel shaft.

Per side the printed parts are the servo cradle, the 19 mm coupler, the two pulleys, and the wheel. Everything else in the drive is purchased metal. The cradle clamps the known 20 × 40.5 × 40.5 case. The coupler runs from the case face at Y 45.5 onto the input shaft, 8 mm bore, 11 mm long. Ear holes and the 25T tooth form stay uncut until the sample is measured; the cradle does not need them.

The 24T is fixed on the input shaft. The 48T prototype bore is 27 mm. A sleeve, OD 26.8 and ID 8.2, fills that bore and is the running fit on the shaft, so the pulley is not floating on a loose bush. Inboard of that pulley, on the wheel shaft: adjuster collar Y 55.75–64.75, Belleville stack Y 64.75–70.75 (OD 23), shaft washer Y 70.75–72.25, fiber washer Y 72.25–74.25, pulley washer Y 74.25–75.75 bolted to the pulley outside the fiber. The shaft washer is locked by a filed flat. Tightening the collar raises the slip torque. A locked wheel slips here and the servo keeps turning. The belt and the 24T are still upstream of the slip.

Left wheel bearings are at Y 98–105 and Y 146–153, with the tire (Y 110–150) between them. The hub tip, the 10 mm spacer, the 0.5 mm shim, and the outer bearing meet at Y 135.5, 145.5, and 146. Each tire face has an 8 mm sidewall. The shaft runs Y 35–160. Input bearings stay at |Y|=70 and 96. Both pulleys stay at Y 75.75–90.25. Input center X=49.6723, Z=123. The right side is the mirror. Slip torque is set on the bench. No number is qualified yet.

## S02 — Barrel envelope

The shell is still the Ø160 / Ø152 × 210 mm barrel. The old saddles, rails, caps, and shelves stay suppressed. Three supports are added on each side, and each one is only where a load enters the tube.

At the mouth, a 32 mm boss with a 22.2 mm seat holds the inner wheel bearing (left Y 97–105) and an 8 mm web drops from that boss to the belly. The outer wheel bearing is out past the tire, so the barrel does not reach it. Beside that, the same boss-and-web holds the outer input bearing (left Y 92.5–99.5) on the input axis. Under the servo, a foot runs from the case bottom at Z 89 down to the shell. The right side repeats at negative Y.

Wheel retention hardware stays: one inboard collar, a 3 mm steel inner-race spacer, then on the outboard side a 10 mm spacer and a 0.5 mm shim filling from the hub tip to the outer bearing. Set measured endplay without bearing preload. The 8 mm sidewalls are the wheel's structure. Positive input-shaft axial retention remains a gate.

## S03 — Access

The curved hatch, lap ledge, and radial nut bosses are suppressed. Access and how the shell closes get decided after the load path is fixed. Hatch closure must not be what locates the shafts.

## S04 — Devices that are not in the load path

Battery, Pi, Pixracer, thermal camera, distance-sensor, and harness plastic are suppressed, along with those nominal envelopes. They come back only after the mechanical positions are settled and the real parts are measured. Keep future wiring away from belts and shafts.

Battery size, fitted boards, sensor depth, and the thermal camera remain unmeasured. No shelf or strap in this model is a fit.

## S05 — Print preparation

No print of the suppressed structure. The next article is whatever integrated shell is built around the positions above, with one drive first. Wheel retention and shaft endplay still have to be set on the real bearings before that shell is released.

## Release gates and records

1. Measure servo ears/horn/mounts; finish supported adapter, input-bearing and shaft retention.
2. Measure battery, fitted boards, sensor depths, thermal optical/connector datums and mated cable bends; finish positive restraints and openings.
3. Obtain exact clutch assembly/interface and duty information; calibrate both breakaway and sliding torque in both directions independently of the servo.
4. Verify one connected watertight shell, no old-frame alternatives, full-travel clearance, bearing alignment, hatch extraction, and complete tool/assembly paths.
5. Source fasteners, coupon fits, establish joint preload, inspect sliced supports/toolpaths, then release prints separately.
6. Before powered tests: numeric torque/current/temperature/slip-duration limits, hold-to-run and accessible actuator cutoff. A wheel sensor alone does not identify internal slip without an input reference or another justified method. Persistent faults must stop both drives and require deliberate rearm; implementation is outside this revision.

Normal turns and the intended rounded floor transition must not require clutch slip. Normal shocks need a measured load envelope. A downstream limiter does not protect an upstream belt/pulley jam. No arbitrary torque, force or speed is declared safe. Powered operation stays held until the protective load band and shutdown/duty design are justified.

Record CAD, slicing and physical observations separately in `test-record.json`. Commit source, parameters, BOM and records together; regenerate `checks/model-review.json` after saving the native source. Git preserves superseded proposals; this is the canonical current plan.
