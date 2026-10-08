"""Package unchanged native fit meshes and slice locally in Bambu Studio."""
from pathlib import Path
import json, struct, subprocess, zipfile, sys
import xml.etree.ElementTree as ET
from bambu_project_settings import preserve_process_overrides

ROOT = Path(__file__).resolve().parents[1]
PARTS = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT / 'first-prints/drivetrain-fit-2026-10-03'
OUT = Path(sys.argv[2]).resolve() if len(sys.argv)>2 else ROOT / 'first-prints/bambu-review-2026-10-04'
OUT.mkdir(parents=True, exist_ok=True)
placements = [
    ('mouth-bearing-retainer', 45, 50),
    ('center-bearing-retainer', 104, 50),
    ('input-inboard-bearing-retainer', 163, 50),
    ('input-outboard-bearing-retainer', 222, 50),
    ('input-sliding-carrier', 180, 150),
    ('servo-upper-bridge', 180, 225),
    ('one-drive-fit-section', 75, 145),
]
if (PARTS/'rigid-output-pulley.stl').exists():
    placements += [('rigid-output-pulley',65,228),('input-pulley-clamp-trial',115,228),
                   ('servo-shaft-clamp-trial',230,150)]
project_name='Roller-300-rigid-belt-first-fit.3mf' if (PARTS/'rigid-output-pulley.stl').exists() else 'Roller-300-first-fit-review.3mf'
if (PARTS/'servo-horn-shaft-adapter.stl').exists():
    placements=[('servo-horn-shaft-adapter' if name=='servo-shaft-clamp-trial' else name,x,y) for name,x,y in placements]
    project_name='Roller-300-servo-horn-first-fit.3mf'
if (PARTS/'servo-horn-rex-adapter.stl').exists():
    placements=[('servo-horn-rex-adapter' if name=='servo-shaft-clamp-trial' else 'input-rex-pulley' if name=='input-pulley-clamp-trial' else name,x,y) for name,x,y in placements]
    project_name='Roller-300-REX-first-fit.3mf'
ns = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('', ns)
tag = lambda name: '{' + ns + '}' + name
model = ET.Element(tag('model'), unit='millimeter')
resources = ET.SubElement(model, tag('resources'))
build = ET.SubElement(model, tag('build'))
for object_id, (name, x, y) in enumerate(placements, 1):
    obj = ET.SubElement(resources, tag('object'), id=str(object_id), type='model', name=name)
    mesh = ET.SubElement(obj, tag('mesh'))
    vertices = ET.SubElement(mesh, tag('vertices'))
    triangles = ET.SubElement(mesh, tag('triangles'))
    data = (PARTS / (name + '.stl')).read_bytes()
    count = struct.unpack_from('<I', data, 80)[0]
    assert len(data) == 84 + 50 * count
    index = {}
    for i in range(count):
        row = struct.unpack_from('<12fH', data, 84 + 50 * i)
        indices = []
        for k in range(3):
            point = tuple(row[3 + 3*k:6 + 3*k])
            if point not in index:
                index[point] = len(index)
                ET.SubElement(vertices, tag('vertex'), x=str(point[0]), y=str(point[1]), z=str(point[2]))
            indices.append(index[point])
        ET.SubElement(triangles, tag('triangle'), v1=str(indices[0]), v2=str(indices[1]), v3=str(indices[2]))
    ET.SubElement(build, tag('item'), objectid=str(object_id), transform=f'1 0 0 0 1 0 0 0 1 {x} {y} 0')
source = OUT / 'first-fit-placement.3mf'
with zipfile.ZipFile(source, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    z.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    z.writestr('3D/3dmodel.model', ET.tostring(model, encoding='utf-8', xml_declaration=True))
settings = PARTS / 'slicer-check/input-sliding-carrier'
if not (settings/'machine.json').exists():settings = ROOT / 'first-prints/drivetrain-fit-2026-10-03/slicer-check/input-sliding-carrier'
args = [r'C:\Program Files\Bambu Studio\bambu-studio.exe', '--debug', '3',
        '--filament-map', '1', '--filament-map-mode', 'Manual', '--arrange', '0',
        '--load-settings', str(settings/'machine.json')+';'+str(settings/'input-sliding-carrier-process.json'),
        '--load-filaments', str(settings/'input-sliding-carrier-filament.json'),
        '--curr-bed-type', 'Textured PEI Plate', '--slice', '0',
        '--export-3mf', project_name, '--outputdir', str(OUT), str(source)]
run = subprocess.run(args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08000000)
(OUT/'stdout.log').write_bytes(run.stdout)
(OUT/'stderr.log').write_bytes(run.stderr)
result = json.loads((OUT/'result.json').read_text()) if (OUT/'result.json').exists() else {}
report = {'exit_code': run.returncode, 'physical_print': False, 'parts': [p[0] for p in placements], 'slice_result': result}
if run.returncode == 0 and result.get('return_code') == 0:
    report['project_settings_check'] = preserve_process_overrides(
        OUT/project_name, json.loads((settings/'input-sliding-carrier-process.json').read_text()))
(OUT/'review-check.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'exit_code':run.returncode, 'return_code':result.get('return_code'),
                  'project':str(OUT/project_name),
                  'warnings':[p.get('warning_message') for p in result.get('sliced_plates',[]) if p.get('warning_message')]}))
assert run.returncode == 0 and result.get('return_code') == 0
