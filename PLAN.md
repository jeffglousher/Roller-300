# Roller-300 — shell-first mechanical master

## Source and status

`Roller-300.nbcad` is the only editable CAD master. Use native visibility, sections and history within it. `parameters.json` is the manually synchronized dimension/measurement record, not another geometry generator. New shell, saddle, carriage, hatch and mounting features replace the inherited frame. Earlier frame versions remain in Git; S01 retains only hardware and wheel references.

This is a mechanical development model, not a print release, structural qualification or powered-test release. No physical tests have been performed. Electrical/software compatibility is outside this revision. Two wheels without a caster remain the accepted architecture; active pitch control is a separate unimplemented requirement.

Sketches, datums and components use S01–S05 names. The app's automatically generated operation names remain unchanged; the feature-ID map identifies their stages honestly.

## Datum and envelope

Millimeters; X forward, Y left, Z up. Ground origin below axle midpoint; axle Z=123. Wheel OD246, width40; outside Y=±150. Barrel D160, ID152, length210, ends Y=±105. Tire inner faces Y=±110 give a nominal5 mm gap; deformation, runout, bearing play and manufacturing variation consume it. It is not a safe finger clearance. Nominal belly clearance43 mm is an unloaded geometric value.

## S01 — Hardware references and load paths

Owned INJORA INJS035-360 partial case, purchased 210-3M-09 belt candidate, 24/48 pulley proposals, 8 mm independent shafts, 608 bearings and wheel/hub references remain. Matching horn, ears, clutch details, shaft retention and manufactured pulley tooth geometry remain HOLD. The ComInTec 00.25 DF d8 T1 is a qualification candidate; see `parts-sources.json` for actual evidence and limitations. No torque setting is qualified.

Per side: purchased horn → supported input shaft/pulley → belt → output pulley/limiter → live wheel shaft and clamp hub. Wheel forces pass through both wheel bearings into integral saddles and shell. Input-pulley forces pass through carriage bearings into the fixed shell. Neither wheel suspension nor sole pinion support uses the servo bearings.

Wheel bearings remain at |Y|=51 and99, span48 mm. The wheel shaft now extends inward to |Y|=35 (113 mm length); wheel/hub positions remain fixed. Input bearings shift to |Y|=70 and96, shaft |Y|=52…101. Pulley pair, belt and clutch move inward4 mm together for support clearance. Input center X=49.6723, Z=123. Slots provide3 mm total carriage travel. Exact checks at -1.5,0,+1.5 mm pass for the modeled movable input group after limiting cap outside corners to R70 and recessing M3 heads. Belt tension, received hardware and complete tool sweeps remain unqualified.

## S02 — Primary barrel shell

The new main shell carries four wheel-bearing saddles, short carriage rails and integral end guards. Wheel caps are removable. D22.2 bearing seats are trial coupon dimensions. Lower wheel-seat shoulders locate outer races within7.2 mm axial pockets; verify contact against the purchased bearing drawing. Clutch adjustment must never clamp inner and outer races together.

Each removable input carriage has two bearing supports, caps, servo locating lips and strap passages. It is a service/tension part, not a separate drive-end chassis. Wheel caps and carriage joints use M4; input caps use recessed M3x30 candidates. Captive-nut fits, screw lengths and preload require verification. Wheel retention uses one inboard collar, a3 mm steel inner-race spacer, and an outboard0.5 mm shim plus10 mm steel spacer against the clamping hub. Set measured endplay without bearing preload. Positive input-shaft and input-bearing axial retention remain explicit gates.

## S03 — Structural access hatch

The upper curved panel comes from the same barrel: approximately120°, opening180 mm long, leaving15 mm end bands. Projected opening corners R8.3; nominal projected panel gap0.3 mm. An approximately8 mm curved lap ledge registers the panel and supplies load-transfer contact surfaces.

Eight radial M4 stations at ±55° from top and Y=−75,−25,25,75 clamp the joint. Candidate screws M4×12,90° countersunk; nut cavities7.3 mm across flats ×3.5 mm deep. Source actual hardware and validate contact, countersink ligaments, preload, PETG creep and repeated opening before any structural claim.

