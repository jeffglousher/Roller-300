import json, pathlib
from OCP.STEPControl import STEPControl_Reader
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane

root = pathlib.Path(__file__).resolve().parents[1]
out = {}
for body in [1, 18, 13, 30, 14, 31, 3, 20, 4, 21, 32]:
    path = root / 'design/chassis-fit-review-2026-10-07/independent' / f'body-{body}.step'
    reader = STEPControl_Reader()
    reader.ReadFile(str(path))
    reader.TransferRoots()
    shape = reader.OneShape()
    box = Bnd_Box(); box.SetGap(0.0); BRepBndLib.Add_s(shape, box, False)
    cyl, planes = [], []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        surf = BRepAdaptor_Surface(TopoDS.Face(exp.Current()), True)
        if surf.GetType() == GeomAbs_Cylinder:
            c = surf.Cylinder()
            fb = Bnd_Box(); fb.SetGap(0.0); BRepBndLib.Add_s(exp.Current(), fb, False)
            cyl.append(dict(radius=c.Radius(), location=list(c.Location().Coord()), direction=list(c.Axis().Direction().Coord()), bbox=list(fb.CornerMin().Coord())+list(fb.CornerMax().Coord())))
        elif surf.GetType() == GeomAbs_Plane:
            p=surf.Plane()
            if abs(p.Axis().Direction().Y()) > .99:
                planes.append(p.Location().Y())
        exp.Next()
    out[str(body)] = dict(path=str(path.relative_to(root)),bbox=list(box.CornerMin().Coord())+list(box.CornerMax().Coord()),y_planes=sorted(set(round(x,6) for x in planes)),cylinders=cyl)
dest = root / 'design/chassis-fit-review-2026-10-07/envelopes-and-wheel-features.json'
dest.write_text(json.dumps(out, indent=2), encoding='utf8')
print(json.dumps({k:dict(bbox=v['bbox'],y_planes=v['y_planes'],cylinders=[c for c in v['cylinders'] if c['radius']<10]) for k,v in out.items() if k != '32'},indent=2))
