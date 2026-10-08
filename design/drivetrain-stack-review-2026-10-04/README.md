# Individual drivetrain review — 2026-10-04

These images are fresh captures from the native noBS CAD desktop, opened from `Roller-300.nbcad`. No independent renderer was used. The canonical file was not saved or modified for this review.

- `one-drive-stack-native.png`: isolated assembled left drive, without wheel, tread or housing. Orange identifies the current clutch reaction plate and split pressure pads. Magenta identifies the provisional servo shaft clamp; it is not a finalized horn adapter. Grey cylinders at the adjusters are spring envelopes, not detailed spring coils.
- `one-drive-top-native.png`: axial stack and belt alignment viewed from above.
- `one-drive-fixture-native.png`: the same drivetrain installed in its roof-open one-drive fit section.
- `clutch-exploded-native.png`: native assembly occurrence poses separated for illustration. From lower left to upper right: metal shaft hub, reaction plate, front lining, pulley/rotor, rear lining, split pressure pads, one representative adjuster/spring/guide/washer group, removable journal bush. The assembled design uses four adjusters. Explosion distances are illustrative; the pressure pads install radially. All moved occurrence poses were restored after capture.

## Start the fit article independently of the barrel

Use the existing native-export STL files in `first-prints/drivetrain-fit-2026-10-03`. Material/nozzle: PETG, 0.4 mm; the recorded offline slice uses 0.2 mm layers, five walls and 15% gyroid. This is an unpowered fit article. No physical fit has passed yet.

1. Print one each of the mouth, center, input-inboard and input-outboard bearing retainers. Check actual bearings, nut pockets, head seats and driver fit.
2. Print one input sliding carrier and one servo upper bridge. Check servo body/ears, guide fit and bearing seats.
3. Print the roof-open one-drive fit section after those smaller checks pass. Assemble bearings and shaft supports, verify nut loading and driver access, then check free rotation and axial play.
4. Defer the large wheel until the actual metal hub/shaft interface fits. Defer clutch-specific prints if changing the preload mechanism. The current pulley and shaft-clamp trial files remain useful geometry trials, not final powered parts.

## Common hardware that remains useful

For one drive: four 608 bearings (ServoCity 1600-0722-0008, two packs); one 8x150 mm wheel shaft (2100-0008-0150); one 8x50 mm input shaft (2100-0008-0050); one 8 mm wheel Hyper Hub (1310-0016-0008); one 8 mm wheel collar, 9 mm long (2910-0921-0008); one 8x10x3 mm inner-race spacer (1522-0010-0030, one pack); one 210-3M-09 belt (Amazon B00ISC4PHG); one candidate metal 25T round horn (ServoCity 1906-0025-0032). Use the existing BOM for exact common screw packs. Receiving checks still apply; the horn's actual servo spline and center-screw engagement need checking.

Do not substitute the stock 9 mm input collar for the modeled 6 mm collar without revising the stack. The 1.7 mm input shim total and 8x11x8 mm wheel-side spacer remain unresolved purchasing items. Clutch guides, spring washers, friction lining and locking nuts also remain unresolved; do not order guessed equivalents. Buying the common hardware does not complete a working drivetrain.

## Clutch recommendation

The current four independent preload screws are a test layout. Their settings can differ, and the two pressure-pad halves can load unevenly. Equal turns or equal spring lengths do not establish equal measured slip torque between the vehicle's two drives.

Retain a replaceable custom clutch, but develop one common metal preload adjustment acting through a guided, stiff pressure assembly. The threaded adjustment and spring seats should use metal hardware. Keep this force loop independent of the wheel-bearing axial stops. A common adjustment is a recommendation, not geometry implemented in this render; it needs a fresh envelope, insertion and interference pass.

Use one bench fixture to measure each clutch's breakaway and sustained slip torque in both directions, with a known lever radius and tangential force (torque = force x radius). Repeat after bedding the selected liner and after wear/temperature checks. Set both drives to an experimentally justified torque band; no numeric target or tolerance has been qualified. The clutches should normally remain engaged and slip only for overload protection. Wheel-speed feedback, rather than clutch preload, should handle left/right motion matching.

Before powered use: finish the metal-horn adapter and screw retention, resolve input axial stops and wheel opposing spacer, qualify the journal/lining/springs and preload mechanism, and validate the loaded assembly. The full barrel is not required for the present fit test.

Reference for the common adjustment/overload principle: [ComInTec friction torque limiter instructions](https://www.comintec.com/download/instruction-sheets/DF_DE-EN.pdf). This reference does not qualify our printed clutch.
