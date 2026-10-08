"""Author an S18 native feature migration; CAD owns solid replay and exports."""
from pathlib import Path
import copy, json, math, zipfile
from drivetrain_native_revision import Native

ROOT = Path(__file__).resolve().parents[1]
n = Native.__new__(Native)
with zipfile.ZipFile(ROOT/'Roller-300.nbcad') as z:
    n.entries = {name:z.read(name) for name in z.namelist()}
n.m = json.loads(n.entries['model.json'])
assert len(n.m['document']['history']['features']) == 1625, 'S18 migration needs preserved S17 baseline'
n.fid = max(f['id'] for f in n.m['document']['history']['features'])
n.did = max(p['datum_id'] for p in n.m['datum_planes'])
n.bid = max([b for e in n.m['extrudes'] for b in e['new_body_ids']] +
            [b for e in n.m['body_features'] for key in ('result_body_ids','new_body_ids','body_ids')
             for b in e.get(key,[])] +
            [e['body_id'] for e in n.m['body_features'] if 'body_id' in e])
n.parts = {}

retired = [307,315,388,389,390,391,442,413,414,415,416,443] + list(range(392,412)) + list(range(417,437))
# Suppress clutch-only creation and finishing features. Filter mixed copy/move
# records in pairs so the retained hub and input parts keep their stable IDs.
retired_set=set(retired)
suppressed=set()
for e in n.m['extrudes']:
    if retired_set.intersection(e.get('new_body_ids',[])+e.get('target_body_ids',[])):
        suppressed.add(e['feature_id'])
for b in n.m['body_features']:
    if b['type'] in ('mirror','move_copy'):
        key='new_body_ids' if b['type']=='mirror' else 'result_body_ids'
        pairs=[(a,z) for a,z in zip(b['body_ids'],b[key]) if a not in retired_set and z not in retired_set]
        if len(pairs)!=len(b['body_ids']):
            if pairs:b['body_ids'],b[key]=map(list,zip(*pairs))
            else:suppressed.add(b['feature_id'])
    elif b.get('body_id') in retired_set or b.get('target_body_id') in retired_set:
        suppressed.add(b['feature_id'])
n.suppress(suppressed)

pattern = [(x,123+z) for x,z in [(-8,-8),(-8,8),(8,-8),(8,8)]]
for side,sign,pulley,hub in [('L',1,9,387),('R',-1,26,412)]:
    # Keep the existing 48T teeth, flanges, and belt alignment at Y65.25..79.75.
    n.box(f'S18 {side} remove obsolete rotor and sleeve',
          [-30,0 if sign==1 else -65.25,93],[60,65.25,60],'cut',pulley)
    # Fill the plain-journal bore and obsolete journal bolt/nut recesses below
    # the existing tooth roots. The resulting part is one connected solid.
    n.ring(f'S18 {side} rigid pulley core',65.25 if sign==1 else -79.75,
           14.5,20.8,4.2,'join',pulley)
    n.move([hub],f'S18 {side} metal output hub beside belt',y=sign*36.95)
    # Purchased hub has a D14 pilot projecting 2 mm beyond its mounting face.
    n.drill(f'S18 {side} hub pilot clearance',pulley,
            65.25 if sign==1 else -67.45,2.2,[(0,123)],7.1)
    n.drill(f'S18 {side} four M4 through mounting bores',pulley,
            65.25 if sign==1 else -79.75,14.5,pattern,2.25)
    n.drill(f'S18 {side} accessible recessed M4 button heads',pulley,
            75.05 if sign==1 else -79.75,4.7,pattern,4)
    n.parts[f'{side} rigid output pulley'] = pulley
    n.parts[f'{side} metal output shaft hub'] = hub

for sketch in n.m['sketches']:
    if sketch['name'].startswith('S18 '):
        sketch.pop('profile_identities',None)
        sketch.pop('entity_id_high_water',None)
        sketch['snapshot']['generated_points']=[]
n.parts['retired clutch bodies'] = retired
n.parts['output attachment'] = {'hub':'1309-0016-0008','bolt':'M4x16 ISO7380-1',
    'count_per_drive':4,'pattern_mm':16,'pulley_bore_mm':8.4,
    'hub_face_y_left_mm':65.25,'hub_pilot_end_y_left_mm':67.25,
    'head_seat_y_left_mm':75.05,'nominal_thread_engagement_mm':6.2,
    'counterbore_diameter_mm':8,'counterbore_depth_mm':4.7}
n.save_candidate('s18-rigid-belt-drive')
