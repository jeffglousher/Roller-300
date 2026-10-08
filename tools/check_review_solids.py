"""Read-only exact STEP checks on review exports from the native master."""
from pathlib import Path
import json
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
import trimesh

OUT=Path(__file__).resolve().parents[1]/'design/review-2026-10-03'
shapes={}
def volume(shape):
    p=GProp_GProps()
    BRepGProp.VolumeProperties_s(shape,p)
    return float(p.Mass())
report={'basis':'Native STEP exports from fresh isolated recomputation; nominal geometry only','bodies':[],'pairs':[],'refined_meshes':[]}
for path in sorted(OUT.glob('body-*.step')):
    bid=int(path.stem.split('-')[1])
    r=STEPControl_Reader()
    r.ReadFile(str(path))
    r.TransferRoots()
    s=r.OneShape()
    shapes[bid]=s
    e=TopExp_Explorer(s,TopAbs_SOLID)
    solids=[]
    solid_shapes=[]
    while e.More():
        solids.append(volume(e.Current()))
        solid_shapes.append(e.Current())
        e.Next()
    item={'body_id':bid,'valid_brep':bool(BRepCheck_Analyzer(s).IsValid()),'solid_count':len(solids),'solid_volumes_mm3':solids,'volume_mm3':volume(s)}
    report['bodies'].append(item)
    if bid in [13,30,32]:
        main=max(range(len(solids)),key=lambda i:solids[i])
        distances=[]
        for i,part in enumerate(solid_shapes):
            if i==main:continue
            gap=BRepExtrema_DistShapeShape(part,solid_shapes[main]);gap.Perform()
            distances.append({'solid_index':i,'distance_to_main_mm':float(gap.Value())})
        item['separate_solid_distances']=distances
    print('EXACT BODY',json.dumps(item),flush=True)
for a,b in [(32,356),(32,300),(32,13),(32,5),(32,22),(32,9),(32,10),(356,1),(356,357),(356,358),(13,359),(2,359),(19,360),(224,32),(227,32),(301,316)]:
    sa,sb=shapes[a],shapes[b]
    common=BRepAlgoAPI_Common(sa,sb)
    common.Build()
    overlap=volume(common.Shape()) if common.IsDone() else None
    d=BRepExtrema_DistShapeShape(sa,sb)
    d.Perform()
    item={'body_a':a,'body_b':b,'overlap_mm3':overlap,'clearance_mm':float(d.Value()) if d.IsDone() else None}
    report['pairs'].append(item)
    print('EXACT PAIR',json.dumps(item),flush=True)
for path in OUT.glob('body-*-review.stl'):
    t=trimesh.load_mesh(path)
    components=t.split(only_watertight=False)
    item={'file':path.name,'watertight':bool(t.is_watertight),'connected_components':len(components),'components':[{'bounds_mm':c.bounds.tolist(),'volume_mm3':float(c.volume),'watertight':bool(c.is_watertight)} for c in components]}
    report['refined_meshes'].append(item)
    print('REFINED MESH',json.dumps(item),flush=True)
(OUT/'exact-checks.json').write_text(json.dumps(report,indent=2))
