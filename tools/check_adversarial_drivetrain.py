"""Independent adversarial probes of native CAD exports, never geometry authoring/rendering."""
from pathlib import Path
import json,math,hashlib
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism,BRepPrimAPI_MakeCylinder
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt,gp_Vec,gp_Trsf,gp_Dir,gp_Ax1,gp_Ax2
R=Path(__file__).resolve().parents[1];OUT=R/'design/adversarial-review-2026-10-06'
shapes={};rows=[]
def load(b):
 if b not in shapes:
  r=STEPControl_Reader();assert r.ReadFile(str(OUT/f'body-{b}.step')).name=='IFSelect_RetDone';r.TransferRoots();shapes[b]=r.OneShape()
 return shapes[b]
def vol(s):
 p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p);return abs(p.Mass())
def overlap(a,b):return vol(BRepAlgoAPI_Common(a,b).Shape())
def move(s,x=0,y=0,z=0):
 t=gp_Trsf();t.SetTranslation(gp_Vec(x,y,z));return BRepBuilderAPI_Transform(s,t,True).Shape()
def turn(s,angle):
 t=gp_Trsf();t.SetRotation(gp_Ax1(gp_Pnt(49.6723,0,123),gp_Dir(0,1,0)),angle);return BRepBuilderAPI_Transform(s,t,True).Shape()
def cyl(x,y,z,r,h,axis=(0,1,0)):
 return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,y,z),gp_Dir(*axis)),r,h).Shape()
def nut(x,y,z,axis='y',af=5.5,h=2.4,angle=0):
 p=BRepBuilderAPI_MakePolygon()
 for i in range(6):
  a=angle+i*math.pi/3;u=af/math.sqrt(3)*math.cos(a);v=af/math.sqrt(3)*math.sin(a)
  p.Add(gp_Pnt(x+u,y,z+v) if axis=='y' else gp_Pnt(x+u,y+v,z))
 p.Close();return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(p.Wire()).Face(),gp_Vec(0,h,0) if axis=='y' else gp_Vec(0,0,h)).Shape()
def rec(name,value,passed,**kw):
 rows.append(dict(name=name,value=value,passed=bool(passed),**kw));print(json.dumps(rows[-1]),flush=True)
