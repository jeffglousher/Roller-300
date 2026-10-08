"""Reconcile the saved S21 native CAD with unchanged fit projects and review records.

Run only after native File/Save of the validated S21 candidate. This records
inspection results; it neither authors geometry nor submits a physical print.
"""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import zipfile

R = Path(__file__).resolve().parents[1]
D = R/'design/chassis-fit-review-2026-10-07'
E = D/'s21-access'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, value):
    p.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')

canonical = R/'Roller-300.nbcad'
native = read(E/'native-replay-export.json')
assert native['feature_count'] == 2033 and not native['feature_errors']
exact = read(E/'exact-fit-inspection.json')
assert exact['all_checks_passed'], 'Native correction fit checks failed'
model = json.loads(zipfile.ZipFile(canonical).read('model.json'))
candidate = E/'native-replay.nbcad'
with zipfile.ZipFile(candidate) as z:
    replay = json.loads(z.read('model.json'))
keys = ['sketches','extrudes','body_features','datum_planes','revolves',
        'sweeps','lofts','ribs','holes','fillets','chamfers']
assert all(model[k] == replay[k] for k in keys), 'Saved geometry differs from native replay'
assert len(model['document']['history']['features']) == 2033
assert not [f for f in model['document']['history']['features']
            if not f['suppressed'] and f['status']['state'] != 'ok']
assert all(next(f for f in model['document']['history']['features'] if f['id']==i)['suppressed']
           for i in [291,302,315,347,375,405,437,450])
source_sha = sha(canonical)
selected_path = R/'first-prints/chassis-fit-2026-10-07/selected-wheel.json'
selected = read(selected_path)
wheel_project = R/selected['selected_project']
wheel_check_path = wheel_project.parent/'wheel-slice-check.json'
wheel_check = read(wheel_check_path)
assert sha(wheel_project) == selected['selected_project_sha256'] == wheel_check['project_sha256']
assert sha(E/'body-13.stl') == selected['native_stl_sha256'] == wheel_check['native_stl_sha256']
assert sha(candidate) == selected['native_source_project_sha256'] == wheel_check['native_source_project_sha256']
with zipfile.ZipFile(candidate) as z:
    candidate_model = json.loads(z.read('model.json'))
assert all(model[k] == candidate_model[k] for k in keys)
with zipfile.ZipFile(wheel_project) as z:
    assert z.testzip() is None
    assert hashlib.md5(z.read('Metadata/plate_1.gcode')).hexdigest().upper() == z.read('Metadata/plate_1.gcode.md5').decode().strip().upper()
    settings = json.loads(z.read('Metadata/project_settings.config'))
    expected = wheel_check['settings_preservation']['process_values']
    assert all(settings[k] == value for k, value in expected.items())
assert wheel_check['native_triangle_connectivity_preserved']
assert wheel_check['slice_result']['sliced_plates'][0]['warning_message'] == ''
reconciliation = dict(canonical_project='Roller-300.nbcad', canonical_project_sha256=source_sha,
    candidate_project=str(candidate.relative_to(R)).replace('\\','/'),
    candidate_project_sha256=sha(candidate), native_geometry_arrays_match=True,
    source_geometry_changed_by_native_save=False,
    note='Wheel was sliced from the explicit native replay candidate. The saved canonical has identical geometry; file hashes differ because of save metadata.')
selected['canonical_native_save_reconciliation'] = reconciliation
write(selected_path, selected)
wheel_check['canonical_native_save_reconciliation'] = reconciliation
write(wheel_check_path, wheel_check)
wheel_estimate = dict(project=selected['selected_project'], grams=selected['grams'],
    time_seconds=selected['seconds'], pose='outboard_face_down',
    source_stl_sha256=selected['native_stl_sha256'], settings_verified=True,
    release='HOLD until receiving/carrier fits pass; unpowered fit candidate',
    canonical_source_geometry_verified=True)
write(D/'wheel-project-validation.json', dict(date='2026-10-07', passed=True,
    selected_project=selected['selected_project'], project_sha256=sha(wheel_project),
    native_stl_sha256=sha(E/'body-13.stl'), reconciliation=reconciliation,
    slice_check=str(wheel_check_path.relative_to(R)).replace('\\','/'),
    native_triangle_connectivity_preserved=True, gcode_md5_valid=True,
    process_settings_verified=True, physical_print=False, powered_release=False))
manifest = read(R/'first-prints/adversarial-fit-2026-10-06/source.json')
parts = []
for p in manifest['parts']:
    if p['body_id'] == 13:
        continue
    src = E/f"body-{p['body_id']}.stl"
    assert sha(src) == p['native_mesh_sha256']
    shutil.copy2(src, D/src.name)
    parts.append(dict(body_id=p['body_id'], name=p['name'], sha256=sha(src),
                      current_native_mesh_matches_print=True))
