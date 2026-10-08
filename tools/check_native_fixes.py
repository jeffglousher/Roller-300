"""Check application-exported STEP and STL; no rendering or geometry changes."""
from pathlib import Path
import json
import hashlib
import trimesh
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt
from OCP.gp import gp_Ax2, gp_Dir
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

root=Path(__file__).resolve().parents[1]
out=root/'design/native-fixes-2026-10-03'
report={'source_sha256':hashlib.sha256((root/'Roller-300.nbcad').read_bytes()).hexdigest(),'basis':'STEP and STL exported through the attached CAD application; nominal geometry only','bodies':[]}
shapes={}
for bid in [10,13,27,30,32,301,309,367,368,373,374,375,376,377,378,379,380,381,382,383,384]:
    reader=STEPControl_Reader()
    assert reader.ReadFile(str(out/f'body-{bid}.step')).name=='IFSelect_RetDone'
    reader.TransferRoots()
    shape=reader.OneShape()
    shapes[bid]=shape
    explorer=TopExp_Explorer(shape,TopAbs_SOLID)
    count=0
    while explorer.More():count+=1;explorer.Next()
    mesh=trimesh.load_mesh(out/f'body-{bid}.stl')
    parts=mesh.split(only_watertight=False)
    row={'body_id':bid,'valid_brep':bool(BRepCheck_Analyzer(shape).IsValid()),'solid_count':count,'watertight_mesh':bool(mesh.is_watertight),'mesh_components':len(parts),'bounds_mm':mesh.bounds.tolist()}
    report['bodies'].append(row)
    print(json.dumps(row))
def volume(shape):
    props=GProp_GProps();BRepGProp.VolumeProperties_s(shape,props);return props.Mass()
report['servo_vertical_insertion']=[]
for side,base in [('L',5),('R',-45.5)]:
    # Conservative 120 mm straight lift of the box case and drawn ears.
    # Upper bridges and front retainers are removed during insertion.
    boxes=[(base,40.5,93,160.5),((29.7 if side=='L' else -32.4),2.7,85.25,127.75),((29.7 if side=='L' else -32.4),2.7,133.5,127.75)]
    overlaps=[]
    for y,depth,z,height in boxes:
        sweep=BRepPrimAPI_MakeBox(gp_Pnt(39.6723,y,z),20,depth,height).Shape()
        common=BRepAlgoAPI_Common(shapes[32],sweep);common.Build()
        assert common.IsDone()
        overlaps.append(max(0.,volume(common.Shape())))
    report['servo_vertical_insertion'].append({'side':side,'lift_mm':120,'overlap_mm3':overlaps,'scope':'case and ear envelopes only; horn, cable and tool access require physical fit'})
(out/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(r['valid_brep'] and r['solid_count']==1 and r['watertight_mesh'] and r['mesh_components']==1 for r in report['bodies']), 'Print connectivity check failed'
assert all(max(r['overlap_mm3'])<0.001 for r in report['servo_vertical_insertion']), 'Servo insertion blocked'
print('Servo case/ear insertion paths clear with bridges removed')

report['clamp_rotation_clearance']=[]
for side,sign in [('L',1),('R',-1)]:
    for name,radius,start,length in [('coupler',15.24,45.8,7.0),('coupler inner-race land',5.5,52.8,1.0),('input pulley',15.24,62.75,17.0),('outer collar hardware envelope',13.65,90,6)]:
        envelope=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(49.6723,sign*start,123),gp_Dir(0,sign,0)),radius,length).Shape()
        overlap=0.
        for stationary in [32,376,377,378,380,381,382,383,384]:
            common=BRepAlgoAPI_Common(shapes[stationary],envelope);common.Build()
            assert common.IsDone()
            overlap+=max(0.,volume(common.Shape()))
        report['clamp_rotation_clearance'].append({'side':side,'part':name,'sweep_radius_mm':radius,'shell_overlap_mm3':overlap,'scope':'conservative 360 degree envelope against stationary shell; excludes unknown horn and cable'})
assert all(r['shell_overlap_mm3']<0.001 for r in report['clamp_rotation_clearance']), 'Rotating clamp hits shell'
(out/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
print('Conservative clamp rotation envelopes clear the stationary shell')

report['retainer_assembly_overlap']=[]
for cap,parent in [(375,13),(379,30),(376,32),(377,32),(378,32),(380,32),(381,32),(382,32),(383,32),(384,32)]:
    common=BRepAlgoAPI_Common(shapes[cap],shapes[parent]);common.Build()
    assert common.IsDone()
    overlap=max(0.,volume(common.Shape()))
    report['retainer_assembly_overlap'].append({'cap_body':cap,'parent_body':parent,'overlap_mm3':overlap})
(out/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(r['overlap_mm3']<0.001 for r in report['retainer_assembly_overlap']), 'Retainer cannot seat on parent'
print('Retainers seat without volumetric assembly interference')
