"""Author native CAD feature DTOs. The CAD application must replay every candidate.

This does not generate geometry or render images. Source archives are untouched.
"""
from pathlib import Path
import base64
import copy
import json
import math
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class Native:
    def __init__(self, source=ROOT / 'Roller-300.nbcad'):
        with zipfile.ZipFile(source) as archive:
            self.entries = {n: archive.read(n) for n in archive.namelist()}
        self.m = json.loads(self.entries['model.json'])
        if len(self.m['document']['history']['features']) != 1208:
            raise ValueError('This one-time migration requires the 1208-feature base. Pass the preserved base archive explicitly; do not reapply it to the revised master.')
        self.fid = max(f['id'] for f in self.m['document']['history']['features'])
        self.did = max(p['datum_id'] for p in self.m['datum_planes'])
        self.bid = max([b for e in self.m['extrudes'] for b in e['new_body_ids']] +
                       [b for e in self.m['body_features'] for b in e.get('result_body_ids', [])])
        self.parts = {}

    def feature(self, kind, name):
        self.fid += 1
        self.m['document']['history']['features'].append(
            dict(id=self.fid, name=name, kind=kind, suppressed=False, status={'state': 'ok'}))
        return self.fid

    def suppress(self, ids):
        for f in self.m['document']['history']['features']:
            if f['id'] in ids:
                f['suppressed'] = True

    def plane(self, axis, pos, name):
        bases = {
            'xz': dict(origin=[0, pos, 0], u=[1, 0, 0], v=[0, 0, 1], normal=[0, -1, 0]),
            'xy': dict(origin=[0, 0, pos], u=[1, 0, 0], v=[0, 1, 0], normal=[0, 0, 1]),
            'yz': dict(origin=[pos, 0, 0], u=[0, 1, 0], v=[0, 0, 1], normal=[1, 0, 0]),
        }
        self.did += 1
        p = dict(feature_id=self.feature('construction_plane', name + ' datum'),
                 name=name + ' datum', datum_id=self.did,
                 source={'type': 'offset', 'reference': {'type': 'origin_plane', 'plane': axis},
                         'distance': -pos if axis == 'xz' else pos}, basis=bases[axis])
        self.m['datum_planes'].append(p)
        self.m['visibility']['hidden_datum_plane_ids'].append(self.did)
        return p

    def extrude(self, name, axis, pos, entities, depth, op='new_body', target=None):
        p = self.plane(axis, pos, name)
        s = copy.deepcopy(next(s for s in self.m['sketches'] if s['feature_id'] == 539))
        s.update(feature_id=self.feature('sketch', name), name=name,
                 plane={'type': 'datum_plane', 'datum_id': p['datum_id']}, basis=copy.deepcopy(p['basis']))
        s['snapshot'].update(entities=entities, constraints=[], next_entity=len(entities) + 1, next_constraint=1)
        self.m['sketches'].append(s)
        self.m['visibility']['hidden_sketch_names'].append(name)
        self.m['counters']['sketch'] += 1
        e = copy.deepcopy(next(e for e in self.m['extrudes'] if e['feature_id'] == 543))
        self.m['counters']['extrude'] += 1
        e.update(feature_id=self.feature('extrude', name), name=name, sketch_name=name,
                 operation=op, extent={'type': 'distance', 'distance': depth}, flip=axis == 'xz',
                 target_body_ids=[] if op == 'new_body' else [target], new_body_ids=[])
        if op == 'new_body':
            self.bid += 1
            e['new_body_ids'] = [self.bid]
        self.m['extrudes'].append(e)
        return self.bid if op == 'new_body' else target

    @staticmethod
    def poly(points):
        n = len(points)
        return [[i + 1, {'type': 'point', 'position': dict(x=x, y=y)}] for i, (x, y) in enumerate(points)] + \
               [[n + i + 1, {'type': 'line', 'start': i + 1, 'end': (i + 1) % n + 1}] for i in range(n)]

    @staticmethod
    def circles(x, y, radii):
        return [[i + 1, {'type': 'circle', 'center': dict(x=x, y=y), 'radius': r}]
                for i, r in enumerate(radii)]

    def box(self, name, lo, size, op='new_body', target=None):
        x, y, z = lo
        dx, dy, dz = size
        return self.extrude(name, 'xz', y, self.poly([(x, z), (x + dx, z), (x + dx, z + dz), (x, z + dz)]), dy, op, target)

    def ring(self, name, y, length, ro, ri, op='new_body', target=None, x=0, z=123):
        return self.extrude(name, 'xz', y, self.circles(x, z, [ro, ri] if ri else [ro]), length, op, target)

    def move(self, bodies, name, x=0, y=0, z=0, copy_bodies=False):
        result = bodies
        if copy_bodies:
            result = list(range(self.bid + 1, self.bid + 1 + len(bodies)))
            self.bid += len(bodies)
        self.m['body_features'].append(dict(type='move_copy', feature_id=self.feature('move_copy', name),
            name=name, body_ids=bodies, translation=dict(x=x, y=y, z=z), rotation=[0, 0, 0, 1],
            pivot=dict(x=0, y=0, z=123), copy=copy_bodies, result_body_ids=result))
        return result

    def mirror(self, bodies, name):
        result = list(range(self.bid + 1, self.bid + 1 + len(bodies)))
        self.bid += len(bodies)
        self.m['body_features'].append(dict(type='mirror', feature_id=self.feature('mirror', name), name=name,
            body_ids=bodies, plane={'type': 'origin_plane', 'plane': 'xz'},
            plane_basis=dict(origin=[0, 0, 0], u=[1, 0, 0], v=[0, 0, 1], normal=[0, -1, 0]), new_body_ids=result))
        return result

    def combine(self, target, tools, op='join', keep=False, name='S13 native combine'):
        self.m['body_features'].append(dict(type='combine', feature_id=self.feature('combine', name), name=name,
            target_body_id=target, tool_body_ids=tools, operation=op, keep_tools=keep))

    def import_step(self, path, name, translation, rotation):
        self.bid += 1
        b = self.bid
        self.m['body_features'].append(dict(type='import_step', feature_id=self.feature('import_step', name),
            name=name, file_name=Path(path).name, data_base64=base64.b64encode(Path(path).read_bytes()).decode(), body_id=b))
        self.move([b], name + ' placement')
        self.m['body_features'][-1].update(translation=dict(zip(('x', 'y', 'z'), translation)), rotation=rotation,
                                          pivot=dict(x=0, y=0, z=0))
        return b

    def drill(self, name, target, y, depth, points, radius):
        entities = [[i+1, {'type':'circle', 'center':dict(x=x,y=z), 'radius':radius}]
                    for i,(x,z) in enumerate(points)]
        self.extrude(name, 'xz', y, entities, depth, 'cut', target)
        self.m['extrudes'][-1]['profile_indices'] = list(range(len(points)))

    def hex_pocket(self, name, target, y, depth, x, z, af=6):
        r = af / math.sqrt(3)
        self.extrude(name, 'xz', y, self.poly([(x+r*math.cos(i*math.pi/3), z+r*math.sin(i*math.pi/3)) for i in range(6)]), depth, 'cut', target)

    def save_candidate(self, name):
        # Derived fit sections must copy the fully revised supports.
        h = self.m['document']['history']['features']
        fixture = [f for f in h if 1023 <= f['id'] <= 1037]
        self.m['document']['history']['features'] = [f for f in h if f not in fixture] + fixture
        self.m['document']['history']['rollback_index'] = len(self.m['document']['history']['features'])
        model_path = ROOT / '.local' / (name + '-model.json')
        model_path.write_text(json.dumps(self.m), encoding='utf-8')
        self.entries['model.json'] = model_path.read_bytes()
        path = ROOT / '.local' / (name + '.nbcad')
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
            for n, data in self.entries.items():
                archive.writestr(n, data)
        (ROOT / '.local' / (name + '-parts.json')).write_text(json.dumps(self.parts, indent=2))
        print(json.dumps({'candidate': str(path), 'features': len(self.m['document']['history']['features']), 'parts': self.parts}))


