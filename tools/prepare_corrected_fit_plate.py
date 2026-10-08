"""Correct the S20 review plate's support cleanup and bed margins.

Keep all ten native meshes unchanged. Added cubes are nonprinting Bambu support
blockers. Offline slicing only: this script cannot send a job to a printer.
"""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import uuid
import xml.etree.ElementTree as ET
import zipfile
from bambu_project_settings import preserve_process_overrides

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'first-prints/bambu-adversarial-review-2026-10-06/Roller-300-REX-first-fit.3mf'
NATIVE = ROOT / 'design/adversarial-review-2026-10-06/body-437.stl'
OUT = ROOT / 'first-prints/corrected-full-fit-2026-10-06'
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
ET.register_namespace('', NS)
ET.register_namespace('p', PROD)
ET.register_namespace('BambuStudio', 'http://schemas.bambulab.com/package/2021')
tag = lambda name: '{' + NS + '}' + name
sha = lambda data: hashlib.sha256(data).hexdigest()


def stl_bounds(path):
    data = path.read_bytes()
    count = struct.unpack_from('<I', data, 80)[0]
    assert len(data) == 84 + count * 50
    points = [row[3 + k * 3:6 + k * 3]
              for i in range(count)
              for row in [struct.unpack_from('<12fH', data, 84 + i * 50)]
              for k in range(3)]
    return [[min(v[j] for v in points) for j in range(3)],
            [max(v[j] for v in points) for j in range(3)]]


def mesh_bounds(mesh):
    points = [tuple(float(v.get(axis)) for axis in 'xyz')
              for v in mesh.find(tag('vertices'))]
    return [[min(v[j] for v in points) for j in range(3)],
            [max(v[j] for v in points) for j in range(3)]]


