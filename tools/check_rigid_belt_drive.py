"""Validate native application exports; does not author or render geometry."""
from pathlib import Path
import hashlib
import json
import sys
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
OUT = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT / 'design/rigid-belt-drive-2026-10-05'
SOURCE = Path(sys.argv[2]).resolve() if len(sys.argv)>2 else ROOT / '.local/s18-rigid-belt-drive-model-replayed.json'
REX = len(sys.argv)>3 and sys.argv[3]=='rex'
HORN = len(sys.argv)>3 and sys.argv[3] in ['horn','rex']
PRINT = [9,10,13,26,27,30,32,301,309,367,368,373,376,377,378,380,381,382,383,384,437,440]
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
for bid in ([1,2,3,4,5,12,18,19,20,21,22,29,224,227,357,358,445,446]+list(range(447,461)) if REX else [1,2,3,4,5,6,12,18,19,20,21,22,23,29,224,227,357,358,369,370,371,372,385,386]):
    r=STEPControl_Reader();r.ReadFile(str(OUT/f'body-{bid}.step'));r.TransferRoots();shapes[bid]=r.OneShape()
if REX:shapes[6]=shapes[447];shapes[23]=shapes[448]

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
        rotations=([('metal horn',49.6723,16,38.1,5.5),('horn flange',49.6723,16.6,41.6,5.7),('positive shaft adapter',49.6723,9.5,45.8,7)] if REX else [ ('metal horn',49.6723,16,38.6,5.5),('horn flange',49.6723,16.6,42.1,5.7),('shaft clamp',49.6723,19.5,45.8,8)] if HORN else [('servo coupler',49.6723,15.24,45.8,7)]) + [
                                 ('coupler race land',49.6723,5.5,52.8,1),
                                 ('24T pulley',49.6723,15.24,62.75,17),
                                 ('input end washer',49.6723,5.45,94.5,1.5) if REX else ('input collar screw envelope',49.6723,13.65,89.7,6)]
        if REX:rotations += [('input pulley front race land',49.6723,5.5,61.2,1.8),('input pulley rear race land',49.6723,5.5,79.3,1.5)]
        for name,x,r,y,length in rotations:
            envelope=cylinder(x+dx,sign*y,123,r,length,sign)
            stationary=[shapes[32],moving,moved(shapes[bridge],dx)]+[moved(shapes[c],dx) for c in caps]
            check('input rotation',[common(s,envelope) for s in stationary],part=name,side=side,dx_mm=dx)
    # Straight vertical servo insertion, with bridges/caps removed.
    for dx in [-2,0,1]:
        # Ear dimensions are the supplied case drawing, not an inferred horn.
        boxes=([(.5 if sign==1 else -38,37.5,93,160.5),(25.2 if sign==1 else -27.9,2.7,85.25,127.75),(25.2 if sign==1 else -27.9,2.7,133.5,127.75)] if REX else [(1 if sign==1 else -38.5,37.5,93,160.5),
                (25.7 if sign==1 else -28.4,2.7,85.25,127.75),
                (25.7 if sign==1 else -28.4,2.7,133.5,127.75)] if HORN else [
                (5 if sign==1 else -45.5,40.5,93,160.5),
                (29.7 if sign==1 else -32.4,2.7,85.25,127.75),
                (29.7 if sign==1 else -32.4,2.7,133.5,127.75)])
        vals=[]
        for y,depth,z,height in boxes:
            env=BRepPrimAPI_MakeBox(gp_Pnt(39.6723+dx,y,z),20,depth,height).Shape()
            vals.extend([common(shapes[32],env),common(moved(shapes[carrier],dx),env)])
        check('servo vertical insertion',vals,side=side,dx_mm=dx,scope='case/ear envelopes; excludes cable and horn')
    # Mounting bolts remain fixed in the bed while the slotted carrier moves.
    for dx in [-2,0,1]:
        servo=BRepPrimAPI_MakeBox(gp_Pnt(39.6723+dx,(.5 if sign==1 else -38) if REX else (1 if sign==1 else -38.5) if HORN else (5 if sign==1 else -45.5),93),20,37.5 if HORN else 40.5,40.5).Shape()
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

