"""Integrated left wheel/belt print proposal. Native NoBS CAD from canonical parameters.
No physical validation. Only the wheel fit set is released for unpowered assessment.
"""
from pathlib import Path
import json,math,base64,datetime,zipfile,sys,struct
from collections import Counter
import build as B
from PIL import Image,ImageDraw,ImageFont
ROOT=B.ROOT;P=B.P;F=P['drive_article'];A=B.A;Z=B.R
YI=F['wheel_inner_y'];YM=F['wheel_main_outer_y'];YO=F['wheel_retainer_outer_y']
RR=F['rim_radius_mm'];RB=F['bead_radius_mm'];RT=F['tread_radius_mm'];NS=F['spokes']
assert abs(2*RT-P['wheel_diameter'])<1e-9 and YO-YI==P['tire_width']
OUT=ROOT/'first-prints';OUT.mkdir(exist_ok=True)
parts=[]
def ring(name,x,y,z,ro,ri,length,kind='printed',release=False):
 q=dict(name=name,type='ring',x=x,z=z,y0=y,length=length,ro=ro,ri=ri,kind=kind,release=release);parts.append(q);return q
def box(name,lo,sz,kind='printed'):
 q=dict(name=name,type='box',lo=lo,sz=sz,kind=kind);parts.append(q);return q
