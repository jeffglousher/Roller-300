# Roller-300 — chassis access and positive REX belt drivetrain, 2026-10-07

Canonical model: `Roller-300.nbcad`, S21, 2,033 native history features. Saved through installed Limo CAD0.2.2 File/Save. Saved geometry exactly matches the validated native replay. S21 exports, exact access/fit checks and native captures are in `design/chassis-fit-review-2026-10-07`; ten smaller drivetrain print meshes remain identical to S20. S20 is preserved in `.local/before-s21-chassis-fit.nbcad.bak`. Earlier drivetrain evidence remains in `design/adversarial-review-2026-10-06`.

Scope: **unpowered, roof-open, one-drive fit and assembly test**, PETG,0.4mm nozzle on the X2D. Print the five small receiving-fit pieces first. Larger carrier/fixture and wheel prints follow successful hardware/PETG fits. No physical print, purchase or powered test has occurred. Full barrel and powered operation remain deferred.

## Adversarial corrections

- Restored shared servo/bridge datums once. Repeated datum moves had put servo ears and bridge restraints inside the servo and placed vertical bridge bores outside the bridge.
- Rounded bridge posts and fitted two side-loaded M3 captures. Four servo ear screws now also use captured nuts. Lower pad support and through-driver passages remove the former base obstruction.
- Removed both input pinch joints. The24T pulley's5mm hub could not enclose its M3 nut reliably, and the adapter's rotating pinch ear touched the carrier.
- Replaced the smooth input shaft/custom thin collar/1.7mm shim with stock48mm REX shaft, factory Eclip and catalog rear retention. Positive AF7.3 bores put the torque connection in the printed parts.
- Added integral pulley inner-race lands. A keyed bore alone did not stop axial pulley movement. Lands give0.4mm total nominal play and stop further movement at the bearing inner races.
- Replaced the unsourced8mm output stop with stock6+2mm metal spacers. Purchased horn, REX shaft and threaded end screw on the right use rotation to preserve handedness.

## Input shaft, horn and axial retention

Purchased horn: goBILDA1906-0025-0032 H25T metal servo hub, native manufacturer STEP. INJORA specifies25T/5.9mm for the owned continuous360 servo. The supplied drawing dimensions the case/ears and labels a270 variant. Its explicit37.5mm case height is used provisionally; the40.5mm table conflicts with the diagram. Received360 geometry still needs a fit check.

Left nominal positions in mm:

- Servo baseY0.5, case front38.0, spline tip42.0, ear thickness25.2..27.9.
- Horn spline entry39.0, mounting face41.6, pilot/center-screw head seat43.6. Four M4x6 heads seat at45.1, with2.5mm nominal metal engagement. Pattern16mm square, adapter D14.4/depth2.8 pilot clearance.
- A nominal low-profile M3 center head D5.7 x1.65 ends at45.25. Nominal REX starts46.5:1.25mm gap,0.883mm conservative gap to the imported shaft STEP's thread overshoot. Select actual center-screw length to seat without bottoming. Install it before inserting the input shaft.
- Stock2106-4008-0480 REX shaft spans46.5..94.5, with M4 tapped ends and factory Eclip49.8..50.5. Adapter pocket49.5..50.7 has a radial insertion window. Adapter and pulley have AF7.3 bores for nominal D8/AF7 stock.
- Input608 bearings54..61 and81..88; adapter race land ends53.8. Pulley R5.5 lands extend61.2..80.8, leaving0.4mm total nominal pulley play. Main rear flange ends79.5,0.5mm from stationary housing nominally and0.3mm at allowed travel.
- Rear stock6mm spacer88..94,0.5mm shim94..94.5,1.5mm washer94.5..96, and M4x8 button screw into the shaft end. Nominal screw engagement6.5mm. Rear metal stack and Eclip pocket give0.2mm nominal shaft travel. Check measured endplay/free rotation; do not preload bearing outer races.

The Eclip is a spring part: remove it before sliding the shaft through bearings/pulley, then install it through the adapter's window with its opening facing the shaft. Fit/remove it with the input module on the bench, before mounting the carrier in the fixture. A tested0.8x3mm flat pusher clears the bench module but intersects the installed fixture. Native probes verify printed access, not clip spring force or fatigue.

## Servo captures and carrier

Each servo uses four M3x10 ear screws. Lower AF6/depth2.8 nut pockets load from the front before installing the servo; upper bridge nuts load from the back. Two vertical M3x16 pan-head bridge screws seat atZ143.25 and terminate127.25. Bridge nuts side-load through extended ports intoZ128.7..131.5 pockets. Nominal M3 nuts are AF5.5/height2.4. Hex flats resist rotation, and installed screws prevent sideways escape. Loose nuts are not snap-retained.

