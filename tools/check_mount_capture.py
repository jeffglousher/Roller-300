"""Check actual native exports: nut loading/rotation, head seats and envelope."""
from pathlib import Path
import math,json,sys
import trimesh
from OCP.STEPControl import STEPControl_Reader
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common,BRepAlgoAPI_Cut
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder,BRepPrimAPI_MakePrism
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir,gp_Vec,gp_Trsf
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'design/mount-capture-2026-10-04'
rows=[];shapes={}
def volume(s):
    p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p);return abs(p.Mass())
def overlap(a,b):return volume(BRepAlgoAPI_Common(a,b).Shape())
def record(name,value,passed,**detail):
    rows.append(dict(name=name,value=value,passed=bool(passed),**detail))
def nut(x,y,z,h=2.4,angle=0):
    p=BRepBuilderAPI_MakePolygon()
    for i in range(6):
        a=i*math.pi/3+angle
        p.Add(gp_Pnt(x+5.5/math.sqrt(3)*math.cos(a),y,z+5.5/math.sqrt(3)*math.sin(a)))
    p.Close();return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(p.Wire()).Face(),gp_Vec(0,h,0)).Shape()
for b in [32,373,377,378,381,382,437,440]:
    r=STEPControl_Reader();r.ReadFile(str(OUT/f'body-{b}.step'));r.TransferRoots();s=r.OneShape();shapes[b]=s
    m=trimesh.load_mesh(OUT/f'body-{b}.stl')
    record('native solid and print mesh',b,BRepCheck_Analyzer(s).IsValid() and m.is_watertight and len(m.split(only_watertight=False))==1,body_id=b)
envelope=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,-200,123),gp_Dir(0,1,0)),80,400).Shape()
for b in [32,373]:
    v=volume(BRepAlgoAPI_Cut(shapes[b],envelope).Shape());record('mount roots inside barrel OD',v,v<.001,body_id=b)
for sign,carrier in [(1,437),(-1,440)]:
    for cx,y,r,parent in [(0,97,17,32),(0,8,17,32),(49.6723,54,20,carrier),(49.6723,81,20,carrier)]:
        for i in range(4):
            a=math.pi/4+i*math.pi/2;x=cx+r*math.cos(a);z=123+r*math.sin(a)
            ny=y+.2 if sign==1 else -y-2.6
            v=overlap(shapes[parent],nut(x,ny,z));record('M3 hex nut seats',v,v<.001,body_id=parent,station=sign*y,hole=i)
            v=overlap(shapes[parent],nut(x,ny,z,angle=math.pi/6));record('M3 nut cannot rotate thirty degrees',v,v>.001,body_id=parent,station=sign*y,hole=i)
            if y==8:
                vals=[]
                for d in [0,1,2,4,6,8,10]:
                    vals.append(overlap(shapes[parent],nut(x+d*math.cos(a),ny,z+d*math.sin(a))))
            else:
                vals=[overlap(shapes[parent],nut(x,(y-8 if sign==1 else -y-2.6),z,h=10.6))]
            record('M3 nut loading path',max(vals),max(vals)<.001,body_id=parent,station=sign*y,hole=i,insertion='radial' if y==8 else 'back face')
    for cap,end in zip([377,378] if sign==1 else [381,382],[62.5,89.5]):
        for i in range(4):
            a=math.pi/4+i*math.pi/2;x=49.6723+20*math.cos(a);z=123+20*math.sin(a)
            y=end if sign==1 else -end
            head=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,y,z),gp_Dir(0,sign,0)),2.75,2.93).Shape()
            v=overlap(shapes[cap],head);record('M3 socket head fits recess',v,v<.001,body_id=cap,hole=i)
report=dict(passed=all(r['passed'] for r in rows),basis='Native application STEP/STL exports; nominal AF5.5/h2.4 M3 nuts and D5.5/h2.93 screw heads; physical PETG fit remains untested.',checks=rows)
(OUT/'capture-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(passed=report['passed'],checks=len(rows),failures=[r for r in rows if not r['passed']])),flush=True)
assert report['passed']