def model_save(c,path):
 d=c.call('cad_project_model');m=d.get('value',d);m=json.loads(m) if isinstance(m,str) else m
 names={a['body_id']:a['material_name'] for a in m['body_appearances']};cs=m['assembly']['component_structure'];cn={}
 for co in cs['definitions']:
  if len(co['body_ids'])==1:co['name']=str(co['id'])+': '+names.get(co['body_ids'][0],co['name'])
  cn[co['id']]=co['name']
 for oc in cs['occurrences']:oc['name']=cn[oc['component_id']]
 manifest={'format':'nbcad-project','container_version':1,'model':'model.json','model_schema_version':m['schema_version'],'application':'noBS CAD','application_version':'0.1.0','saved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('manifest.json',json.dumps(manifest));z.writestr('model.json',json.dumps(m))
 return m
def refine_clearances(c,source,upgrade_wheel=False):
 """Clear known review-model overlaps. Does not close the held interfaces."""
 def find(prefix):return next(q for q in source if q['name'].startswith(prefix))
 def move(b,xyz):c.call('solid_move_copy',{'body_ids':[b],'translation':dict(zip('xyz',xyz)),'pivot':{'x':0,'y':0,'z':0},'copy':False})
 def circular_cut(b,x,z,r,y,l):
  move(b,[0,-y,0]);s=c.sketch();c.circle(x,z,r);c.extrude(s,l,b);move(b,[0,y,0])
 def box_cut(b,lo,sz):
  x,y,z=lo;dx,dy,dz=sz;move(b,[0,-y,0]);s=c.sketch();c.rectangle(x,z,dx,dz);c.extrude(s,dy,b);move(b,[0,y,0])
 fb=find('P04')['body_id'];cb=find('P06')['body_id'];gb=find('P10')['body_id']
 if upgrade_wheel:
  wheel=find('P01')['body_id'];pc=F['wheel_bolt_circle_mm']/2
  for k in range(NS):
   t=k*math.tau/NS
   q=dict(name='construction nut seat reinforcement',type='ring',x=pc*math.cos(t),z=Z+pc*math.sin(t),y0=YI+2.8,length=3.7,ro=7,ri=4.8,kind='printed');c.part(q)
   c.call('solid_combine',{'target_body_id':wheel,'tool_body_ids':[q['body_id']],'operation':'join','keep_tools':False})
 # Thin front relief clears the flange. Shift the outer input bearing to99 so its
 # seven-mm race sits beyond the relief, with its end retaining ring beyond it.
 for prefix,x,y,r,l in [('P05 wheel bearing cap 99',0,93.5,24.5,1.75),('P07 input bearing cap 98',A,92.5,13.4,2.75)]:
  for b in [find(prefix)['body_id'],fb if x==0 else cb]:circular_cut(b,x,Z,r,y,l)
 for prefix in ['B 608 input bearing 98','U DIN471 retaining ring']:
  q=find(prefix);move(q['body_id'],[0,1,0]);q['y0']+=1
 # Remove the small rail overlap with the sliding carriage, retaining the main rail.
 box_cut(fb,[A-23.2,10,Z-31],[2,90,12])
 # Bearing blocks form the central portions of the outside cover. Cut mating windows
 # with explicit lateral clearance; full sealed shaft passages remain a power gate.
 for x,half in [(0,23),(A,20)]:box_cut(gb,[x-half-.2,101.9,Z-34.2],[2*half+.4,3.2,50.4])
 # Eliminate the unexplained one-mm support gap under the tension carriage.
 q=dict(name='construction carriage sole',type='box',lo=[A-23,6,Z-32],sz=[46,98,1.01],kind='printed');c.part(q);sole=q['body_id']
 for x in [A-17,A+17]:
  for y in [18,58]:
   s=c.sketch('xy');c.rectangle(x-3.7,y-2.2,7.4,4.4);c.extrude(s,0,sole,True,False)
 c.call('solid_combine',{'target_body_id':cb,'tool_body_ids':[sole],'operation':'join','keep_tools':False})
 find('P06')['lo'][2]=Z-32;find('P06')['sz'][2]=7
 # Split hub journal and nut so the explanatory metal drive plate is not drawn
 # through a solid nut. These internal dimensions remain schematic placeholders.
 hub=find('U ComInTec hub');q=dict(name='construction journal',type='ring',x=0,z=Z,y0=63,length=26,ro=7,ri=4,kind='unresolved');c.part(q)
 c.call('solid_combine',{'target_body_id':hub['body_id'],'tool_body_ids':[q['body_id']],'operation':'intersect','keep_tools':False});hub['ro']=7
 q=dict(name='U clutch adjustment nut - schematic envelope',type='ring',x=0,z=Z,y0=63,length=11,ro=11,ri=7,kind='unresolved');c.part(q);source.append(q)
 c.ids=[q['id'] for q in c.call('solid_scene')['bodies']]
 print('Cleared carriage, bearing-front and cover overlaps; held interfaces remain labeled',flush=True)
def build():
 c=B.CAD();c.call('cad_set_document_name',{'name':'Roller-300 | INJORA wheel-belt article | powered release HOLD'})
 def create(q):c.part(q);return q['body_id']
 def rawring(x,y,z,ro,ri,l):
  q=dict(name='construction',type='ring',x=x,z=z,y0=y,length=l,ro=ro,ri=ri,kind='printed');c.part(q);return q['body_id']
 def rawbox(lo,sz):
  q=dict(name='construction',type='box',lo=lo,sz=sz,kind='printed');c.part(q);return q['body_id']
 def sync():c.ids=[b['id'] for b in c.call('solid_scene')['bodies']]
 def join(target,tools):
  c.call('solid_combine',{'target_body_id':target,'tool_body_ids':tools,'operation':'join','keep_tools':False});sync()
 def move(b,xyz,rotation=None):
  args={'body_ids':[b],'translation':dict(zip('xyz',xyz)),'pivot':{'x':0,'y':0,'z':0},'copy':False}
  if rotation:args['rotation']=rotation
  c.call('solid_move_copy',args)
 def holes(b,centers,r):
  for x,z in centers:
   s=c.sketch();c.circle(x,z,r);c.extrude(s,0,b,True)
 def recess(b,x,z,r,y,l):
  move(b,[0,-y,0]);s=c.sketch();c.circle(x,z,r);c.extrude(s,l,b);move(b,[0,y,0])
 def hexrecess(b,x,z,af,y,l):
  move(b,[0,-y,0]);s=c.sketch();c.call('sketch_polygon',{'center':{'x':x,'y':z},'edge_count':6,'radius_text':str(af/2),'rotation_deg':30,'mode':'circumscribed'});c.extrude(s,l,b);move(b,[0,y,0])
 pc=F['wheel_bolt_circle_mm']/2
 wheelholes=[(pc*math.cos(k*math.tau/NS),Z+pc*math.sin(k*math.tau/NS)) for k in range(NS)]
 hubholes=[(x,Z+z) for x in [-8,8] for z in [-8,8]]
 # Wheel: continuous inboard guarding disk, thin rim, eight deep ribs, thick hub web.
 w=ring('P01 wheel center - ribs and continuous inner disk',0,YI,Z,RB,32,3,release=True);bid=create(w)
 wy0,wy1=F['web_y'];bits=[rawring(0,YI+2.8,Z,RR,RR-4,YM-YI-2.8),rawring(0,YI+2.8,Z,28,17,wy0-YI-2.5),rawring(0,wy0,Z,28,F['hub_register_hole_mm']/2,wy1-wy0)]
 for k in range(NS):
  t=math.tau*k/NS;co,si=math.cos(t),math.sin(t)
  poly=[]
  sw=F['spoke_width_mm']/2
  for u,v in [(25,-sw),(RR-3,-sw),(RR-3,sw),(25,sw)]:poly.append([u*co-v*si,Z+u*si+v*co])
  q={'name':'construction','type':'poly','y0':YI+2.8,'length':wy1-YI-2.8,'contours':[poly],'kind':'printed'};c.part(q);bits.append(q['body_id'])
 for x,z in wheelholes:
  bits.append(rawring(x,YI+2.8,z,5,0,YM-YI-2.8))
  bits.append(rawring(x,YI+2.8,z,7,4.8,3.7))
 join(bid,bits);holes(bid,wheelholes,2.2);holes(bid,hubholes,2.2)
 for x,z in wheelholes:hexrecess(bid,x,z,7.3,YI,5.2)
 # Inboard access opening leaves clamp-hub screws reachable before wheel installation.
 print('Built ribbed full-size wheel center',flush=True)
 w2=ring('P02 removable outer bead retainer - recessed M4 heads',0,YM,Z,RB,pc-3,YO-YM,release=True);br=create(w2);holes(br,wheelholes,2.2)
 for x,z in wheelholes:recess(br,x,z,4.3,YO-4.5,4.5)
 # TPU tread has stepped beads: positive lateral retention by both PETG flanges.
 clr=F['tire_fit_radial_clearance_mm']
 tr=ring('P03 TPU tread - smooth indoor surface, captured beads',0,YI,Z,RT,RB+clr,3,'tire',True);tb=create(tr)
 join(tb,[rawring(0,YI+3,Z,RT,RR+clr,YM-YI-3),rawring(0,YM,Z,RT,RB+clr,YO-YM)])
 # Eight shallow torque keys at the center of the rim, mirrored by tread cutouts.
 # Keys overlap structural rim; tire pockets are cut from the matching local coordinates.
 for k in range(NS):
  t=math.tau*(k+.5)/NS;co,si=math.cos(t),math.sin(t);poly=[]
  for u,v in [(RR-1.5,-2),(RB,-2),(RB,2),(RR-1.5,2)]:poly.append([u*co-v*si,Z+u*si+v*co])
  q={'name':'construction','type':'poly','y0':YI+9,'length':16,'contours':[poly],'kind':'printed'};c.part(q);join(bid,[q['body_id']])
  # Oversize cavity is a temporary solid tool; numeric clearance is explicit.
  poly=[]
  for u,v in [(RR-.5,-2.2),(RB+.2,-2.2),(RB+.2,2.2),(RR-.5,2.2)]:poly.append([u*co-v*si,Z+u*si+v*co])
  q={'name':'construction','type':'poly','y0':YI+8.8,'length':16.4,'contours':[poly],'kind':'printed'};c.part(q)
  c.call('solid_combine',{'target_body_id':tb,'tool_body_ids':[q['body_id']],'operation':'cut','keep_tools':False});sync()
 # Rest of module: review geometry; all uncertain interfaces remain amber and held.
 create(ring('B wheel shaft 8 mm - prepared 110 mm length HOLD',0,38,Z,4,0,110,'purchased'))
 for yc in [51,99]:create(ring('B 608 wheel bearing '+str(yc),0,yc-3.5,Z,11,4,7,'purchased'))
 for y in [38.5,102.5]:create(ring('B 8x21x9 wheel clamp collar',0,y,Z,10.5,4,9,'purchased'))
 create(ring('B HyperHub 1310-0016-0008 full bounding envelope',0,113,Z,15.3,4,20.5,'purchased'))
 create(ring('B HyperHub 14 mm register',0,133.5,Z,7,4,2,'purchased'))
 for x,z in hubholes:
  create(ring('B M4x10 wheel-hub screw',x,128.5,z,2,0,10,'purchased'))
  create(ring('B M4 wheel-hub screw head',x,138.5,z,3.5,0,4,'purchased'))
 for x,z in wheelholes:
  create(ring('B M4x35 bead screw',x,110.5,z,2,0,35,'purchased'))
  create(ring('B recessed M4 bead screw head',x,145.5,z,3.5,0,4,'purchased'))
  create(ring('B captured M4 nut envelope',x,112,z,4.04,2,3.2,'purchased'))
 # Structural base and registered bearing blocks are one native solid.
 frame=box('P04 integrated drive frame - mount detail HOLD',[-32,5,Z-40],[114,100,8]);fb=create(frame)
 bparts=[]
 for yc in [51,99]:
  block=rawbox([-23,yc-5.5,Z-33],[46,11,33]);holes(block,[(0,Z)],11.075);bparts.append(block)
 # Deep fore/aft rails carry bending back to future barrel mounting interface.
 bparts.extend([rawbox([-30,10,Z-33],[8,90,13]),rawbox([20,10,Z-33],[8,90,13])]);join(fb,bparts)
 # Caps stay separate. Seat fit still coupon-dependent; shoulders oppose collars.
 for yc in [51,99]:
  q=box('P05 wheel bearing cap '+str(yc),[-23,yc-5.5,Z],[46,11,16]);cap=create(q);holes(cap,[(0,Z)],11.075)
  # Vertical M4 bolt passages, through cap and saddle, open nut access below base.
  for x in [-17,17]:
   for body in [cap,fb]:
    s=c.sketch('xy');c.circle(x,yc,2.2);c.extrude(s,0,body,True,False)
  # Outer-race retention lips; clear inner races and metal collars radially.
  lip_y=yc-5.5 if yc==51 else yc+3.5
  for body,sign in [(fb,-1),(cap,1)]:
   lip=rawring(0,lip_y,Z,14,10.7,2)
   s=c.sketch();c.rectangle(-15,Z if sign<0 else Z-15,30,15);c.extrude(s,0,lip,True)
   join(body,[lip])
 # Input carriage carries BOTH bearings and servo; whole carriage will tension together.
 carr=box('P06 input carriage - servo cradle measurement HOLD',[A-23,6,Z-31],[46,98,6]);cb=create(carr)
 for yc in [72,98]:
  b=rawbox([A-20,yc-5.5,Z-25],[40,11,25]);holes(b,[(A,Z)],11.075);join(cb,[b])
  q=box('P07 input bearing cap '+str(yc),[A-20,yc-5.5,Z],[40,11,16]);cap=create(q);holes(cap,[(A,Z)],11.075)
  for x in [A-15,A+15]:
   for b in [cap,cb]:
    s=c.sketch('xy');c.circle(x,yc,2.2);c.extrude(s,0,b,True,False)
  create(ring('B 608 input bearing '+str(yc),A,yc-3.5,Z,11,4,7,'purchased'))
 create(ring('B independent 8 mm input shaft - end grooves HOLD',A,55,Z,4,0,49,'purchased'))
 create(ring('U input inboard clamp/bridge interface',A,57,Z,10,4,10,'unresolved'))
 create(ring('U DIN471 retaining ring + groove position to specify',A,101.7,Z,4.6,3.6,0.8,'unresolved'))
 create(box('B owned INJORA - published CASE only, ears absent',[A-30,8,Z-10],[40.5,40.5,20],'purchased'))
 create(ring('B owned purchased spool - 19 x11 overall only',A,49,Z,9.5,3,11,'purchased'))
 create(ring('U floating spool-to-shaft torque adapter HOLD',A,59,Z,12,4.2,9,'unresolved'))
 # Four frame/carriage M4 slots; bearings and motor translate together +/-1.5 mm.
 for x in [A-17,A+17]:
  for y in [18,58]:
   s=c.sketch('xy');c.rectangle(x-3.7,y-2.2,7.4,4.4);c.extrude(s,0,cb,True,False)
   s=c.sketch('xy');c.circle(x,y,2.2);c.extrude(s,0,fb,True,False)
 print('Built frame, supported shafts, caps and input carriage',flush=True)
 # Explicit clutch functional stack. Internal thicknesses are explanatory placeholders.
 create(ring('U ComInTec hub and adjustment nut - supplier candidate',0,63,Z,11,4,26,'unresolved'))
 create(ring('U metal pressure flange section - schematic',0,79.5,Z,12.5,7,1.5,'unresolved'))
 create(ring('U friction face 1 - thickness unconfirmed',0,81,Z,12.5,7,1,'unresolved'))
 plate=ring('U metal driven plate 40x2 - bush bore must be confirmed',0,82,Z,20,8,2,'unresolved');pl=create(plate)
 create(ring('U friction face 2 - thickness unconfirmed',0,84,Z,12.5,7,1,'unresolved'))
 create(ring('U metal fixed flange - schematic',0,85,Z,12.5,7,4,'unresolved'))
 # Tooth shape follows traced HTD3M coordinates. Bore/attachment are separate print gates.
 prof=[[-1.135062,0],[-1.048323,.015484],[-.974284,.058517],[-.919162,.123974],[-.889176,.206728],[-.81721,.579614],[-.778384,.72416],[-.716685,.856903],[-.634505,.975764],[-.534238,1.078662],[-.418278,1.16352],[-.289019,1.228257],[-.148854,1.270793],[0,1.28905],[.148515,1.270895],[.288716,1.228406],[.418018,1.163675],[.534017,1.078795],[.634307,.975857],[.716481,.856953],[.778133,.724174],[.816857,.579614],[.888471,.206728],[.919014,.123974],[.974328,.058517],[1.048362,.015484],[1.135062,0]]
 for n,x,ri in [(48,0,13.5),(24,A,4.1)]:
  r=n*3/math.tau-.381;cont=[]
  for k in range(n):
   t=k*math.tau/n
   # Place tooth-space data on chord, as source generator; retain land arc.
   for u,h in prof:
    rr=r-h;cont.append([x+rr*math.cos(t)-u*math.sin(t),Z+rr*math.sin(t)+u*math.cos(t)])
  q=dict(name=f'P08 {n}T HTD3M pulley - tooth-fit / adapter HOLD',type='poly',y0=82,length=12,contours=[cont],kind='unresolved');parts.append(q);pb=create(q);holes(pb,[(x,Z)],ri)
  if n==48:
   recess(pb,0,Z,20.15,82,2)
   hh=[(17*math.cos(k*math.pi/2),Z+17*math.sin(k*math.pi/2)) for k in range(4)]
   holes(pb,hh,1.65);holes(pl,hh,1.65)
   for xx,zz in hh:hexrecess(pb,xx,zz,5.7,91,3)
  # Flanges are modeled, attachment remains part of held pulley detail.
  create(ring(f'P09 {n}T inboard belt flange',x,80.5,Z,r+2,ri,1.5,'unresolved'))
  create(ring(f'P09 {n}T outboard belt flange',x,94,Z,r+2,ri,1,'unresolved'))
  print('Built '+str(n)+'T traced HTD profile',flush=True)
 # Purchased belt swept loop envelope. Teeth not modeled on purchased belt.
 r1,r2=B.BPR;theta=math.acos((r2-r1)/A)
 def contour(off):return [[(r2+off)*math.cos(t),Z+(r2+off)*math.sin(t)] for t in [theta+(math.tau-2*theta)*j/60 for j in range(61)]]+[[A+(r1+off)*math.cos(t),Z+(r1+off)*math.sin(t)] for t in [-theta+2*theta*j/40 for j in range(41)]]
 q=dict(name='B accepted 210-3M-09 endless belt envelope',type='poly',y0=83.5,length=9,contours=[contour(1.6),contour(-1.1)],kind='belt');parts.append(q);create(q)
 # Guard cap: three-sided removable cover; full sealing / axial passages still HOLD.
 guard=box('P10 removable belt guard - service and seal detail HOLD',[-30,102,Z-34],[106,3,68]);gb=create(guard);holes(gb,[(0,Z),(A,Z)],11)
 walls=[rawbox([-30,76,Z-34],[106,26,3]),rawbox([-30,76,Z+31],[106,26,3]),rawbox([-30,76,Z-31],[3,26,62]),rawbox([73,76,Z-31],[3,26,62])];join(gb,walls)
 for xx,zz in [(-24,Z-28),(70,Z-28),(-24,Z+28),(70,Z+28)]:holes(gb,[(xx,zz)],2.2)
 print('Built proposed removable guard',flush=True)
 refine_clearances(c,parts)
 pre=c.call('solid_export_preflight');m=model_save(c,ROOT/'drive-article.nbcad');scene=c.call('solid_scene')
 (ROOT/'drive-article-scene.json').write_text(json.dumps(scene));(ROOT/'drive-article-source-map.json').write_text(json.dumps(parts,indent=2))
 checks={'preflight':pre,'physical_tests':'NOT PERFORMED','powered_release':False,'release_scope':'P01/P02/P03 unpowered wheel fit set only. All module parts remain review geometry pending interface closure.','stl':[]}
 checks['stl']=export_fit_meshes(c,parts)
 c.call('cad_load_project_model',{'model_json':json.dumps(m)});checks['reload_preflight']=c.call('solid_export_preflight');(ROOT/'drive-article-checks.json').write_text(json.dumps(checks,indent=2));c.proc.terminate()
 print('Saved native article and three wheel fit STLs',flush=True)
 render(scene,parts)
 package()
def export_fit_meshes(c,parts):
 checks={'stl':[]}
 # Export complete solids in a print orientation: axle Y maps to build Z.
 for q in parts:
  if not q.get('release'):continue
  b=q['body_id'];ex=c.call('solid_export_stl',{'body_ids':[b],'linear_deflection':.05,'angular_deflection':.12});data=next(base64.b64decode(v) for k,v in ex.items() if 'base64' in k and isinstance(v,str))
  n=struct.unpack_from('<I',data,80)[0];vertices=[];faces=[]
  for j in range(n):
   v=struct.unpack_from('<12fH',data,84+50*j);tri=[]
   for k in range(3):
    x,y,z=v[3+3*k:6+3*k];tri.append((x,-(z-Z),y-110))
   faces.append(tri);vertices.extend(tri)
  # Put each individual part on Z=0 without modifying assembly coordinates.
  mz=min(v[2] for v in vertices);dst=bytearray(b'Roller300 unpowered wheel-fit prototype; units mm'.ljust(80,b' ')+struct.pack('<I',n));edges=Counter();vol=0
  for tri in faces:
   tri=[(v[0],v[1],v[2]-mz) for v in tri];a,b,d=tri;u=[b[k]-a[k] for k in range(3)];v=[d[k]-a[k] for k in range(3)];normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];l=math.sqrt(sum(t*t for t in normal));normal=[t/l if l else 0 for t in normal]
   dst.extend(struct.pack('<12fH',*normal,*a,*b,*d,0))
   for j in range(3):edges[tuple(sorted([tuple(round(t,4) for t in tri[j]),tuple(round(t,4) for t in tri[(j+1)%3])]))]+=1
   vol+=(a[0]*(b[1]*d[2]-b[2]*d[1])+a[1]*(b[2]*d[0]-b[0]*d[2])+a[2]*(b[0]*d[1]-b[1]*d[0]))/6
  name={'P01':'wheel-center-246-fit.stl','P02':'wheel-bead-retainer-fit.stl','P03':'tpu-tread-246-fit.stl'}[q['name'][:3]];(OUT/name).write_bytes(dst)
  checks['stl'].append({'file':name,'triangles':n,'nonmanifold_edges':sum(v!=2 for v in edges.values()),'solid_volume_mm3':abs(vol),'bounds_mm':[[min(v[k] for v in vertices)-(mz if k==2 else 0) for k in range(3)],[max(v[k] for v in vertices)-(mz if k==2 else 0) for k in range(3)]]})
 return checks['stl']