Rounded OD10 posts atX34.1723 and65.1723,Y21.7 support the removable bridge. Lower nut pads have solid backing; lower bolt/head/driver corridors clear the carrier base. A0.95mm local upper nut-pocket lip is backed by4.2mm solid axial material. This revision qualifies nominal fit, not powered plastic joint strength.

Servo, horn, bearings, shaft, pulley and rear retention move together on carriers437/440. Guide keys constrain transverse movement. TravelX-2..+1mm about nominal24/48T center distance49.6723mm permits belt installation/adjustment; it does not prescribe belt stretch or tension.

Three M4x14 carrier screws per drive use9x4.3x0.8mm washers and AF7/height3.2 M4 nuts. Left fixed centers:(32.5,12),(60,50),(30.5,79). Outer nut loads horizontally through its side port; the other nuts load from below with carrier removed. Captures and driver access pass for the roof-open section373. S21 adds D4.4 vertical service bores atX30.5,Y±79 through the full-frame guardZ156..164; D3 drivers clear with0.7mm radial allowance. Use the bores with the chassis open.

## Output support and rigid belt

Uncut smooth8x150mm wheel shaft spansY8..158. Two stationary608 bearings at8..15 and98..105 provide90mm center span. Outer races seat against printed shoulders and removable retainers. The redundant rotating wheel bearing is retired.

The uncut shafts produce316mm hardware width versus the300mm wheel-face target. S21 opens both wheel faces insideD216, retaining theD230/40mm rim and4mm hub web. The fourM4x10 wheel bolts can be inserted/driven through the open face. Native wheel/retainer clearance is24mm nominal and23.8mm at inward axial travel; minimum wheel/full-shell gap is28.3mm. Bare-wheel belly clearance is35mm;43mm assumes theD246 tread allowance. The width target and tread attachment remain open.

Wheel axial stops: metal collar85.8..94.8 and3mm inner-race spacer94.8..97.8, opposed by stock1522-0010-0060 spacer105..111 plus1522-0010-0020 spacer111..113 against the wheel hub. Total8mm, nominal D10/ID8. Wheel endplay0.2mm is a receiving setting. Verify the hub's actual rear abutment and free rotation before tightening.

The48T printed output pulley remainsY65.25..79.75,14.5mm long,8.4mm shaft clearance. Purchased1309-0016-0008 Sonic hub mounting face65.25, D14 pilot to67.25; pulley pilot recessD14.2/depth2.2. Four M4x16 button screws use16mm square pattern, D4.5 bores, D8/depth4.7 recesses. Head seat75.05 leaves9.8mm plastic to the hub face and6.2mm nominal metal thread engagement. Bolt hub/pulley together on the bench; rear bearing obstructs installed straight screwdriver access. Tighten shaft clamp with input carrier removed.

Torque path: servo, metal horn, printed positive REX adapter, supported keyed input shaft,24T pulley,210-3M-09 belt, rigid48T pulley, metal Sonic hub, wheel shaft, metal wheel hub and printed wheel. Ratio2:1; belt bandY68..77. Mechanical clutch and all friction/spring/adjuster hardware are retired. No mechanical torque limiter is fitted; a toothed belt is not a calibrated overload release. Powered loads, reversal/shock and temperatures remain unqualified.

## Unpowered assembly order

1. Check small keyed bores, nut captures, head seats and bearing seats with received hardware. Remove supports carefully. Confirm servo center-screw seating before the larger fixture/wheel prints.
2. Load fixed-frame M4 nuts, fit stationary wheel bearings/retainers and leave input carrier out.
3. Bench-bolt48T pulley to Sonic hub with four M4x16 screws; verify pilot/engagement. Place loose belt around the pulley.
4. Lower hub/pulley into roof-open section. Thread wheel shaft through both bearings and hub, placing collar and stock spacers as above. Tighten hub clamp with carrier removed; check hand rotation and measured wheel endplay. Install the open-face wheel and metal wheel hub with fourM4x10 bolts through the exposed hub web; verify actual clamp-tool access before closing anything.
5. Bench-bolt metal horn to positive REX adapter with four M4x6 screws. Fit it to servo and install low-profile center screw through adapter bore. Verify seating and shaft clearance.
6. Load four servo ear nuts and two bridge nuts. Fit servo/bridge to carrier with four M3x10 and two M3x16 screws. Fit input bearings/retainers and loose keyed pulley between them.
7. Remove factory Eclip, slide REX shaft through rear bearing, pulley, front bearing and adapter. Reinstall clip through radial window. Fit rear6mm spacer,0.5mm shim, washer and M4x8 end screw. Check hand rotation, shaft/pulley endplay and inner-race contacts.
8. Offer carrier into frame at reduced center distance, fit belt, then move/clamp carrier with three M4x14 screws/washers. Confirm free hand rotation, tooth seating and flange tracking. Record actual fits; no powered test in this article.