def retention(n):
    # Retire the wheel-mounted bearing, while retaining the two stationary supports.
    n.box('S13 L retire rotating wheel bearing', [-12, 145, 111], [24, 10, 24], 'cut', 2)
    n.box('S13 R retire rotating wheel bearing', [-12, -155, 111], [24, 10, 24], 'cut', 19)
    for side, body, y in [('L', 13, 142), ('R', 30, -150)]:
        n.ring(f'S13 {side} restore wheel outer wall clearance bore9', y, 8, 22, 4.5, 'join', body)
        n.box(f'S13 {side} remove redundant bearing boss extension', [-23, 150 if side == 'L' else -158, 100], [46, 8, 46], 'cut', body)
    retired = {494, 497}
    retired.update(e['feature_id'] for e in n.m['extrudes'] if any(b in e['new_body_ids'] + e['target_body_ids'] for b in (375, 379)))
    n.suppress(retired)
    mirror = next(b for b in n.m['body_features'] if b['feature_id'] == 498)
    mirror.update(body_ids=[224], new_body_ids=[227])
    # A nominal 8 mm metal stack abuts the mouth inner race and the hub face.
    b = n.ring('S13 L metal opposing mouth inner-race spacer 8x11x8', 105, 8, 5.5, 4)
    n.parts['L mouth opposing metal spacer'] = b
    n.parts['R mouth opposing metal spacer'] = n.mirror([b], 'S13 R opposing mouth inner-race spacer')[0]
    n.move([3, 224], 'S13 L nominal wheel endplay0p2', y=-0.2)
    n.move([20, 227], 'S13 R nominal wheel endplay0p2', y=0.2)
    # Keep the full 6 mm collar on the 50 mm shaft and clear the 1.5 mm cap.
    # Nominal cap-to-collar gap 0.2; shaft-end reserve 0.3. Verify on receipt.
    n.move([369], 'S13 L input collar cap gap0p2 reserve0p3', y=-.3)
    n.move([371], 'S13 R input collar cap gap0p2 reserve0p3', y=.3)
    for e in n.m['extrudes']:
        if any(b in e['new_body_ids'] for b in (370, 372)):
            e['extent']['distance'] = 1.7


