"""S20 native feature authoring. Limo CAD replays every solid and renders every view."""
from pathlib import Path
import copy,json,math,zipfile
from drivetrain_native_revision import Native
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'.local/before-s20-adversarial.nbcad.bak'
if not src.exists():src.write_bytes((ROOT/'Roller-300.nbcad').read_bytes())
n=Native.__new__(Native)
with zipfile.ZipFile(src) as z:n.entries={p:z.read(p) for p in z.namelist()}
n.m=json.loads(n.entries['model.json'])
assert len(n.m['document']['history']['features'])==1740,'Requires preserved S19'
old=json.loads(zipfile.ZipFile(ROOT/'.local/before-s19-servo-horn.nbcad.bak').read('model.json'))
n.fid=max(f['id'] for f in n.m['document']['history']['features'])
n.did=max(p['datum_id'] for p in n.m['datum_planes'])
n.bid=max([b for e in n.m['extrudes'] for b in e['new_body_ids']]+[b for e in n.m['body_features'] for k in ('body_ids','new_body_ids','result_body_ids') for b in e.get(k,[])]+[e['body_id'] for e in n.m['body_features'] if 'body_id' in e]);n.parts={}
datums={p['datum_id']:p for p in n.m['datum_planes']};oldplanes={p['datum_id']:p for p in old['datum_planes']}
def set_plane(did,y):
 p=datums[did];p['basis']['origin'][1]=y;p['source']['distance']=-y
 for s in n.m['sketches']:
  if s['plane'].get('datum_id')==did:s['basis']=copy.deepcopy(p['basis'])
def clean(s):
 s.pop('profile_identities',None);s.pop('entity_id_high_water',None);s['snapshot']['generated_points']=[]
def opposite_stock(body,name,x=49.6723):
 result=n.move([body],name,copy_bodies=True)[0]
 n.m['body_features'][-1].update(rotation=[0,0,1,0],pivot=dict(x=x,y=0,z=123))
 return result

# Change each shared datum exactly once; sketch repetitions must never accumulate moves.
changes={}
for s in n.m['sketches']:
 name=s['name']
 if name.startswith('S07 ') and any(w in name for w in ['servo cradle root','servo ear insertion','servo ear mounting','servo ear M3','top bridge bolt supports','removable upper ear support','upper ear M3']):
  did=s['plane']['datum_id'];dy=4.5 if name.startswith('S07 R ') else -4.5
  changes[did]=oldplanes[did]['basis']['origin'][1]+dy
 if name=='S01 L servo cradle pocket':changes[s['plane']['datum_id']]=.2
 if name=='S15 L carrier lower servo ear clearance':changes[s['plane']['datum_id']]=25.2
 if name=='S15 L bed lower servo ear clearance':changes[s['plane']['datum_id']]=24.9
for did,y in changes.items():set_plane(did,y)

# Old smooth-shaft clamps and fabricated thin collar are retired, not hidden substitutes.
retired={6,23,369,370,371,372,385,386}
n.suppress({6,817,820,823,824,992,995,1013,1016,1242,1243,904,913,919,930,925,927,936,938,
 854,857,1688,1694,1697,1700,1703,1728,1734,1737,1740,1743,
 977,979,981,984,986,989,998,1000,1002,1005,1007,1010})
for e in n.m['extrudes']:
 if set([385,386]).intersection(e['new_body_ids']):n.suppress({e['feature_id']})
for bf in n.m['body_features']:
 if set([385,386]).intersection(bf.get('body_ids',[])+bf.get('new_body_ids',[])):n.suppress({bf['feature_id']})
