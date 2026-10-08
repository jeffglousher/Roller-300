"""Validate native application exports; does not author or render geometry."""
from pathlib import Path
import hashlib
import json
import trimesh
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir, gp_Trsf, gp_Vec
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'design/drivetrain-revision-2026-10-03'
SOURCE = ROOT / '.local/s15-carrier-model-replayed.json'
PRINT = [9,10,13,26,27,30,32,301,307,309,315,367,368,373,
         376,377,378,380,381,382,383,384,388,391,413,416,437,440,442,443]
report = {'source_model_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'basis': 'Native CAD replay and STEP/STL exports; nominal CAD clearances, not physical tolerances or load qualification.',
          'print_scope':'Unpowered one-drive test in the roof-open section, not the complete barrel.',
          'bodies': [], 'checks': []}
shapes = {}

def volume(shape):
    p = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, p)
    return abs(p.Mass())

def moved(shape, dx=0, dy=0, dz=0):
    t = gp_Trsf(); t.SetTranslation(gp_Vec(dx,dy,dz))
    return BRepBuilderAPI_Transform(shape,t,True).Shape()

def common(a,b):
    op = BRepAlgoAPI_Common(a,b); op.Build()
    assert op.IsDone()
    return volume(op.Shape())

def check(name, values, **detail):
    row = dict(name=name, overlap_mm3=values, passed=max(values,default=0)<0.001, **detail)
    report['checks'].append(row)
    print(json.dumps(row),flush=True)

def cylinder(x,y,z,r,length,sign=1):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,y,z),gp_Dir(0,sign,0)),r,length).Shape()

def z_cylinder(x,y,z,r,length):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,y,z),gp_Dir(0,0,1)),r,length).Shape()

def z_nut(x,y,z,af,height):
    import math
    p=BRepBuilderAPI_MakePolygon()
    for i in range(6):
        a=i*math.pi/3
        p.Add(gp_Pnt(x+af/math.sqrt(3)*math.cos(a),y+af/math.sqrt(3)*math.sin(a),z))
    p.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(p.Wire()).Face(),gp_Vec(0,0,height)).Shape()

def horizontal_nut_sweep(x,y,z,af,height,travel):
    import math
    r=af/math.sqrt(3)
    points=[(r,0),(r/2,af/2),(-r/2-travel,af/2),(-r-travel,0),(-r/2-travel,-af/2),(r/2,-af/2)]
    p=BRepBuilderAPI_MakePolygon()
    for a,b in points:p.Add(gp_Pnt(x+a,y+b,z))
    p.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(p.Wire()).Face(),gp_Vec(0,0,height)).Shape()

for bid in PRINT:
    r = STEPControl_Reader()
    assert r.ReadFile(str(OUT/f'body-{bid}.step')).name=='IFSelect_RetDone'
    r.TransferRoots(); s=r.OneShape(); shapes[bid]=s
    e=TopExp_Explorer(s,TopAbs_SOLID); count=0
    while e.More(): count+=1; e.Next()
    mesh=trimesh.load_mesh(OUT/f'body-{bid}.stl')
    row=dict(body_id=bid,valid_brep=bool(BRepCheck_Analyzer(s).IsValid()),solid_count=count,
             watertight_mesh=bool(mesh.is_watertight),mesh_components=len(mesh.split(only_watertight=False)),
             bounds_mm=mesh.bounds.tolist())
    row['passed']=row['valid_brep'] and count==1 and row['watertight_mesh'] and row['mesh_components']==1
    report['bodies'].append(row); print(json.dumps(row),flush=True)

for bid in [11,28,387,412]:
    r=STEPControl_Reader();r.ReadFile(str(OUT/f'body-{bid}.step'));r.TransferRoots();shapes[bid]=r.OneShape()

for cap,parent in [(376,32),(380,32),(383,32),(384,32),(377,437),(378,437),(381,440),(382,440)]:
    check('retainer seats',[common(shapes[cap],shapes[parent])],body_id=cap,parent=parent)