Both wheel-bearing pairs remain in the main shell. Hatch closure must not alter alignment or tension. Electronics remain fixed when the panel lifts away. Outer cap tool access with a wheel installed needs a long angled hex tool through the hatch. Once unbolted, slide the outer cap inward before lifting through the opening. A blind relief behind the end guard clears the outer bearing during lowering. Board-shelf driver holes expose the inner cap screws after board removal. Actual swept-tool/physical verification remains necessary.

## S04 — Direct mounting and service paths

The shell directly supports a low battery platform with strap passages/stops; Pi and Pixracer shelves; a forward thermal cradle; front distance-sensor locating rails; and rear harness saddles with tie passages. Keep wiring away from belts and shafts. Cameras stay forward; rear ranging is a future option.

The battery90×85×30 allowance is UNMEASURED. Pi geometry is nominal bare-board only. Original Pixracer36×36 and four distance modules20×12 are footprint-only sketches: fitted height, sensor depth and connectors are unknown. These do not constitute3D fit passes. The TOPDON TC002C Duo reference has moved3 mm forward and3 mm down to clear the battery allowance and hatch. It uses its nominal device envelope; received lens, contour and connector measurements govern final retention and optical opening. No guessed aperture or cable envelope is modeled.

Board positive retainers, exact sensor retention, cable bends and charging-contact capture remain detailing gates. Broad shelves and strap passages allow measured adjustments without reviving the old frame.

## S05 — Print preparation and complete drive test

The complete test article is this main shell and hatch with ONE populated supported drive, hub and wheel. Add the other drive to the same housing later. There is no structural drive-end split solely for testing.

Assembly: install nuts; fit endless belt around pulley/shaft assemblies before placing them; lower assemblies through hatch; seat bearings and install caps; secure verified shaft retainers/hub; set carriage tension; secure horn/servo restraint; route restrained wiring; install hatch last. Verify reverse removal with wheel fitted and removed. Retention and full guarding gates must close before claiming a complete test-ready assembly.

Evaluate axle-vertical first (nominal160×160×210), then opening-down. Use installed X2D0.4 profiles and actual slices to compare supports, removal access, bearing-seat finish, pocket roofs and layer-load directions. Footprint alone cannot release a print. Print bearing/nut/strap coupons first. Both housing orientations slice: axle-vertical1189.5 g/~29.9 h; opening-down1099.9 g/~29.8 h including supports. Estimated actual shell plastic is596.7 g versus622.6 g; hatch145.0 g plus~2.8 g supports. The support burden is substantial and visual removal review is still blocked by the desktop security prompt. No orientation is released. Carriage review uses floor-down; caps and rim have separate bed-oriented review exports.

Historical `first-prints/drive-end-section/` exports remain unchanged, pinned to `drive-fit-candidate-2026-09-19`. They are not the new complete test unit. New review exports are derived artifacts, not alternate CAD masters.

## Release gates and records

1. Measure servo ears/horn/mounts; finish supported adapter, input-bearing and shaft retention.
2. Measure battery, fitted boards, sensor depths, thermal optical/connector datums and mated cable bends; finish positive restraints and openings.
3. Obtain exact clutch assembly/interface and duty information; calibrate both breakaway and sliding torque in both directions independently of the servo.
4. Verify one connected watertight shell, no old-frame alternatives, full-travel clearance, bearing alignment, hatch extraction, and complete tool/assembly paths.
5. Source fasteners, coupon fits, establish joint preload, inspect sliced supports/toolpaths, then release prints separately.
6. Before powered tests: numeric torque/current/temperature/slip-duration limits, hold-to-run and accessible actuator cutoff. A wheel sensor alone does not identify internal slip without an input reference or another justified method. Persistent faults must stop both drives and require deliberate rearm; implementation is outside this revision.

Normal turns and the intended rounded floor transition must not require clutch slip. Normal shocks need a measured load envelope. A downstream limiter does not protect an upstream belt/pulley jam. No arbitrary torque, force or speed is declared safe. Powered operation stays held until the protective load band and shutdown/duty design are justified.

Record CAD, slicing and physical observations separately in `test-record.json`. Commit source, parameters, BOM and records together; regenerate `checks/model-review.json` after saving the native source. Git preserves superseded proposals; this is the canonical current plan.