for bf in n.m['body_features']:
 if bf['feature_id'] in [18,19,20]:
  for k in ['body_ids','new_body_ids','result_body_ids']:
   if k in bf:bf[k]=[x for x in bf[k] if x not in retired]
 # Purchased threaded horns are copies rotated 180 degrees, never reflected.
 if bf.get('type')=='mirror' and bf.get('new_body_ids')==[446]:
  fid,name=bf['feature_id'],bf['name'];bf.clear()
  bf.update(type='move_copy',feature_id=fid,name=name+' proper stock rotation',body_ids=[445],translation=dict(x=0,y=0,z=0),rotation=[0,0,1,0],pivot=dict(x=49.6723,y=0,z=123),copy=True,result_body_ids=[446])
  next(f for f in n.m['document']['history']['features'] if f['id']==fid).update(kind='move_copy',name=bf['name'])

# Horn moves 0.5 mm to open the factory rear bosses' running clearance.
for e in n.m['extrudes']:
 if e['sketch_name'].startswith('S19 ') and any(t in e['sketch_name'] for t in ['integral horn flange','horn pilot','four horn M4','recessed M4']):
  s=next(s for s in n.m['sketches'] if s['name']==e['sketch_name']);did=s['plane']['datum_id']
  set_plane(did,datums[did]['basis']['origin'][1]+(.5 if 'S19 R ' in s['name'] else -.5))
 if 'horn and adapter complete rotation clearance' in e['sketch_name']:
  s=next(s for s in n.m['sketches'] if s['name']==e['sketch_name']);set_plane(s['plane']['datum_id'],37.6 if ' L ' in s['name'] else -53.8);e['extent']['distance']=16.2

