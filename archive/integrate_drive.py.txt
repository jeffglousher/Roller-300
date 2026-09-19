"""Vehicle end-section revision. Reuses the existing mechanism, not the bench base.
Editable native CAD; no physical validation or powered-test release.
"""
from pathlib import Path
import json,math,zipfile,copy,base64,struct
import build as B
import drive_article as D
ROOT=B.ROOT;P=B.P;A=B.A;Z=B.R
CFG=P['integrated_drive'];RO=CFG['outside_diameter_mm']/2;RI=RO-CFG['shell_mm']
parts=[]
def keep_mechanism():
 old=json.loads((ROOT/'drive-article-source-map.json').read_text())
 def wanted(q):
  n=q['name']
  return not n.startswith(('P01','P02','P03','P04','P06','P10')) and not any(t in n for t in ['bead screw','captured M4','wheel-hub screw']) and not ('INJORA' in n and q['type']=='box')
 selected=[copy.deepcopy(q) for q in old if wanted(q)];kept={q['body_id'] for q in selected};needed=set(kept)
 with zipfile.ZipFile(ROOT/'drive-article.nbcad') as z:m=json.loads(z.read('model.json'))
 # Follow the actual boolean dependency graph to retain consumed construction tools.
 changed=True
 while changed:
  before=set(needed)
  for f in m['body_features']:
   if f['type']=='combine' and f['target_body_id'] in needed:needed.update(f['tool_body_ids'])
  changed=needed!=before
 ex=[f for f in m['extrudes'] if needed.intersection(f.get('new_body_ids',[])+f.get('target_body_ids',[]))]
 names={f['sketch_name'] for f in ex};sk=[s for s in m['sketches'] if s['name'] in names]
 bf=[f for f in m['body_features'] if (f['type']=='combine' and f['target_body_id'] in needed) or (f['type']!='combine' and needed.intersection(f.get('body_ids',[])+f.get('result_body_ids',[])))]
 ids={f['feature_id'] for f in ex+sk+bf};m.update(extrudes=ex,sketches=sk,body_features=bf)
 m['document']['history']['features']=[f for f in m['document']['history']['features'] if f['id'] in ids];m['document']['history']['rollback_index']=len(ids)
 m['body_appearances']=[q for q in m['body_appearances'] if q['body_id'] in kept]
 cs=m['assembly']['component_structure'];cs['definitions']=[q for q in cs['definitions'] if set(q['body_ids']).issubset(kept)];defs={q['id'] for q in cs['definitions']};cs['occurrences']=[q for q in cs['occurrences'] if q['component_id'] in defs]
 m['visibility']['hidden_body_ids']=[]
 return m,selected,kept

def merged_model(old,new):
 """Combine independent native feature histories, preserving editable sketches and booleans."""
 n=copy.deepcopy(new);off=10000
 families=['sketches','extrudes','revolves','sweeps','lofts','ribs','fillets','chamfers','holes','datum_planes','body_features']
 for family in families:
  for f in n[family]:
   f['feature_id']+=off;f['name']='End_'+f['name']
   if f.get('sketch_name'):f['sketch_name']='End_'+f['sketch_name']
   for key in ['new_body_ids','target_body_ids','body_ids','tool_body_ids','result_body_ids']:
    if key in f:f[key]=[v+off for v in f[key]]
   if 'target_body_id' in f:f['target_body_id']+=off
  old[family].extend(n[family])
 for f in n['document']['history']['features']:f['id']+=off;f['name']='End_'+f['name']
 old['document']['history']['features'].extend(n['document']['history']['features'])
 old['document']['history']['rollback_index']=len(old['document']['history']['features'])
 old['document']['name']='Roller-300 | vehicle drive end section | fit review'
 for q in n['body_appearances']:q['body_id']+=off
 old['body_appearances'].extend(n['body_appearances'])
 a=old['assembly']['component_structure'];b=n['assembly']['component_structure']
 for q in b['definitions']:q['id']+=off;q['body_ids']=[v+off for v in q['body_ids']];q['name']='End_'+q['name']
 for q in b['occurrences']:
  q['id']+=off;q['component_id']+=off;q['name']='End_'+q['name']
  if q['parent_occurrence_id'] is not None:q['parent_occurrence_id']+=off
 for key in ['definitions','occurrences']:a[key].extend(b[key])
 for key in ['next_component_id','next_occurrence_id']:a[key]=b[key]+off
 old['counters']={k:max(v,n['counters'][k]) for k,v in old['counters'].items()}
 old['visibility']['hidden_sketch_names'].extend('End_'+v for v in n['visibility']['hidden_sketch_names'])
 return old
