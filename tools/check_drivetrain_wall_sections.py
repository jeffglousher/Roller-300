"""Wall gauges inspect native application geometry; they do not author the design."""
from pathlib import Path
import json,math
from OCP.STEPControl import STEPControl_Reader
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder,BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common,BRepAlgoAPI_Cut
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt,gp_Dir,gp_Ax2
R=Path(__file__).resolve().parents[1];OUT=R/'design/adversarial-review-2026-10-06';rows=[]
def vol(s):
 p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p);return abs(p.Mass())
def cyl(y,l,r,sign):return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(49.6723,y,123),gp_Dir(0,sign,0)),r,l).Shape()
def ring(y,l,ro,ri,sign):return BRepAlgoAPI_Cut(cyl(y,l,ro,sign),cyl(y,l,ri,sign)).Shape()
for b,sign in [(301,1),(309,-1)]:
 r=STEPControl_Reader();r.ReadFile(str(OUT/f'body-{b}.step'));r.TransferRoots();s=r.OneShape()
 for name,y,l,ro,ri,thickness,limit,half in [
  ('REX bearing land',52.85,.9,5.45,4.23,5.5-7.3/math.sqrt(3),1.2,False),
  ('horn counterbore outer rim',45.15,2.1,16.55,15.34,16.6-(math.sqrt(128)+4),1.2,False),
  ('Eclip pocket rear half annulus',49.55,1.1,9.45,7.05,2.5,2.4,True)]:
  g=ring(sign*y,l,ro,ri,sign)
  if half:g=BRepAlgoAPI_Common(g,BRepPrimAPI_MakeBox(gp_Pnt(39.6723,-60,110),9.95,120,26).Shape()).Shape()
  fraction=vol(BRepAlgoAPI_Common(s,g).Shape())/vol(g)
  rows.append(dict(body=b,name=name,nominal_wall_mm=thickness,verified_continuous_gauge_width_mm=ro-ri,material_fraction=fraction,passed=fraction>.9999 and thickness>=limit))
report=dict(passed=all(x['passed'] for x in rows),scope='Torque-bearing land, horn screw rim and Eclip annulus. Continuous wall gauges only; does not claim every cosmetic lip is >=1.2mm. Upper servo-nut lower lip is0.95mm with solid axial backing; receiving/physical fit test, no powered-load qualification.',checks=rows)
for b,sign in [(10,1),(27,-1)]:
 r=STEPControl_Reader();r.ReadFile(str(OUT/f'body-{b}.step'));r.TransferRoots();s=r.OneShape()
 for name,y,l in [('pulley front race land',61.25,1.4),('pulley rear race land',79.6,1.1)]:
  g=ring(sign*y,l,5.45,4.23,sign);fraction=vol(BRepAlgoAPI_Common(s,g).Shape())/vol(g)
  rows.append(dict(body=b,name=name,nominal_wall_mm=5.5-7.3/math.sqrt(3),verified_continuous_gauge_width_mm=1.22,material_fraction=fraction,passed=fraction>.9999))
report['passed']=all(x['passed'] for x in rows)
(OUT/'wall-section-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert report['passed']
