"""Rebuild the Roller-300 packaging study from parameters.json using installed NoBS CAD.
Creates an isolated headless CAD process. Never attaches to or clears a desktop document.
All geometry is packaging/source evidence, NOT production or physical validation.
Run with the bundled Python runtime. --draw-only refreshes the current component sheet.
--refresh reuses unchanged independent bodies from the last native export.
"""
from pathlib import Path
import json, math, subprocess, sys, zipfile, datetime, base64
from PIL import Image, ImageDraw, ImageFont
from array import array
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'parameters.json').read_text())
R=P['wheel_diameter']/2; BR=P['body_diameter']/2
# Stored component positions use the axle frame; world Z is derived once.
for key in ['battery','pixracer','pi']:
 P[key+'_min_xyz']=[v+(R if j==2 else 0) for j,v in enumerate(P[key+'_min_xyz_axle'])]
P['servo_z0']=R+P['servo_z_from_axle']
for q in P['mass_estimates']:
 q['xyz']=[v+(R if j==2 else 0) for j,v in enumerate(q['xyz_axle'])]
P.update(body_length=2*BR,body_rear_x=-BR,body_floor_z=R-BR,body_height=2*BR)
GA=P['gear_module']*sum(P['gear_teeth'])/2
GI=P['gear_teeth'][1]/P['gear_teeth'][0]
bt=P['belt_trial']; BPR=[t*bt['pitch_mm']/(2*math.pi) for t in bt['pulley_teeth']]
def belt_length(c):
 r1,r2=BPR
 return 2*math.sqrt(c*c-(r2-r1)**2)+math.pi*(r1+r2)+2*(r2-r1)*math.asin((r2-r1)/c)
lo,hi=BPR[1]-BPR[0]+.01,bt['pitch_length_mm']/2
for _ in range(60):
 mid=(lo+hi)/2
 if belt_length(mid)>bt['pitch_length_mm']:hi=mid
 else:lo=mid
A=(lo+hi)/2; I=bt['pulley_teeth'][1]/bt['pulley_teeth'][0]
GEAR_RO=[P['gear_module']*(t+2)/2 for t in P['gear_teeth']]
TRACK=P['body_width']+2*P['wheel_gap']+P['tire_width']
HW=P['body_width']/2; TY=HW+P['wheel_gap']; SW=P.get('bearing_support_width',46)
parts=[]
COL={'printed':(92,141,151),'purchased':(123,133,149),'unresolved':(214,149,67),'tire':(61,67,76),'clearance':(115,174,125),'conflict':(190,75,70)}
COL.update(optics=(176,106,162),range_sensor=(69,161,147),belt=(61,67,76))
def box(name,lo,sz,kind='printed',holes=None):
 parts.append(dict(name=name,type='box',lo=lo,sz=sz,kind=kind,holes=holes or []));return parts[-1]
def ring(name,x,z,y0,length,ro,ri=0,kind='purchased',trim=None):
 parts.append(dict(name=name,type='ring',x=x,z=z,y0=y0,length=length,ro=ro,ri=ri,kind=kind,trim=trim));return parts[-1]