def clears(name,values,**kw):rec(name,values,max(values,default=0)<.001,**kw)
for sign,side,carrier,bridge,servo,adapter,pulley,shaft,bearing,spacer,shim,washer,screw in [(1,'L',437,367,12,301,10,447,5,449,451,453,455),(-1,'R',440,368,29,309,27,448,22,450,452,454,456)]:
 for b in [carrier,bridge,servo,adapter,pulley,shaft,bearing,spacer,shim,washer,screw,32,373]:load(b)
 for x in [44.6723,54.6723]:
  for z,body,y in [(88.75,carrier,22.6),(137.75,bridge,18.4)]:
   by=y if sign==1 else -y-2.4
   n=nut(x,by,z);clears('servo ear nut seating',[overlap(load(body),n)],side=side,body=body,x=x,z=z)
   rotated=nut(x,by,z,angle=math.pi/6);v=overlap(load(body),rotated);rec('servo ear nut cannot rotate',v,v>.001,side=side,body=body,x=x,z=z)
   if z==88.75:sweep=nut(x,by if sign==1 else by-12,z,h=14.4)
   else:sweep=nut(x,by-12 if sign==1 else by,z,h=14.4)
   clears('servo ear nut loading before servo',[overlap(load(body),sweep)],side=side,body=body,x=x,z=z)
   bolt=cyl(x,sign*17.9,z,1.5,10,(0,sign,0));head=cyl(x,sign*27.9,z,2.75,2.93,(0,sign,0))
   clears('servo M3x10 bolt reaches nut',[overlap(load(body),bolt),overlap(load(servo),bolt),overlap(load(servo),head)],side=side,body=body,x=x,z=z)
   driver=cyl(x,sign*30.83,z,2,35,(0,sign,0))
   clears('servo ear driver access before belt carrier installation',[overlap(load(body),driver),overlap(load(servo),driver)],side=side,body=body,x=x,z=z)
 for x in [34.1723,65.1723]:
  y=sign*21.7;n=nut(x,y,128.9,'z',angle=math.pi/6)
  clears('bridge nut seating',[overlap(load(carrier),n)],side=side,x=x)
  v=overlap(load(carrier),nut(x,y,128.9,'z',angle=0));rec('bridge nut rotation blocked',v,v>.001,side=side,x=x)
  vals=[overlap(load(carrier),move(n,y=-sign*d)) for d in [0,1,2,3,5,8,12]]
  clears('bridge nut side loading',vals,side=side,x=x)
  shank=cyl(x,y,127.25,1.5,16,(0,0,1));head=cyl(x,y,143.25,3,2.5,(0,0,1))
  clears('M3x16 bridge bolt passage',[overlap(load(carrier),shank),overlap(load(bridge),shank),overlap(load(bridge),head)],side=side,x=x,head_envelope='D6 x2.5; pan head receiving fit')
  clears('bridge screw driver access',[overlap(load(servo),cyl(x,y,145.75,2,40,(0,0,1))),overlap(load(bridge),cyl(x,y,145.75,2,40,(0,0,1)))],side=side,x=x)
 # Actual supplied REX CAD includes a shaft and its factory Eclip as separate solids.
 e=TopExp_Explorer(load(shaft),TopAbs_SOLID);sol=[]
 while e.More():sol.append(e.Current());e.Next()
 assert len(sol)==2;clip=min(sol,key=vol);metalshaft=max(sol,key=vol)
 clears('actual REX shaft and clip clear keyed printed parts',[overlap(load(adapter),load(shaft)),overlap(load(pulley),load(shaft))],side=side)
 for dy in [-.2,0,.2]:
  p=move(load(pulley),y=sign*dy)
  clears('input pulley axial travel clears stationary housing and caps',[overlap(p,load(b)) for b in [carrier,377 if sign==1 else 381,378 if sign==1 else 382,bearing]],side=side,dy=dy,total_nominal_play=.4)
 for dy in [-.3,.3]:
  v=overlap(move(load(pulley),y=sign*dy),load(bearing));rec('integral pulley lands stop further axial travel',v,v>1,side=side,dy=dy,stop='Bearing inner race, R5.5 land; no stationary plastic contact')
 for b in [adapter,pulley]:
  v=overlap(load(b),turn(metalshaft,math.pi/6));rec('positive hex drive blocks thirty degree shaft turn',v,v>1,side=side,body=b)
 clears('Eclip radial access window',[overlap(load(adapter),move(clip,x=d)) for d in [0,1,2,4,8,12,20]],side=side,limitation='Checks printed access. Spring clip elastically expands over the shaft; rotate clip mouth toward shaft before installation.')
 # The clip rear pocket wall and rear metal stack give independent shaft stops.
 clears('input shaft clip has nominal 0.2mm axial travel',[overlap(load(adapter),move(clip,y=sign*d)) for d in [0,.1,.2]],side=side)
 v=overlap(load(adapter),move(clip,y=sign*.3));rec('input shaft forward travel stops at clip pocket',v,v>1,side=side,dy=.3)
 clears('input shaft rear stop can move outward',[overlap(load(bearing),move(load(spacer),y=sign*d)) for d in [0,.1,.2]],side=side)
 v=overlap(load(bearing),move(load(spacer),y=-sign*.1));rec('input shaft inward travel stops on rear inner race',v,v>1,side=side,dy=-.1)
 clears('rear spacer and shim clear bearing cap',[overlap(load(b),load(378 if sign==1 else 382)) for b in [spacer,shim,washer,screw]],side=side)
 clears('rear stop clears shaft material',[overlap(load(b),metalshaft) for b in [spacer,shim,washer]],side=side)
 # The purchased screw/shaft helices need thread contact; examine safe depth separately.
 d=BRepExtrema_DistShapeShape(load(spacer),load(bearing));d.Perform();rec('rear spacer seats on bearing',d.Value(),d.Value()<.001,side=side)
 for a,b in [(spacer,shim),(shim,washer),(washer,screw)]:
  d=BRepExtrema_DistShapeShape(load(a),load(b));d.Perform();rec('rear retention stack contacts',d.Value(),d.Value()<.001,side=side,bodies=[a,b])
 # Read axial dimensions from the actual vendor model, including its thread overshoot.
 clears('rear end screw driver corridor',[overlap(load(b),cyl(49.6723,sign*98.3,123,1.5,40,(0,sign,0))) for b in [carrier,adapter,pulley,servo]],side=side)
 for dx in [-2,0,1]:
  clears('actual servo and bridge clear frame at carrier travel',[overlap(move(load(servo),x=dx),load(32)),overlap(move(load(servo),x=dx),move(load(carrier),x=dx)),overlap(move(load(servo),x=dx),move(load(bridge),x=dx))],side=side,dx=dx)

model=json.loads((R/'.local/s20-adversarial-model-replayed.json').read_text())
for b in [446,448,456]:
 f=next(f for f in model['body_features'] if b in f.get('new_body_ids',[])+f.get('result_body_ids',[]) and (f.get('copy') or f['type']=='mirror'))
 rec('stock threaded hardware retains handedness',f['type'],f['type']=='move_copy' and f['copy'] and abs(sum(v*v for v in f['rotation'])-1)<1e-9,body=b)
report={'passed':all(r['passed'] for r in rows),'source_model_sha256':hashlib.sha256((R/'.local/s20-adversarial-model-replayed.json').read_bytes()).hexdigest(),'basis':'Exact OCP probes of native CAD application STEP exports; nominal dimensions, unpowered test only. Nut and fastener tolerance must be checked on receipt.','checks':rows}
(OUT/'adversarial-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':len(rows),'failed':[r for r in rows if not r['passed']]}),flush=True)
assert report['passed'],'Adversarial native geometry checks failed'
