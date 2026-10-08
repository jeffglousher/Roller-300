"""S19 native CAD features; the application owns replay, solids and renders."""
from pathlib import Path
import copy,json,math,zipfile
from drivetrain_native_revision import Native

ROOT=Path(__file__).resolve().parents[1]
n=Native.__new__(Native)
with zipfile.ZipFile(ROOT/'Roller-300.nbcad') as z:n.entries={p:z.read(p) for p in z.namelist()}
n.m=json.loads(n.entries['model.json'])
assert len(n.m['document']['history']['features'])==1657,'Requires the saved S18 model'
n.fid=max(f['id'] for f in n.m['document']['history']['features'])
n.did=max(p['datum_id'] for p in n.m['datum_planes'])
n.bid=max([b for e in n.m['extrudes'] for b in e['new_body_ids']]+[b for e in n.m['body_features'] for k in ('body_ids','new_body_ids','result_body_ids') for b in e.get(k,[])]+[e['body_id'] for e in n.m['body_features'] if 'body_id' in e])
n.parts={}
(ROOT/'.local/before-s19-servo-horn.nbcad.bak').write_bytes((ROOT/'Roller-300.nbcad').read_bytes())

def shift_plane(s,dy):
    s['basis']['origin'][1]+=dy
    p=next(p for p in n.m['datum_planes'] if p['datum_id']==s['plane']['datum_id'])
    p['basis']['origin'][1]+=dy;p['source']['distance']=-p['basis']['origin'][1]

# Relocate the removable servo supports together. Belt plane and bearings stay put.
for s in n.m['sketches']:
    name=s['name']
    if name=='S01 L servo cradle pocket':
        shift_plane(s,-4)
        next(e for e in n.m['extrudes'] if e['sketch_name']==name)['extent']['distance']=38.1
    if name.startswith('S07 ') and any(w in name for w in ('servo cradle root','servo ear insertion','servo ear mounting','servo ear M3','top bridge bolt supports','removable upper ear support','upper ear M3')):
        shift_plane(s,4 if 'S07 R ' in name else -4)
        if 'servo cradle root' in name:next(e for e in n.m['extrudes'] if e['sketch_name']==name)['extent']['distance']=37.5
    if name.startswith('S07 ') and ('bridge M3 vertical' in name or 'bridge M3 support' in name):
        dy=4 if 'S07 R ' in name else -4
        for _,ent in s['snapshot']['entities']:
            for k in ('position','center'):
                if k in ent:ent[k]['y']+=dy
        s.pop('profile_identities',None);s['snapshot']['generated_points']=[]
    if name in ('S15 L carrier lower servo ear clearance','S15 L bed lower servo ear clearance'):shift_plane(s,-4)