def clutch(n):
    # Retire smooth annular placeholders, not the stock shaft.
    old = set(range(338, 350))
    n.suppress({e['feature_id'] for e in n.m['extrudes'] if old.intersection(e['new_body_ids'])} | {811, 814})
    for bf in n.m['body_features']:
        if bf['feature_id'] in (821, 822):
            bf['body_ids'] = [b for b in bf['body_ids'] if b not in old]
            bf['result_body_ids'] = [b for b in bf['result_body_ids'] if b not in old]
    # Vendor STEP: 8 mm main hub thickness plus 2 mm centering pilot.
    hub = n.import_step(ROOT/'.local/sonic-hub-8.step', 'S14 L purchased Sonic hub 1309-0016-0008',
                        [17.009945126176262, 16.155318, 123.57759806543345],
                        [-math.sqrt(.5), 0, 0, math.sqrt(.5)])
    n.parts['L clutch purchased metal hub'] = hub
    reaction = n.ring('S14 L driven reaction plate', 28.3, 4, 28.75, 7.1)
    n.parts['L clutch reaction plate'] = reaction
    pattern = [(x, 123+z) for x,z in [(-8,-8),(-8,8),(8,-8),(8,8)]]
    n.drill('S14 L reaction metal hub M4 clearance', reaction, 28.3, 4, pattern, 2.25)
    n.drill('S14 L reaction M4 button head recess', reaction, 30.1, 2.2, pattern, 4)
    guide = [(24*math.cos(math.pi/4+i*math.pi/2), 123+24*math.sin(math.pi/4+i*math.pi/2)) for i in range(4)]
    for i,(x,z) in enumerate(guide):
        n.ring(f'S14 L nyloc captive boss{i+1}', 24.3, 4, 4.5, 0, 'join', reaction, x, z)
        n.hex_pocket(f'S14 L M3 nyloc pocket{i+1}', reaction, 24.3, 4, x, z)
    n.drill('S14 L reaction spring screw bores', reaction, 28.3, 4, guide, 1.7)
    n.parts['L clutch front cork liner'] = n.ring('S14 L front cork 0p5 trial', 32.3, .5, 22, 13.7)
    # Rotor and journal sleeve belong to the pulley, not the shaft.
    n.ring('S14 L integral pulley rotor sleeve wall2p5', 34.8, 31.05, 16, 13.5, 'join', 9)
    n.ring('S14 L integral friction rotor', 32.8, 2, 22, 13.5, 'join', 9)
    n.ring('S14 R integral pulley rotor sleeve wall2p5', -65.85, 31.05, 16, 13.5, 'join', 26)
    n.ring('S14 R integral friction rotor', -34.8, 2, 22, 13.5, 'join', 26)
    n.parts['L clutch rear cork liner'] = n.ring('S14 L rear cork 0p5 trial', 34.8, .5, 22, 16.7)
    pressure = n.ring('S14 L keyed pressure plate', 35.3, 3, 28.75, 16.5)
    n.parts['L clutch pressure plate'] = pressure
    n.drill('S14 L pressure guide bores', pressure, 35.3, 3, guide, 1.7)
    # Long plain bush installs from the pulley rear and bolts positively to it.
    e = next(e for e in n.m['extrudes'] if e['feature_id'] == 561)
    s = next(s for s in n.m['sketches'] if s['name'] == e['sketch_name'])
    p = next(p for p in n.m['datum_planes'] if p['datum_id'] == s['plane']['datum_id'])
    s['basis']['origin'][1] = p['basis']['origin'][1] = 43.3
    p['source']['distance'] = -43.3
    e['extent']['distance'] = 46.95
    n.ring('S14 L removable journal flange', 79.75, 4, 20, 4.1, 'join', 307)
    n.ring('S14 R removable journal flange', -83.75, 4, 20, 4.1, 'join', 315)
    rear_points = [(17*math.cos(math.pi/4+i*math.pi/2),123+17*math.sin(math.pi/4+i*math.pi/2)) for i in range(4)]
    for side,pulley,bush,y in [('L',9,307,73.75),('R',26,315,-79.75)]:
        n.drill(f'S14 {side} pulley journal screw bores', pulley, y, 6, rear_points, 1.7)
        n.drill(f'S14 {side} journal flange bolt bores', bush,79.75 if side=='L' else -83.75,4,rear_points,1.7)
        for i,(x,z) in enumerate(rear_points):
            n.hex_pocket(f'S14 {side} pulley captive journal nut{i+1}',pulley,76.95 if side=='L' else -79.75,2.8,x,z)
    n.parts['L clutch journal bush'] = 307
    n.parts['R clutch journal bush'] = 315
    refs = [hub,reaction,n.parts['L clutch front cork liner'],n.parts['L clutch rear cork liner'],pressure]
    # Hardware is supplier envelopes; no invented spring rate or slip torque.
    for i,(x,z) in enumerate(guide):
        for name,y,length,ro,ri in [('spring 2916-0001-0002 envelope',38.3,18,4,3),
                                  ('purchased minimum16 spring guide',38.3,16,2.5,1.6),
                                  ('metal spring washer',56.3,1,4.5,1.6),
                                  ('M3x35 adjuster shank envelope',22.3,35,1.5,0),
                                  ('M3 adjuster head envelope',57.3,3,2.75,0)]:
            b=n.ring(f'S14 L {name}{i+1}',y,length,ro,ri,x=x,z=z);refs.append(b)
            n.parts[f'L clutch {name}{i+1}']=b
    mirrored=n.mirror(refs,'S14 R complete clutch hub plates and hardware')
    for l,r in zip(refs,mirrored):
        for name,b in list(n.parts.items()):
            if b==l and name.startswith('L '):n.parts['R '+name[2:]]=r


