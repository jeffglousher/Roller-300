# Corrected full fit plate — later stage

Start with [the small receiving-fit plate](../receiving-fit-gate-2026-10-06/Roller-300-small-fit-gate.3mf). Then trial the corrected carrier alone. This full plate follows successful hardware seating, clip seating and carrier roof/nut-capture tests.

[Roller-300-full-fit-corrected.3mf](Roller-300-full-fit-corrected.3mf) contains ten unchanged S20 native print meshes. Nonprinting support blockers keep the E-clip pocket and carrier nut-loading channels clear; the large fixture and output pulley have moved to provide bed margin. X2D /0.4 mm /PETG /0.2 mm layers /five walls /15% gyroid; approximately 294.12 g /9 h 41 min. Its process overrides persist on reopening.

Fresh actual toolpaths have zero support in the queried clip/nut cavities, no first-layer footprint overlaps and a 3.92 mm bed margin. The carrier's pocket roofs include unsupported wall/overhang runs of 9.12 mm and 16.37 mm. They require a physical trial for sag and nut insertion; warning-free slicing does not establish that result. The old individual carrier slice fills those channels and should not be used for this trial.

The five small parts can be reused in the final assembly. Remove their duplicates from this plate and reslice if those first prints fit. The separate 609 g wheel remains deferred until the interfaces and carrier fit. No physical print, powered test or printer submission has occurred.

[Fresh print decision](../../design/print-decision-2026-10-06/README.md), [toolpath inspection](../../design/print-decision-2026-10-06/corrected-full-toolpaths.json), [mesh/settings validation](../../design/print-decision-2026-10-06/print-project-validation.json).