for carrier,side,sign,bridge,caps in [(437,'L',1,367,[377,378]),(440,'R',-1,368,[381,382])]:
    for x,y in [(32.5,12),(60,50),(30.5,79)]:
        nut_sweep=horizontal_nut_sweep(x,sign*y,79.2,7,3.2,10) if x==60 else z_nut(x,sign*y,69.2,7,13.2)
        check('carrier captive nut insertion',[common(shapes[32],nut_sweep)],side=side,anchor=[x,sign*y],
              insertion='10 mm horizontal from inner cavity' if x==60 else '10 mm lift from below; carrier removed')
    for dx in [-2,-1,0,.5,1]:
        moving = moved(shapes[carrier],dx)
        check('carrier translation',[common(shapes[32],moving)],side=side,dx_mm=dx)
        for name,x,r,y,length in [('servo coupler',49.6723,15.24,45.8,7),
                                 ('coupler race land',49.6723,5.5,52.8,1),
                                 ('24T pulley',49.6723,15.24,62.75,17),
                                 ('input collar screw envelope',49.6723,13.65,89.7,6)]:
            envelope=cylinder(x+dx,sign*y,123,r,length,sign)
            stationary=[shapes[32],moving,moved(shapes[bridge],dx)]+[moved(shapes[c],dx) for c in caps]
            check('input rotation',[common(s,envelope) for s in stationary],part=name,side=side,dx_mm=dx)
        # A rotating reaction plate and its spring hardware need full-circle clearance.
        for name,r,y,length in [('reaction plate and captive bosses',28.75,24.3,8),
                                 ('pressure plate',28.75,35.3,3),
                                 ('spring sweep',28,38.3,18),
                                 ('adjuster washer and head sweep',28.5,56.3,4)]:
            envelope=cylinder(0,sign*y,123,r,length,sign)
            stationary=[shapes[32],moving,moved(shapes[bridge],dx)]+[moved(shapes[c],dx) for c in caps]
            check('clutch rotation',[common(s,envelope) for s in stationary],part=name,side=side,dx_mm=dx)
    # Straight vertical servo insertion, with bridges/caps removed.
    for dx in [-2,0,1]:
        # Ear dimensions are the supplied case drawing, not an inferred horn.
        boxes=[(5 if sign==1 else -45.5,40.5,93,160.5),
               (29.7 if sign==1 else -32.4,2.7,85.25,127.75),
               (29.7 if sign==1 else -32.4,2.7,133.5,127.75)]
        vals=[]
        for y,depth,z,height in boxes:
            env=BRepPrimAPI_MakeBox(gp_Pnt(39.6723+dx,y,z),20,depth,height).Shape()
            vals.extend([common(shapes[32],env),common(moved(shapes[carrier],dx),env)])
        check('servo vertical insertion',vals,side=side,dx_mm=dx,scope='case/ear envelopes; excludes cable and horn')
    # Mounting bolts remain fixed in the bed while the slotted carrier moves.
    for dx in [-2,0,1]:
        servo=BRepPrimAPI_MakeBox(gp_Pnt(39.6723+dx,5 if sign==1 else -45.5,93),20,40.5,40.5).Shape()
        moving=moved(shapes[carrier],dx)
        for x,y in [(32.5,12),(60,50),(30.5,79)]:
            y*=sign
            shank=z_cylinder(x,y,77.8,2,14)
            washer=z_cylinder(x,y,91,4.5,.8)
            head=z_cylinder(x,y,91.8,3.8,2.2)
            nut=z_nut(x,y,79.2,7,3.2)
            check('carrier mounting screw fit',[common(shapes[32],shank),common(moving,shank),
                                               common(shapes[32],nut),common(moving,washer),
                                               common(servo,head)],side=side,dx_mm=dx,anchor=[x,y],
                  hardware='M4x14 ISO7380-1; DIN125 washer 9x4.3x0.8; nut AF7 height3.2')
            # 3 mm diameter straight hex driver shaft; handle stays above model.
            driver=z_cylinder(x,y,94,1.5,70)
            fixture=shapes[373]
            if sign==-1:
                t=gp_Trsf();t.SetMirror(gp_Ax2(gp_Pnt(0,0,0),gp_Dir(0,1,0)))
                fixture=BRepBuilderAPI_Transform(fixture,t,True).Shape()
            check('roof-open fixture mounting screw driver access',[common(fixture,driver),common(moving,driver),
                                                         common(moved(shapes[bridge],dx),driver),common(servo,driver),
                                                         common(moved(shapes[10 if sign==1 else 27],dx),driver),
                                                         common(shapes[9 if sign==1 else 26],driver),
                                                         common(shapes[11 if sign==1 else 28],driver)],
                  side=side,dx_mm=dx,anchor=[x,y],full_frame_overlap_mm3=common(shapes[32],driver),
                  limitation='Existing upper guard blocks the rear straight driver in the whole frame; service access remains held for the barrel revision.')

# The actual adjacent moving/fixed clutch parts, excluding intentional face contact.
for a,b in [(9,307),(9,388),(9,391),(26,315),(26,413),(26,416),(388,387),(413,412),
            (9,442),(26,443),(391,442),(416,443),(388,32),(391,32),(413,32),(416,32)]:
    check('clutch assembly interference',[common(shapes[a],shapes[b])],bodies=[a,b])

# Radial pressure-pad insertion with guide screws/springs removed. The solid
# pulley exports include both flanges, so a trapped closed ring cannot pass.
for bid,pulley,direction in [(391,9,-1),(442,9,1),(416,26,-1),(443,26,1)]:
    check('pressure pad radial insertion',[common(shapes[pulley],moved(shapes[bid],dz=direction*distance))
                                           for distance in [0,.5,1,2,5,10,20,40]],body_id=bid)
lift_overlaps=[]
# The swept cross section of a round part is a capsule, not its bounding
# rectangle. Split by axial section so narrow sleeves do not inherit the
# front plate's diameter. Each envelope also covers a full rotation.
for radius,y,length in [(28.75,20.3,18),(28.5,38.3,22),(16,60.3,4.95),
                        (26,65.25,14.5),(20,79.75,7)]:
    envelopes=[cylinder(0,y,123,radius,length),cylinder(0,y,243,radius,length),
               BRepPrimAPI_MakeBox(gp_Pnt(-radius,y,123),2*radius,length,120).Shape()]
    lift_overlaps.extend(common(shapes[373],s) for s in envelopes)
check('bench-assembled clutch lowers into roof-open fixture',lift_overlaps,
      scope='Conservative round-part sweep by axial section; input carrier removed, wheel shaft inserted afterwards; excludes unknown servo horn')

report['passed']=all(x['passed'] for x in report['bodies']+report['checks'])
(OUT/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'failed_bodies':[x for x in report['bodies'] if not x['passed']],
                  'failed_checks':[x for x in report['checks'] if not x['passed']]}),flush=True)
assert report['passed'], 'Native drivetrain validation failed; see checks.json'
