"""Rigid placement of native CAD exports for offline slicing; no rendering."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'design/drivetrain-revision-2026-10-03'
OUT=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else ROOT/'first-prints/drivetrain-fit-2026-10-03'
PARTS=[('one-drive-fit-section',373,'y'),('input-sliding-carrier',437,'z'),
       ('clutch-reaction-plate',388,'y'),('clutch-pressure-pad',391,'y'),
       ('clutch-journal-bush',307,'y'),('clutch-output-pulley',9,'y'),
       ('servo-upper-bridge',367,'z'),('servo-shaft-clamp-trial',301,'y'),
       ('input-pulley-clamp-trial',10,'y'),('mouth-bearing-retainer',376,'y'),
       ('input-inboard-bearing-retainer',377,'y'),('input-outboard-bearing-retainer',378,'y'),
       ('center-bearing-retainer',383,'y'),('left-wheel-axle-vertical',13,'y')]
REX=len(sys.argv)>3 and sys.argv[3]=='rex'
HORN=len(sys.argv)>3 and sys.argv[3] in ['horn','rex']
if len(sys.argv)>3 and sys.argv[3] in ['rigid','horn','rex']:
    PARTS=[p for p in PARTS if not p[0].startswith('clutch-')]
    PARTS.insert(2,('rigid-output-pulley',9,'y'))
if HORN:PARTS=[('servo-horn-shaft-adapter' if name=='servo-shaft-clamp-trial' else name,bid,axis) for name,bid,axis in PARTS]
if REX:PARTS=[('servo-horn-rex-adapter' if name=='servo-horn-shaft-adapter' else 'input-rex-pulley' if name=='input-pulley-clamp-trial' else name,bid,axis) for name,bid,axis in PARTS]
OUT.mkdir(parents=True,exist_ok=True)
rows=[]
for name,bid,axis in PARTS:
    path=SOURCE/f'body-{bid}.stl'
    m=trimesh.load_mesh(path)
    if axis=='y':m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    m.apply_translation([-m.bounds[:,0].mean(),-m.bounds[:,1].mean(),-m.bounds[0,2]])
    assert m.is_watertight and len(m.split(only_watertight=False))==1
    m.export(OUT/f'{name}.stl')
    rows.append(dict(name=name,body_id=bid,native_mesh_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     quantity=2 if name=='clutch-pressure-pad' else 1,bed_bounds_mm=m.bounds.tolist()))
(OUT/'source.json').write_text(json.dumps(dict(source='Roller-300.nbcad',
    source_sha256=hashlib.sha256((ROOT/'Roller-300.nbcad').read_bytes()).hexdigest(),
    basis='Native CAD STL exports; rigid rotation/translation only',material='PETG',nozzle_mm=.4,
    whole_vehicle_release=False,powered=False,horn_adapter_release=HORN,positive_rex_input=REX,
    scope='Unpowered roof-open one-drive fit; nominal purchased H25T horn interface defined' if HORN else 'Unpowered roof-open one-drive fit; clamp trial has no finalized horn interface',parts=rows),indent=2)+'\n')
print('Prepared',len(rows),'connected native fit parts')
