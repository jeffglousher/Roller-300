"""Verify current native meshes, nonprinting modifiers and fit-project settings."""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
from bambu_project_settings import PROCESS_OVERRIDE_KEYS

R = Path(__file__).resolve().parents[1]
current = json.loads((R/'parameters.json').read_text(encoding='utf-8-sig'))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--evidence', type=Path,
                    default=Path(current.get('current_native_mesh_evidence',
                                             'design/print-decision-2026-10-06')))
args = parser.parse_args()
D = R/args.evidence
P = R/'first-prints/adversarial-fit-2026-10-06'
PROJECTS = [R/'first-prints/receiving-fit-gate-2026-10-06/Roller-300-small-fit-gate.3mf']
full = R/'first-prints/corrected-full-fit-2026-10-06/Roller-300-full-fit-corrected.3mf'
if full.exists(): PROJECTS.append(full)
carrier = R/'first-prints/carrier-roof-trial-2026-10-06/Roller-300-carrier-roof-trial.3mf'
if carrier.exists(): PROJECTS.append(carrier)
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fresh = json.loads((D/'fresh-native-replay.json').read_text())
assert fresh['passed'] and not fresh['feature_errors']
assert fresh['source_sha256']==sha(R/'Roller-300.nbcad')
assert all(x['current_native_mesh_matches_print'] and sha(D/f"body-{x['body_id']}.stl")==x['sha256'] for x in fresh['parts'])
ns='{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
prod='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
reports=[]
for project in PROJECTS:
    with zipfile.ZipFile(project) as z:
        assert z.testzip() is None
        cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
        by_id={o.get('id'):o for o in cfg.findall('object')}
        model=ET.fromstring(z.read('3D/3dmodel.model'))
        meshes=[]; blockers=[]
        for o in model.find(ns+'resources').findall(ns+'object'):
            settings=by_id[o.get('id')]
            name=next(m.get('value') for m in settings.findall('metadata') if m.get('key')=='name')
            parts={p.get('id'):p.get('subtype') for p in settings.findall('part')}
            for comp in o.find(ns+'components'):
                cid=comp.get('objectid');role=parts[cid]
                if role=='support_blocker':blockers.append(dict(parent=name,subtype=role));continue
                assert role=='normal_part',role
                child=ET.fromstring(z.read(comp.get(prod+'path').lstrip('/')))
                obj=next(v for v in child.find(ns+'resources') if v.get('id')==cid)
                mesh=obj.find(ns+'mesh')
                vertices=np.array([[float(v.get(k)) for k in ['x','y','z']] for v in mesh.find(ns+'vertices')])
                faces=np.array([[int(v.get(k)) for k in ['v1','v2','v3']] for v in mesh.find(ns+'triangles')])
                actual=vertices[faces]
                data=(P/(name+'.stl')).read_bytes();count=struct.unpack_from('<I',data,80)[0]
                assert count==len(actual)
                expected=np.array([struct.unpack_from('<12fH',data,84+50*i)[3:12] for i in range(count)]).reshape((-1,3,3))
                actual-=(actual.min(axis=(0,1))+actual.max(axis=(0,1)))/2
                expected-=(expected.min(axis=(0,1))+expected.max(axis=(0,1)))/2
                error=float(np.abs(actual-expected).max())
                assert error<.00005,(name,error)
                meshes.append(dict(name=name,triangles=count,max_coordinate_error_mm=error))
        s=json.loads(z.read('Metadata/project_settings.config'))
        assert set(PROCESS_OVERRIDE_KEYS)<=set(s['different_settings_to_system'][0].split(';'))
        assert s['wall_loops']=='5' and s['sparse_infill_pattern']=='gyroid'
        assert s['enable_support']=='1' and s['support_on_build_plate_only']=='0'
        assert s['layer_height']=='0.2' and s['nozzle_diameter'][0]=='0.4'
        assert 'PETG' in s['filament_type'][0] and 'X2D' in s['printer_model']
        g=z.read('Metadata/plate_1.gcode')
        assert hashlib.md5(g).hexdigest().upper()==z.read('Metadata/plate_1.gcode.md5').decode().strip().upper()
        reports.append(dict(project=str(project.relative_to(R)),sha256=sha(project),native_meshes=meshes,
                            nonprinting_support_blockers=blockers,gui_process_keys_preserved=True,gcode_md5_valid=True))
counts={'Roller-300-small-fit-gate.3mf':(5,1),'Roller-300-full-fit-corrected.3mf':(10,3),
        'Roller-300-carrier-roof-trial.3mf':(1,2)}
for r in reports:
    n,b=counts[Path(r['project']).name]
    assert len(r['native_meshes'])==n and len(r['nonprinting_support_blockers'])==b
report=dict(source_sha256=fresh['source_sha256'],fresh_native_export_count=len(fresh['parts']),
            native_geometry_changed=fresh.get('native_geometry_changed',False),print_geometry_changed=False,
            physical_print=False,projects=reports,passed=True)
(D/'print-project-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(passed=True,verified_projects=len(reports),fresh_native_exports=len(fresh['parts']))))