for side,sign,servo,adapter,pulley,carrier,bridge,horn in [('L',1,12,301,10,437,367,445),('R',-1,29,309,27,440,368,446)]:
 n.move([servo,horn],f'S20 {side} servo and metal horn clearance adjustment',y=-.5*sign)
 # Add case ears only after the global servo move, so the mounting datums agree.
 for z in [85.25,133.5]:
  n.box(f'S20 {side} supplied case ear reference Z{z}',[39.6723,25.2 if sign==1 else -27.9,z],[20,2.7,7.75],'join',servo)
 for x in [44.6723,54.6723]:
  for z,edge in [(88.75,85.25),(137.75,141.25)]:
   n.drill(f'S20 {side} nominal servo ear open slot {x} {z}',servo,25.2 if sign==1 else -27.9,2.7,[(x,z)],2.1)
   n.box(f'S20 {side} nominal slot mouth {x} {z}',[x-2.1,25.2 if sign==1 else -27.9,min(edge,z)],[4.2,2.7,abs(edge-z)],'cut',servo)
 n.box(f'S20 {side} open cradle rear for case and wire clearance',[39.3723,-.5 if sign==1 else -.6,92.7],[20.6,1.1,41.1],'cut',carrier)
 # Small rounded posts outside the case replace the original square supports.
 for x in [34.1723,65.1723]:
  y=sign*21.7
  n.extrude(f'S20 {side} rounded carrier bridge post X{x}','xy',123.8,n.circles(x,y,[5]),10,'join',carrier)
  n.extrude(f'S20 {side} rounded bridge end X{x}','xy',133.8,n.circles(x,y,[5]),9.45,'join',bridge)
  n.extrude(f'S20 {side} bridge vertical M3 bore X{x}','xy',123.8,n.circles(x,y,[1.7]),10,'cut',carrier)
  n.extrude(f'S20 {side} bridge through M3 bore X{x}','xy',133.8,n.circles(x,y,[1.7]),9.45,'cut',bridge)
  r=6/math.sqrt(3)
  pts=[(x+r*math.cos(math.pi/6+i*math.pi/3),y+r*math.sin(math.pi/6+i*math.pi/3)) for i in range(6)]
  n.extrude(f'S20 {side} captive bridge M3 hex X{x}','xy',128.7,n.poly(pts),2.8,'cut',carrier)
  n.box(f'S20 {side} bridge nut side insertion X{x}',[x-3,sign*21.7-22 if sign==1 else sign*21.7,128.7],[6,22,2.8],'cut',carrier)
 # Extend the lower ear pad below the sliding base; clear its entire travel in the bed.
 # Its nut loads from the servo-facing side and is trapped when the servo is seated.
 n.box(f'S20 {side} full lower servo nut pad',[35.6723,20.2 if sign==1 else -25.2,84],[28,5,8.7],'join',carrier)
 n.box(f'S20 {side} lower ear pad bed travel clearance',[33.3723,19.9 if sign==1 else -28.2,83.7],[31.6,8.3,2.9],'cut',32)
 # The sliding base would otherwise block both the screw tips and screwdriver.
 n.drill(f'S20 {side} lower ear M3 complete passage',carrier,17.8 if sign==1 else -25.2,7.4,[(44.6723,88.75),(54.6723,88.75)],1.7)
 n.drill(f'S20 {side} lower ear nut head and driver corridor',carrier,25.2 if sign==1 else -68.2,43,[(44.6723,88.75),(54.6723,88.75)],3.5)
 # Face-load servo nuts while each support is on the bench, then seat the servo.
 for x in [44.6723,54.6723]:
  n.hex_pocket(f'S20 {side} captured lower servo ear nut X{x}',carrier,22.4 if sign==1 else -25.2,2.8,x,88.75,6)
  n.hex_pocket(f'S20 {side} captured upper servo ear nut X{x}',bridge,18.2 if sign==1 else -21.0,2.8,x,137.75,6)
 # Restore an uninterrupted hub, then cut a positive keyed bore (AF7.3 clearance).
 n.ring(f'S20 {side} restore adapter core',44.4 if sign==1 else -53.8,9.4,5.5,0,'join',adapter,49.6723)
 n.hex_pocket(f'S20 {side} positive REX adapter AF7p3',adapter,44.4 if sign==1 else -53.8,9.4,49.6723,123,7.3)
 n.ring(f'S20 {side} factory Eclip captive pocket D14',49.5 if sign==1 else -50.7,1.2,7,0,'cut',adapter,49.6723)
 n.box(f'S20 {side} factory Eclip radial insertion window',[49.6723,49.5 if sign==1 else -50.7,116],[12,1.2,14],'cut',adapter)
 n.ring(f'S20 {side} restore balanced input pulley core',62.75 if sign==1 else -79.75,17,8,0,'join',pulley,49.6723)
 n.hex_pocket(f'S20 {side} positive REX pulley AF7p3',pulley,62.75 if sign==1 else -79.75,17,49.6723,123,7.3)
 # Positive bores transmit torque but do not locate a pulley axially.
 # Integral lands stop at the two bearing INNER races, clearing stationary caps.
 n.box(f'S20 {side} pulley rear flange running gap0p5',[29.6723,79.5 if sign==1 else -79.75,103],[40,.25,40],'cut',pulley)
 n.ring(f'S20 {side} pulley front inner race land',61.2 if sign==1 else -63.0,1.8,5.5,4.1,'join',pulley,49.6723)
 n.ring(f'S20 {side} pulley rear inner race land',79.3 if sign==1 else -80.8,1.5,5.5,4.1,'join',pulley,49.6723)
 n.hex_pocket(f'S20 {side} pulley lands positive REX bore',pulley,61.2 if sign==1 else -80.8,19.6,49.6723,123,7.3)
 n.drill(f'S20 {side} rear housing race land running throat D12',carrier,79.3 if sign==1 else -81.1,1.8,[(49.6723,123)],6)

rex=n.import_step(ROOT/'design/vendor/input-rex-48/input-rex-48.step','S20 L purchased REX48 and factory Eclip',
 [93.02629616519453,23.08096482024346,116.03323396981114],[0,0,0,1])
