"""Prepare a small receiving-fit plate from unchanged native CAD meshes.

The only added geometry is a Bambu support blocker, never a printed part.
Offline slicing only; no connection to or submission to a printer.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import uuid
import xml.etree.ElementTree as ET
import zipfile
from bambu_project_settings import preserve_process_overrides

R = Path(__file__).resolve().parents[1]
SOURCE = R / 'first-prints/bambu-adversarial-review-2026-10-06/Roller-300-REX-first-fit.3mf'
OUT = R / 'first-prints/receiving-fit-gate-2026-10-06'
OUT.mkdir(parents=True, exist_ok=True)
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
P = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
ET.register_namespace('', NS)
ET.register_namespace('p', P)
ET.register_namespace('BambuStudio', 'http://schemas.bambulab.com/package/2021')
tag = lambda n: '{' + NS + '}' + n

with zipfile.ZipFile(SOURCE) as z:
    entries = {n: z.read(n) for n in z.namelist()}
model = ET.fromstring(entries['3D/3dmodel.model'])
config = ET.fromstring(entries['Metadata/model_settings.config'])
selected = {'2': (80, 90), '6': (140, 90), '12': (80, 150),
            '18': (140, 150), '20': (190, 150)}
names = []
for obj in list(model.find(tag('resources'))):
    if obj.get('id') not in selected:
        model.find(tag('resources')).remove(obj)
for item in list(model.find(tag('build'))):
    oid = item.get('objectid')
    if oid not in selected:
        model.find(tag('build')).remove(item)
    else:
        transform = item.get('transform').split()
        transform[9:11] = [str(v) for v in selected[oid]]
        item.set('transform', ' '.join(transform))
for obj in list(config.findall('object')):
    if obj.get('id') not in selected:
        config.remove(obj)
    else:
        names.append(next(m.get('value') for m in obj.findall('metadata') if m.get('key') == 'name'))
for plate in config.findall('plate'):
    for md in list(plate):
        if md.get('key') in {'gcode_file', 'thumbnail_file', 'thumbnail_no_light_file', 'top_file', 'pick_file'}:
            plate.remove(md)

# Adapter local Z is centered at 6.10000038 mm on the print bed.
# Cover the clip cavity and its roof (bed Z7.8..9.6), including the radial window.
# Leave the horn/head recess supports below it enabled.
adapter_file = '3D/Objects/object_10.model'
child = ET.fromstring(entries[adapter_file])
blocker = ET.SubElement(child.find(tag('resources')), tag('object'), id='100', type='model')
mesh = ET.SubElement(blocker, tag('mesh'))
vertices = ET.SubElement(mesh, tag('vertices'))
triangles = ET.SubElement(mesh, tag('triangles'))
lo, hi = (-10.0, -10.0, 1.69999962), (17.0, 10.0, 3.49999962)
points = [(lo[0],lo[1],lo[2]), (hi[0],lo[1],lo[2]),
          (hi[0],hi[1],lo[2]), (lo[0],hi[1],lo[2]),
          (lo[0],lo[1],hi[2]), (hi[0],lo[1],hi[2]),
          (hi[0],hi[1],hi[2]), (lo[0],hi[1],hi[2])]
for x,y,z in points:
    ET.SubElement(vertices,tag('vertex'),x=str(x),y=str(y),z=str(z))
faces = [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
         (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
for a,b,c in faces:
    ET.SubElement(triangles,tag('triangle'),v1=str(a),v2=str(b),v3=str(c))
parent = next(o for o in model.find(tag('resources')) if o.get('id')=='20')
ET.SubElement(parent.find(tag('components')), tag('component'),
              {f'{{{P}}}path': '/'+adapter_file, 'objectid':'100',
               f'{{{P}}}UUID':str(uuid.uuid4()), 'transform':'1 0 0 0 1 0 0 0 1 0 0 0'})
cfg = next(o for o in config.findall('object') if o.get('id')=='20')
part = ET.SubElement(cfg,'part',id='100',subtype='support_blocker',uuid=str(uuid.uuid4()))
ET.SubElement(part,'metadata',key='name',value='Keep E-clip pocket free of supports')
ET.SubElement(part,'metadata',key='matrix',value='1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
ET.SubElement(part,'mesh_stat',face_count='12',edges_fixed='0',degenerate_facets='0',
              facets_removed='0',facets_reversed='0',backwards_edges='0')
for filename, tree in [('3D/3dmodel.model', model), ('Metadata/model_settings.config',config), (adapter_file,child)]:
    entries[filename] = ET.tostring(tree, encoding='utf-8', xml_declaration=True)
placement = OUT/'receiving-fit-placement.3mf'
with zipfile.ZipFile(placement,'w',zipfile.ZIP_DEFLATED) as z:
    for name, data in entries.items():
        if name.startswith(('3D/', '_rels/')) or name in {'[Content_Types].xml','Metadata/project_settings.config','Metadata/model_settings.config'}:
            z.writestr(name,data)
settings = R/'first-prints/adversarial-fit-2026-10-06/slicer-check/input-sliding-carrier'
project = 'Roller-300-small-fit-gate.3mf'
args = [r'C:\Program Files\Bambu Studio\bambu-studio.exe','--debug','3',
        '--filament-map','1','--filament-map-mode','Manual','--arrange','0',
        '--load-settings',str(settings/'machine.json')+';'+str(settings/'input-sliding-carrier-process.json'),
        '--load-filaments',str(settings/'input-sliding-carrier-filament.json'),
        '--curr-bed-type','Textured PEI Plate','--slice','0','--export-3mf',project,
        '--outputdir',str(OUT),str(placement)]
run = subprocess.run(args,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=0x08000000)
(OUT/'stdout.log').write_bytes(run.stdout)
(OUT/'stderr.log').write_bytes(run.stderr)
result = json.loads((OUT/'result.json').read_text()) if (OUT/'result.json').exists() else {}
report = dict(source_project=str(SOURCE.relative_to(R)),source_project_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              native_geometry_changed=False,physical_print=False,parts=names,support_blocker_bed_z_mm=[7.8,9.6],
              exit_code=run.returncode,slice_result=result)
(OUT/'slice-check.json').write_text(json.dumps(report,indent=2)+'\n')
assert run.returncode==0 and result.get('return_code')==0, 'Inspect slice logs'
assert all(not p.get('warning_message') for p in result['sliced_plates']), 'Inspect slice warnings'
final = OUT/project
preserved = preserve_process_overrides(final,json.loads((settings/'input-sliding-carrier-process.json').read_text()))
report.update(gui_process_preservation=preserved,project_sha256=preserved['project_sha256'])
(OUT/'slice-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(project=str(OUT/project),grams=sum(float(f['total_used_g']) for p in result['sliced_plates'] for f in p['filaments']),
                      seconds=sum(float(p['total_predication']) for p in result['sliced_plates']))))
