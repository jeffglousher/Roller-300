"""Reconcile native CAD, inspection exports and actual slicer project geometry."""
from pathlib import Path
import hashlib,json,zipfile,struct,xml.etree.ElementTree as ET
import numpy as np
R=Path(__file__).resolve().parents[1];D=R/'design/adversarial-review-2026-10-06';P=R/'first-prints/adversarial-fit-2026-10-06';B=R/'first-prints/bambu-adversarial-review-2026-10-06'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
canonical=R/'Roller-300.nbcad';m=json.loads(zipfile.ZipFile(canonical).read('model.json'));replay=R/'.local/s20-adversarial-model-replayed.json';v=read(replay)
keys=['sketches','extrudes','body_features','datum_planes','revolves','sweeps','lofts','ribs','holes','fillets','chamfers']
assert all(m[k]==v[k] for k in keys),'Saved native CAD differs from validated replay'
assert len(m['document']['history']['features'])==2015
assert not [f for f in m['document']['history']['features'] if not f['suppressed'] and f['status']['state']!='ok']
geo=hashlib.sha256(json.dumps({k:m[k] for k in keys},sort_keys=True,separators=(',',':')).encode()).hexdigest();archive_sha=sha(canonical)
reports={n:read(D/n) for n in ['checks.json','adversarial-checks.json','capture-checks.json','wall-section-checks.json']}
assert all(d['passed'] and all(c['passed'] for c in d['checks']) for d in reports.values())
assert reports['checks.json']['source_model_sha256']==sha(replay)==reports['adversarial-checks.json']['source_model_sha256']
interference=[]
for n,expected in [('left-roof-open-native-interference.json',{frozenset(p) for p in [(11,9),(11,10),(445,12)]}),('right-full-frame-native-interference.json',{frozenset(p) for p in [(28,26),(28,27),(446,29)]})]:
 d=read(D/n);assert d['exact'] and d['source_model_sha256']==hashlib.sha256(replay.read_text(encoding='utf-8').encode()).hexdigest()
 overlaps=[p for p in d['pairs'] if p['interfering']];assert {frozenset((p['body_a'],p['body_b'])) for p in overlaps}==expected
 interference.append(dict(report=n,checked_body_ids=d['body_ids_checked'],reported_pairs=len(d['pairs']),expected_reference_overlaps=[dict(bodies=[p['body_a'],p['body_b']],volume_mm3=p['overlap_volume_mm3']) for p in overlaps],unexpected_overlaps=0,separately_probed_threaded_bodies=d['separately_inspected_threaded_bodies']))
manifest=read(P/'source.json');slices=read(P/'slice-checks.json');assert slices['passed'] and len(slices['parts'])==11
slice_by={x['part']:x for x in slices['parts']};hash_rows=[]
for p in manifest['parts']:
 native=D/f"body-{p['body_id']}.stl";s=slice_by[p['name']]
 assert sha(native)==p['native_mesh_sha256']==s['native_mesh_sha256'] and s['passed'] and not s['warnings']
 hash_rows.append(dict(name=p['name'],body_id=p['body_id'],native_mesh_sha256=sha(native),print_mesh_sha256=sha(P/(p['name']+'.stl'))))
# Inspect the exported Bambu project, including its external object meshes.
ns='{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}';prod='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
project=B/'Roller-300-REX-first-fit.3mf';plate=read(B/'review-check.json');assert plate['exit_code']==0 and plate['slice_result']['return_code']==0
assert all(not x['warning_message'] for x in plate['slice_result']['sliced_plates'])
plate_meshes=[]
with zipfile.ZipFile(project) as z:
 cfg=ET.fromstring(z.read('Metadata/model_settings.config'));names={o.attrib['id']:next(q.attrib['value'] for q in o.findall('metadata') if q.attrib.get('key')=='name') for o in cfg.findall('object')}
 model=ET.fromstring(z.read('3D/3dmodel.model'))
 for o in model.find(ns+'resources').findall(ns+'object'):
  name=names[o.attrib['id']];comp=o.find(ns+'components').find(ns+'component');obj=ET.fromstring(z.read(comp.attrib[prod+'path'].lstrip('/'))).find(ns+'resources').find(ns+'object');mesh=obj.find(ns+'mesh')
  verts=np.array([[float(q.attrib[k]) for k in ['x','y','z']] for q in mesh.find(ns+'vertices')]);faces=np.array([[int(q.attrib[k]) for k in ['v1','v2','v3']] for q in mesh.find(ns+'triangles')]);actual=verts[faces]
  data=(P/(name+'.stl')).read_bytes();count=struct.unpack_from('<I',data,80)[0];assert count==len(actual)
  expected=np.array([struct.unpack_from('<12fH',data,84+50*i)[3:12] for i in range(count)]).reshape((-1,3,3))
  actual-= (actual.min(axis=(0,1))+actual.max(axis=(0,1)))/2;expected-= (expected.min(axis=(0,1))+expected.max(axis=(0,1)))/2
  error=float(np.abs(actual-expected).max());assert error<.00005,(name,error)
  plate_meshes.append(dict(name=name,triangle_count=count,maximum_coordinate_difference_mm=error,passed=True))
 assert len(plate_meshes)==10 and set(names.values())==set(plate['parts'])
 settings=json.loads(z.read('Metadata/project_settings.config'));assert settings['wall_loops']=='5' and settings['sparse_infill_density']=='15%' and settings['layer_height']=='0.2'
 assert settings['nozzle_diameter'][0]=='0.4' and 'X2D' in settings['printer_model'] and 'PETG' in settings['filament_type'][0]
views=read(R/'design/assembly-view-presets-validation.json');assert views['passed'] and len(views['views'])==7 and views['source_sha256']==archive_sha
for p in [D/'checks.json',D/'adversarial-checks.json',D/'capture-checks.json',D/'wall-section-checks.json',P/'source.json',P/'slice-checks.json',B/'review-check.json']:
 d=read(p);d.update(source_sha256=archive_sha,geometry_signature_sha256=geo);write(p,d)
report=dict(date='2026-10-06',revision='S20',cad_application='Installed Limo CAD 0.2.2; native replay, exact BRep interference and native application captures',source='Roller-300.nbcad',source_sha256=archive_sha,geometry_signature_sha256=geo,replay_file_sha256=sha(replay),replay_normalized_text_sha256=hashlib.sha256(replay.read_text(encoding='utf-8').encode()).hexdigest(),saved_native_geometry_matches_replay=True,features=2015,feature_errors=0,geometry_checks=sum(len(x['checks']) for x in reports.values()),check_counts={n:len(x['checks']) for n,x in reports.items()},valid_connected_watertight_print_bodies=len(reports['checks.json']['bodies']),native_interference=interference,interference_scope='27 bodies per side; exact reported pairs. Dense threaded REX shaft/screw solids are separately probed in adversarial-checks.json. Expected simplified belt/tooth and spline-envelope overlaps remain; no belt mesh or thread-fit qualification.',print_meshes=hash_rows,bambu_project=str(project.relative_to(R)).replace('\\','/'),bambu_project_sha256=sha(project),bambu_project_meshes_match_current_prints=plate_meshes,individual_warning_free_slices=11,review_plate_warning_free=True,native_named_views=7,physical_test_performed=False,powered_release=False,whole_barrel_release=False,passed=True)
write(D/'validation-summary.json',report)
print(json.dumps({k:report[k] for k in ['passed','features','geometry_checks','valid_connected_watertight_print_bodies','source_sha256']}))
