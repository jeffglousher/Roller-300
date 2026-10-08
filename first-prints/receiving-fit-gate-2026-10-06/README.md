# Small receiving-fit test

Print [Roller-300-small-fit-gate.3mf](Roller-300-small-fit-gate.3mf) first. It contains the unchanged S20 native horn/REX adapter, input pulley, upper servo bridge, mouth retainer and one input retainer. The added support blocker is a slicer instruction and does not print.

X2D, 0.4 mm, PETG, 0.2 mm layers, five walls and 15% gyroid. Native Bambu CLI and a fresh GUI reslice agree at approximately **25.48 g / 1 h 16 min**. Reopening preserves the intended process overrides. No job was sent to a printer.

The adapter's E-clip pocket is free of support paths. Its roof bridges at Z9.4; the longest individual bridge move is 9.23 mm. Remove accessible supports from the horn recess, pulley bore/flanges and short bridge nut pockets. This is a physical bridge/fit trial; a successful slice does not establish the printed clearance.

Check the actual REX shaft slides through both keyed bores, the supplied clip seats fully without damage, the metal horn pilot and four mounting screws seat, and the actual M3 center screw fits without bottoming. Check actual nuts and screw heads in these representative captures. Check both printed pulley lands are clean and flat against bearing inner races. The carrier's bearing seats and complete shaft endplay require the later carrier/fixture assembly; these five pieces do not establish those fits.

Install the E-clip with the input module on the bench, before mounting the carrier in the fixture. A tested flat pusher clears the bench module but is obstructed by the installed fixture.

After these checks pass, print [the corrected carrier trial](../carrier-roof-trial-2026-10-06/Roller-300-carrier-roof-trial.3mf), approximately 55.05 g /2 h 22 min, for its unsupported pocket roofs, nut loading and bearing seats. Then proceed to the larger fixture/assembly and measure bearing seating, 0.2 mm nominal shaft play, 0.4 mm nominal pulley play and belt tracking. Hold the separate approximately609 g wheel until the interfaces work. Keep the article unpowered.

Fresh evidence: [print decision](../../design/print-decision-2026-10-06/README.md), [native replay](../../design/print-decision-2026-10-06/fresh-native-replay.json), [toolpath inspection](../../design/print-decision-2026-10-06/small-plate-toolpaths.json), [project geometry/settings validation](../../design/print-decision-2026-10-06/print-project-validation.json).