def build():
 c=B.CAD();m,retained,kept=keep_mechanism();parts.extend(retained)
 print('Building vehicle structure independently; retained belt mechanism joins at final native reload',flush=True)
 c.call('cad_set_document_name',{'name':'Roller-300 | reusable vehicle drive end section | prototype'})
 def create(q,record=True):
  c.part(q)
  if record:parts.append(q)
  return q['body_id']
 def box(name,lo,sz,kind='printed',record=True):return create(dict(name=name,type='box',lo=lo,sz=sz,kind=kind),record)
 def ring(name,x,y,z,ro,ri,l,kind='printed',record=True):return create(dict(name=name,type='ring',x=x,z=z,y0=y,length=l,ro=ro,ri=ri,kind=kind),record)
 def sync():c.ids=[q['id'] for q in c.call('solid_scene')['bodies']]
 def combine(target,tools,op='join'):
  c.call('solid_combine',{'target_body_id':target,'tool_body_ids':tools,'operation':op,'keep_tools':False});sync()
 def move(b,y):c.call('solid_move_copy',{'body_ids':[b],'translation':{'x':0,'y':y,'z':0},'pivot':{'x':0,'y':0,'z':0},'copy':False})
 def ycut(b,x,z,r,y=0,l=0):
  if y:move(b,-y)
  s=c.sketch();c.circle(x,z,r);c.extrude(s,l,b,l==0)
  if y:move(b,y)
 def cutbox(b,lo,sz):combine(b,[box('construction',lo,sz,record=False)],'cut')
 def zhole(b,x,y,r,depth):
  c.call('solid_move_copy',{'body_ids':[b],'translation':{'x':0,'y':0,'z':-Z},'pivot':{'x':0,'y':0,'z':0},'copy':False})
  s=c.sketch('xy');c.circle(x,y,r);c.extrude(s,depth,b,False,True)
  c.call('solid_move_copy',{'body_ids':[b],'translation':{'x':0,'y':0,'z':Z},'pivot':{'x':0,'y':0,'z':0},'copy':False})
 def nut_side(b,x,y,outside_x):
  lo=min(x-4.1,outside_x);hi=max(x+4.1,outside_x)
  cutbox(b,[lo,y-3.7,Z-18.5],[hi-lo,7.4,3.6])
 def hex_y(b,x,z,af,y,l):
  move(b,-y);s=c.sketch();c.call('sketch_polygon',{'center':{'x':x,'y':z},'edge_count':6,'radius_text':str(af/2),'rotation_deg':30,'mode':'circumscribed'});c.extrude(s,l,b);move(b,y)
 servo=box('B owned INJORA case / rotated / ears and axis offset unmeasured',[A-10,8,Z-30],[20,40.5,40.5],'purchased')
 # These are final-body datums, also usable as protected clamp faces.
 frame=ring('P04 vehicle drive end section / D159 body interface',0,44,Z,RO,63,6)
 pilot=ring('construction',0,42,Z,75.5,63,2.2,record=False)
 skin=ring('construction',0,49.8,Z,RO,RI,52.2,record=False)
 cutbox(skin,[-RO-1,49,Z],[2*RO+2,54,RO+1])
 end=ring('construction',0,96,Z,RO,72.5,6,record=False)
 combine(frame,[pilot,skin,end])
 # Shared body-interface opening clears the complete nominal carriage travel.
 cutbox(frame,[24,41.9,Z-40],[49,8.2,23])
 # Two ribbed wheel-bearing bulkheads. Their lower edges follow the body circle.
 ribs=[]
 for yc in [51,99]:
  rib=ring('construction',0,yc-5.5,Z,RO,0,11,record=False)
  cutbox(rib,[-RO-1,yc-6,Z],[2*RO+2,12,RO+1])
  for x in [-RO-1,23]:cutbox(rib,[x,yc-6,Z-RO-1],[RO-22,12,RO+2])
  ycut(rib,0,Z,11.075)
  cutbox(rib,[-12,yc-6,Z-61],[24,12,34])
  ribs.append(rib)
 combine(frame,ribs)
 # Rails remain inside the future central body's wall and support the sliding input spine.
 for x in [A-18,A+13]:
  rail=box('construction',[x-4,50.5,Z-38],[8,53.5,9],record=False);combine(frame,[rail])
 # Cross-web links the rails to the inner wheel bulkhead, preserving the belt bay.
 cross=box('construction',[-22,50.5,Z-38],[90,8,9],record=False);combine(frame,[cross])
 # Motor/carriage attachment uses the same four holes for the vehicle and bench tests.
 for x in [A-18,A+13]:
  for y in [56,84]:
   # Blind vertical holes in the rails; side-entry M4 nuts are accessible from below the saddle.
   zhole(frame,x,y,2.2,41)
   cutbox(frame,[x-4.2,y-3.7,Z-36.5],[8.4,7.4,3.6])
 for yc in [51,99]:
  for x in [-17,17]:zhole(frame,x,yc,2.2,24);nut_side(frame,x,yc,-23.2 if x<0 else 23.2)
 # Outer-race lips oppose the shaft collars; no clutch preload enters these races.
 for yc,y in [(51,45.5),(99,102.5)]:
  lip=ring('construction',0,y,Z,14,10.7,2,record=False);cutbox(lip,[-15,y-.1,Z],[30,2.2,15]);combine(frame,[lip])
 ycut(frame,0,Z,24.5,93.5,1.75)
 mount=[]
 for k in range(4):
  t=k*math.pi/2;x=69*math.cos(t);z=Z+69*math.sin(t);mount.append([x,z-Z]);ycut(frame,x,z,2.2);hex_y(frame,x,z,7.3,46.6,3.4)
 print('Built curved load-bearing end section and body register',flush=True)
 # Carriage + replaceable saddle: all move together for tension adjustment.
 carr=box('P06 input spine / belt tension and removable servo saddle',[A-23,6,Z-29],[41.5,98,4])
 cutbox(carr,[A-11.5,5.9,Z-29.1],[23,44.1,4.2])
 for yc in [72,98]:
  post=box('construction',[A-20,yc-5.5,Z-25],[40,11,25],record=False);combine(carr,[post])
 ycut(carr,A,Z,11.075);ycut(carr,A,Z,13.4,92.5,2.75)
 for yc in [72,98]:
  for x in [A-15,A+15]:zhole(carr,x,yc,2.2,24);nut_side(carr,x,yc,A-20.2 if x<A else A+20.2)
 for x in [A-18,A+13]:
  for y in [56,84]:
   c.call('solid_move_copy',{'body_ids':[carr],'translation':{'x':0,'y':0,'z':-Z},'pivot':{'x':0,'y':0,'z':0},'copy':False})
   s=c.sketch('xy');c.rectangle(x-3.7,y-2.2,7.4,4.4);c.extrude(s,40,carr,False,True)
   c.call('solid_move_copy',{'body_ids':[carr],'translation':{'x':0,'y':0,'z':Z},'pivot':{'x':0,'y':0,'z':0},'copy':False})
 # Tall cheeks support the saddle without pretending the unmeasured mounting ears are fitted.
 # A small replaceable saddle is the only servo-specific print. Main carrier survives measurement changes.
 saddle=box('U replaceable INJORA saddle / mounting measurements required',[A-11,7,Z-34],[22,43,4],'unresolved')
 for y in [12,42]:
  tab=box('construction',[A-17.5,y-4,Z-33],[35,8,4],kind='unresolved',record=False);combine(saddle,[tab])
  for x in [A-14.5,A+14.5]:
   zhole(carr,x,y,1.7,35);zhole(saddle,x,y,1.7,35)
 # Clearance relief on the saddle's lower forward corners for the full +1.5 mm tension travel.
 x=A+17.5;s=c.sketch();pts=[(x-2,Z-33.1),(x+.1,Z-33.1),(x+.1,Z-31)]
 for a,b in zip(pts,pts[1:]+pts[:1]):c.call('sketch_add_line',{'from':dict(zip(['x','y'],a)),'to_raw':dict(zip(['x','y'],b)),'ctrl_held':True})
 c.extrude(s,0,saddle,True)
 # Low side ribs stiffen the motor's cantilever without inventing its ear geometry.
 for x in [A-23,A+15.5]:
  rib=box('construction',[x,6,Z-25],[3,44,6],record=False);combine(carr,[rib])
 print('Built common motor/input-bearing spine; full servo mount still requires measurement',flush=True)
 # Cover matches the drum. Bearing bulkheads form portions of the outside wall.
 cover=ring('P10 circular end cover / mating window finish required',0,102,Z,RO,0,3)
 for x,half,bottom in [(0,23.3,-RO-1),(A,21.8,-36.3)]:cutbox(cover,[x-half,101.9,Z+bottom],[2*half,3.2,16.3-bottom])
 # Four conventional M3 countersunk cover screws; nut pockets open inboard.
 for k in range(4):
  t=(k+.5)*math.pi/2;x=73*math.cos(t);z=Z+73*math.sin(t)
  boss=ring('construction',x,96,z,6,0,6,record=False);combine(frame,[boss]);ycut(frame,x,z,1.7);hex_y(frame,x,z,5.8,96,3)
  ycut(cover,x,z,1.7)
  # Revolved 90-degree countersink; screw head remains within Y105.
  # Sketch XY at Z=0, translate the target in Z to put the local screw axis on it.
  c.call('solid_move_copy',{'body_ids':[cover],'translation':{'x':0,'y':0,'z':-z},'pivot':{'x':0,'y':0,'z':0},'copy':False})
  sk=c.sketch('xy');pts=[(x+1.7,103.55),(x+3.15,105),(x+1.7,105)]
  for a,b in zip(pts,pts[1:]+pts[:1]):c.call('sketch_add_line',{'from':dict(zip(['x','y'],a)),'to_raw':dict(zip(['x','y'],b)),'ctrl_held':True})
  c.call('sketch_finish');c.call('solid_revolve',{'sketch_name':sk,'profile_indices':[0],'axis_origin':{'x':x,'y':0},'axis_direction':{'x':0,'y':1},'angle_deg':360,'flip':False,'operation':'cut','target_body_ids':[cover]})
  c.call('solid_move_copy',{'body_ids':[cover],'translation':{'x':0,'y':0,'z':z},'pivot':{'x':0,'y':0,'z':0},'copy':False})
 # A short segment of the REAL mating body, shown for interface review only.
 parent=ring('C final central-body mating bulkhead / reference segment',0,38,Z,80,63,6,'clearance')
 ycut(parent,0,Z,75.65,42,2)
 cutbox(parent,[24,37.9,Z-40],[49,6.2,23])
 for x,z in mount:ycut(parent,x,Z+z,2.2)
 print('Built round cover and matching central-body interface',flush=True)
 pre=c.call('solid_export_preflight');assert pre['ok'],pre
 model=D.model_save(c,ROOT/'drive-end-structure.nbcad');scene=c.call('solid_scene')
 (ROOT/'drive-end-structure-source-map.json').write_text(json.dumps(parts[len(retained):],indent=2))
 merged=merged_model(m,model)
 print('Reloading complete editable mechanism with the new end section',flush=True)
 c.call('cad_load_project_model',{'model_json':json.dumps(merged)})
 for q in parts[len(retained):]:q['body_id']+=10000
 frame+=10000;carr+=10000
 pre=c.call('solid_export_preflight');assert pre['ok'],pre
 D.model_save(c,ROOT/'drive-end-section.nbcad');scene=c.call('solid_scene')
 (ROOT/'drive-end-section-scene.json').write_text(json.dumps(scene));(ROOT/'drive-end-section-source-map.json').write_text(json.dumps(parts,indent=2))
 # Geometry check, not a clearance/strength certification. Envelope applies to this drive section, not the outboard hub.
 labels={q['body_id']:q for q in parts};radial={}
 for b in scene['bodies']:
  q=labels[b['id']]
  if q['name'].startswith(('P04','P06','P10','U replaceable')):
   vv=b['mesh']['positions'];rmax=max(math.hypot(vv[j],vv[j+2]-Z) for j in range(0,len(vv),3));radial[q['name']]=rmax
   assert rmax<=RO+.02,(q['name'],rmax)
 out=ROOT/'first-prints'/'drive-end-section';out.mkdir(exist_ok=True)
 exported=[]
 for name,b in [('carrier-end-section-fit.stl',frame),('input-spine-fit.stl',carr)]:
  result=c.call('solid_export_stl',{'body_ids':[b],'linear_deflection':.05,'angular_deflection':.12});data=next(base64.b64decode(v) for k,v in result.items() if 'base64' in k and isinstance(v,str))
  # Model Y becomes print Z; each separate part rests on Z0.
  n=struct.unpack_from('<I',data,80)[0];ys=[]
  for j in range(n):ys.extend(struct.unpack_from('<12fH',data,84+50*j)[4:12:3])
  y0=min(ys);dst=bytearray(data[:84])
  for j in range(n):
   v=list(struct.unpack_from('<12fH',data,84+50*j));normal=[v[0],-v[2],v[1]];verts=[]
   for k in range(3):x,y,z=v[3+3*k:6+3*k];verts.extend([x,-(z-Z),y-y0])
   dst.extend(struct.pack('<12fH',*normal,*verts,0))
  (out/name).write_bytes(dst);exported.append(name)
 (ROOT/'drive-end-section-checks.json').write_text(json.dumps({'preflight':pre,'structural_radial_bounds_mm':radial,'body_interface':CFG,'exports':exported,'physical_tests':'NOT PERFORMED','powered_release':False,'open_interfaces':['owned servo saddle and torque adapter','input shaft groove/retention specification','clutch driven plate/bush and qualified torque/duty','cover windows and complete tool-access/fastener fit verification']},indent=2))
 c.proc.terminate();print('Saved native vehicle end section and two unpowered structural-fit STLs',flush=True)
 render(scene,parts)