def carriage(n):
    # Extract only internal drivetrain supports. The polygon remains inside
    # the barrel's existing 76 mm inner radius throughout the adjustment range.
    carrier = n.move([32], 'S15 copy L input support for sliding carrier', copy_bodies=True)[0]
    region = n.poly([(28.5,87),(65.5,87),(65.5,102.5),(71.5,102.5),(71.5,145),(28.5,145)])
    blank = n.extrude('S15 L input carrier isolation volume','xz',0,region,90)
    n.combine(carrier,[blank],'intersect',name='S15 L isolate internal input supports')
    # Detach complete regions before adding slotted bases; subtracting the
    # finished slotted carrier would leave stationary islands in its slots.
    n.extrude('S15 L detach input supports from fixed frame','xz',0,region,90,'cut',32)
    n.extrude('S15 R detach input supports from fixed frame','xz',-90,region,90,'cut',32)
    n.box('S15 L sliding carrier base',[25.5,0,87],[40,90,4],'join',carrier)
    n.box('S15 L carrier lower servo ear clearance',[39.37,29.4,87],[20.61,3.3,5.7],'cut',carrier)
    n.box('S15 L support separation clearance',[25.5,0,86.6],[40,90,.4],'cut',32)
    n.box('S15 R support separation clearance',[25.5,-90,86.6],[40,90,.4],'cut',32)
    fixed = n.box('S15 L fixed internal slide bed',[25.5,0,83],[40.5,90,3.6])
    n.box('S15 L bed lower servo ear clearance',[37,29.4,83],[26,3.3,3.6],'cut',fixed)
    # The outer forward screw sits behind the servo case for head/driver access.
    # Three mounts give a triangle; rear driver is behind the belt and clear
    # of both bearing supports. A 3 mm diameter driver shaft fits there.
    anchors=[(32.5,12),(60,50),(30.5,79)]
    for i,(x,y) in enumerate(anchors):
        # Independent nuts can be loaded from below before inserting the carrier.
        n.extrude(f'S15 L stationary M4 nut boss{i+1}','xy',79,n.circles(x,y,[5.5]),4,'join',fixed)
        n.extrude(f'S15 L fixed anchor bore{i+1}','xy',79,n.circles(x,y,[2.2]),7.6,'cut',fixed)
        r=7.4/math.sqrt(3)
        n.extrude(f'S15 L fixed anchor hex nut{i+1}','xy',79,
                  n.poly([(x+r*math.cos(j*math.pi/3),y+r*math.sin(j*math.pi/3)) for j in range(6)]),3.4,'cut',fixed)
        n.extrude(f'S15 L carrier M4 slide slot{i+1}','xy',87,
                  n.poly([(x-3.2,y-2.2),(x+4.2,y-2.2),(x+4.2,y+2.2),(x-3.2,y+2.2)]),4,'cut',carrier)
        n.box(f'S15 L moving washer and screw head clearance{i+1}',[x-5.6,y-4.6,91],[12.2,9.2,5],'cut',carrier)
        if i==0:
            n.box('S15 L forward driver corridor for full travel',[x-2.8,y-1.8,96],[6.6,3.6,50],'cut',carrier)
    for i,y in enumerate((3,85)):
        n.box(f'S15 L transverse guide key{i+1}',[32,y,86.6],[32,2,1.2],'join',fixed)
        n.box(f'S15 L carrier guide groove{i+1}',[28,y-.3,87],[40,2.6,1],'cut',carrier)
    n.box('S15 L inward travel stop',[21.5,40,83],[2,10,9.5],'join',fixed)
    n.box('S15 L inward stop supporting web',[21.5,40,83],[4.5,10,3.6],'join',fixed)
    n.box('S15 L outward stop supporting web',[65.5,40,83],[3,10,3.6],'join',fixed)
    n.box('S15 L outward travel stop',[66.5,40,83],[2,10,9.5],'join',fixed)
    right = n.mirror([carrier,fixed],'S15 R sliding input carrier and fixed bed')
    n.combine(32,[fixed,right[1]],name='S15 integrate fixed drivetrain slide beds')
    # The existing internal frame can intrude into a pocket after the bed is
    # joined. Recut the actual assembled frame, including bolt-tip clearance.
    for sign,side in [(1,'L'),(-1,'R')]:
        for i,(x,y) in enumerate(anchors):
            y*=sign
            n.extrude(f'S15 {side} completed-frame bolt clearance{i+1}','xy',77.5,n.circles(x,y,[2.2]),9.1,'cut',32)
            r=7.4/math.sqrt(3)
            n.extrude(f'S15 {side} completed-frame nut clearance{i+1}','xy',79,
                      n.poly([(x+r*math.cos(j*math.pi/3),y+r*math.sin(j*math.pi/3)) for j in range(6)]),3.4,'cut',32)
            if i==1:
                # Load the outer nut horizontally from the open inner cavity;
                # the barrel skin prevents a straight lift from below here.
                n.box(f'S15 {side} outer anchor nut loading port',[x-15.5,y-3.8,79],[15.5,7.6,3.4],'cut',32)
    n.parts['L sliding input carrier']=carrier
    n.parts['R sliding input carrier']=right[0]
    n.parts['stationary frame']=32
    # Slot mounts: M4x14, DIN125 M4 washer 9x4.3x0.8, standard 3.2 mm M4 nut. Shaft and
    # coupler axes move with the carrier; no independent servo tension slots.
    n.parts['input adjustment travel mm']=[-2,1]
    n.parts['input moving bodies L']=[carrier,5,6,10,12,301,367,369,370,377,378]
    n.parts['input moving bodies R']=[right[0],22,23,27,29,309,368,371,372,381,382]


