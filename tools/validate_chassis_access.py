"""Exact inspection of installed-CAD-authored S21 export; never author geometry here."""
from pathlib import Path
import json,hashlib
import trimesh
from OCP.STEPControl import STEPControl_Reader
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common,BRepAlgoAPI_Cut
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir,gp_Trsf,gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

R=Path(__file__).resolve().parents[1]
OUT=R/'design/chassis-fit-review-2026-10-07/s21-access'
OLD=R/'design/chassis-fit-review-2026-10-07/independent'
HIST=R/'design/adversarial-review-2026-10-06'
def read(p):
 r=STEPControl_Reader();assert int(r.ReadFile(str(p)))==1;r.TransferRoots();return r.OneShape()
def vol(s):
 p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p);return abs(p.Mass())
def bounds(s):
 b=Bnd_Box();BRepBndLib.Add_s(s,b)
 return None if b.IsVoid() else [list(b.CornerMin().Coord()),list(b.CornerMax().Coord())]
def cyl(x,y,z,r,l,axis=(0,1,0)):
 return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,y,z),gp_Dir(*axis)),r,l).Shape()
def common(a,b):return BRepAlgoAPI_Common(a,b).Shape()
def minus(a,b):return BRepAlgoAPI_Cut(a,b).Shape()
def overlap(a,b):return vol(common(a,b))
def move(s,y):
 t=gp_Trsf();t.SetTranslation(gp_Vec(0,y,0));return BRepBuilderAPI_Transform(s,t,True).Shape()
def distance(a,b):
 q=BRepExtrema_DistShapeShape(a,b);q.Perform();assert q.IsDone();return q.Value()
def solid_count(s):
 e=TopExp_Explorer(s,TopAbs_SOLID);n=0
 while e.More():n+=1;e.Next()
 return n

report={'qualification':'Exact STEP gauge inspection of native CAD-authored S21 geometry. Nominal fit only; not physical fit, material strength or motion qualification.','native_export_provenance':json.loads((OUT/'native-replay-export.json').read_text()),'body_validation':[],'wheel_access':[],'preserved_wheel_regions':[],'driver_service':[],'nominal_clearances':[]}
new={b:read(OUT/f'body-{b}.step') for b in [32,13,30]}
old={b:read(OLD/f'body-{b}.step') for b in [32,13,30]}
for b,s in new.items():
 mesh=trimesh.load(OUT/f'body-{b}.stl',force='mesh')
 row={'body':b,'valid_brep':BRepCheck_Analyzer(s).IsValid(),'solid_count':solid_count(s),'watertight_mesh':mesh.is_watertight,'mesh_components':len(mesh.split(only_watertight=False)),'bounds_mm':bounds(s),'volume_mm3':vol(s)}
 report['body_validation'].append(row);assert row['valid_brep'] and row['solid_count']==1 and row['watertight_mesh'] and row['mesh_components']==1
 print('Validated solid and mesh',b,flush=True)

for b,sign in [(13,1),(30,-1)]:
 for x in [-8,8]:
  for z in [115,131]:
   driver=cyl(x,sign*141.6,z,1.75,48.4,(0,sign,0))
   head_sweep=cyl(x,sign*137.5,z,3.5,52.5,(0,sign,0))
   shank=cyl(x,sign*133.5,z,2,4,(0,sign,0))
   row={'body':b,'bolt_center_xz':[x,z],'driver_diameter_mm':3.5,'driver_overlap_mm3':overlap(new[b],driver),'head_diameter_mm':7,'head_insertion_sweep_overlap_mm3':overlap(new[b],head_sweep),'shank_diameter_mm':4,'shank_web_overlap_mm3':overlap(new[b],shank)}
   report['wheel_access'].append(row);assert max(row['driver_overlap_mm3'],row['head_insertion_sweep_overlap_mm3'],row['shank_web_overlap_mm3'])<1e-5
 web=cyl(0,sign*133.5,123,108.2,4,(0,sign,0))
 outer=cyl(0,sign*110,123,115,40,(0,sign,0));inner=cyl(0,sign*110,123,108,40,(0,sign,0));rim=minus(outer,inner)
 row={'body':b,'hub_web_axial_mm':[sign*133.5,sign*137.5],'hub_web_original_volume_mm3':overlap(old[b],web),'hub_web_revised_volume_mm3':overlap(new[b],web),'rim_radial_mm':[108,115],'rim_original_volume_mm3':overlap(old[b],rim),'rim_revised_volume_mm3':overlap(new[b],rim),'added_material_mm3':vol(minus(new[b],old[b])),'removed_material_mm3':vol(minus(old[b],new[b])),'removed_material_bounds_mm':bounds(minus(old[b],new[b])),'nominal_open_face_diameter_mm':216}
 report['preserved_wheel_regions'].append(row)
 assert abs(row['hub_web_original_volume_mm3']-row['hub_web_revised_volume_mm3'])<1e-4
 assert abs(row['rim_original_volume_mm3']-row['rim_revised_volume_mm3'])<1e-4
 assert row['added_material_mm3']<1e-5
 print('Wheel access and preserved web/rim',b,flush=True)

for sign in [1,-1]:
 gauge=cyl(30.5,sign*79,96,1.5,160,(0,0,1))
 cutter=cyl(30.5,sign*79,155.8,2.2,8.4,(0,0,1))
 removed=common(old[32],cutter)
 row={'side':'L' if sign==1 else 'R','driver_diameter_mm':3,'service_bore_diameter_mm':4.4,'radial_clearance_mm':.7,'old_driver_overlap_mm3':overlap(old[32],gauge),'new_driver_overlap_mm3':overlap(new[32],gauge),'removed_roof_mm3':vol(removed),'removed_roof_bounds_mm':bounds(removed),'adjacent_body_cutter_overlaps':[]}
 for b in [9,10,367,301,376,377,378,383,437,12]:
  p=OLD/f'body-{b}.step'
  if not p.exists():p=HIST/f'body-{b}.step'
  v=overlap(read(p),cutter);row['adjacent_body_cutter_overlaps'].append({'body':b,'volume_mm3':v});assert v<1e-5
 report['driver_service'].append(row);assert row['new_driver_overlap_mm3']<1e-5
 print('Rear driver bore',sign,flush=True)

for wheel,sign,cap in [(13,1,376),(30,-1,380)]:
 obstacles={32:new[32],cap:read(HIST/f'body-{cap}.step')}
 for dy in [-.2,0,.2]:
  shifted=move(new[wheel],dy)
  for b,s in obstacles.items():
   row={'wheel':wheel,'other_body':b,'axial_shift_mm':dy,'minimum_surface_gap_mm':distance(shifted,s),'intersection_mm3':overlap(shifted,s)}
   report['nominal_clearances'].append(row);assert row['intersection_mm3']<1e-5
 print('Wheel shell/cap clearances',wheel,flush=True)

report['all_checks_passed']=True
(OUT/'exact-fit-inspection.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'all_checks_passed':True,'minimum_surface_gap_mm':min(x['minimum_surface_gap_mm'] for x in report['nominal_clearances']),'ten_unchanged_fit_parts':len(report['native_export_provenance']['unchanged_current_fit_parts'])}),flush=True)