def render(scene,source):
 # Reuse the same native mesh renderer, with this revision's titles and assembly views.
 import inspect
 code=inspect.getsource(D.render)
 code=code.replace("['overall','drive','wheel']","['overall','drive']")
 code=code.replace('ONE WHEEL + BELT / INTEGRATED TEST ARTICLE','VEHICLE DRIVE END SECTION / BODY INTERFACE')
 code=code.replace('DRIVE MODULE / WHEEL AND GUARD REMOVED','DRIVE END SECTION / ROUND COVER REMOVED')
 code=code.replace("'P01','P02','P03'","'P01','P02','P03'")
 code=code.replace('246 x40 wheel | 210 mm purchased belt | 24/48T proposed reduction','159 mm end section inside the 160 mm drum | final body register and M4 mounts')
 code=code.replace('Guard lifted for inspection. Teal = printed structure; gray = purchased; amber = unfinished interface.','Cover lifted. Green = mating central-body section. Amber = unmeasured / unqualified interfaces.')
 code=code.replace('Input carriage moves motor and both bearing seats together. Case shown at published size; ears unmeasured.','Same end section for the vehicle and clamped tests. Tire and wheel printing deferred.')
 code=code.replace("'drive-article-'","'drive-end-section-'")
 env=dict(D.__dict__);exec(code,env);env['render'](scene,source)
if __name__=='__main__':
 if '--render-only' in __import__('sys').argv:render(json.loads((ROOT/'drive-end-section-scene.json').read_text()),json.loads((ROOT/'drive-end-section-source-map.json').read_text()))
 else:build()