pattern=[(49.6723+x,123+z) for x,z in [(-8,-8),(-8,8),(8,-8),(8,8)]]
n.suppress({943,946,949,952,954,957,960,963,966,969,971,974})
for side,sign,servo,adapter,carrier in [('L',1,12,301,437),('R',-1,29,309,440)]:
    n.move([servo],f'S19 {side} servo seated at new ear datum',y=-4*sign)
    # The supplied drawing distinguishes 37.5 case from the 4 mm shaft projection.
    n.box(f'S19 {side} case drawing top datum',[35,38.5 if sign==1 else -41.5,90],[30,3,47],'cut',servo)
    n.ring(f'S19 {side} nominal 5p9 spline envelope',38.5 if sign==1 else -42.5,4,2.95,0,'join',servo,49.6723)
    n.ring(f'S19 {side} integral horn flange',42.1 if sign==1 else -47.8,5.7,16.6,4.1,'join',adapter,49.6723)
    n.drill(f'S19 {side} horn pilot D14p4 clearance',adapter,42.1 if sign==1 else -44.9,2.8,[(49.6723,123)],7.2)
    n.drill(f'S19 {side} four horn M4 bores',adapter,42.1 if sign==1 else -47.8,5.7,pattern,2.25)
    n.drill(f'S19 {side} recessed M4x6 button heads',adapter,45.6 if sign==1 else -47.8,2.2,pattern,4)
    n.box(f'S19 {side} raised shaft pinch ears',[43.6723,47.8 if sign==1 else -53.8,131],[12,6,10.5],'join',adapter)
    n.ring(f'S19 {side} restore narrow inner race land',52.8 if sign==1 else -53.8,1,5.5,4.1,'join',adapter,49.6723)
    n.box(f'S19 {side} continue shaft pinch relief',[49.2223,44.9 if sign==1 else -53.8,126.8],[.9,8.9,16],'cut',adapter)
    n.extrude(f'S19 {side} raised M3 pinch through','yz',43.6723,n.circles(sign*50.8,138,[1.7]),12,'cut',adapter)
    n.extrude(f'S19 {side} M3 pinch head seat','yz',43.6723,n.circles(sign*50.8,138,[3.1]),3.2,'cut',adapter)
    r=6/math.sqrt(3)
    n.extrude(f'S19 {side} captive M3 pinch nut','yz',52.8723,n.poly([(sign*50.8+r*math.cos(i*math.pi/3),138+r*math.sin(i*math.pi/3)) for i in range(6)]),2.8,'cut',adapter)
    n.drill(f'S19 {side} horn and adapter complete rotation clearance',carrier,38.5 if sign==1 else -53.8,15.3,[(49.6723,123)],19.8)
    n.parts[f'{side} integrated horn shaft adapter']=adapter

horn=n.import_step(ROOT/'design/vendor/servo-horn-1906-0025-0032/1906-0025-0032.STEP','S19 L purchased H25T horn 1906-0025-0032',[49.6723,39.5,123],[0,math.sin(math.pi/8),0,math.cos(math.pi/8)])
right=n.mirror([horn],'S19 R purchased H25T horn')[0]
n.parts.update({'L metal horn':horn,'R metal horn':right,'horn_fasteners':{'pattern_mm':[16,16],'count_per_drive':4,'bolt':'M4x6 ISO7380-1','nominal_engagement_mm':2.5,'head_seat_y_mm':45.6,'center_screw':'M3 low-profile button head, nominal head D5.7 x 1.65 mm; length selected to seat without bottoming'},'nominal_axial_stack_left_mm':{'servo_base':1,'case_top':38.5,'spline_tip':42.5,'horn_thread_boss_back':38.6,'horn_spline_entry':39.5,'horn_face':42.1,'horn_pilot_end':44.1,'center_head_seat':44.1,'input_shaft_start':46,'adapter_race_land_end':53.8,'first_bearing_start':54},'release':'Unpowered fit; nominal 3mm spline engagement. Verify actual seating, screw length and thread before power.'})
for b in [horn,right]:
    n.m['body_appearances'].append(dict(body_id=b,color=dict(r=165,g=173,b=185,a=255),material_name='Purchased metal H25T horn 1906-0025-0032',filament_type='REFERENCE',brand='goBILDA',color_name='',filament_id=None,preset_id=None,density_g_cm3=None,diameter_mm=1.75))
for a in n.m['body_appearances']:
    if a['body_id'] in [301,309]:a.update(material_name='PETG integrated H25T horn / supported shaft adapter',filament_type='PETG')
    if a['body_id'] in [12,29]:a['material_name']='INJORA supplied drawing case / nominal 25T spline envelope'
for v in n.m['views']:
    if v['name'].startswith('01 '):v['visible_body_ids']+= [horn,right]
    elif v['name'].startswith(('02 ','03 ')):v['visible_body_ids']+=[horn]
n.m['views'].append(dict(name='05 Servo horn and adapter detail',camera=dict(position=[105,92,162],target=[49.6723,45,123],up=[0,0,1]),visible_body_ids=[6,12,301,horn]))
for s in n.m['sketches']:
    if s['name'].startswith('S19 '):
        s.pop('profile_identities',None);s.pop('entity_id_high_water',None);s['snapshot']['generated_points']=[]
n.save_candidate('s19-servo-horn')
