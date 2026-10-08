# Historical drive-unit export — superseded, do not print this set

The instructions below describe an obsolete drivetrain and shell/hatch candidate. They do not apply to the current native assembly. The shaft stack, pulley mounting, retainers and clutch architecture have changed; do not order hardware or print a chassis from this folder.

Start with [the current five-piece receiving fit gate](../receiving-fit-gate-2026-10-06/Roller-300-small-fit-gate.3mf), then [the isolated carrier roof trial](../carrier-roof-trial-2026-10-06/Roller-300-carrier-roof-trial.3mf). The full chassis, wheel and curved hatch need their own current fit review before release. See [the current plan](../../PLAN.md).

## Archived instructions

Every file here except the `*-assembly.stl` pair is bed-oriented. Open this folder in the slicer and print the set. This is a fit assembly for one left drive with a belt and bearings. It is not a powered-test release. Bearing seats are the trial diameters already in the model.

| Part | File | Notes |
|------|------|--------|
| 24T input pulley | `input-pulley-24t.stl` | 26 × 26 × 14.5 mm. Bore 8.2 mm for the 8 mm input shaft |
| 48T output pulley | `output-pulley-48t.stl` | 49 × 49 × 14.5 mm. Bore 27 mm |
| Shaft sleeve | `output-pulley-shaft-sleeve.stl` | OD 26.6, ID 8.2, length 14.5. Slips the 48T pulley onto the 8 mm wheel shaft |
| Input carriage | `left-input-carriage-floor-down.stl` | Two input 608 seats |
| Input cap, inner | `input-cap-inner-axle-vertical.stl` | |
| Input cap, outer | `input-cap-outer-axle-vertical.stl` | |
| Wheel cap, inner | `wheel-cap-inner-axle-vertical.stl` | |
| Wheel cap, outer | `wheel-cap-outer-axle-vertical.stl` | |
| Wheel | `left-wheel-axle-vertical.stl` | Rigid rim. 246 mm OD includes tread that is not on this mesh |
| Main shell | `main-shell-opening-down.stl` | Wheel-bearing saddles. About 1.10 kg and 30 h with supports |
| Hatch | `curved-hatch-axle-vertical.stl` | About 145 g |

The `*-assembly.stl` files are the pulleys in model coordinates (input center X=49.67, both pulleys Y 75.75–90.25, axle Z=123). Do not slice those. That position centers them between the input posts at Y66–74 and Y92–100, with 1.75 mm of clearance on each side.

The pulleys are the native prototypes from `Roller-300.nbcad` (input body 10, output body 9). The sleeve is there because the 48T bore is 27 mm. It is a slip fit so the belt can be assembled. It is not the clutch.

## Bring to the bench

- Four 608 bearings. Input centers at |Y|=70 and 96. Wheel centers at |Y|=51 and 99.
- One 210-3M-09 belt (3 mm pitch, 9 mm wide, 70 teeth).
- One 8 mm input shaft, 49 mm long (Y 52 to 101).
- One 8 mm wheel shaft, 113 mm long (Y 35 to 148).
- M3 screws for the input caps. M4 screws for the wheel caps and the hatch.
- The goBILDA hub and the inboard collar if the wheel is retained the way the model shows.

Put the belt around the pulleys before the shafts go into the bearings. The servo horn and the clutch are not in this set.