## Evidence, printing and purchasing

`design/adversarial-review-2026-10-06/validation-summary.json`:496 nominal geometry/assembly checks,22 valid connected watertight print bodies, seven persistent native Named Views and0 history errors. Native exact interference checked27 selected bodies per side. Only simplified belt/tooth and nominal servo-spline reference overlaps remain. Dense threaded REX/screw solids were inspected separately with exported native geometry probes; no manufactured spline/thread/belt mesh qualification is claimed.

Native export preflight contains layout warnings because bodies are in assembly positions. It is not the print arrangement. S21 freshly rechecked three existing fit projects against ten unchanged native meshes within0.00005mm after translation. The open-face wheel has a separate fresh native export and rigidly placed slice; the old closed-wheel print is superseded.

Current first print: `first-prints/receiving-fit-gate-2026-10-06/Roller-300-small-fit-gate.3mf`, five unchanged native parts, approximately25.48g /1h16m. X2D, PETG,0.4mm,0.2mm layers,5 walls,15% gyroid. The clip cavity is free of support paths and its roof bridges; actual clip seating after printing is a test target. Bambu GUI reopening and fresh reslicing preserve these settings and agree with the CLI estimate. These five interfaces do not qualify the later carrier's608 housing seats or complete shaft endplay.

The old ten-part review project is superseded: its G-code filled narrow clip/nut channels with support, placed an output-pulley brim fractionally beyond the bed, and its GUI reopened with default process settings. The separately corrected full plate has support-free clip/nut channels and improved bed margins. Check the small hardware fits first, then trial the carrier's unsupported channel roofs and nut insertion before spending material on the larger fixture. The S21 open-face wheel is approximately336.71g /8h38m, outboard-face down with accessible supports; it follows receiving fits. The old609.4g closed-wheel project is superseded. Current evidence is in `design/chassis-fit-review-2026-10-07`, with prior toolpath fixes in `design/print-decision-2026-10-06`. No print sent.

Full-chassis fit remains incomplete. The suppressed historical hatch collides when restored; electronics/optics/harness mounts are inactive and require received geometry and positive retention. The uncut316mm shaft envelope does not meet the300mm wheel-width target. These are fit/interface issues to resolve before full-shell printing, separate from deferred strength work.

Seven native Named Views: overall, roof-open fit, drivetrain stack, output hub, horn/adapter, servo captures and positive REX input. `design/assembly-view-presets.json` mirrors them; view recalls preserve solid geometry. The additional `Roller-300-review-cutaway.nbcad` is inspection only: its removed half-sections must never be printed.

`BOM.xlsx` and `parts-sources.json` contain current stock retention and fasteners. Partial priced purchase subtotals:$100.12 first drive /$173.59 two drives, crediting confirmed ownership. Excludes tax, shipping, filament, unresolved hardware and final electronics. Exact carrier washer source, wheel fasteners and center-screw length remain receiving/sourcing checks. Other catalog offers retain their original check dates. No orders placed.

Current dimensions, provenance and physical gates are in `parameters.json` and `test-record.json`. Older print/model folders and records are historical.

## Historical mount capture correction, 2026-10-04

Previous S17 print set: `first-prints/drivetrain-fit-2026-10-04`; seven-part review plate: `first-prints/bambu-capture-review-2026-10-04/Roller-300-first-fit-review.3mf`. The S18 rigid-drive files supersede these assembly sets; mounting corrections remain in current geometry.

Existing M3 hex pockets are AF6/depth2.8, for nominal AF5.5/height2.4 nuts. Load mouth and input-support nuts from the back face, with the carrier on the bench; load center-support nuts radially through the existing side ports. Hex flats prevent rotation; the installed screw retains the nut. Loose nuts are not snap-retained. Input caps now have local round OD9 bosses and OD6.2/depth3.2 head seats above the original1.5 mm cap floor. Screw seating planes and bearing stack positions are unchanged. Recessed screws remain removable; no captive-screw clip is claimed.

Fixed square roots that extended through the barrel are trimmed to the160 mm OD curve. The derived roof-open fixture inherits this native feature. At S17,1,625 history features,30 print bodies,167 drivetrain checks and122 mounting checks passed. Historical captures/checks remain in `design/mount-capture-2026-10-04`; current evidence is in `design/adversarial-review-2026-10-06`.

## Future control development

Preserve independent wheel drives and the removable actuator carrier. After mass, speed, duty and power are measured, require continuous velocity control, speed/position feedback, documented local current control or a fast current limit, temperature feedback and a communication watchdog.

An electronic differential commands appropriate different speeds during turns. Traction control also needs a vehicle-motion estimate; unequal wheel speeds alone do not prove slip. Jam detection uses current and speed feedback separately. Electronic protection cannot remove the first mechanical impact.