# Check the new torque connection against the actual imported purchased hubs.
import math
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
pattern=[(-8,115),(-8,131),(8,115),(8,131)]
for side,sign,pulley,hub,shaft,carrier,bridge,caps in [
    ('L',1,9,387,1,437,367,[377,378]),('R',-1,26,412,18,440,368,[381,382])]:
    check('rigid pulley clears metal hub',[common(shapes[pulley],shapes[hub])],side=side)
    check('rigid pulley clears wheel shaft',[common(shapes[pulley],shapes[shaft])],side=side)
    for i,(x,z) in enumerate(pattern):
        shank=cylinder(x,sign*59.05,z,2,16,sign)
        head=cylinder(x,sign*75.05,z,3.8,2.2,sign)
        check('M4x16 recessed screw fit',[common(shapes[pulley],shank),common(shapes[pulley],head)],
              side=side,hole=i,thread_engagement_mm=6.2,remaining_pulley_floor_mm=9.8)
        # Tap-hole center must coincide with our bolt pattern. Threads are not
        # modeled as helices; this verifies center, axial overlap and metal land.
        pilot=cylinder(x,sign*59.05,z,1.5,6.2,sign)
        check('metal hub tapped hole centers align',[common(shapes[hub],pilot)],side=side,hole=i)
        annulus=BRepAlgoAPI_Cut(cylinder(x,sign*59.05,z,3.1,6.2,sign),
                              cylinder(x,sign*59.05,z,2.3,6.2,sign)).Shape()
        ratio=common(shapes[hub],annulus)/volume(annulus)
        report['checks'].append(dict(name='metal surrounds mounting thread engagement',side=side,hole=i,
                                     material_fraction=ratio,passed=ratio>.98))
        driver=cylinder(x,sign*77.25,z,1.5,50,sign)
        check('pulley mounting screw bench driver access',[common(shapes[pulley],driver)],
              side=side,hole=i,assembly='Bolt pulley to hub on bench before fitting stationary center bearing')
    for dx in [-2,-1,0,.5,1]:
        stationary=[shapes[32],moved(shapes[carrier],dx),moved(shapes[bridge],dx)]+[moved(shapes[c],dx) for c in caps]
        for name,r,y,length in [('metal hub',18,57.25,8),('rigid output pulley',26,65.25,14.5)]:
            env=cylinder(0,sign*y,123,r,length,sign)
            check('rigid output full rotation clearance',[common(s,env) for s in stationary],side=side,dx_mm=dx,part=name)
    # Purchased shaft hub's radial clamp is tightened with the belt and input
    # carrier removed. A full annular access corridor reaches the inner cavity.
    # Actual wrench approach still depends on the received hub screw geometry.
    check('output assembly clears retained axial stops',[
        common(shapes[pulley],shapes[3 if sign==1 else 20]),
        common(shapes[hub],shapes[3 if sign==1 else 20])],side=side)

lift=[]
for radius,y,length in [(18,57.25,8),(26,65.25,14.5)]:
    envelopes=[cylinder(0,y,123,radius,length),cylinder(0,y,243,radius,length),
               BRepPrimAPI_MakeBox(gp_Pnt(-radius,y,123),2*radius,length,120).Shape()]
    lift.extend(common(shapes[373],s) for s in envelopes)
check('bench-assembled rigid hub and pulley lower into roof-open fixture',lift,
      assembly='Input carrier removed; wheel shaft inserted through hub afterwards')

for bid in [9,26]:
    mesh=trimesh.load_mesh(OUT/f'body-{bid}.stl')
    height=float(mesh.bounds[1,1]-mesh.bounds[0,1])
    report['checks'].append(dict(name='obsolete long pulley sleeve removed',body_id=bid,
                                 pulley_axial_length_mm=height,passed=abs(height-14.5)<.001))