assert len(parts) == 10
fresh = dict(date='2026-10-07', source_sha256=source_sha, features=2033,
             feature_errors=[], native_geometry_changed=True,
             native_change_scope='Shell rear driver bores and open-face wheels only',
             current_fit_project_geometry_changed=False, parts=parts,
             changed_wheel_bodies=[13,30], changed_shell_body=32,
             native_replay_export='s21-access/native-replay-export.json', passed=True)
write(D/'fresh-native-replay.json', fresh)
revision = dict(date='2026-10-07', revision='S21', source='Roller-300.nbcad',
                source_sha256=source_sha, features=2033, feature_errors=0,
                checks='design/chassis-fit-review-2026-10-07/validation-summary.json',
                native_geometry_matches_saved_replay=True,
                inherited_drivetrain_review='design/adversarial-review-2026-10-06/validation-summary.json',
                unchanged_current_fit_print_bodies=10,
                wheel_cap_minimum_gap_at_axial_extreme_mm=23.8,
                wheel_shell_minimum_gap_at_axial_extreme_mm=28.3,
                whole_chassis_fit_released=False, powered_release=False,
                wheel_print_estimate=wheel_estimate)
for name in ['parameters.json','test-record.json']:
    p = read(R/name)
    previous = {k:copy.deepcopy(p[k]) for k in ['revision','current_revision',
                'native_fit_revision','current_native_fit_revision','current_native_fit',
                'current_CAD_checks','print_decision','status'] if k in p}
    p.setdefault('historical_s20_before_chassis_access',previous)
    p.update(status='S21 SMALL FIT GATE READY; OPEN-FACE WHEEL FIT CANDIDATE; FULL CHASSIS FIT INCOMPLETE',
             current_print_decision='design/chassis-fit-review-2026-10-07/README.md',
             current_native_mesh_evidence='design/chassis-fit-review-2026-10-07',
             chassis_access_revision=revision,
             print_release_note='Five small interfaces first, then carrier roof/bearing trial. Existing three fit projects retain their exact native meshes. Old closed wheels are superseded; use the separately sliced S21 open-face wheel after hardware fits. Full chassis/hatch/electronics fit is incomplete.')
    if name == 'parameters.json':
        p.update(revision='chassis-fit-review-2026-10-07',native_fit_revision=revision)
        p['body'].update(actual_wheel_width_mm=300, actual_uncut_shaft_width_mm=316,
                         bare_wheel_diameter_mm=230, bare_wheel_belly_clearance_mm=35,
                         tread_envelope_belly_clearance_mm=43,
                         width_target_qualified=False)
        p['chassis_fit_review'].update(current_revision=revision,
            corrected_native_interfaces=['Rear carrier straight driver service bores D4.4',
                                         'Open wheel faces D216; hub web/rim retained'],
            historical_hatch_reactivation_result='FAIL: hatch/shell overlap1334.910mm3 plus new retainer/carrier overlaps; remains inactive')
    else:
        p.update(date='2026-10-07', current_revision='chassis-fit-review-2026-10-07',
                 current_native_fit_revision=revision,current_native_fit=revision,current_CAD_checks=revision,
                 current_print_release=p['print_release_note'],
                 physical_test_performed=False,powered_release=False)
        p['gates'].update(complete_one_side_detail_and_guarding='S21 service bores and open wheel faces validated nominally. Full hatch/electronics fit remains incomplete.',
                         printer_slicer_footprint='Three existing fit projects rechecked against10 unchanged S21 native meshes. Closed S20 wheel projects superseded; fresh open-face wheel slice verified against saved canonical geometry.',
                         whole_vehicle_trials='NOT RELEASED: inactive colliding historical hatch, inactive/unmeasured electronics and316mm hardware width')
    if 'print_decision' in p:
        decision=copy.deepcopy(p['print_decision'])
        decision.update(date='2026-10-07',source_sha256=source_sha,features=2033,
                        fresh_native_exports_matching_prints=10,
                        native_geometry_changed=True,current_fit_project_geometry_changed=False,
                        compatibility_evidence='design/chassis-fit-review-2026-10-07/print-project-validation.json',
                        wheel_status='S21 open-face wheel slice verified at336.71g/8h38m; S20 closed-wheel slice superseded; receiving/carrier fits must pass first')
        p['print_decision']=decision
    write(R/name,p)
sources=read(R/'parts-sources.json')
sources.setdefault('chassis_access_revision', {}).update(revision)
write(R/'parts-sources.json',sources)
summary=dict(**revision,review_completed=True,passed=True,
             passed_scope='Saved native replay and unchanged10 current fit meshes; whole chassis remains incomplete',
             cad_executable_sha256=native['cad_executable_sha256'],
             fixes=['Two D4.4 carrier driver service bores','Both wheel faces opened insideR108'],
             remaining=['Historical hatch reactivation collides','Electronics/optics/plug restraints inactive and unmeasured',
                        'Actual316mm shaft width exceeds300mm target','PETG/hardware receiving fits not performed'],
             physical_print=False)
write(D/'validation-summary.json',summary)
print(json.dumps(dict(saved_source_sha256=source_sha,features=2033,unchanged_fit_meshes=10,passed=True)))