shell=ring('P barrel lower shell; integration study',0,R,-HW+3,2*HW-6,BR,BR-P['skin'],'printed',('above',R+P['body_lid_split_height_above_axle']))
lid=ring('P removable curved electronics lid',0,R,-HW+3,2*HW-6,BR,BR-P['skin'],'printed',('below',R+P['body_lid_split_height_above_axle']))
# Camera openings await actual lens centers and complete connector envelopes.
nr=BR
for s,side in [(1,'L'),(-1,'R')]:
 def yr(a,b): return (a,b-a) if s==1 else (-b,b-a)
 def sr(n,x,z,a,b,ro,ri=0,k='purchased'):
  y,l=yr(a,b);return ring(f'{side} {n}',x,z,y,l,ro,ri,k)
 def sb(n,x,z,a,b,dx,dz,k='printed',holes=None):
  y,l=yr(a,b);return box(f'{side} {n}',[x,y,z],[dx,l,dz],k,holes)
 cv=sr('P transmission cover allowance',0,R,HW-3,HW,BR,8.5,'printed');cv['holes']=[(A,R,8.5)]
 sr('P wheel rim allowance; replace with ribs',0,R,TY,TY+P['tire_width'],R-P['wheel_tread_radial'],25,'printed')
 sr('P TPU tire allowance',0,R,TY,TY+P['tire_width'],R,R-P['wheel_tread_radial'],'tire')
 sr('B 8 mm smooth wheel shaft',0,R,*P['wheel_shaft_y'],4)
 sr('B 8 mm smooth input shaft',A,R,*P['input_shaft_y'],4)
 for x,ys,tag in [(0,P['output_bearing_y'],'wheel'),(A,P['input_bearing_y'],'input')]:
  for j,yc in enumerate(ys):
   sr(f'B 608 {tag} bearing {j+1}',x,R,yc-3.5,yc+3.5,11,4)
   low=R-math.sqrt((BR-4)**2-min(abs(x)+SW/2,BR-5)**2)
   # Lower saddle and removable cap have independently cut bearing-seat openings.
   sb(f'P integrated {tag} saddle {j+1}',x-SW/2,low,yc-4.5,yc+4.5,SW,R-low,
      holes=[(x,R,(P['bearing_od']+P['bearing_seat_diametral_allowance'])/2)])
   sb(f'P removable {tag} bearing cap {j+1}',x-SW/2,R,yc-4.5,yc+4.5,SW,17,
      holes=[(x,R,(P['bearing_od']+P['bearing_seat_diametral_allowance'])/2)])
 # Published clutch envelope; plate/bush detail is an explicitly unresolved interface.
 cy=P['clutch_y0']; ce=cy+P['clutch_length']; boss=ce-P['clutch_boss_length']
 sr('U ComInTec 00.25 DF d8 T1 supplier envelope; qualification pending',0,R,cy,ce,P['clutch_od']/2,4,'unresolved')
 sr('U proposed ground metal drive plate OD40 x2; bore/bush unresolved',0,R,82,84,20,0,'unresolved')
 fy=bt['pulley_face_y0_mm'];fw=bt['pulley_axial_envelope_mm']
 sr('U 48T pulley PITCH envelope; metal plate adapter unresolved',0,R,fy,fy+fw,BPR[1],13.5,'unresolved')
 sr('U 24T pulley PITCH envelope; no tooth form',A,R,fy,fy+fw,BPR[0],4,'unresolved')
 theta=math.acos((BPR[1]-BPR[0])/A)
 def belt_contour(offset):
  r1,r2=[v+offset for v in BPR]
  return [[r2*math.cos(a),R+r2*math.sin(a)] for a in [theta+(2*math.pi-2*theta)*j/20 for j in range(21)]]+[[A+r1*math.cos(a),R+r1*math.sin(a)] for a in [-theta+2*theta*j/16 for j in range(17)]]
 y,length=yr(fy+1.5,fy+1.5+9)
 parts.append(dict(name=f'{side} B 210-3M-09 belt LOOP ENVELOPE',type='poly',y0=y,length=length,contours=[belt_contour(1.5),belt_contour(-1.5)],kind='belt'))
 for location in ['inboard','outboard']:
  sr('B 2910-0921-0008 wheel collar '+location,0,R,*P['wheel_collars'][location+'_y'],10.5,4)
 sr('B 1310-0016-0008 wheel hub full circumscribed envelope',0,R,*P['wheel_hub']['overall_y'],15.3,4)
 sr('P wheel mounting web allowance; M4 pattern16 square',0,R,116,120,25,7,'printed')
 sv=P['servo_reserve_xyz'];sx=A+P['servo_x_offset_from_axis']
 sb('B goBILDA25-2 full fixed hardware envelope from STEP',sx,P['servo_z0'],P['servo_min_abs_y'],P['servo_min_abs_y']+sv[1],sv[0],sv[2],'purchased')
 # Horn and misalignment-tolerant torque-only bridge; NOT a torque limiter.
 sr('U included matching horn sweep; sample measurement pending',A,R,54.1,61,12,3,'unresolved')
 sr('P floating horn drive bridge allowance',A,R,61,68,10,4,'printed')
 sb('P servo cradle landing; replaceable retainer to detail',sx,P['servo_z0']-4,P['servo_min_abs_y'],54.1,sv[0],4)
 # Removable axial retention is kept separate from clutch preload.
 sr('U input retention allowance - actual hardware NOT selected',A,R,63,69,7,4,'unresolved')
for name,key in [('Battery','battery'),('Pixracer','pixracer')]:
 box('U '+name+' installation reserve',P[key+'_min_xyz'],P[key+'_size_xyz'],'unresolved')
box('B Pi Zero Wi-Fi nominal bare-board envelope - variant pending',P['pi_min_xyz'],P['pi_size_xyz'],'purchased')
b=P['battery_min_xyz'];bs=P['battery_size_xyz']
box('P battery cradle floor',[b[0]-2,b[1]-2,b[2]-4],[bs[0]+4,bs[1]+4,4])
for x in [b[0]-4,b[0]+bs[0]]:
 box('P battery end stop',[x,b[1]-2,b[2]],[4,bs[1]+4,10])
for key,name in [('pixracer','P controller shelf'),('pi','P removable future Pi shelf')]:
 lo=P[key+'_min_xyz'];sz=P[key+'_size_xyz']
 box(name,[lo[0]-2,lo[1]-2,lo[2]-4],[sz[0]+4,sz[1]+4,4])
# Wire volumes are empty keep-outs, not solid printed ducts or selected cables.
for q in P['harness_reserves']:
 lo=[v+(R if j==2 else 0) for j,v in enumerate(q['min_xyz_axle'])]
 box('C '+q['name']+' - EMPTY HARNESS SPACE',lo,q['size_xyz'],'clearance')
q=P['power_distribution_reserve']
box('U power distribution / cutoff reserve',[v+(R if j==2 else 0) for j,v in enumerate(q['min_xyz_axle'])],q['size_xyz'],'unresolved')
th=P['camera_layout']['thermal']
box('B TOPDON TC002C Duo overall incl built-in USB plug',[v+(R if j==2 else 0) for j,v in enumerate(th['trial_min_xyz_axle'])],th['trial_size_xyz'],'optics')
# ToF has an exact front footprint but unknown depth; visible camera identity is unknown.
# Neither is represented by a guessed solid. Footprints and intended zones appear in sections.