if HORN:
    for side,sign,adapter,horn,shaft,bearings,carrier,bridge in [('L',1,301,445,6,5,437,367),('R',-1,309,446,23,22,440,368)]:
        r=STEPControl_Reader();r.ReadFile(str(OUT/f'body-{horn}.step'));r.TransferRoots();shapes[horn]=r.OneShape()
        check('purchased horn clears printed adapter',[common(shapes[horn],shapes[adapter])],side=side)
        check('horn adapter clears shaft and input bearings',[common(shapes[adapter],shapes[shaft]),common(shapes[adapter],shapes[bearings])],side=side)
        case=BRepPrimAPI_MakeBox(gp_Pnt(39.6723,(.5 if sign==1 else -38) if REX else (1 if sign==1 else -38.5),93),20,37.5,40.5).Shape()
        check('metal horn clears supplied drawing case envelope',[common(case,shapes[horn])],side=side)
        head=cylinder(49.6723,sign*(43.6 if REX else 44.1),123,2.85,1.65,sign)
        check('servo center screw head clearance',[common(head,s) for s in [shapes[horn],shapes[adapter],shapes[shaft]]],side=side,maximum_head_height_mm=1.65,shaft_gap_mm=1.25 if REX else .25)
        driver=cylinder(49.6723,sign*(45.25 if REX else 45.75),123,1.5,50,sign)
        check('servo center screw accessible before input shaft',[common(driver,shapes[adapter])],side=side,assembly='Fit center retaining screw through adapter bore before inserting the independent shaft')
        pinch_shank=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(46.8723,sign*50.8,138),gp_Dir(1,0,0)),1.5,10).Shape()
        pinch_head=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(43.9423,sign*50.8,138),gp_Dir(1,0,0)),2.75,2.93).Shape()
        if not REX:check('raised M3 shaft pinch screw fit',[common(pinch_shank,shapes[adapter]),common(pinch_head,shapes[adapter])],side=side)
        for i,(x,z) in enumerate([(49.6723+x,123+z) for x,z in [(-8,-8),(-8,8),(8,-8),(8,8)]]):
            shank=cylinder(x,sign*(39.1 if REX else 39.6),z,2,6,sign);head=cylinder(x,sign*(45.1 if REX else 45.6),z,3.8,2.2,sign)
            check('horn M4x6 recessed screw fit',[common(shank,shapes[adapter]),common(head,shapes[adapter]),common(shank,case)],side=side,hole=i,thread_engagement_mm=2.5)
            if not REX:check('horn screws clear raised shaft pinch screw',[common(s,t) for s in [shank,head] for t in [pinch_shank,pinch_head]],side=side,hole=i)
            pilot=cylinder(x,sign*(39.1 if REX else 39.6),z,1.3,2.5,sign)
            check('manufacturer STEP tapped centers match adapter',[common(pilot,shapes[horn])],side=side,hole=i)
            annulus=BRepAlgoAPI_Cut(cylinder(x,sign*(39.1 if REX else 39.6),z,3.1,2.5,sign),cylinder(x,sign*(39.1 if REX else 39.6),z,2.3,2.5,sign)).Shape()
            ratio=common(annulus,shapes[horn])/volume(annulus)
            report['checks'].append(dict(name='horn metal thread engagement land',side=side,hole=i,material_fraction=ratio,passed=ratio>.98))
            driver=cylinder(x,sign*(47.3 if REX else 47.8),z,1.5,40,sign)
            check('horn mounting screw bench driver access',[common(driver,shapes[adapter])],side=side,hole=i)
        for dx in [-2,0,1]:
            check('complete horn adapter assembly stationary clearance',[common(moved(s,dx),t) for s in [shapes[horn],shapes[adapter]] for t in [shapes[32],moved(shapes[carrier],dx),moved(shapes[bridge],dx)]],side=side,dx_mm=dx)

report['passed']=all(x['passed'] for x in report['bodies']+report['checks'])
(OUT/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'bodies':len(report['bodies']),'checks':len(report['checks']),
                  'failed_bodies':[x for x in report['bodies'] if not x['passed']],
                  'failed_checks':[x for x in report['checks'] if not x['passed']]}),flush=True)
assert report['passed'], 'Native rigid drivetrain validation failed; see checks.json'

