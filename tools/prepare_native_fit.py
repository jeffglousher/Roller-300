"""Place unchanged CAD-exported meshes on the slicer bed; no rendering."""
from pathlib import Path
import hashlib
import json
import numpy as np
import trimesh
root=Path(__file__).resolve().parents[1]
source=root/'design/native-fixes-2026-10-03'
out=root/'first-prints/native-fit-2026-10-03'
out.mkdir(parents=True,exist_ok=True)
parts=[('center-bearing-retainer',383)]
for name,bid in parts+[('main-shell-axle-vertical',32),('left-wheel-axle-vertical',13),('servo-upper-bridge',367),('one-drive-fit-section',373),('outer-wheel-bearing-coupon',374),('servo-shaft-clamp-trial',301),('input-pulley-clamp-trial',10),('wheel-bearing-retainer',375),('mouth-bearing-retainer',376),('input-inboard-bearing-retainer',377),('input-outboard-bearing-retainer',378)]:
    mesh=trimesh.load_mesh(source/f'body-{bid}.stl')
    mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    mesh.apply_translation([-mesh.bounds[:,0].mean(),-mesh.bounds[:,1].mean(),-mesh.bounds[0,2]])
    mesh.export(out/f'{name}.stl')
(out/'source.json').write_text(json.dumps({'source':'Roller-300.nbcad','sha256':hashlib.sha256((root/'Roller-300.nbcad').read_bytes()).hexdigest(),'basis':'Application native STL exports, rigid rotation and placement only','release':False,'material':'PETG','nozzle_mm':0.4,'powered':False},indent=2)+'\n')
print('Prepared native mesh fit candidates; whole vehicle print release remains HOLD')