def add_blocker(entries, model, config, parent_id, child_file, child_id,
                lo, hi, name):
    child = ET.fromstring(entries[child_file])
    assert all(o.get('id') != str(child_id) for o in child.find(tag('resources')))
    obj = ET.SubElement(child.find(tag('resources')), tag('object'), id=str(child_id), type='model')
    mesh = ET.SubElement(obj, tag('mesh'))
    vertices = ET.SubElement(mesh, tag('vertices'))
    triangles = ET.SubElement(mesh, tag('triangles'))
    points = [(lo[0], lo[1], lo[2]), (hi[0], lo[1], lo[2]),
              (hi[0], hi[1], lo[2]), (lo[0], hi[1], lo[2]),
              (lo[0], lo[1], hi[2]), (hi[0], lo[1], hi[2]),
              (hi[0], hi[1], hi[2]), (lo[0], hi[1], hi[2])]
    faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
             (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
             (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    for x, y, z in points:
        ET.SubElement(vertices, tag('vertex'), x=str(x), y=str(y), z=str(z))
    for a, b, c in faces:
        ET.SubElement(triangles, tag('triangle'), v1=str(a), v2=str(b), v3=str(c))
    parent = next(o for o in model.find(tag('resources')) if o.get('id') == str(parent_id))
    ET.SubElement(parent.find(tag('components')), tag('component'),
                  {f'{{{PROD}}}path': '/' + child_file, 'objectid': str(child_id),
                   f'{{{PROD}}}UUID': str(uuid.uuid4()),
                   'transform': '1 0 0 0 1 0 0 0 1 0 0 0'})
    obj_cfg = next(o for o in config.findall('object') if o.get('id') == str(parent_id))
    part = ET.SubElement(obj_cfg, 'part', id=str(child_id), subtype='support_blocker', uuid=str(uuid.uuid4()))
    ET.SubElement(part, 'metadata', key='name', value=name)
    ET.SubElement(part, 'metadata', key='matrix', value='1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
    ET.SubElement(part, 'mesh_stat', face_count='12', edges_fixed='0', degenerate_facets='0',
                  facets_removed='0', facets_reversed='0', backwards_edges='0')
    entries[child_file] = ET.tostring(child, encoding='utf-8', xml_declaration=True)
    return dict(name=name, parent_id=parent_id, nonprinting=True,
                child_file=child_file, child_id=child_id,
                local_bounds_mm=[list(lo), list(hi)])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(SOURCE) as z:
        entries = {n: z.read(n) for n in z.namelist()}
    original_meshes = {}
    for file in entries:
        if file.startswith('3D/Objects/') and file.endswith('.model'):
            child = ET.fromstring(entries[file])
            for obj in child.find(tag('resources')):
                if obj.find(tag('mesh')) is not None:
                    original_meshes[(file, obj.get('id'))] = ET.tostring(obj.find(tag('mesh')))
    model = ET.fromstring(entries['3D/3dmodel.model'])
    config = ET.fromstring(entries['Metadata/model_settings.config'])
    # Original object ids: 14=fixture; 16=output pulley.
    moved = {'14': [75, 139], '16': [65, 224]}
    for item in model.find(tag('build')):
        if item.get('objectid') in moved:
            transform = item.get('transform').split()
            transform[9:11] = [str(v) for v in moved[item.get('objectid')]]
            item.set('transform', ' '.join(transform))
    for plate in config.findall('plate'):
        for md in list(plate):
            if md.get('key') in {'gcode_file', 'thumbnail_file', 'thumbnail_no_light_file', 'top_file', 'pick_file'}:
                plate.remove(md)
    blockers = [add_blocker(entries, model, config, 20, '3D/Objects/object_10.model', 100,
                            (-10, -10, 1.69999962), (17, 10, 3.49999962),
                            'Keep E-clip pocket free of supports')]
    # Carrier is printed in native XYZ orientation, rigidly centered. Derive
    # that translation from fresh exported vertices and verify the source child.
    native_bounds = stl_bounds(NATIVE)
    mid = [(a + b) / 2 for a, b in zip(*native_bounds)]
    child = ET.fromstring(entries['3D/Objects/object_5.model'])
    normal = next(o for o in child.find(tag('resources')) if o.get('id') == '9')
    child_bounds = mesh_bounds(normal.find(tag('mesh')))
    expected = [[native_bounds[k][j] - mid[j] for j in range(3)] for k in range(2)]
    assert max(abs(child_bounds[k][j] - expected[k][j]) for k in range(2) for j in range(3)) < 1e-5
    for bid, x in [(101, 34.1723), (102, 65.1723)]:
        # Include the hex end as well as the 22 mm straight loading channel.
        # Block the supporting roof and its surrounding OD10 post as well as
        # the void. A void-only blocker leaves the overhang seeds in adjacent
        # walls active, allowing generated support to expand into the channel.
        native_lo = [x - 5.6, -.4, 128.5]
        native_hi = [x + 5.6, 27.5, 132.0]
        local_lo = [a - b for a, b in zip(native_lo, mid)]
        local_hi = [a - b for a, b in zip(native_hi, mid)]
        rec = add_blocker(entries, model, config, 10, '3D/Objects/object_5.model', bid,
                          local_lo, local_hi, f'Keep bridge nut channel X{x} free of supports')
        rec.update(native_bounds_mm=[native_lo, native_hi], bed_z_mm=[native_lo[2] - native_bounds[0][2], native_hi[2] - native_bounds[0][2]])
        blockers.append(rec)
    # A support modifier must never change an original normal mesh.
    for (file, oid), before in original_meshes.items():
        child = ET.fromstring(entries[file])
        after = ET.tostring(next(o for o in child.find(tag('resources')) if o.get('id') == oid).find(tag('mesh')))
        assert before == after, (file, oid)
    entries['3D/3dmodel.model'] = ET.tostring(model, encoding='utf-8', xml_declaration=True)
    entries['Metadata/model_settings.config'] = ET.tostring(config, encoding='utf-8', xml_declaration=True)
    placement = OUT / 'corrected-full-fit-placement.3mf'
    with zipfile.ZipFile(placement, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in entries.items():
            if name.startswith(('3D/', '_rels/')) or name in {'[Content_Types].xml', 'Metadata/project_settings.config', 'Metadata/model_settings.config'}:
                z.writestr(name, data)
    settings = ROOT / 'first-prints/adversarial-fit-2026-10-06/slicer-check/input-sliding-carrier'
    project = 'Roller-300-full-fit-corrected.3mf'
    args = [r'C:\Program Files\Bambu Studio\bambu-studio.exe', '--debug', '3',
            '--filament-map', '1', '--filament-map-mode', 'Manual', '--arrange', '0',
            '--load-settings', str(settings / 'machine.json') + ';' + str(settings / 'input-sliding-carrier-process.json'),
            '--load-filaments', str(settings / 'input-sliding-carrier-filament.json'),
            '--curr-bed-type', 'Textured PEI Plate', '--slice', '0', '--export-3mf', project,
            '--outputdir', str(OUT), str(placement)]
    run = subprocess.run(args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08000000)
    (OUT / 'stdout.log').write_bytes(run.stdout)
    (OUT / 'stderr.log').write_bytes(run.stderr)
    result = json.loads((OUT / 'result.json').read_text()) if (OUT / 'result.json').exists() else {}
    report = dict(source_project=str(SOURCE.relative_to(ROOT)), source_project_sha256=sha(SOURCE.read_bytes()),
                  native_geometry_changed=False, physical_print=False, support_blockers=blockers,
                  native_carrier_mesh_sha256=sha(NATIVE.read_bytes()), native_carrier_bounds_mm=native_bounds,
                  original_normal_meshes_unchanged=len(original_meshes), moved_object_centers_mm=moved,
                  normal_meshes=[dict(file=f, object_id=i, xml_sha256=sha(v)) for (f, i), v in original_meshes.items()],
                  exit_code=run.returncode, slice_result=result)
    (OUT / 'slice-check.json').write_text(json.dumps(report, indent=2) + '\n')
    assert run.returncode == 0 and result.get('return_code') == 0, 'Inspect full slice logs'
    assert all(not p.get('warning_message') for p in result['sliced_plates']), 'Inspect slice warnings'
    final = OUT / project
    report['gui_settings_preservation'] = preserve_process_overrides(final, json.loads((settings / 'input-sliding-carrier-process.json').read_text()))
    report['project_sha256'] = sha(final.read_bytes())
    (OUT / 'slice-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(project=str(final), grams=sum(float(f['total_used_g']) for p in result['sliced_plates'] for f in p['filaments']),
                          seconds=sum(float(p['total_predication']) for p in result['sliced_plates']))))


if __name__ == '__main__':
    main()