def package():
 checks=json.loads((ROOT/'drive-article-checks.json').read_text())
 assert len(checks['stl'])==3
 assert all(q['nonmanifold_edges']==0 and q['solid_volume_mm3']>0 for q in checks['stl'])
 for q in checks['stl']:
  data=(OUT/q['file']).read_bytes();n=struct.unpack_from('<I',data,80)[0];parents=list(range(n));seen={}
  def root(i):
   while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
   return i
  for i in range(n):
   v=struct.unpack_from('<12fH',data,84+50*i);tri=[tuple(round(t,4) for t in v[3+3*k:6+3*k]) for k in range(3)]
   for j in range(3):
    edge=tuple(sorted([tri[j],tri[(j+1)%3]]))
    if edge in seen:parents[root(i)]=root(seen[edge])
    else:seen[edge]=i
  q['connected_mesh_components']=len({root(i) for i in range(n)})
  assert q['connected_mesh_components']==1,(q['file'],q['connected_mesh_components'])
 checks['known_clearance_corrections']=['bearing-front pulley relief','outer input bearing and ring moved one mm','carriage rail relief and continuous sole','cover mating windows','schematic clutch journal/nut split','wheel captive-nut seats locally thickened to seven mm radius']
 (ROOT/'drive-article-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
 slices=[]
 for q in checks['stl']:
  stem=Path(q['file']).stem;sp=OUT/'slicer-check'/(stem+'-slice-result.json')
  if not sp.exists():continue
  r=json.loads(sp.read_text())
  if r.get('return_code')!=0:continue
  plate=r['sliced_plates'][0]
  with zipfile.ZipFile(OUT/'slicer-check'/(stem+'-estimate.3mf')) as z:bounds=json.loads(z.read('Metadata/plate_1.json'))['bbox_all']
  assert min(bounds)>=0 and max(bounds)<=256
  slices.append({'part':stem,'filament_g':sum(f['total_used_g'] for f in plate['filaments']),'estimated_hours':plate['total_predication']/3600,'first_layer_xy_bounds_mm':bounds,'warning_message':plate['warning_message']})
 checks['offline_slicer_estimates']={'parts':slices,'all_three_sliced':len(slices)==3,'basis':'Installed X2D 0.4 mm profile; generic PETG/TPU, 0.2 mm layers, 15% gyroid; PETG five walls, TPU three. Explicit center (128,128), main nozzle only, 3 mm brim. Estimated consumption includes print aids. Actual nozzle/material and physical results unconfirmed.','toolpath_review':'First-layer bounds, generated support presence and native slicer thumbnails checked; not a complete layer-by-layer print qualification.'}
 (ROOT/'drive-article-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
 instructions='''Roller-300 / 246 mm wheel fit set / 13 September 2026

Unpowered fit and assembly prototype. Not a qualified running wheel or a complete powered belt assembly.
Editable CAD: drive-article.nbcad. Canonical decisions and sources: PLAN.md and parameters.json.

Print one of each STL, in millimetres, at 100% scale. Each is oriented on Z=0.
- wheel-center-246-fit.stl: PETG. Inner guarding disk on bed. Local support is needed under the central hub barrel and raised hub web; inspect the pilot bore after removing support.
- wheel-bead-retainer-fit.stl: PETG. Flat inner face on bed; counterbores upward.
- tpu-tread-246-fit.stl: TPU. One bead face on bed. Inspect bead steps and internal key-pocket roofs in the slicer.

Starting settings only: 0.2 mm layers; PETG five walls, TPU three walls. Material grade, infill, creep and strength are not qualified. Use the X2D main nozzle alone for the 246 mm tread. Center the part at (128,128); automatic arrangement in the tested CLI incorrectly limited it to the two-nozzle intersection. Review the actual printer/nozzle/filament profile and toolpaths before printing.

Wheel-only assembly hardware: goBILDA 1310-0016-0008 HyperHub, four M4x10 cap screws, eight M4x35 cap screws, eight M4 plain hex nuts. Verify actual thread engagement and access before tightening. Shaft, bearings, clutch and complete drive hardware are additional BOM items.

Fit the captive nuts first. Align the TPU keys over the rim, fit the outer retaining ring and install the eight bead screws. Tighten the shaft clamp before attaching the wheel to its hub with four screws. Confirm the tire seats fully, the ring closes flat, and no screw projects outside the 40 mm tire width. Check wobble, bead/key fit, hub register and tool access by hand. Do not apply powered or deliberate overload tests yet.

Record slicer/material settings, printed mass, fits and observations in test-record.json. CAD solid/mesh checks do not establish physical performance. The servo mount/adapter, shaft retention, clutch interfaces and guarding remain unfinished in the proposed belt module.
'''
 with zipfile.ZipFile(OUT/'wheel-fit-set.zip','w',zipfile.ZIP_DEFLATED) as z:
  for q in checks['stl']:z.write(OUT/q['file'],q['file'])
  z.writestr('READ-ME-FIRST.txt',instructions)
 record=json.loads((ROOT/'test-record.json').read_text())
 record['drive_article']['actual_CAD_checks']=checks
 record['drive_article']['sliced']=len(slices)==3
 record['drive_article']['archive']='first-prints/wheel-fit-set.zip'
 record['current_CAD_checks']={'article':'drive-article-checks.json','BOM':'bom-check.json','historical_whole_vehicle':'cad-reload-check.json'}
 (ROOT/'test-record.json').write_text(json.dumps(record,indent=2)+'\n')
 print('Packaged three manifold wheel-fit meshes; offline slices: '+str(len(slices))+'/3; physical tests NOT PERFORMED',flush=True)
def render(scene,source):
 # CAD mesh view. Open review state and exploded wheel set, never pretend a physical photograph.
 import numpy as np
 colors=B.COL;labels={q['body_id']:q for q in source}
 for mode in ['overall','drive','wheel']:
  W,H=1600,1000;im=Image.new('RGB',(W,H),(247,249,251));d=ImageDraw.Draw(im)
  font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
  title={'overall':'ONE WHEEL + BELT / INTEGRATED TEST ARTICLE','drive':'DRIVE MODULE / WHEEL AND GUARD REMOVED','wheel':'FIRST SUBSTANTIAL PRINT / FULL-SIZE WHEEL FIT SET'}[mode]
  d.text((40,24),title,font=font(31),fill=(25,48,62));d.text((40,71),'Native CAD geometry. Powered release HOLD: servo mount / adapter, input retention, clutch and guarding.',font=font(20),fill=(158,94,26))
  right=np.array([-.72,.694,0]);up=np.array([-.29,-.301,.908]);front=np.cross(right,up)
  shown=[]
  for b in scene['bodies']:
   q=labels.get(b['id']);
   if not q:continue
   n=q['name']
   if mode=='drive' and (n.startswith(('P01','P02','P03')) or 'bead screw' in n or 'captured M4 nut' in n or 'wheel-hub screw' in n or n.startswith('P10')):continue
   if mode=='wheel' and not q.get('release'):continue
   v=np.array(b['mesh']['positions']).reshape(-1,3).copy();v[:,2]-=Z;v[:,1]-=80
   if mode=='wheel':v[:,1]+= {'P01':0,'P02':75,'P03':-70}[n[:3]]
   if mode=='overall' and n.startswith('P10'):v[:,1]-=65;v[:,2]+=60
   coords=np.column_stack([v@right,v@up,v@front]);shown.append((b,q,coords))
  allp=np.concatenate([t[2] for t in shown]);low=allp[:,:2].min(axis=0);high=allp[:,:2].max(axis=0);scale=min(1320/(high[0]-low[0]),720/(high[1]-low[1]));center=(low+high)/2
  zbuf=np.full((H,W),-1e30);pix=im.load()
  for b,q,coords in shown:
   vv=coords.copy();vv[:,0]=800+(vv[:,0]-center[0])*scale;vv[:,1]=480-(vv[:,1]-center[1])*scale
   norms=np.array(b['mesh']['normals']).reshape(-1,3);inds=b['mesh']['indices'];col=colors[q['kind']]
   for j in range(0,len(inds),3):
    ids=inds[j:j+3];p=vv[ids];brightness=.50+.50*abs(float(norms[ids].mean(axis=0)@front));color=tuple(int(t*brightness) for t in col)
    for row in range(max(110,math.ceil(p[:,1].min())),min(880,math.floor(p[:,1].max()))+1):
     cuts=[];scan=row+.5
     for k in range(3):
      a,bp=p[k],p[(k+1)%3]
      if min(a[1],bp[1])<=scan<max(a[1],bp[1]):
       t=(scan-a[1])/(bp[1]-a[1]);cuts.append((a[0]+t*(bp[0]-a[0]),a[2]+t*(bp[2]-a[2])))
     if len(cuts)!=2:continue
     (xl,zl),(xr,zr)=sorted(cuts)
     if xr-xl<1e-8:continue
     for cc in range(max(0,math.ceil(xl-.5)),min(W-1,math.floor(xr-.5))+1):
      zz=zl+(cc+.5-xl)*(zr-zl)/(xr-xl)
      if zz>zbuf[row,cc]:zbuf[row,cc]=zz;pix[cc,row]=color
  notes={'overall':['246 x40 wheel | 210 mm purchased belt | 24/48T proposed reduction','Guard lifted for inspection. Teal = printed structure; gray = purchased; amber = unfinished interface.'], 'drive':['Two bearings per shaft; belt loads carried by frame. Clutch at driven pulley.','Input carriage moves motor and both bearing seats together. Case shown at published size; ears unmeasured.'],'wheel':['PETG ribbed center + PETG bolted bead ring + TPU tread with eight internal drive keys','STLs are for unpowered fit / assembly assessment. Verify printer margin, hub fit, tire fit and bolt access.']}[mode]
  for j,line in enumerate(notes):d.text((40,899+j*34),line,font=font(22),fill=(29,50,63))
  im.save(ROOT/('drive-article-'+mode+'.png'))
 print('Rendered three CAD views',flush=True)
if __name__=='__main__':
 if '--package-only' in sys.argv:package()
 elif '--render-only' in sys.argv:render(json.loads((ROOT/'drive-article-scene.json').read_text()),json.loads((ROOT/'drive-article-source-map.json').read_text()))
 elif '--refine-only' in sys.argv:
  c=B.CAD()
  with zipfile.ZipFile(ROOT/'drive-article.nbcad') as zz:m=json.loads(zz.read('model.json'))
  c.call('cad_load_project_model',{'model_json':json.dumps(m)});c.ids=[b['id'] for b in c.call('solid_scene')['bodies']]
  source=json.loads((ROOT/'drive-article-source-map.json').read_text());refine_clearances(c,source,upgrade_wheel=True);m=model_save(c,ROOT/'drive-article.nbcad');scene=c.call('solid_scene')
  (ROOT/'drive-article-scene.json').write_text(json.dumps(scene));(ROOT/'drive-article-source-map.json').write_text(json.dumps(source,indent=2));checks=json.loads((ROOT/'drive-article-checks.json').read_text());checks['stl']=export_fit_meshes(c,source);checks['refined_preflight']=c.call('solid_export_preflight');checks['known_clearance_corrections']=['bearing-front pulley relief','carriage rail relief and continuous sole','cover mating windows','schematic clutch journal/nut split'];(ROOT/'drive-article-checks.json').write_text(json.dumps(checks,indent=2));c.proc.terminate();render(scene,source)
 else:build()