def split_pressure_pads(n):
    # A closed ring cannot pass the integral rotor or pulley flanges. Each
    # semicircular pad installs radially, then is captured by two guide bolts.
    top=n.move([391],'S16 copy upper clutch pressure pad',copy_bodies=True)[0]
    n.box('S16 L retain lower pressure pad',[-30,35.3,122.8],[60,3,32],'cut',391)
    n.box('S16 L retain upper pressure pad',[-30,35.3,92],[60,3,31.2],'cut',top)
    n.box('S16 R retain lower pressure pad',[-30,-38.3,122.8],[60,3,32],'cut',416)
    right_top=n.mirror([top],'S16 R upper pressure pad')[0]
    n.parts.pop('L clutch pressure plate');n.parts.pop('R clutch pressure plate')
    n.parts.update({'L clutch lower pressure pad':391,'L clutch upper pressure pad':top,
                    'R clutch lower pressure pad':416,'R clutch upper pressure pad':right_top})
    # Rear lining is cut into matching half sheets; front lining remains whole.
    n.box('S16 L rear lining split0p4',[-23,34.8,122.8],[46,.5,.4],'cut',390)
    n.box('S16 R rear lining split0p4',[-23,-35.3,122.8],[46,.5,.4],'cut',415)


if __name__ == '__main__':
    n = Native(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'Roller-300.nbcad')
    retention(n)
    clutch(n)
    carriage(n)
    split_pressure_pads(n)
    printed={32,301,307,309,315,367,368,388,391,413,416,437,440,442,443}
    cork={389,390,414,415}
    replacements={}
    for name,b in n.parts.items():
        if not isinstance(b,int):continue
        color=(49,133,143) if b in printed else (183,145,93) if b in cork else (145,153,161)
        replacements[b]=dict(body_id=b,color=dict(zip(('r','g','b','a'),(*color,255))),material_name=name,
                             filament_type='PETG' if b in printed else 'REFERENCE',brand='Generic',color_name='',
                             filament_id=None,preset_id=None,density_g_cm3=None,diameter_mm=1.75)
    n.m['body_appearances']=[a for a in n.m['body_appearances'] if a['body_id'] not in replacements]+list(replacements.values())
    n.m['visibility']['hidden_body_ids']=[373,374]
    n.save_candidate('s15-carrier')