def calculations():
 def intersects(a,b):
  return all(min(a['lo'][j]+a['sz'][j],b['lo'][j]+b['sz'][j])-max(a['lo'][j],b['lo'][j])>1e-6 for j in range(3))
 hardware=[q for q in parts if q['type']=='box' and q['kind'] in ['purchased','unresolved','optics']]
 wires=[q for q in parts if q['kind']=='clearance']
 structure=[q for q in parts if q['type']=='box' and q['kind']=='printed']
 thermal=next(q for q in hardware if 'TOPDON' in q['name'])
 rmax=max(math.hypot(thermal['lo'][0]+i*thermal['sz'][0],thermal['lo'][2]+j*thermal['sz'][2]-R) for i in [0,1] for j in [0,1])
 data={'revision':P['revision'],'scope':'Current mechanical CAD packaging checks only. No physical tests or complete-installed-fit claim.',
  'width_mm':TRACK+P['tire_width'],'wheel_diameter_mm':2*R,'body_diameter_mm':2*BR,'body_width_mm':2*HW,
  'active_belt_centers_mm':A,'belt_ratio':I,'nominal_shell_ground_clearance_mm':R-BR,
  'hardware_box_intersections':[[a['name'],b['name']] for k,a in enumerate(hardware) for b in hardware[k+1:] if intersects(a,b)],
  'harness_box_intersections':[[a['name'],b['name']] for a in wires for b in hardware+structure if intersects(a,b)],
  'thermal_inner_shell_corner_clearance_mm':BR-P['skin']-rmax,
  'thermal_above_servo_reserve_gap_mm':thermal['lo'][2]-(P['servo_z0']+P['servo_reserve_xyz'][2]),
  'pi_nominal_hardware_xyz_mm':P['pi_size_xyz'],'thermal_nominal_hardware_xyz_mm':thermal['sz'],
  'range_module_front_outline_width_height_mm':[20,12],'range_module_depth_mm':None,'visible_camera_size_mm':None,
  'optical_apertures_and_mated_connectors_complete':False,'raised_cover_withdrawn':True,
  'clutch_outer_bearing_nominal_gap_mm':(P['output_bearing_y'][1]-P['bearing_width']/2)-(P['clutch_y0']+P['clutch_length']),
  'clutch_inner_bearing_nominal_gap_mm':P['clutch_y0']-(P['output_bearing_y'][0]+P['bearing_width']/2),
  'wheel_bearing_span_mm':P['output_bearing_y'][1]-P['output_bearing_y'][0],
  'drive_detail_open':['input shaft retention and torque-only horn bridge','pulley tooth form / flanges / tension travel','metal clutch plate bush bore and attachment','wheel web/hub positive joint','cap bolts and axial shoulders'],
  'component_envelopes':P['component_envelopes'],'physical_validation':False,'all_hardware_packaged':False}
 assert abs(data['width_mm']-300)<1e-6
 assert not data['hardware_box_intersections'],data['hardware_box_intersections']
 assert not data['harness_box_intersections'],data['harness_box_intersections']
 assert data['thermal_inner_shell_corner_clearance_mm']>0
 (ROOT/'checks.json').write_text(json.dumps(data,indent=2)+'\n')
 return data

