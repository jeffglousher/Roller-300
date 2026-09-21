# main_shell (body 32) — native feature dump

Source: `Roller-300.nbcad` → `model.json` (schema 7). Structured twin: `main_shell-32.json`.

**Dump + JSONC complete (pre-Combine16).** Chapter `design/design_v0_1_barrel_shell.nbcad.jsonc` via `tools/dump_to_jsonc.py` — **no invented geometry**. Hatch 141 blank-doc can proceed (MoveCopy5); Combine16 still needs hatch solid for final shell AABB.

## Creation
- **Extrude1** (`new_body`) from sketch **S02 A continuous exoskeleton 160OD 152ID 210L**
- Datum 21: offset **105** from origin **XZ** (basis origin `[0, -105, 0]`, normal −Y)
- Profile: concentric circles Ø160 / Ø152 centered UV `(0, 123)` → world axle Z=123
- Extent: **distance 210**, `flip: true` → body **32**
- Owning combines: **Combine1** intersect tools [71], **Combine2** intersect tools [96], **Combine3** join tools [125, 126, 127, 128, 129, 130, 131, 132], **Combine5** cut tools [143], **Combine9** join tools [144], **Combine10** join tools [147, 148, 149, 150, 151, 152, 153, 154], **Combine11** cut tools [155, 157, 158, 159, 160, 161, 162, 163], **Combine12** cut tools [164, 165, 166, 167, 168, 169, 170, 171], **Combine15** intersect tools [217], **Combine16** cut tools [141]
- Used as source: **MoveCopy5** copy → hatch body **141** (identity); hatch chapter owns post-copy hatch ops
- Tool-body prerequisites included (interesting): `[32, 71, 96, 125, 126, 127, 128, 129, 130, 131, 132, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 217]`
- Excluded transitive expand: **141** (hatch chain lives in `hatch-141.*`; Combine16 references it)

## Feature sequence (329 features — all fids/ops/extents)