rr=opposite_stock(rex,'S20 R purchased REX48 and factory Eclip proper stock rotation')
n.parts.update({'L input REX shaft and Eclip':rex,'R input REX shaft and Eclip':rr})
refs=[rex]
for name,part,pos in [('input rear spacer6','input-spacer-6',91),('input rear shim0p5','input-rear-shim',94),('input rear washer1p5','input-rear-washer',94.5)]:
 b=n.import_step(ROOT/f'design/vendor/{part}/{part}.step',f'S20 L purchased {name}',[49.6723,pos,123],[0,0,0,1]);refs.append(b)
 n.parts['L '+name]=b;n.parts['R '+name]=opposite_stock(b,f'S20 R purchased {name}')
# Vendor screw has head top at Z0 and shank toward -Z; rotate its axis into +Y.
# Head undersurface is Z-2.2, so it seats on the washer back at Y96.
b=n.import_step(ROOT/'design/vendor/input-end-screw/input-end-screw.step','S20 L purchased input end M4x8',
 [49.6723,98.2,123],[-math.sqrt(.5),0,0,math.sqrt(.5)])
n.parts['L input end screw']=b;n.parts['R input end screw']=opposite_stock(b,'S20 R purchased input end M4x8 proper stock rotation');refs.append(b)
for name,part,pos in [('output mouth spacer6','input-spacer-6',108),('output mouth spacer2','output-spacer-2',112)]:
 b=n.import_step(ROOT/f'design/vendor/{part}/{part}.step',f'S20 L purchased {name}',[0,pos,123],[0,0,0,1])
 n.parts['L '+name]=b;n.parts['R '+name]=opposite_stock(b,f'S20 R purchased {name}',0)

# Named views are native saved configurations, with retired bodies removed.
for a in n.m['body_appearances']:
 if a['body_id'] in [301,309]:a.update(material_name='PETG positive REX horn adapter with captive Eclip',filament_type='PETG')
 if a['body_id'] in [10,27]:a.update(material_name='PETG positive REX 24T pulley',filament_type='PETG')
for name,b in n.parts.items():
 n.m['body_appearances'].append(dict(body_id=b,color=dict(r=175,g=185,b=200,a=255),material_name=name,filament_type='REFERENCE',brand='goBILDA',color_name='',filament_id=None,preset_id=None,density_g_cm3=None,diameter_mm=1.75))
for v in n.m['views']:
 original=set(v['visible_body_ids']);v['visible_body_ids']=[b for b in v['visible_body_ids'] if b not in retired]
 if 6 in original:v['visible_body_ids'] += refs
 if 23 in original:v['visible_body_ids'] += [n.parts[k] for k in n.parts if k.startswith('R ')]
 if 385 in original:v['visible_body_ids'] += [n.parts[k] for k in n.parts if k.startswith('L output mouth')]
v=dict(name='06 Servo mounts and captured nuts',camera=dict(position=[110,75,172],target=[49.6723,23,126],up=[0,0,1]),visible_body_ids=[12,367,437])
n.m['views'].append(v)
n.m['views'].append(dict(name='07 Positive REX input stack',camera=dict(position=[110,110,168],target=[49.6723,65,123],up=[0,0,1]),visible_body_ids=[5,445,301,10,377,378]+refs))
for s in n.m['sketches']:
 if s['name'].startswith('S20 '):clean(s)
n.m['visibility']['hidden_body_ids']=[b for b in n.m['visibility']['hidden_body_ids'] if b not in retired]
n.parts.update({'retired_body_ids':sorted(retired),'revision':'S20','input_key_af_mm':7.3,'nominal_input_shaft_start_mm':46.5,'nominal_input_shaft_end_mm':94.5,'clip_pocket_y_mm':[49.5,50.7],'clip_y_mm':[49.8,50.5],'bridge_bolt':'M3x16','servo_ear_bolt':'M3x10','nominal_input_endplay_mm':.2,'nominal_input_pulley_endplay_mm':.4,'pulley_lands_y_mm':[61.2,80.8]})
n.save_candidate('s20-adversarial')