class CAD:
 def __init__(self):
  self.proc=subprocess.Popen([r'C:\Users\jeffg\AppData\Local\nbcad\mcp\nbcad-mcp.exe'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=(ROOT/'cad-runtime.log').open('w'),text=True,encoding='utf-8',creationflags=0x08000000)
  self.seq=0;self.ids=[];self.trace=[]
 def call(self,n,a=None):
  self.seq+=1;a=a or {};self.proc.stdin.write(json.dumps({'jsonrpc':'2.0','id':self.seq,'method':'tools/call','params':{'name':n,'arguments':a}})+'\n');self.proc.stdin.flush()
  while True:
   line=self.proc.stdout.readline()
   if not line:raise RuntimeError('CAD process ended')
   r=json.loads(line)
   if r.get('id')!=self.seq:continue
   if 'error' in r:raise RuntimeError(r)
   v=r['result']
   if v.get('isError'):raise RuntimeError(n+': '+str(v))
   d=v.get('structuredContent') or json.loads(v['content'][0]['text'])
   self.trace.append({'name':n,'arguments':a});return d
 def sketch(self,plane='xz'):
  name=self.call('sketch_begin',{'plane':{'type':'origin_plane','plane':plane}})['name']
  # Raw-coordinate tools still grid-snap on this installed CAD version.
  self.call('sketch_set_grid_snap',{'enabled':False})
  return name
 def rectangle(self,x,z,dx,dz):self.call('sketch_add_rectangle',{'mode':'two_point','p1':{'x':x,'y':z},'p2':{'x':x+dx,'y':z+dz},'ctrl_held':True})
 def circle(self,x,z,r):self.call('sketch_add_circle',{'mode':'center_diameter','p1':{'x':x,'y':z},'p2':{'x':x+r,'y':z},'ctrl_held':True})
 def extrude(self,sk,l,target=None,through=False,flip=True):
  self.call('sketch_finish')
  d=self.call('solid_extrude',{'sketch_name':sk,'profile_indices':[0],'operation':'cut' if target else 'new_body','extent':{'type':'through_all'} if through else {'type':'distance','distance':l},'taper_angle_deg':0,'flip':flip,'target_body_ids':[target] if target else []})
  if target:return target
  # Returned engine IDs, never guessed from operation count.
  scene=d.get('scene') or self.call('solid_scene');bs=scene.get('bodies',[])
  ids=[b.get('id',b.get('body_id')) for b in bs]
  fresh=[v for v in ids if v not in self.ids]
  if len(fresh)!=1:raise RuntimeError('Expected one new body: '+str(scene.keys())+str(fresh))
  self.ids=ids;return fresh[0]
 def part(self,q):
  sk=self.sketch()
  if q['type']=='box':
   x,y,z=q['lo'];dx,l,dz=q['sz'];self.rectangle(x,z,dx,dz)
  elif q['type']=='poly':
   y=q['y0'];l=q['length']
   for contour in q['contours']:
    for a,b in zip(contour,contour[1:]+contour[:1]):
     self.call('sketch_add_line',{'from':dict(zip(['x','y'],a)),'to_raw':dict(zip(['x','y'],b)),'ctrl_held':True})
  else:
   y=q['y0'];l=q['length'];self.circle(q['x'],q['z'],q['ro'])
   if q['ri']:self.circle(q['x'],q['z'],q['ri'])
  bid=self.extrude(sk,l)
  if y:self.call('solid_move_copy',{'body_ids':[bid],'translation':{'x':0,'y':y,'z':0},'pivot':{'x':0,'y':0,'z':0},'copy':False})
  for x,z,r in q.get('holes',[]):
   sk=self.sketch();self.circle(x,z,r);self.extrude(sk,0,bid,True)
  if q.get('trim'):
   direction,level=q['trim'];sk=self.sketch();self.rectangle(-BR-1,level if direction=='above' else -1,2*BR+2,2*BR+R if direction=='above' else level+1);self.extrude(sk,0,bid,True)
  for x,z,dx,dz in q.get('clip_rects',[]):
   sk=self.sketch();self.rectangle(x,z,dx,dz);self.extrude(sk,0,bid,True)
  for lo,sz in q.get('window_cuts',[]):
   x,yc,z=lo;dx,dy,dz=sz
   self.call('solid_move_copy',{'body_ids':[bid],'translation':{'x':0,'y':-yc,'z':0},'pivot':{'x':0,'y':0,'z':0},'copy':False})
   sk=self.sketch();self.rectangle(x,z,dx,dz);self.extrude(sk,dy,bid)
   self.call('solid_move_copy',{'body_ids':[bid],'translation':{'x':0,'y':yc,'z':0},'pivot':{'x':0,'y':0,'z':0},'copy':False})
  color=COL[q['kind']]
  self.call('set_body_appearance',{'body_id':bid,'material_name':q['name'],'filament_type':'PETG' if q['kind']=='printed' else 'TPU' if q['kind']=='tire' else 'REFERENCE','color_name':q['kind'],'color':dict(zip(['r','g','b','a'],[*color,255]))})
  q['body_id']=bid
 def save(self):
  d=self.call('cad_project_model')
  # Model response is a tagged wrapper on some installed versions.
  if 'value' in d:model=json.loads(d['value']) if isinstance(d['value'],str) else d['value']
  elif 'model_json' in d:model=json.loads(d['model_json']) if isinstance(d['model_json'],str) else d['model_json']
  else:model=d
  if model.get('format')!='nbcad-project':raise RuntimeError('Unexpected project response: '+str(d.keys()))
  names={a['body_id']:a['material_name'] for a in model['body_appearances']}
  cs=model['assembly']['component_structure'];cn={}
  for co in cs['definitions']:
   if len(co['body_ids'])==1:co['name']=str(co['id'])+': '+names.get(co['body_ids'][0],co['name'])
   cn[co['id']]=co['name']
  for oc in cs['occurrences']:oc['name']=cn[oc['component_id']]
  manifest={'format':'nbcad-project','container_version':1,'model':'model.json','model_schema_version':model['schema_version'],'application':'noBS CAD','application_version':'0.1.0','saved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  with zipfile.ZipFile(ROOT/'Roller-300.nbcad','w',zipfile.ZIP_DEFLATED) as z:
   z.writestr('manifest.json',json.dumps(manifest));z.writestr('model.json',json.dumps(model))
  pre=self.call('solid_export_preflight');(ROOT/'cad-check.json').write_text(json.dumps(pre,indent=2))
  scene=self.call('solid_scene');preview(scene,parts)
  (ROOT/'source-map.json').write_text(json.dumps(parts,indent=2))
  exp=self.call('solid_export_step')
  for key,v in exp.items():
   if 'base64' in key and isinstance(v,str):(ROOT/'Roller-300.step').write_bytes(base64.b64decode(v))
  # Native reload is the meaningful editable-file check.
  self.call('cad_load_project_model',{'model_json':json.dumps(model)})
  verify=self.call('solid_export_preflight');(ROOT/'cad-reload-check.json').write_text(json.dumps(verify,indent=2))
  self.proc.terminate()

def preview(scene,source):
 # Orthographic triangle rendering of actual OCCT tessellation, not an imagined product image.
 im=Image.new('RGB',(1800,1000),'white');dr=ImageDraw.Draw(im)
 font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
 dr.text((45,28),'ROUND TWO-WHEEL ROLLER / 300 mm wide',font=font(34),fill=(32,43,54))
 dr.text((45,80),'Native CAD study - selected servo / hubs; amber = unresolved interfaces. Green = wiring space. NOT FOR PRINT.',font=font(23),fill=(158,96,20))
 labels={q['body_id']:q for q in source if 'body_id' in q}
 # Direction to viewer (0.55,0.8,0.4); view X basis perpendicular in XY.
 right=(.824,-.566,0);up=(-.212,-.309,.927);front=(.524,.763,.375)
 for panel in [0,1]:
  triangles=[];cx=470+850*panel;cy=585;scale=1.62
  depth_buffer=array('f',[-1e20])*(1800*1000)
  for body in scene['bodies']:
   q=labels[body['id']];n=q['name']
   if panel and ('lid' in n or 'cover' in n or ('L ' in n and ('wheel rim' in n or 'TPU tire' in n))):continue
   mesh=body['mesh'];v=mesh['positions'];inds=mesh['indices'];normals=mesh['normals']
   color=COL[q['kind']]
   for k in range(0,len(inds),3):
    ids=inds[k:k+3];points=[];depth=0;nn=[0,0,0]
    for idx in ids:
     p=(v[3*idx],v[3*idx+1],v[3*idx+2]-R)
     points.append((cx+scale*sum(p[j]*right[j] for j in range(3)),cy-scale*sum(p[j]*up[j] for j in range(3)),sum(p[j]*front[j] for j in range(3))))
     depth+=sum(p[j]*front[j] for j in range(3))/3
     for j in range(3):nn[j]+=normals[3*idx+j]/3
    brightness=.65+.35*abs(sum(nn[j]*front[j] for j in range(3)))
    triangles.append((depth,points,tuple(int(c*brightness) for c in color)))
  pix=im.load()
  for _,poly,color in triangles:
   for row in range(max(130,math.ceil(min(t[1] for t in poly))),min(840,math.floor(max(t[1] for t in poly)))+1):
    intersections=[];scan=row+.5
    for j in range(3):
     v0,v1=poly[j],poly[(j+1)%3]
     if min(v0[1],v1[1])<=scan<max(v0[1],v1[1]):
      t=(scan-v0[1])/(v1[1]-v0[1]);intersections.append((v0[0]+t*(v1[0]-v0[0]),v0[2]+t*(v1[2]-v0[2])))
    if len(intersections)!=2:continue
    (xl,zl),(xr,zr)=sorted(intersections)
    if xr-xl<1e-9:continue
    dz=(zr-zl)/(xr-xl)
    for col in range(max(0,math.ceil(xl-.5)),min(1799,math.floor(xr-.5))+1):
     zz=zl+(col+.5-xl)*dz;ix=row*1800+col
     if zz>depth_buffer[ix]:depth_buffer[ix]=zz;pix[col,row]=color
  dr.text((55+850*panel,855),'Full exterior envelope' if panel==0 else 'Cutaway: left tire/rim, lids and covers hidden',font=font(25),fill=(32,43,54))
 dr.text((45,915),f'{2*R:g} mm wheels / D{2*BR:g} drum. Thermal + Pi nominal hardware; amber = unselected reserves. Sensor solids incomplete.',font=font(23),fill=(45,55,65))
 im.save(ROOT/'packaging-preview.png')
 bounds=[[min(b['mesh']['positions'][j::3]) for j in range(3)] for b in scene['bodies']]
 upper=[[max(b['mesh']['positions'][j::3]) for j in range(3)] for b in scene['bodies']]
 discrepancies=[]
 for body,low,high in zip(scene['bodies'],bounds,upper):
  q=labels[body['id']]
  if q['type']=='box':
   err=max(abs(low[j]-q['lo'][j]) for j in range(3))
   err=max(err,max(abs(high[j]-q['lo'][j]-q['sz'][j]) for j in range(3)))
   if err>.02:discrepancies.append({'name':q['name'],'max_error_mm':err})
 (ROOT/'native-parameter-check.json').write_text(json.dumps({'scope':'Every rectangular body mesh bounding box versus source, tolerance 0.02 mm. Does not qualify fits or known clutch interference.','box_mismatches':discrepancies},indent=2))
 assert not discrepancies,discrepancies
 (ROOT/'native-bounds.json').write_text(json.dumps({'status':'Tessellated CAD sample bounds; exact circles may extend beyond sampled vertices. No physical validation.','minimum_xyz_mm':[min(b[j] for b in bounds) for j in range(3)],'maximum_xyz_mm':[max(b[j] for b in upper) for j in range(3)],'body_count':len(scene['bodies']),'cad_scene_errors':scene.get('errors',[])},indent=2))

def hardware_layout(check):
 # Dimensioned projections of source envelopes, not cosmetic product illustrations.
 im=Image.new('RGB',(1800,1320),(248,250,252));d=ImageDraw.Draw(im)
 ink=(29,44,59);muted=(89,106,121);plum=(153,80,139);green=(50,137,116);amber=(159,102,33)
 def text(x,y,t,n=23,c=ink,bold=False):
  d.text((x,y),t,font=ImageFont.truetype('C:/Windows/Fonts/'+('arialbd.ttf' if bold else 'arial.ttf'),n),fill=c)
 def line(points,c=muted,w=2):d.line(points,fill=c,width=w)
 text(42,28,'TIGHT BELLY / COMPONENT ENVELOPES',37,bold=True)
 text(42,83,'300 mm overall width  |  246 mm wheels  |  160 mm round drum  |  two accepted 210-3M-09 belts',23)
 text(42,123,'Nominal source dimensions. Unknown optical parts are not represented by guessed solids. Not physically validated.',22,amber)
 text(42,190,'CENTRAL SIDE SECTION',26,bold=True)
 ox,oz,sc=390,515,1.92
 def pt(x,z):return(ox+x*sc,oz-z*sc)
 for rad,color in [(R,(202,211,219)),(BR,(63,115,128)),(BR-P['skin'],(144,179,188))]:
  d.ellipse([pt(-rad,rad),pt(rad,-rad)],outline=color,width=3)
 line([pt(-137,0),pt(137,0)],(207,216,223),1)
 def rect(lo,sz,color):d.rectangle([pt(lo[0],lo[2]+sz[2]),pt(lo[0]+sz[0],lo[2])],fill=color,outline=ink,width=2)
 for key,col in [('battery',(237,208,164)),('pixracer',(228,195,148)),('pi',(174,210,189))]:rect(P[key+'_min_xyz_axle'],P[key+'_size_xyz'],col)
 t=P['camera_layout']['thermal'];rect(t['trial_min_xyz_axle'],t['trial_size_xyz'],(213,171,205))
 text(46,265,'Rear',22);text(637,265,'Front',22)
 text(38,363,'Pi hardware',21,green);line([(183,378),pt(-18,33)],green)
 text(40,449,'Pixracer reserve',21,amber);line([(207,465),pt(-38,3)],amber)
 text(511,294,'Thermal',22,plum,True);line([(550,327),pt(29,66)],plum)
 text(539,357,'14 x 71 x 42',20,plum)
 text(49,685,'Battery reserve',21,amber);line([(215,694),pt(-10,-45)],amber)
 # Intent cross has no assumed size, lens center or thickness.
 vx,vz=pt(61,16);line([(vx-7,vz),(vx+7,vz)],plum);line([(vx,vz-7),(vx,vz+7)],plum)
 text(544,467,'Visible camera',20,plum);text(544,494,'zone only',20,plum)
 for sign in [-1,1]:line([pt(sign*75,-10),pt(sign*75,2)],green,4)
 text(510,564,'Range row',20,green);text(510,591,'depth unknown',20,green)
 text(42,765,'Thermal is 16 mm above the selected servo hull.',21)
 text(42,797,'Closest box corner is 1.68 mm inside inner shell.',21)
 text(42,829,'No raised cover. Mounts / plugs / apertures remain open.',21,amber)
 text(807,190,'KNOWN DEVICE ENVELOPES',26,bold=True)
 d.rectangle((807,235,1738,469),fill='white',outline=(216,225,232),width=2)
 d.rectangle((842,279,1055,405),fill=(226,196,219),outline=plum,width=3)
 text(887,245,'71 mm',20,plum);text(850,415,'42 mm high / 14 mm deep',19,plum)
 text(1101,255,'TOPDON TC002C Duo / 1',25,plum,True)
 text(1101,300,'Overall 71 x 42 x 14 mm',24)
 text(1101,341,'Built-in USB-C plug is INCLUDED.',21)
 text(1101,379,'No invented lens position or case contours.',21,muted)
 text(1101,416,'Mated extension plug and cable still unmeasured.',20,amber)
 d.rectangle((807,486,1738,682),fill='white',outline=(216,225,232),width=2)
 d.rectangle((851,535,1046,625),fill=(186,218,202),outline=green,width=3)
 text(882,501,'65 x 30 mm',20,green)
 text(1101,507,'Pi Zero Wi-Fi / version pending',25,green,True)
 text(1101,552,'65 x 30 x 5 mm nominal bare board',23)
 text(1101,592,'Published bare-board size; accessories pending.',21,muted)
 text(1101,631,'Added header, plugs and access space are separate.',20,amber)
 d.rectangle((807,699,1738,879),fill='white',outline=(216,225,232),width=2)
 # Exact XY footprint, enlarged 6x and explicitly not a thickness model.
 d.rectangle((893,752,1013,824),outline=green,width=3)
 text(867,712,'20 x 12 mm',21,green);text(853,839,'2D outline only',19,green)
 text(1101,719,'ACEIRMC TOF400C / 4 front + 4 rear provision',22,green,True)
 text(1101,759,'Exact listing confirms front footprint.',22)
 text(1101,799,'Hood / header / solder depth is missing.',21,amber)
 text(1101,837,'Visible Pi camera not owned; model to select.',21,amber)
 line([(42,914),(1738,914)],(194,206,216))
 text(42,943,'PACKAGING ORDER',26,bold=True)
 text(42,990,'End bays',23,bold=True);text(220,990,'Two servos + horns; two belts / four pulleys; two limiters;',22)
 text(220,1024,'independent shafts, wheel hubs, bearings and removable caps.',22)
 text(42,1071,'Low center',23,bold=True);text(220,1071,'Secured battery, actual plug space and accessible strap release.',22)
 text(42,1118,'Above / rear',23,bold=True);text(220,1118,'Pixracer; thin removable Pi tray; thermal above servo bays.',22)
 text(42,1165,'Front / rear',23,bold=True);text(220,1165,'Visible camera zone; curved range rows; removable sensor panels.',22)
 text(1030,946,'STILL NEEDED TO CLOSE THE FIT',24,amber,True)
 for j,msg in enumerate(['Exact visible-camera identity / drawing','ToF depth over optical hood and solder','Battery / Pixracer case and plug measurements','Mated plugs, cable bends and removal sweeps','Clutch plate, input retention, horn bridge']):
  text(1030,991+39*j,'- '+msg,21)
 text(42,1263,'Sourced servo / hub / collar envelopes. Clutch candidate has axial room; complete mechanism remains unqualified.',21,amber)
 im.save(ROOT/'hardware-layout.png')

def refresh_native(cad):
 # Generated parts are independent; reuse only exact source-map matches.
 # Changes/removals delete the whole originating feature chain before native replay.
 from collections import defaultdict,deque
 previous=json.loads((ROOT/'source-map.json').read_text())
 by_name=defaultdict(deque)
 for q in previous:by_name[q['name']].append(q)
 def definition(q):return json.dumps({k:v for k,v in q.items() if k!='body_id'},sort_keys=True)
 keep=set();add=[]
 for q in parts:
  candidates=by_name[q['name']]
  old=candidates.popleft() if candidates else None
  if old and definition(q)==definition(old):q['body_id']=old['body_id'];keep.add(old['body_id'])
  else:add.append(q)
 removed={q['body_id'] for q in previous}-keep
 with zipfile.ZipFile(ROOT/'Roller-300.nbcad') as z:model=json.loads(z.read('model.json'))
 feature_ids=set();sketch_names=set()
 for e in model['extrudes']:
  if removed.intersection(e.get('new_body_ids',[])+e.get('target_body_ids',[])):
   feature_ids.add(e['feature_id']);sketch_names.add(e['sketch_name'])
 for e in model['body_features']:
  if removed.intersection(e.get('body_ids',[])+e.get('result_body_ids',[])):feature_ids.add(e['feature_id'])
 for e in model['sketches']:
  if e['name'] in sketch_names:feature_ids.add(e['feature_id'])
 for key in ['sketches','extrudes','body_features']:model[key]=[q for q in model[key] if q['feature_id'] not in feature_ids]
 model['document']['history']['features']=[q for q in model['document']['history']['features'] if q['id'] not in feature_ids]
 model['document']['history']['rollback_index']=len(model['document']['history']['features'])
 model['body_appearances']=[q for q in model['body_appearances'] if q['body_id'] in keep]
 cs=model['assembly']['component_structure']
 cs['definitions']=[q for q in cs['definitions'] if set(q['body_ids']).issubset(keep)]
 definitions={q['id'] for q in cs['definitions']}
 cs['occurrences']=[q for q in cs['occurrences'] if q['component_id'] in definitions]
 model['visibility']['hidden_body_ids']=[v for v in model['visibility']['hidden_body_ids'] if v in keep]
 cad.call('cad_load_project_model',{'model_json':json.dumps(model)})
 scene=cad.call('solid_scene');cad.ids=[q['id'] for q in scene['bodies']]
 assert set(cad.ids)==keep,(set(cad.ids)-keep,keep-set(cad.ids))
 print(f'Reused {len(keep)} unchanged bodies; rebuilding {len(add)} changed bodies.',flush=True)
 for q in add:cad.part(q);print('Updated '+q['name'],flush=True)

def drive_sections():
 # Dimensioned X-constant sections from the same assembly definitions.
 im=Image.new('RGB',(1800,1180),(248,250,252));d=ImageDraw.Draw(im)
 ink=(29,44,59);amber=(169,103,25);blue=COL['printed'];gray=COL['purchased']
 def txt(x,y,s,n=22,c=ink,bold=False):d.text((x,y),s,font=ImageFont.truetype('C:/Windows/Fonts/'+('arialbd.ttf' if bold else 'arial.ttf'),n),fill=c)
 txt(50,25,'DRIVE FIRST / LEFT-SIDE AXIAL SECTIONS',35,bold=True)
 txt(50,77,'Same 300 mm width. Y increases toward left wheel; Z is relative to axle. Right side mirrors this.',23)
 txt(50,112,'Source-derived sections, not a validated assembly. Amber parts/interfaces still require detailing.',22,amber)
 x=lambda y:80+7.8*y
 for base,ax,name in [(365,0,'OUTPUT / WHEEL AXIS  X = 0'),(805,A,'INPUT / SERVO AXIS  X = 49.672')]:
  txt(50,base-172,name,27,bold=True)
  d.line((x(0),base,x(152),base),fill=(184,195,205),width=2)
  for y in [0,50,100,150]:
   d.line((x(y),base+88,x(y),base+96),fill=ink,width=2);txt(x(y)-10,base+101,str(y),18)
  d.line((x(105),base-93,x(105),base+85),fill=(140,156,167),width=2)
  def rect(a,b,z0,z1,col):d.rectangle((x(a),base-3*z1,x(b),base-3*z0),fill=col,outline=ink,width=2)
  if ax==0:
   for yc in P['output_bearing_y']:rect(yc-4.5,yc+4.5,-27,-11,blue)
   rect(*P['wheel_shaft_y'],-4,4,gray)
   for a,b in [P['wheel_collars']['inboard_y'],P['wheel_collars']['outboard_y']]:rect(a,b,-10.5,10.5,gray)
   rect(P['clutch_y0'],P['clutch_y0']+P['clutch_length'],-12.5,12.5,COL['unresolved'])
   rect(82,84,-20,20,(223,196,151))
   for yc in P['output_bearing_y']:
    rect(yc-3.5,yc+3.5,-11,11,(159,178,195));rect(yc-3.5,yc+3.5,-4,4,gray)
   rect(*P['wheel_hub']['overall_y'],-15.3,15.3,gray)
   txt(x(38)-15,base-105,'Collar',19);txt(x(50)-6,base-70,'608',19)
   txt(x(63),base-112,'Clutch: 26 mm',21,amber)
   txt(x(90),base-70,'608',19);txt(x(113),base-110,'Wheel hub',21)
   txt(70,base+155,'38.5..47.5 collar  |  51 / 99 bearing centers  |  63..89 clutch  |  113..135.5 hub',21)
   txt(70,base+191,'48 mm bearing span; 31 mm wheel-center overhang. Prepared 110 mm smooth shaft remains a purchase hold.',21,amber)
  else:
   sv=P['servo_reserve_xyz'];rect(P['servo_min_abs_y'],P['servo_min_abs_y']+sv[1],P['servo_z_from_axle'],10,gray)
   rect(*P['input_shaft_y'],-4,4,gray)
   rect(54.1,61,-12,12,COL['unresolved']);rect(61,69,-10,10,COL['unresolved'])
   rect(bt['pulley_face_y0_mm'],bt['pulley_face_y0_mm']+bt['pulley_axial_envelope_mm'],-BPR[0],BPR[0],COL['unresolved'])
   for yc in P['input_bearing_y']:
    rect(yc-4.5,yc+4.5,-27,-11,blue);rect(yc-3.5,yc+3.5,-11,11,(159,178,195));rect(yc-3.5,yc+3.5,-4,4,gray)
   txt(x(10),base-80,'Selected servo / full fixed hardware hull',22)
   txt(x(53),base-115,'Horn + bridge',19,amber);txt(x(70),base-70,'608',19)
   txt(x(82),base-110,'24T pitch only',19,amber);txt(x(96),base-70,'608',19)
   txt(70,base+155,'Full hull is only 20.15 mm tall; original 45 mm allowance removed. Flexible lead and horn are separate.',21)
   txt(70,base+191,'Input shaft retention and floating bridge remain OPEN. Do not add an unsupported pulley to the servo.',21,amber)
 txt(1360,220,'SUPPORT',24,bold=True)
 for j,s in enumerate(['Wheel loads go through','two chassis bearings.','Servo carries torque','through a floating bridge.']):txt(1360,263+30*j,s,21)
 txt(1360,430,'CLUTCH INTERFACE',24,bold=True)
 for j,s in enumerate(['Metal plate between pads.','Pulley bolts to that plate.','Bore / bush / attachment','are not finalized.']):txt(1360,473+30*j,s,21,amber)
 txt(1360,695,'PRINT NOW',24,bold=True)
 for j,s in enumerate(['Servo fit gauge.','Bearing fit coupon.','','Powered drive and','main body still held.']):txt(1360,738+30*j,s,21)
 txt(50,1116,'Clutch nominal axial room is demonstrated; strength, retention, belt tooth form, full service access and physical fit are not.',21,amber)
 im.save(ROOT/'drive-section.png')

def fit_coupons():
 # Native millimetre solids, broad face on XY, through holes vertical for first fit tests.
 # Neither gauge is a vehicle load-bearing bracket.
 c=CAD();names={};cfg=P['fit_coupons'];out=ROOT/'first-prints';out.mkdir(exist_ok=True)
 try:
  bx,by,bz=cfg['bearing_plate_xyz_mm'];gx,gy,gz=cfg['servo_plate_xyz_mm']
  sk=c.sketch('xy');c.rectangle(0,0,bx,by);bearing=c.extrude(sk,bz,flip=False)
  for x,dia in zip([14,40,66],cfg['bearing_diameters_mm']):
   sk=c.sketch('xy');c.circle(x,by/2,dia/2);c.extrude(sk,0,bearing,True,False)
  names[bearing]='bearing-fit-22_05-22_15-22_25'
  x0=bx+10;cx=x0+gx/2;cy=gy/2
  sk=c.sketch('xy');c.rectangle(x0,0,gx,gy);servo=c.extrude(sk,gz,flip=False)
  wx,wy=cfg['servo_window_mm'];sk=c.sketch('xy');c.rectangle(cx-wx/2,cy-wy/2,wx,wy);c.extrude(sk,0,servo,True,False)
  hx,hy=cfg['servo_mount_pattern_mm']
  for x in [cx-hx/2,cx+hx/2]:
   for y in [cy-hy/2,cy+hy/2]:
    sk=c.sketch('xy');c.circle(x,y,cfg['servo_hole_diameter_mm']/2);c.extrude(sk,0,servo,True,False)
  names[servo]='servo-fit-gobilda25-2'
  scene=c.call('solid_scene');pre=c.call('solid_export_preflight');checks=[]
  for b in scene['bodies']:
   v=b['mesh']['positions'];lo=[min(v[j::3]) for j in range(3)];hi=[max(v[j::3]) for j in range(3)]
   assert abs(lo[2])<.001 and abs(hi[2]-(bz if b['id']==bearing else gz))<.001
   stl=c.call('solid_export_stl',{'body_ids':[b['id']],'linear_deflection':.03,'angular_deflection':.15})
   data=next(base64.b64decode(v) for k,v in stl.items() if 'base64' in k and isinstance(v,str))
   (out/(names[b['id']]+'.stl')).write_bytes(data)
   checks.append({'name':names[b['id']],'bounds':[lo,hi],'triangles':len(b['mesh']['indices'])//3})
  d=c.call('cad_project_model');model=json.loads(d['value']) if isinstance(d.get('value'),str) else d.get('value',d)
  manifest={'format':'nbcad-project','container_version':1,'model':'model.json','model_schema_version':model['schema_version'],'application':'noBS CAD','application_version':'0.1.0','saved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  with zipfile.ZipFile(out/'fit-gauges.nbcad','w',zipfile.ZIP_DEFLATED) as z:
   z.writestr('manifest.json',json.dumps(manifest));z.writestr('model.json',json.dumps(model))
  (out/'checks.json').write_text(json.dumps({'preflight':pre,'bounds':checks,'physical_tests':'NOT PERFORMED','purpose':'NON-POWERED FIT GAUGES ONLY'},indent=2))
  print('Exported two native CAD fit gauges and millimetre STL files',flush=True)
 finally:c.proc.terminate()

if __name__=='__main__':
 if '--coupons' in sys.argv:fit_coupons();sys.exit(0)
 c=calculations();hardware_layout(c);drive_sections()
 if '--draw-only' not in sys.argv:
  cad=CAD()
  try:
   if '--refresh' in sys.argv:refresh_native(cad)
   else:
    empty=cad.call('cad_document');assert not empty['features'],'Isolated process unexpectedly has work; do not clear it'
    cad.call('cad_set_document_name',{'name':'Roller-300 - MECHANICAL ENVELOPES - NOT VALIDATED'})
    for j,q in enumerate(parts):
     cad.part(q)
     if j%10==0:print(f'Created {j+1}/{len(parts)} packaging bodies',flush=True)
   cad.save();print('Saved native CAD, STEP, current component sheet and reload checks',flush=True)
  finally:
   if cad.proc.poll() is None:cad.proc.terminate()