| fid | Feature | Kind | Notes |
|-----|---------|------|-------|
| 21 | S02 A continuous exoskeleton 160OD 152ID 210L datum | datum_plane |  |
| 22 | S02 A continuous exoskeleton 160OD 152ID 210L | sketch | ents 2 {'circle': 2} · UV 160×160 · origin [0.0, -105.0, 0.0] |
| 23 | Extrude1 | extrude | new_body · extent {'distance': 210.0, 'type': 'distance'} · S02 A continuous exoskeleton 160OD 152ID 210L · new [32] |
| 24 | S02 B integral end guard Y-105 datum | datum_plane |  |
| 25 | S02 B integral end guard Y-105 | sketch | ents 2 {'circle': 2} · UV 160×160 · origin [0.0, -105.0, 0.0] |
| 26 | Extrude2 | extrude | join · extent {'distance': 3.0, 'type': 'distance'} · S02 B integral end guard Y-105 · tgt [32] · new [33] |
| 27 | S02 B integral end guard Y102 datum | datum_plane |  |
| 28 | S02 B integral end guard Y102 | sketch | ents 2 {'circle': 2} · UV 160×160 · origin [0.0, 102.0, 0.0] |
| 29 | Extrude3 | extrude | join · extent {'distance': 3.0, 'type': 'distance'} · S02 B integral end guard Y102 · tgt [32] · new [34] |
| 30 | S02 C output saddle at Y-99 datum | datum_plane |  |
| 31 | S02 C output saddle at Y-99 | sketch | ents 13 {'point': 7, 'line': 6} · UV 50×80 · origin [0.0, -105.0, 0.0] |
| 32 | Extrude4 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S02 C output saddle at Y-99 · tgt [32] · new [35] |
| 33 | S02 D 608 lower seat at Y-99 datum | datum_plane |  |
| 34 | S02 D 608 lower seat at Y-99 | sketch | ents 1 {'circle': 1} · UV 22.2×22.2 · origin [0.0, -105.0, 0.0] |
| 35 | Extrude5 | extrude | cut · extent {'distance': 12.0, 'type': 'distance'} · S02 D 608 lower seat at Y-99 · tgt [32] · new [36] |
| 36 | S02 E output cap service clearance Y-99 datum | datum_plane |  |
| 37 | S02 E output cap service clearance Y-99 | sketch | ents 8 {'point': 4, 'line': 4} · UV 50.6×19 · origin [0.0, -105.2, 0.0] |
| 38 | Extrude6 | extrude | cut · extent {'distance': 12.4, 'type': 'distance'} · S02 E output cap service clearance Y-99 · tgt [32] · new [37] |
| 45 | S02 H M4 cap holes Y-99 datum | datum_plane |  |
| 46 | S02 H M4 cap holes Y-99 | sketch | ents 2 {'circle': 2} · UV 40.44×4.472 · origin [0.0, 0.0, 104.0] |
| 47 | Extrude9 | extrude | cut · extent {'distance': 40.0, 'type': 'distance'} · S02 H M4 cap holes Y-99 · tgt [32, 38] · new [40, 41] |
| 48 | S02 I side-load nut pocket (-18, -99) datum | datum_plane |  |
| 49 | S02 I side-load nut pocket (-18, -99) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.3×3.5 · origin [0.0, -105.1, 0.0] |
| 50 | Extrude10 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 I side-load nut pocket (-18, -99) · tgt [32] · new [42] |
| 51 | S02 I side-load nut pocket (18, -99) datum | datum_plane |  |
| 52 | S02 I side-load nut pocket (18, -99) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.3×3.5 · origin [0.0, -105.1, 0.0] |
| 53 | Extrude11 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 I side-load nut pocket (18, -99) · tgt [32] · new [43] |
| 54 | S02 C output saddle at Y-51 datum | datum_plane |  |
| 55 | S02 C output saddle at Y-51 | sketch | ents 13 {'point': 7, 'line': 6} · UV 50×80 · origin [0.0, -57.0, 0.0] |
| 56 | Extrude12 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S02 C output saddle at Y-51 · tgt [32] · new [44] |
| 57 | S02 D 608 lower seat at Y-51 datum | datum_plane |  |
| 58 | S02 D 608 lower seat at Y-51 | sketch | ents 1 {'circle': 1} · UV 22.2×22.2 · origin [0.0, -57.0, 0.0] |
| 59 | Extrude13 | extrude | cut · extent {'distance': 12.0, 'type': 'distance'} · S02 D 608 lower seat at Y-51 · tgt [32] · new [45] |
| 60 | S02 E output cap service clearance Y-51 datum | datum_plane |  |
| 61 | S02 E output cap service clearance Y-51 | sketch | ents 8 {'point': 4, 'line': 4} · UV 50.6×19 · origin [0.0, -57.2, 0.0] |
| 62 | Extrude14 | extrude | cut · extent {'distance': 12.4, 'type': 'distance'} · S02 E output cap service clearance Y-51 · tgt [32] · new [46] |
| 69 | S02 H M4 cap holes Y-51 datum | datum_plane |  |
| 70 | S02 H M4 cap holes Y-51 | sketch | ents 2 {'circle': 2} · UV 40.44×4.472 · origin [0.0, 0.0, 104.0] |
| 71 | Extrude17 | extrude | cut · extent {'distance': 40.0, 'type': 'distance'} · S02 H M4 cap holes Y-51 · tgt [32, 47] · new [49, 50] |
| 72 | S02 I side-load nut pocket (-18, -51) datum | datum_plane |  |
| 73 | S02 I side-load nut pocket (-18, -51) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.3×3.5 · origin [0.0, -57.1, 0.0] |
| 74 | Extrude18 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 I side-load nut pocket (-18, -51) · tgt [32] · new [51] |
| 75 | S02 I side-load nut pocket (18, -51) datum | datum_plane |  |
| 76 | S02 I side-load nut pocket (18, -51) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.3×3.5 · origin [0.0, -57.1, 0.0] |
| 77 | Extrude19 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 I side-load nut pocket (18, -51) · tgt [32] · new [52] |
| 78 | S02 C output saddle at Y51 datum | datum_plane |  |
| 79 | S02 C output saddle at Y51 | sketch | ents 13 {'point': 7, 'line': 6} · UV 50×80 · origin [0.0, 45.0, 0.0] |
| 80 | Extrude20 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S02 C output saddle at Y51 · tgt [32] · new [53] |
| 81 | S02 D 608 lower seat at Y51 datum | datum_plane |  |
| 82 | S02 D 608 lower seat at Y51 | sketch | ents 1 {'circle': 1} · UV 22.2×22.2 · origin [0.0, 45.0, 0.0] |
| 83 | Extrude21 | extrude | cut · extent {'distance': 12.0, 'type': 'distance'} · S02 D 608 lower seat at Y51 · tgt [32] · new [54] |
| 84 | S02 E output cap service clearance Y51 datum | datum_plane |  |
| 85 | S02 E output cap service clearance Y51 | sketch | ents 8 {'point': 4, 'line': 4} · UV 50.6×19 · origin [0.0, 44.8, 0.0] |
| 86 | Extrude22 | extrude | cut · extent {'distance': 12.4, 'type': 'distance'} · S02 E output cap service clearance Y51 · tgt [32] · new [55] |
| 93 | S02 H M4 cap holes Y51 datum | datum_plane |  |
| 94 | S02 H M4 cap holes Y51 | sketch | ents 2 {'circle': 2} · UV 40.44×4.472 · origin [0.0, 0.0, 104.0] |
| 95 | Extrude25 | extrude | cut · extent {'distance': 40.0, 'type': 'distance'} · S02 H M4 cap holes Y51 · tgt [32, 56] · new [58, 59] |
| 96 | S02 I side-load nut pocket (-18, 51) datum | datum_plane |  |
| 97 | S02 I side-load nut pocket (-18, 51) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.3×3.5 · origin [0.0, 44.9, 0.0] |
| 98 | Extrude26 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 I side-load nut pocket (-18, 51) · tgt [32] · new [60] |
| 99 | S02 I side-load nut pocket (18, 51) datum | datum_plane |  |
| 100 | S02 I side-load nut pocket (18, 51) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.3×3.5 · origin [0.0, 44.9, 0.0] |
| 101 | Extrude27 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 I side-load nut pocket (18, 51) · tgt [32] · new [61] |
| 102 | S02 C output saddle at Y99 datum | datum_plane |  |
| 103 | S02 C output saddle at Y99 | sketch | ents 13 {'point': 7, 'line': 6} · UV 50×80 · origin [0.0, 93.0, 0.0] |
| 104 | Extrude28 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S02 C output saddle at Y99 · tgt [32] · new [62] |
| 105 | S02 D 608 lower seat at Y99 datum | datum_plane |  |
| 106 | S02 D 608 lower seat at Y99 | sketch | ents 1 {'circle': 1} · UV 22.2×22.2 · origin [0.0, 93.0, 0.0] |
| 107 | Extrude29 | extrude | cut · extent {'distance': 12.0, 'type': 'distance'} · S02 D 608 lower seat at Y99 · tgt [32] · new [63] |
| 108 | S02 E output cap service clearance Y99 datum | datum_plane |  |
| 109 | S02 E output cap service clearance Y99 | sketch | ents 8 {'point': 4, 'line': 4} · UV 50.6×19 · origin [0.0, 92.8, 0.0] |
| 110 | Extrude30 | extrude | cut · extent {'distance': 12.4, 'type': 'distance'} · S02 E output cap service clearance Y99 · tgt [32] · new [64] |
| 117 | S02 H M4 cap holes Y99 datum | datum_plane |  |
| 118 | S02 H M4 cap holes Y99 | sketch | ents 2 {'circle': 2} · UV 40.44×4.472 · origin [0.0, 0.0, 104.0] |
| 119 | Extrude33 | extrude | cut · extent {'distance': 40.0, 'type': 'distance'} · S02 H M4 cap holes Y99 · tgt [32, 65] · new [67, 68] |
| 120 | S02 I side-load nut pocket (-18, 99) datum | datum_plane |  |
| 121 | S02 I side-load nut pocket (-18, 99) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.3×3.5 · origin [0.0, 92.9, 0.0] |
| 122 | Extrude34 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 I side-load nut pocket (-18, 99) · tgt [32] · new [69] |
| 123 | S02 I side-load nut pocket (18, 99) datum | datum_plane |  |
| 124 | S02 I side-load nut pocket (18, 99) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.3×3.5 · origin [0.0, 92.9, 0.0] |
| 125 | Extrude35 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 I side-load nut pocket (18, 99) · tgt [32] · new [70] |
| 126 | S02 J outer-surface trim tool datum | datum_plane |  |
| 127 | S02 J outer-surface trim tool | sketch | ents 1 {'circle': 1} · UV 160×160 · origin [0.0, -105.0, 0.0] |
| 128 | Extrude36 | extrude | new_body · extent {'distance': 210.0, 'type': 'distance'} · S02 J outer-surface trim tool · new [71] |
| 129 | Combine1 | combine | intersect · tgt [32] · tools [71] · keep_tools=False |
| 130 | S02 K integral rail rib (34, -56) datum | datum_plane |  |
| 131 | S02 K integral rail rib (34, -56) | sketch | ents 9 {'point': 5, 'line': 4} · UV 10×45 · origin [0.0, -62.0, 0.0] |
| 132 | Extrude37 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S02 K integral rail rib (34, -56) · tgt [32] · new [72] |
| 133 | S02 L rail M4 hole (34, -56) datum | datum_plane |  |
| 134 | S02 L rail M4 hole (34, -56) | sketch | ents 1 {'circle': 1} · UV 4.4×4.4 · origin [0.0, 0.0, 79.0] |
| 135 | Extrude38 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 L rail M4 hole (34, -56) · tgt [32] · new [73] |
| 136 | S02 M rail nut insertion (34, -56) datum | datum_plane |  |
| 137 | S02 M rail nut insertion (34, -56) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.65×4.5 · origin [0.0, -62.1, 0.0] |
| 138 | Extrude39 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 M rail nut insertion (34, -56) · tgt [32] · new [74] |
| 139 | S02 K integral rail rib (61, -56) datum | datum_plane |  |
| 140 | S02 K integral rail rib (61, -56) | sketch | ents 9 {'point': 5, 'line': 4} · UV 10×45 · origin [0.0, -62.0, 0.0] |
| 141 | Extrude40 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S02 K integral rail rib (61, -56) · tgt [32] · new [75] |
| 142 | S02 L rail M4 hole (61, -56) datum | datum_plane |  |
| 143 | S02 L rail M4 hole (61, -56) | sketch | ents 1 {'circle': 1} · UV 4.4×4.4 · origin [0.0, 0.0, 79.0] |
| 144 | Extrude41 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 L rail M4 hole (61, -56) · tgt [32] · new [76] |
| 145 | S02 M rail nut insertion (61, -56) datum | datum_plane |  |
| 146 | S02 M rail nut insertion (61, -56) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.65×4 · origin [0.0, -62.1, 0.0] |
| 147 | Extrude42 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 M rail nut insertion (61, -56) · tgt [32] · new [77] |
| 148 | S02 K integral rail rib (34, -84) datum | datum_plane |  |
| 149 | S02 K integral rail rib (34, -84) | sketch | ents 9 {'point': 5, 'line': 4} · UV 10×45 · origin [0.0, -90.0, 0.0] |
| 150 | Extrude43 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S02 K integral rail rib (34, -84) · tgt [32] · new [78] |
| 151 | S02 L rail M4 hole (34, -84) datum | datum_plane |  |
| 152 | S02 L rail M4 hole (34, -84) | sketch | ents 1 {'circle': 1} · UV 4.4×4.4 · origin [0.0, 0.0, 79.0] |
| 153 | Extrude44 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 L rail M4 hole (34, -84) · tgt [32] · new [79] |
| 154 | S02 M rail nut insertion (34, -84) datum | datum_plane |  |
| 155 | S02 M rail nut insertion (34, -84) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.65×4.5 · origin [0.0, -90.1, 0.0] |
| 156 | Extrude45 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 M rail nut insertion (34, -84) · tgt [32] · new [80] |
| 157 | S02 K integral rail rib (61, -84) datum | datum_plane |  |
| 158 | S02 K integral rail rib (61, -84) | sketch | ents 9 {'point': 5, 'line': 4} · UV 10×45 · origin [0.0, -90.0, 0.0] |
| 159 | Extrude46 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S02 K integral rail rib (61, -84) · tgt [32] · new [81] |
| 160 | S02 L rail M4 hole (61, -84) datum | datum_plane |  |
| 161 | S02 L rail M4 hole (61, -84) | sketch | ents 1 {'circle': 1} · UV 4.4×4.4 · origin [0.0, 0.0, 79.0] |
| 162 | Extrude47 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 L rail M4 hole (61, -84) · tgt [32] · new [82] |
| 163 | S02 M rail nut insertion (61, -84) datum | datum_plane |  |
| 164 | S02 M rail nut insertion (61, -84) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.65×4 · origin [0.0, -90.1, 0.0] |
| 165 | Extrude48 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 M rail nut insertion (61, -84) · tgt [32] · new [83] |
| 166 | S02 K integral rail rib (34, 56) datum | datum_plane |  |
| 167 | S02 K integral rail rib (34, 56) | sketch | ents 9 {'point': 5, 'line': 4} · UV 10×45 · origin [0.0, 50.0, 0.0] |
| 168 | Extrude49 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S02 K integral rail rib (34, 56) · tgt [32] · new [84] |
| 169 | S02 L rail M4 hole (34, 56) datum | datum_plane |  |
| 170 | S02 L rail M4 hole (34, 56) | sketch | ents 1 {'circle': 1} · UV 4.4×4.4 · origin [0.0, 0.0, 79.0] |
| 171 | Extrude50 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 L rail M4 hole (34, 56) · tgt [32] · new [85] |
| 172 | S02 M rail nut insertion (34, 56) datum | datum_plane |  |
| 173 | S02 M rail nut insertion (34, 56) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.65×4.5 · origin [0.0, 49.9, 0.0] |
| 174 | Extrude51 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 M rail nut insertion (34, 56) · tgt [32] · new [86] |
| 175 | S02 K integral rail rib (61, 56) datum | datum_plane |  |
| 176 | S02 K integral rail rib (61, 56) | sketch | ents 9 {'point': 5, 'line': 4} · UV 10×45 · origin [0.0, 50.0, 0.0] |
| 177 | Extrude52 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S02 K integral rail rib (61, 56) · tgt [32] · new [87] |
| 178 | S02 L rail M4 hole (61, 56) datum | datum_plane |  |
| 179 | S02 L rail M4 hole (61, 56) | sketch | ents 1 {'circle': 1} · UV 4.4×4.4 · origin [0.0, 0.0, 79.0] |
| 180 | Extrude53 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 L rail M4 hole (61, 56) · tgt [32] · new [88] |
| 181 | S02 M rail nut insertion (61, 56) datum | datum_plane |  |
| 182 | S02 M rail nut insertion (61, 56) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.65×4 · origin [0.0, 49.9, 0.0] |
| 183 | Extrude54 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 M rail nut insertion (61, 56) · tgt [32] · new [89] |
| 184 | S02 K integral rail rib (34, 84) datum | datum_plane |  |
| 185 | S02 K integral rail rib (34, 84) | sketch | ents 9 {'point': 5, 'line': 4} · UV 10×45 · origin [0.0, 78.0, 0.0] |
| 186 | Extrude55 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S02 K integral rail rib (34, 84) · tgt [32] · new [90] |
| 187 | S02 L rail M4 hole (34, 84) datum | datum_plane |  |
| 188 | S02 L rail M4 hole (34, 84) | sketch | ents 1 {'circle': 1} · UV 4.4×4.4 · origin [0.0, 0.0, 79.0] |
| 189 | Extrude56 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 L rail M4 hole (34, 84) · tgt [32] · new [91] |
| 190 | S02 M rail nut insertion (34, 84) datum | datum_plane |  |
| 191 | S02 M rail nut insertion (34, 84) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.65×4.5 · origin [0.0, 77.9, 0.0] |
| 192 | Extrude57 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 M rail nut insertion (34, 84) · tgt [32] · new [92] |
| 193 | S02 K integral rail rib (61, 84) datum | datum_plane |  |
| 194 | S02 K integral rail rib (61, 84) | sketch | ents 9 {'point': 5, 'line': 4} · UV 10×45 · origin [0.0, 78.0, 0.0] |
| 195 | Extrude58 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S02 K integral rail rib (61, 84) · tgt [32] · new [93] |
| 196 | S02 L rail M4 hole (61, 84) datum | datum_plane |  |
| 197 | S02 L rail M4 hole (61, 84) | sketch | ents 1 {'circle': 1} · UV 4.4×4.4 · origin [0.0, 0.0, 79.0] |
| 198 | Extrude59 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 L rail M4 hole (61, 84) · tgt [32] · new [94] |
| 199 | S02 M rail nut insertion (61, 84) datum | datum_plane |  |
| 200 | S02 M rail nut insertion (61, 84) | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.65×4 · origin [0.0, 77.9, 0.0] |
| 201 | Extrude60 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S02 M rail nut insertion (61, 84) · tgt [32] · new [95] |
| 202 | S02 N trim rail roots to shell outside datum | datum_plane |  |
| 203 | S02 N trim rail roots to shell outside | sketch | ents 1 {'circle': 1} · UV 160×160 · origin [0.0, -105.0, 0.0] |
| 204 | Extrude61 | extrude | new_body · extent {'distance': 210.0, 'type': 'distance'} · S02 N trim rail roots to shell outside · new [96] |
| 205 | Combine2 | combine | intersect · tgt [32] · tools [96] · keep_tools=False |
| 278 | S02 Y wheel outer-race axial shoulder master datum | datum_plane |  |
| 279 | S02 Y wheel outer-race axial shoulder master | sketch | ents 10 {'arc': 2, 'point': 6, 'line': 2} · UV 22.3×22.3 · origin [0.0, -105.0, 0.0] |
| 280 | Extrude85 | extrude | new_body · extent {'distance': 2.4, 'type': 'distance'} · S02 Y wheel outer-race axial shoulder master · new [125] |
| 281 | RectangularPattern1 | rectangular_pattern | new [126] · from [125] · count 2 spacing 9.6 |
| 282 | RectangularPattern2 | rectangular_pattern | new [127, 128] · from [125, 126] · count 2 spacing 48.0 |
| 283 | Mirror3 | mirror | new [129, 130, 131, 132] · from [125, 126, 127, 128] |
| 284 | Combine3 | combine | join · tgt [32] · tools [125, 126, 127, 128, 129, 130, 131, 132] · keep_tools=False |
| 291 | MoveCopy5 | move_copy | new [141] · from [32] · copy=True · T {'x': 0.0, 'y': 0.0, 'z': 0.0} |
| 296 | S03 B hatch opening with 0p3 perimeter clearance datum | datum_plane |  |
| 297 | S03 B hatch opening with 0p3 perimeter clearance | sketch | ents 21 {'point': 13, 'line': 4, 'arc': 4} · UV 138.6×180 · origin [0.0, 0.0, 123.0] |
| 298 | Extrude89 | extrude | new_body · extent {'distance': 110.0, 'type': 'distance'} · S03 B hatch opening with 0p3 perimeter clearance · new [143] |
| 299 | Combine5 | combine | cut · tgt [32] · tools [143] · keep_tools=False |
| 300 | S03 C curved structural lap ledge R72 to77 datum | datum_plane |  |
| 301 | S03 C curved structural lap ledge R72 to77 | sketch | ents 2 {'circle': 2} · UV 154×154 · origin [0.0, -98.0, 0.0] |
| 302 | Extrude90 | extrude | new_body · extent {'distance': 196.0, 'type': 'distance'} · S03 C curved structural lap ledge R72 to77 · new [144] |
| 303 | S03 D ledge outer boundary datum | datum_plane |  |
| 304 | S03 D ledge outer boundary | sketch | ents 21 {'point': 13, 'line': 4, 'arc': 4} · UV 154.6×196 · origin [0.0, 0.0, 123.0] |
| 305 | Extrude91 | extrude | new_body · extent {'distance': 110.0, 'type': 'distance'} · S03 D ledge outer boundary · new [145] |
| 306 | Combine6 | combine | intersect · tgt [144] · tools [145] · keep_tools=False |
| 307 | S03 E clear center of lap ledge datum | datum_plane |  |
| 308 | S03 E clear center of lap ledge | sketch | ents 21 {'point': 13, 'line': 4, 'arc': 4} · UV 122.6×164 · origin [0.0, 0.0, 123.0] |
| 309 | Extrude92 | extrude | new_body · extent {'distance': 110.0, 'type': 'distance'} · S03 E clear center of lap ledge · new [146] |
| 310 | Combine7 | combine | cut · tgt [144] · tools [146] · keep_tools=False |
| 311 | Combine8 | combine | cut · tgt [144] · tools [141] · keep_tools=True |
| 312 | Combine9 | combine | join · tgt [32] · tools [144] · keep_tools=False |
| 313 | S03 F radial M4 nut boss master datum | datum_plane |  |
| 314 | S03 F radial M4 nut boss master | sketch | ents 1 {'circle': 1} · UV 12×12 · origin [0.0, 0.0, 191.0] |
| 315 | Extrude93 | extrude | new_body · extent {'distance': 8.0, 'type': 'distance'} · S03 F radial M4 nut boss master · new [147] |
| 316 | MoveCopy6 | move_copy | new [147] · from [147] · copy=False · T {'x': 0.0, 'y': -75.0, 'z': 0.0} · quat [0.0, 0.4617486132350339, 0.0, 0.8870108331782217] |
| 317 | RectangularPattern3 | rectangular_pattern | new [148, 149, 150] · from [147] · count 4 spacing 50.0 |
| 318 | Mirror4 | mirror | new [151, 152, 153, 154] · from [147, 148, 149, 150] |
| 319 | Combine10 | combine | join · tgt [32] · tools [147, 148, 149, 150, 151, 152, 153, 154] · keep_tools=False |
| 320 | S03 G hex nut pocket master datum | datum_plane |  |
| 321 | S03 G hex nut pocket master | sketch | ents 13 {'point': 7, 'line': 6} · UV 7.3×8.429 · origin [0.0, 0.0, 193.0] |
| 322 | Extrude94 | extrude | new_body · extent {'distance': 3.5, 'type': 'distance'} · S03 G hex nut pocket master · new [155] |
| 323 | S03 H nut side insertion master datum | datum_plane |  |
| 324 | S03 H nut side insertion master | sketch | ents 8 {'point': 4, 'line': 4} · UV 7.3×7 · origin [0.0, 0.0, 193.0] |
| 325 | Extrude95 | extrude | join · extent {'distance': 3.5, 'type': 'distance'} · S03 H nut side insertion master · tgt [155] · new [156] |
| 326 | MoveCopy7 | move_copy | new [155] · from [155] · copy=False · T {'x': 0.0, 'y': -75.0, 'z': 0.0} · quat [0.0, 0.4617486132350339, 0.0, 0.8870108331782217] |
| 327 | RectangularPattern4 | rectangular_pattern | new [157, 158, 159] · from [155] · count 4 spacing 50.0 |
| 328 | Mirror5 | mirror | new [160, 161, 162, 163] · from [155, 157, 158, 159] |
| 329 | Combine11 | combine | cut · tgt [32] · tools [155, 157, 158, 159, 160, 161, 162, 163] · keep_tools=False |
| 330 | S03 I radial screw clearance master datum | datum_plane |  |
| 331 | S03 I radial screw clearance master | sketch | ents 1 {'circle': 1} · UV 4.4×4.4 · origin [0.0, 0.0, 190.0] |
| 332 | Extrude96 | extrude | new_body · extent {'distance': 18.0, 'type': 'distance'} · S03 I radial screw clearance master · new [164] |
| 333 | MoveCopy8 | move_copy | new [164] · from [164] · copy=False · T {'x': 0.0, 'y': -75.0, 'z': 0.0} · quat [0.0, 0.4617486132350339, 0.0, 0.8870108331782217] |
| 334 | RectangularPattern5 | rectangular_pattern | new [165, 166, 167] · from [164] · count 4 spacing 50.0 |
| 335 | Mirror6 | mirror | new [168, 169, 170, 171] · from [164, 165, 166, 167] |
| 336 | Combine12 | combine | cut · tgt [32] · tools [164, 165, 166, 167, 168, 169, 170, 171] · keep_tools=True |
| 345 | S04 A battery support rib Y-17 datum | datum_plane |  |
| 346 | S04 A battery support rib Y-17 | sketch | ents 8 {'point': 4, 'line': 4} · UV 74×34 · origin [0.0, -18.5, 0.0] |
| 347 | Extrude97 | extrude | join · extent {'distance': 3.0, 'type': 'distance'} · S04 A battery support rib Y-17 · tgt [32] · new [180] |
| 348 | S04 A battery support rib Y17 datum | datum_plane |  |
| 349 | S04 A battery support rib Y17 | sketch | ents 8 {'point': 4, 'line': 4} · UV 74×34 · origin [0.0, 15.5, 0.0] |
| 350 | Extrude98 | extrude | join · extent {'distance': 3.0, 'type': 'distance'} · S04 A battery support rib Y17 · tgt [32] · new [181] |
| 351 | S04 B battery platform for UNMEASURED allowance datum | datum_plane |  |
| 352 | S04 B battery platform for UNMEASURED allowance | sketch | ents 8 {'point': 4, 'line': 4} · UV 82×3 · origin [0.0, -22.0, 0.0] |
| 353 | Extrude99 | extrude | join · extent {'distance': 44.0, 'type': 'distance'} · S04 B battery platform for UNMEASURED allowance · tgt [32] · new [182] |
| 354 | S04 C battery strap passage (-40, -19.5) datum | datum_plane |  |
| 355 | S04 C battery strap passage (-40, -19.5) | sketch | ents 8 {'point': 4, 'line': 4} · UV 12×7 · origin [0.0, -21.0, 0.0] |
| 356 | Extrude100 | extrude | cut · extent {'distance': 3.0, 'type': 'distance'} · S04 C battery strap passage (-40, -19.5) · tgt [32] · new [183] |
| 357 | S04 C battery strap passage (-40, 19.5) datum | datum_plane |  |
| 358 | S04 C battery strap passage (-40, 19.5) | sketch | ents 8 {'point': 4, 'line': 4} · UV 12×7 · origin [0.0, 18.0, 0.0] |
| 359 | Extrude101 | extrude | cut · extent {'distance': 3.0, 'type': 'distance'} · S04 C battery strap passage (-40, 19.5) · tgt [32] · new [184] |
| 360 | S04 C battery strap passage (5, -19.5) datum | datum_plane |  |
| 361 | S04 C battery strap passage (5, -19.5) | sketch | ents 8 {'point': 4, 'line': 4} · UV 12×7 · origin [0.0, -21.0, 0.0] |
| 362 | Extrude102 | extrude | cut · extent {'distance': 3.0, 'type': 'distance'} · S04 C battery strap passage (5, -19.5) · tgt [32] · new [185] |
| 363 | S04 C battery strap passage (5, 19.5) datum | datum_plane |  |
| 364 | S04 C battery strap passage (5, 19.5) | sketch | ents 8 {'point': 4, 'line': 4} · UV 12×7 · origin [0.0, 18.0, 0.0] |
| 365 | Extrude103 | extrude | cut · extent {'distance': 3.0, 'type': 'distance'} · S04 C battery strap passage (5, 19.5) · tgt [32] · new [186] |
| 366 | S04 D battery lateral stop Y-20 datum | datum_plane |  |
| 367 | S04 D battery lateral stop Y-20 | sketch | ents 8 {'point': 4, 'line': 4} · UV 74×3 · origin [0.0, -20.0, 0.0] |
| 368 | Extrude104 | extrude | join · extent {'distance': 1.5, 'type': 'distance'} · S04 D battery lateral stop Y-20 · tgt [32] · new [187] |
| 369 | S04 D battery lateral stop Y18.5 datum | datum_plane |  |
| 370 | S04 D battery lateral stop Y18.5 | sketch | ents 8 {'point': 4, 'line': 4} · UV 74×3 · origin [0.0, 18.5, 0.0] |
| 371 | Extrude105 | extrude | join · extent {'distance': 1.5, 'type': 'distance'} · S04 D battery lateral stop Y18.5 · tgt [32] · new [188] |
| 373 | S04 E Pi support bridge -79 datum | datum_plane |  |
| 374 | S04 E Pi support bridge -79 | sketch | ents 8 {'point': 4, 'line': 4} · UV 46×4 · origin [0.0, -81.0, 0.0] |
| 375 | Extrude106 | extrude | join · extent {'distance': 4.0, 'type': 'distance'} · S04 E Pi support bridge -79 · tgt [32] · new [189] |
| 376 | S04 E Pi support bridge -24 datum | datum_plane |  |
| 377 | S04 E Pi support bridge -24 | sketch | ents 8 {'point': 4, 'line': 4} · UV 46×4 · origin [0.0, -26.0, 0.0] |
| 378 | Extrude107 | extrude | join · extent {'distance': 4.0, 'type': 'distance'} · S04 E Pi support bridge -24 · tgt [32] · new [190] |
| 379 | S04 F Pi integral shelf datum | datum_plane |  |
| 380 | S04 F Pi integral shelf | sketch | ents 8 {'point': 4, 'line': 4} · UV 32×2.5 · origin [0.0, -85.0, 0.0] |
| 381 | Extrude108 | extrude | join · extent {'distance': 67.0, 'type': 'distance'} · S04 F Pi integral shelf · tgt [32] · new [191] |
| 382 | S04 G Pi edge registration -31 datum | datum_plane |  |
| 383 | S04 G Pi edge registration -31 | sketch | ents 8 {'point': 4, 'line': 4} · UV 0.7×1.5 · origin [0.0, -84.0, 0.0] |
| 384 | Extrude109 | extrude | join · extent {'distance': 65.0, 'type': 'distance'} · S04 G Pi edge registration -31 · tgt [32] · new [192] |
| 385 | S04 G Pi edge registration -0.0 datum | datum_plane |  |
| 386 | S04 G Pi edge registration -0.0 | sketch | ents 8 {'point': 4, 'line': 4} · UV 0.7×1.5 · origin [0.0, -84.0, 0.0] |
| 387 | Extrude110 | extrude | join · extent {'distance': 65.0, 'type': 'distance'} · S04 G Pi edge registration -0.0 · tgt [32] · new [193] |
| 388 | S04 H Pixracer support bridge 49 datum | datum_plane |  |
| 389 | S04 H Pixracer support bridge 49 | sketch | ents 8 {'point': 4, 'line': 4} · UV 36×4 · origin [0.0, 47.0, 0.0] |
| 390 | Extrude111 | extrude | join · extent {'distance': 4.0, 'type': 'distance'} · S04 H Pixracer support bridge 49 · tgt [32] · new [194] |
| 391 | S04 H Pixracer support bridge 79 datum | datum_plane |  |
| 392 | S04 H Pixracer support bridge 79 | sketch | ents 8 {'point': 4, 'line': 4} · UV 36×4 · origin [0.0, 77.0, 0.0] |
| 393 | Extrude112 | extrude | join · extent {'distance': 4.0, 'type': 'distance'} · S04 H Pixracer support bridge 79 · tgt [32] · new [195] |
| 394 | S04 I original Pixracer shelf - height and retainers HOLD datum | datum_plane |  |
| 395 | S04 I original Pixracer shelf - height and retainers HOLD | sketch | ents 8 {'point': 4, 'line': 4} · UV 38×3 · origin [0.0, 45.0, 0.0] |
| 396 | Extrude113 | extrude | join · extent {'distance': 38.0, 'type': 'distance'} · S04 I original Pixracer shelf - height and retainers HOLD · tgt [32] · new [196] |
| 397 | S04 I2 inner wheel-cap driver access through board shelves datum | datum_plane |  |
| 398 | S04 I2 inner wheel-cap driver access through board shelves | sketch | ents 2 {'circle': 2} · UV 8×110 · origin [0.0, 0.0, 157.0] |
| 399 | Extrude114 | extrude | cut · extent {'distance': 13.0, 'type': 'distance'} · S04 I2 inner wheel-cap driver access through board shelves · tgt [32] · new [197, 198] |
| 403 | S04 J thermal cradle shell rib -34 datum | datum_plane |  |
| 404 | S04 J thermal cradle shell rib -34 | sketch | ents 8 {'point': 4, 'line': 4} · UV 40×6 · origin [0.0, -35.5, 0.0] |
| 405 | Extrude115 | extrude | join · extent {'distance': 3.0, 'type': 'distance'} · S04 J thermal cradle shell rib -34 · tgt [32] · new [199] |
| 406 | S04 J thermal cradle shell rib 34 datum | datum_plane |  |
| 407 | S04 J thermal cradle shell rib 34 | sketch | ents 8 {'point': 4, 'line': 4} · UV 40×6 · origin [0.0, 32.5, 0.0] |
| 408 | Extrude116 | extrude | join · extent {'distance': 3.0, 'type': 'distance'} · S04 J thermal cradle shell rib 34 · tgt [32] · new [200] |
| 409 | S04 K thermal cradle base datum | datum_plane |  |
| 410 | S04 K thermal cradle base | sketch | ents 8 {'point': 4, 'line': 4} · UV 23×3 · origin [0.0, -37.0, 0.0] |
| 411 | Extrude117 | extrude | join · extent {'distance': 74.0, 'type': 'distance'} · S04 K thermal cradle base · tgt [32] · new [201] |
| 412 | S04 L thermal side registration -37 datum | datum_plane |  |
| 413 | S04 L thermal side registration -37 | sketch | ents 8 {'point': 4, 'line': 4} · UV 14×5 · origin [0.0, -37.0, 0.0] |
| 414 | Extrude118 | extrude | join · extent {'distance': 1.2, 'type': 'distance'} · S04 L thermal side registration -37 · tgt [32] · new [202] |
| 415 | S04 L thermal side registration 35.8 datum | datum_plane |  |
| 416 | S04 L thermal side registration 35.8 | sketch | ents 8 {'point': 4, 'line': 4} · UV 14×5 · origin [0.0, 35.8, 0.0] |
| 417 | Extrude119 | extrude | join · extent {'distance': 1.2, 'type': 'distance'} · S04 L thermal side registration 35.8 · tgt [32] · new [203] |
| 418 | S04 M thermal rear registration datum | datum_plane |  |
| 419 | S04 M thermal rear registration | sketch | ents 8 {'point': 4, 'line': 4} · UV 1.7×4 · origin [0.0, -35.5, 0.0] |
| 420 | Extrude120 | extrude | join · extent {'distance': 71.0, 'type': 'distance'} · S04 M thermal rear registration · tgt [32] · new [204] |
| 421 | S04 M2 thermal strap passage (25.5, -20) datum | datum_plane |  |
| 422 | S04 M2 thermal strap passage (25.5, -20) | sketch | ents 8 {'point': 4, 'line': 4} · UV 2×5 · origin [0.0, -25.0, 0.0] |
| 423 | Extrude121 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S04 M2 thermal strap passage (25.5, -20) · tgt [32] · new [205] |
| 424 | S04 M2 thermal strap passage (25.5, 20) datum | datum_plane |  |
| 425 | S04 M2 thermal strap passage (25.5, 20) | sketch | ents 8 {'point': 4, 'line': 4} · UV 2×5 · origin [0.0, 15.0, 0.0] |
| 426 | Extrude122 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S04 M2 thermal strap passage (25.5, 20) · tgt [32] · new [206] |
| 427 | S04 M2 thermal strap passage (42.5, -20) datum | datum_plane |  |
| 428 | S04 M2 thermal strap passage (42.5, -20) | sketch | ents 8 {'point': 4, 'line': 4} · UV 2×5 · origin [0.0, -25.0, 0.0] |
| 429 | Extrude123 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S04 M2 thermal strap passage (42.5, -20) · tgt [32] · new [207] |
| 430 | S04 M2 thermal strap passage (42.5, 20) datum | datum_plane |  |
| 431 | S04 M2 thermal strap passage (42.5, 20) | sketch | ents 8 {'point': 4, 'line': 4} · UV 2×5 · origin [0.0, 15.0, 0.0] |
| 432 | Extrude124 | extrude | cut · extent {'distance': 10.0, 'type': 'distance'} · S04 M2 thermal strap passage (42.5, 20) · tgt [32] · new [208] |
| 433 | S04 N sensor locating rail Z109 datum | datum_plane |  |
| 434 | S04 N sensor locating rail Z109 | sketch | ents 8 {'point': 4, 'line': 4} · UV 7×3 · origin [0.0, -48.0, 0.0] |
| 435 | Extrude125 | extrude | join · extent {'distance': 96.0, 'type': 'distance'} · S04 N sensor locating rail Z109 · tgt [32] · new [209] |
| 436 | S04 N sensor locating rail Z127 datum | datum_plane |  |
| 437 | S04 N sensor locating rail Z127 | sketch | ents 8 {'point': 4, 'line': 4} · UV 7×3 · origin [0.0, -48.0, 0.0] |
| 438 | Extrude126 | extrude | join · extent {'distance': 96.0, 'type': 'distance'} · S04 N sensor locating rail Z127 · tgt [32] · new [210] |
| 447 | S04 O harness saddle -65 datum | datum_plane |  |
| 448 | S04 O harness saddle -65 | sketch | ents 8 {'point': 4, 'line': 4} · UV 12×5 · origin [0.0, -71.0, 0.0] |
| 449 | Extrude127 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S04 O harness saddle -65 · tgt [32] · new [211] |
| 450 | S04 P harness tie passage -65 datum | datum_plane |  |
| 451 | S04 P harness tie passage -65 | sketch | ents 8 {'point': 4, 'line': 4} · UV 10×2 · origin [0.0, -67.0, 0.0] |
| 452 | Extrude128 | extrude | cut · extent {'distance': 4.0, 'type': 'distance'} · S04 P harness tie passage -65 · tgt [32] · new [212] |
| 453 | S04 O harness saddle 0 datum | datum_plane |  |
| 454 | S04 O harness saddle 0 | sketch | ents 8 {'point': 4, 'line': 4} · UV 12×5 · origin [0.0, -6.0, 0.0] |
| 455 | Extrude129 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S04 O harness saddle 0 · tgt [32] · new [213] |
| 456 | S04 P harness tie passage 0 datum | datum_plane |  |
| 457 | S04 P harness tie passage 0 | sketch | ents 8 {'point': 4, 'line': 4} · UV 10×2 · origin [0.0, -2.0, 0.0] |
| 458 | Extrude130 | extrude | cut · extent {'distance': 4.0, 'type': 'distance'} · S04 P harness tie passage 0 · tgt [32] · new [214] |
| 459 | S04 O harness saddle 65 datum | datum_plane |  |
| 460 | S04 O harness saddle 65 | sketch | ents 8 {'point': 4, 'line': 4} · UV 12×5 · origin [0.0, 59.0, 0.0] |
| 461 | Extrude131 | extrude | join · extent {'distance': 12.0, 'type': 'distance'} · S04 O harness saddle 65 · tgt [32] · new [215] |
| 462 | S04 P harness tie passage 65 datum | datum_plane |  |
| 463 | S04 P harness tie passage 65 | sketch | ents 8 {'point': 4, 'line': 4} · UV 10×2 · origin [0.0, 63.0, 0.0] |
| 464 | Extrude132 | extrude | cut · extent {'distance': 4.0, 'type': 'distance'} · S04 P harness tie passage 65 · tgt [32] · new [216] |
| 465 | S04 Q trim direct mounts at outside barrel surface datum | datum_plane |  |
| 466 | S04 Q trim direct mounts at outside barrel surface | sketch | ents 1 {'circle': 1} · UV 160×160 · origin [0.0, -105.0, 0.0] |
| 467 | Extrude133 | extrude | new_body · extent {'distance': 210.0, 'type': 'distance'} · S04 Q trim direct mounts at outside barrel surface · new [217] |
| 468 | Combine15 | combine | intersect · tgt [32] · tools [217] · keep_tools=False |
| 476 | S02 assembly L outer bearing lowering clearance datum | datum_plane |  |
| 477 | S02 assembly L outer bearing lowering clearance | sketch | ents 8 {'point': 4, 'line': 4} · UV 24×24 · origin [0.0, 102.0, 0.0] |
| 478 | Extrude136 | extrude | cut · extent {'distance': 1.0, 'type': 'distance'} · S02 assembly L outer bearing lowering clearance · tgt [32] · new [220] |
| 486 | S02 assembly R outer bearing lowering clearance datum | datum_plane |  |
| 487 | S02 assembly R outer bearing lowering clearance | sketch | ents 8 {'point': 4, 'line': 4} · UV 24×24 · origin [0.0, -103.0, 0.0] |
| 488 | Extrude139 | extrude | cut · extent {'distance': 1.0, 'type': 'distance'} · S02 assembly R outer bearing lowering clearance · tgt [32] · new [223] |
| 505 | Combine16 | combine | cut · tgt [32] · tools [141] · keep_tools=True |

