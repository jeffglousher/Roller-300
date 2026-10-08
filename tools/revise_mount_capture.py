"""Author native features; all geometry must be replayed by noBS CAD."""
from pathlib import Path
import copy, json, zipfile, math
from drivetrain_native_revision import Native

ROOT = Path(__file__).resolve().parents[1]
n = Native.__new__(Native)
with zipfile.ZipFile(ROOT/'Roller-300.nbcad') as z:
    n.entries = {name:z.read(name) for name in z.namelist()}
n.m = json.loads(n.entries['model.json'])
assert len(n.m['document']['history']['features']) == 1561, 'One-time migration baseline changed'
n.fid = max(f['id'] for f in n.m['document']['history']['features'])
n.did = max(p['datum_id'] for p in n.m['datum_planes'])
n.bid = max([b for e in n.m['extrudes'] for b in e['new_body_ids']] +
            [b for e in n.m['body_features'] for key in ('result_body_ids','new_body_ids','body_ids')
             for b in e.get(key,[])] +
            [e['body_id'] for e in n.m['body_features'] if 'body_id' in e])
n.parts = {}

# Existing hex pockets remain at AF6/depth2.8: nominal AF5.5/h2.4 nuts.
# Counterbores are head seats, not snap-captive screws. Local round bosses
# preserve the 1.5 mm retainer floor and avoid changing the bearing stack.
for side,sign,caps in [('L',1,[377,378]),('R',-1,[381,382])]:
    for cap,end in zip(caps,[62.5,89.5]):
        pts = [(49.6723+20*math.cos(math.pi/4+i*math.pi/2),
                123+20*math.sin(math.pi/4+i*math.pi/2)) for i in range(4)]
        for i,(x,z) in enumerate(pts):
            n.ring(f'S17 {side} retainer{cap} round head seat{i+1}',
                   end if sign==1 else -end-3.2,3.2,4.5,0,'join',cap,x,z)
        n.drill(f'S17 {side} retainer{cap} recessed M3 heads',cap,
                end if sign==1 else -end-3.2,3.2,pts,3.1)

# Trim fixed mounting roots at the exact D160 envelope. Do this before the
# derived roof-open section so both print and complete assembly inherit it.
envelope=n.ring('S17 exact barrel outer envelope D160',-106,212,80,0)
n.combine(32,[envelope],'intersect',name='S17 trim protruding mounting roots to barrel OD')
# Do not inherit the copied template's stable profile identities. Native
# replay must assign them to the newly authored circles and drill profiles.
for sketch in n.m['sketches']:
    if sketch['name'].startswith('S17 '):
        sketch.pop('profile_identities',None)
        sketch.pop('entity_id_high_water',None)
        sketch['snapshot']['generated_points']=[]
n.save_candidate('s17-mount-capture')
