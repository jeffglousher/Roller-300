# Chassis print fit review

Scope: geometric fit, hardware insertion/retention, driver access and print cleanup for an unpowered PETG article. This is not a load or strength qualification. No physical print or hardware receiving test has been performed.

The fresh S20 native baseline is `Roller-300.nbcad`, SHA256 `bf4561cd9261083763b1f117bf14007dcaf6202b5efd19679aec39a4e36bd52b`, 2015 features. The independent native replay reports zero errors. S21 corrections are recorded separately; the findings below identify what triggered them.

## Confirmed fit findings

- The actual moving wheel-to-mouth-retainer gap is **0.5 mm** on both sides, while the wheel-to-shell end gap is5 mm. At the permitted0.2 mm wheel endplay, the retainer clearance can fall to0.3 mm before printed runout/warp. Native overlap is zero; the PETG wheel must still rotate freely while pushed to both axial stops. See `fresh-native-wheel-clearances.json`.
- Fresh STEP envelopes give rigid wheel diameter230 mm, wheel outer faces atY±150 (300 mm wide), shaft endpointsY±158 (**316 mm metal width**), and tread placeholders diameter246 mm. The tread is a planning envelope. Without that8 mm radial tread, nominal shell belly ground clearance is35 mm, rather than43 mm. No additional wheel end screw is modeled; clamp screw projection is not represented by the generic hub/collar envelopes.
- Four wheel D4.4 bores are correctly centered on a16 mm square and cross the4 mm webY133.5..137.5. However, the old closed outboard plateY142..150 blocked every straight driver. Exact D3.5 cylinder probes intersect76.969 mm³ at each position on both wheels, although nominal D7x4 socket heads themselves fit. See `wheel-driver-probes.json`. S21 must remove the obstruction in native CAD before a new wheel project is used.
- The old closed wheel also enclosed broad D216 support cavities. Historical actual G-code contains approximately105.9 g of supports below the hub web and42.4 g in the4.5 mm shallow cavity above it. Four small screw ports alone do not establish removal of that support. See `wheel-support-cavities.json`. Opening both faces preserves the hub web/rim and provides direct cleanup and driver paths; the fresh candidate still needs a new slice and cleanup inspection.
- The structural hatch141 and electronics envelope bodies15/16/17 are absent from the active native S20 inventory. Historical curved-hatch and complete-shell projects are not a current closed-chassis release. The shell mesh is valid, but a complete closure/retention and electronics package is unqualified.
- Full-shell straight access to the rear carrier screw is obstructed by the upper guard; the roof-open fixture373 avoids the guard. The independent native agent owns the specific corridor correction and its fresh probes.

## Receiving fit gates

Use actual purchased hardware to qualify printed holes; nominal CAD clearance does not establish a PETG fit. Do not apply a universal hole compensation based only on a successful slice.

1. Print the25.48 g /1 h16 min five-piece receiving gate. Check the actual metal horn pilot and four M4x6 screws, REX AF7.3 bores, factory clip seating/removal through its slot, the bridge face-loaded nuts, and retainer passages. The clip roof bridge and receiving fits are physical test targets.
2. Print the55.05 g /2 h22 min isolated carrier trial. Check actual608 bearings in the22.2 mm seats, their full seating/removal and free rotation, actual M3 nuts in AF6/depth2.8 captures, M4 nuts in their captures, and both unsupported nut-channel roofs. The two longest unsupported roof wall runs are9.12/16.37 mm; slicer bridge labels alone do not qualify their quality.
3. Test the roof-open fixture before the whole shell. Load the three carrier nuts from their intended ports, fit washers and screws, exercise the complete adjustment range, then assemble the shaft/hub/spacer stack and set measured endplay without loading bearing outer races. Verify all drivers with real tools.
4. Use a fresh open-face wheel candidate only after those fits. Check the D14.4 pilot against the actual D14 metal hub, D4.4 bores with four actual M4x10 screws, head and driver insertion, nominal6 mm thread engagement without bottoming, and actual clamp screw access. Bench-assemble the wheel/hub first. The purchased Hyper Hub and collar clamp screw geometry remains unmodeled; no virtual clamp-access pass is claimed.
5. Check full chassis running clearance with the wheel installed at both axial stops, across a complete revolution. Measure wheel face runout near the retainer and remove only residual support material. If the actual gap closes, correct the CAD clearance/stack before a second expensive print.

If a carrier seat fails, use a short native CAD coupon in the same print orientation and local wall construction before changing the whole assembly. A candidate22.1/22.2/22.3/22.4 mm bearing-seat ladder brackets the current22.2 mm starting value. Actual nuts and shafts should be tried in the unchanged receiving parts first; a cosmetic or unrelated coupon does not qualify their narrow roofs/capture entrances.

Current source inconsistencies identified for register correction: `parameters.wheel_collars` retains the oldY35.5..44.5 collar/10 mm spacer language; the current assembly isY85.8..94.8 plus3 mm inboard and6+2 mm outboard spacers. BOM H08 provisionally counts four M3x12 servo-ear screws, while the active servo/PLAN describes M3x10. The extra2 mm tip travel requires clearance verification; correct engagement alone is insufficient. Wheel screws H04 and carrier washers H19 remain exact-candidate/source receiving gates.

Historical `first-prints/drive-unit/README.md` has been explicitly superseded. All closed-face606/609 g wheel projects are historical; they must not be treated as the new open-face wheel slice.

## Validated S21 fit candidate

The native candidate `.local/s21-chassis-access-replayed.nbcad` has2033 features, zero replay errors, source SHA256 `f44c1acb824ed2a0a4b773db5265e754d7f9c1fd45e0c9c5e64d964533201312`. It removes both wheel closure faces insideR108, preserving the4 mm mounting web and7 mm radial rim, and adds the rear carrier driver passages. Native exact probes report valid one-solid wheels, unobstructed head/driver/shank paths, and wheel-to-retainer clearance24 mm (23.8 mm at inward0.2 mm play); the former0.5 mm clearance finding is resolved by the open-face correction.

The selected held wheel project is [the outboard-face-down candidate](../../first-prints/chassis-fit-2026-10-07/outboard-down/Roller-300-wheel-open-fit.3mf): **336.71 g /8 h38 min**, X2D main nozzle, PETG,0.4 mm,0.2 mm,5 walls,15% gyroid and normal auto supports. Its4064 triangles preserve the native STL connectivity and vertices within0.0000043 mm after rigid placement. The actual G-code has one connected annular first layer, minimum10.137 mm bed margin, support atZ0.2..12.4 only, and zero support in the mounting/pilot bores or above the retained web. Outer/inner wall widths are at least0.42 mm; sub0.2 mm paths are gap fill, not structural walls.

Approximately87.38 g of support remains beneath the web, directly accessible through theD216 bed-facing opening. Physical support removal and actual hardware/PETG fits remain tests. The alternative inboard-down candidate is preserved for inspection at398.76 g /9 h52 min; flipping the unchanged wheel saves62.05 g and1 h13 min. Do not print both candidates.

Evidence: `s21-wheel-outboard-toolpaths.json`, `s21-access/exact-fit-inspection.json` and the selected project's `wheel-slice-check.json`. Canonical native save/provenance reconciliation is owned by the root review; no wheel print or whole-chassis release is implied by this candidate slice.