## Feature counts

- **combine**: 13
- **datum_plane**: 101
- **extrude**: 101
- **mirror**: 4
- **move_copy**: 4
- **rectangular_pattern**: 5
- **sketch**: 101
- **total**: 329

## AABB check

| Source | AABB (mm) |
|--------|-----------|
| Seed sketch S02 A UV (circles Ø160/Ø152) | U[-80.0,80.0] V[43.0,203.0] → **160.0 × 160.0** |
| `first-prints/shell-first-review/main-shell-assembly-coordinates.stl` | X[-79.9502,80.0000] Y[-105.0000,105.0000] Z[43.0125,202.9875] → **159.9502 × 210.0000 × 159.9751** (tris 18188) |
| `first-prints/shell-first-review/main-shell-axle-vertical.stl` | X[-79.9751,79.9751] Y[-79.9875,79.9875] Z[0.0000,210.0000] → **159.9502 × 159.9751 × 210.0000** (tris 18188) |
| Blank-doc JSONC replay (pre-Combine16) | X[-79.9259,80] Y[-105,105] Z[43.0185,202.9815] → **159.9259 × 210 × 159.9630** (tris ~13462); skipped MoveCopy5/Combine8/Combine16 |

## VERIFY gaps (before JSONC rebuild)
1. **hatch_tool_dependency** (Combine16): Combine16 cuts shell 32 with hatch body 141 (keep_tools). Full final shell AABB matching review STL needs hatch solid or hatch chapter first. Early shell port may compare pre-Combine16 AABB separately.
2. **transient_new_body_ids** (join/cut extrudes): Join/cut extrudes list transient new_body_ids auto-booleaned into 32. Do not keep as SoT bodies unless visibility says so.
3. **no_fillet_chamfer_hole_features** (document): Native file has zero fillet/chamfer/hole features — all detail is sketch+extrude(+combine/pattern).
4. **quat_rotation_movecopy** (MoveCopy6): Port exact quat [0.0, 0.4617486132350339, 0.0, 0.8870108331782217] and translation {'x': 0.0, 'y': -75.0, 'z': 0.0} — do not invent angle.
5. **quat_rotation_movecopy** (MoveCopy7): Port exact quat [0.0, 0.4617486132350339, 0.0, 0.8870108331782217] and translation {'x': 0.0, 'y': -75.0, 'z': 0.0} — do not invent angle.
6. **quat_rotation_movecopy** (MoveCopy8): Port exact quat [0.0, 0.4617486132350339, 0.0, 0.8870108331782217] and translation {'x': 0.0, 'y': -75.0, 'z': 0.0} — do not invent angle.

## How the JSONC chapter should be rebuilt
1. Port Extrude1 seed tube (S02 A) exactly — OD160/ID152, extent 210, flip true
2. Replay all join/cut extrudes targeting body 32 in fid order with exact sketch entities
3. Replay combines targeting 32 with tool bodies created in-chapter (or retained)
4. S03 shell-side features (lap ledge / radial cuts) after hatch copy timing — see fids in summary
5. Combine16 needs hatch body 141 (keep_tools) — coordinate with hatch chapter or retain solid
6. Blank-doc replay; AABB vs first-prints/shell-first-review/main-shell-assembly-coordinates.stl

See `main_shell-32.json` for full sketch entity lists, datums, and per-feature payloads.
