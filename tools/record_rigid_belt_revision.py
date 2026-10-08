"""Synchronize current registers and BOM with the validated native S18 model."""
from pathlib import Path
import copy,hashlib,json,math,zipfile
R=Path(__file__).resolve().parents[1]
DATE='2026-10-05'
OUT=R/'design/rigid-belt-drive-2026-10-05'
PRINT=R/'first-prints/rigid-belt-fit-2026-10-05'
REVIEW=R/'first-prints/bambu-rigid-review-2026-10-05'
def read(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
sha=hashlib.sha256((R/'Roller-300.nbcad').read_bytes()).hexdigest()
m=json.loads(zipfile.ZipFile(R/'Roller-300.nbcad').read('model.json'))
assert len(m['document']['history']['features'])==1657
checks=read(OUT/'checks.json');mount=read(OUT/'capture-checks.json');slices=read(PRINT/'slice-checks.json')
assert checks['passed'] and mount['passed'] and slices['passed']
retired=read(R/'.local/s18-rigid-belt-drive-parts.json')['retired clutch bodies']
attachment=read(R/'.local/s18-rigid-belt-drive-parts.json')['output attachment']
for p in [OUT/'checks.json',OUT/'capture-checks.json',PRINT/'source.json',PRINT/'slice-checks.json',REVIEW/'review-check.json']:
    v=read(p);v['source_sha256']=sha;write(p,v)
rev=dict(date=DATE,source='Roller-300.nbcad',source_sha256=sha,features=1657,
    checks='design/rigid-belt-drive-2026-10-05/checks.json',
    print_candidates='first-prints/rigid-belt-fit-2026-10-05',shell_body=32,fit_section_body=373,
    carrier_bodies=[437,440],output_pulley_bodies=[9,26],output_metal_hub_bodies=[387,412],
    bearing_retainer_bodies=[376,377,378,380,381,382,383,384],retired_clutch_bodies=retired,
    physical_test_performed=False,unpowered_coupon_files_ready=True,powered_release=False,
    scope='Unpowered roof-open one-drive fit; final horn, physical fits and powered tests remain pending',
    save_note='Saved through native Limo CAD File/Save. Saved solid feature geometry exactly equals validated native replay.',
    validation=dict(connected_valid_watertight_print_bodies=len(checks['bodies']),
                    nominal_clearance_checks=len(checks['checks']),mount_capture_checks=len(mount['checks']),
                    warning_free_individual_slices=len(slices['parts']),warning_free_review_plate_slices=1),
    bambu_review_project='first-prints/bambu-rigid-review-2026-10-05/Roller-300-rigid-belt-first-fit.3mf',
    native_named_views=4)
p=read(R/'parameters.json')
p['historical_s17_native_fit_revision']=p['native_fit_revision'];p['native_fit_revision']=rev
p['revision']='rigid-belt-drive-'+DATE
p['status']='UNPOWERED RIGID BELT FIT FILES READY; NO TORQUE LIMITER; HORN AND PHYSICAL FITS PENDING'
p['historical_clutch_before_rigid_drive']=p.pop('clutch')
p['rigid_output_attachment']=attachment
p['transmission']['clutch_candidate']=None
p['transmission']['clutch_status']='Retired by user-approved S18 rigid belt drive; no mechanical overload protection'
p['transmission']['output_attachment']='48T printed pulley bolts to metal 8mm Sonic hub with four recessed M4x16 screws'
p['assembly_parts']={k:v for k,v in p['assembly_parts'].items() if 'clutch' not in k.lower()}
p['assembly_parts'].update({'L rigid output pulley':9,'R rigid output pulley':26,
                           'L output shaft metal hub':387,'R output shaft metal hub':412})
p['slicer_estimates']=slices['parts']
p['measurement_gates']=[x for x in p['measurement_gates'] if 'clutch' not in x.lower()]
p['measurement_gates']+=['received output hub pilot/threads and M4x16 engagement',
                         'supervised low-speed powered tests after final horn and physical retention checks']
p['retired_current_prints']+=['clutch-reaction-plate','clutch-pressure-pad','clutch-journal-bush','clutch-output-pulley']
p['views']={'latest':'design/rigid-belt-drive-2026-10-05/drivetrain-stack-native.png',
            'output':'design/rigid-belt-drive-2026-10-05/output-hub-native.png',
            'one_drive':'design/rigid-belt-drive-2026-10-05/one-drive-fit-native.png'}
p['control_upgrade_path']={'actuator_carrier':'Removable supported input module retained',
    'future_requirements':['continuous velocity control','position/speed feedback','documented local current limit or current control',
                           'temperature feedback','communication watchdog'],
    'current_limit':'Owned INJORA has no external torque feedback; speed command does not set a reliable torque ceiling',
    'impact_limit':'Electronic protection cannot prevent the first mechanical impact'}
write(R/'parameters.json',p)
t=read(R/'test-record.json');t['rigid_belt_revision']=rev;t['current_native_fit_revision']=rev
t['historical_pending_physical_fit_before_rigid_drive']=t.get('pending_physical_fit')
t['pending_physical_fit']=['608 bearing seats and free rotation after retainer tightening',
    'Wheel hub abutment, metal collars/spacers and measured endplay without preload',
    'M3/M4 nut loading, screw seats and support removal',
    'Carrier motion, belt installation and measured tension',
    'Purchased output hub pilot, clamp access and four M4x16 screw engagements',
    'Actual servo/horn/cable dimensions and final horn adapter',
    'Supervised low-speed powered qualification; no mechanical torque limiter fitted']
t['physical_test_performed']=False;t['powered_release']=False;write(R/'test-record.json',t)
s=read(R/'parts-sources.json')
s['historical_bom_before_rigid_drive']=copy.deepcopy(s['bom'])
s['current_packaging_revision']='rigid-belt-drive-'+DATE
s['requirements_revision']='user-approved rigid belt drive; future serial-bus current control'
s['obstacle_selection_gate']='No mechanical torque limiter fitted. Actual mass, duty and obstacle loads remain unmeasured; first article is unpowered.'
s['historical_clutch_candidates_before_rigid_drive']=s.pop('clutch_candidates')
s['clutch_candidates']=[]
rows=s['bom']['rows'];index={q['id']:q for q in rows}
for qid in ['M17','M21','H16','H18','H20','H22']:
    q=index[qid];q['stage']='RETIRED CLUTCH';q['vehicle_qty']=q['first_stage_qty']=0
    q['notes']='Retired by approved rigid belt drive on '+DATE+'. No current print or purchase requirement.'
index['M16'].update(item='Rigid output shaft clamping hub',notes='Existing metal Sonic hub moved beside 48T pulley, mounting face |Y|65.25. Four recessed M4x16 screws; nominal6.2mm engagement. Verify pilot, clamp and threads on receipt.')
index['H14'].update(item='Rigid output pulley mounting screws',model='2802-0004-0016; M4x0.7 button head,16mm',
    pack_price_usd=3.79,source='https://www.servocity.com/2802-series-zinc-plated-steel-button-head-screw-m4-x-0-7mm-16mm-length-25-pack/',
    checked=DATE,notes='Four per drive. Replaces M4x8 clutch screws. D8/depth4.7 counterbores; screw seats |Y|75.05; nominal6.2mm metal thread engagement. Bench-assemble before insertion into stationary bearings.',source_status='EXACT CATALOG MATCH; NOMINAL CAD FIT VERIFIED')
index['H15'].update(item='Input pulley/coupler pinch screws',vehicle_qty=4,first_stage_qty=2,
    notes='Two M3x10 pinch screws per drive. Four obsolete journal screws per drive removed. One six-pack covers both drives; plain nuts included in H11/H21.')
index['H11'].update(vehicle_qty=48,first_stage_qty=24,
    notes='24 per drive: retainers16 + pinch2 + provisional servo ears4 + upper bridge2. Included in H21; old journal nuts removed. Verify received AF/height against printed pockets.')
index['H21']['notes']='One kit charged once: M3x25 bridge bolts plus plain nuts H11. Kit also contains unused longer sizes; no M3x35 clutch adjusters required.'
index['P01']['notes']='Current 24T input clamp trial and rigid 48T output pulley. PETG/.4mm; no clutch sleeve or journal. Final horn interface remains separate.'
index['P06'].update(model='Carrier, roof-open section,4 retainers,servo bridge and clamp trial',
    notes='Current S18 native exports:11 connected print pieces including separately listed wheel and two pulleys. Four clutch print pieces per drive retired; no pressure pads or journal bush.')
index['S04'].update(item='Future wheel motion readers and targets',notes='Deferred control development. One wheel encoder per side can support speed control; traction estimation also needs vehicle-motion information.')
index['S05'].update(item='Mechanical clutch slip comparison readers',stage='RETIRED CLUTCH',vehicle_qty=0,first_stage_qty=0,
    notes='Separate before/after-clutch reader pair is unnecessary with rigid belt drive. Future bus-actuator feedback is evaluated with the controller upgrade.')
def subtotal(field,credit=True):
    return round(sum(math.ceil(max((q.get(field) or 0)-((q.get('owned_qty') or 0)+(q.get('ordered_qty') or 0) if credit else 0),0)/q['pack_qty'])*q['pack_price_usd'] for q in rows if isinstance(q.get('pack_price_usd'),(int,float))),2)
s['bom'].update(scope='Rigid belt drivetrain; clutch retired; barrel and powered electronics deferred',
    priced_first_stage_subtotal_usd=subtotal('first_stage_qty'),priced_vehicle_purchase_subtotal_usd=subtotal('vehicle_qty'),
    priced_vehicle_purchase_without_owned_credit_usd=subtotal('vehicle_qty',False),sourcing_checked=DATE,
    sourcing_status='Retained sources keep their prior check dates; M4x16 checked '+DATE+'. Physical fit and remaining retention sources pending.')
s['historical_other_parts_before_rigid_drive']=s['other_parts']
s['other_parts']=[dict(item=q['item'],quantity=q['vehicle_qty'],model=q['model'],classification=q['stage'],source=q.get('source'),action=q['notes'])
                  for q in rows if (q.get('vehicle_qty') or 0)>0 and q['group'] not in ['Electronics','Sensors']]
s['historical_cost_review_before_rigid_drive']=copy.deepcopy(s['cost_review'])
cost=s['cost_review'];cost.update(date=DATE,one_drive_priced_purchase_usd=subtotal('first_stage_qty'),
    two_drive_priced_purchase_usd=subtotal('vehicle_qty'),two_drive_priced_purchase_without_owned_credit_usd=subtotal('vehicle_qty',False),
    current_fit_set_grams_including_supports=sum(q['grams'] for q in slices['parts'] if q['part']!='left-wheel-axle-vertical'),
    current_wheel_slice_grams_including_supports=next(q['grams'] for q in slices['parts'] if q['part']=='left-wheel-axle-vertical'),
    first_stage_print_kg_including_wheel=sum(q['grams'] for q in slices['parts'])/1000,
    print_mass_scope='11 current native print pieces including wheel, fresh warning-free individual X2D PETG slices. Supports included; final horn and tread excluded.',
    complete_vehicle_unpriced_rows=[q['id'] for q in rows if (q.get('vehicle_qty') or 0)>0 and q.get('pack_price_usd') is None and q['stage']!='OWNED'],
    unknown_vehicle_quantity_rows=[q['id'] for q in rows if q.get('vehicle_qty') is None])
for rec in cost['recommendations']:
    if 'spring' in rec['action'] or 'clutch' in rec['action']:
        rec.update(action='Retire mechanical clutch and validate rigid belt drive; preserve removable actuator carrier for future current-controlled bus actuator.',status='Implemented in native S18; physical and powered tests pending.')
s['sourcing_revision']['unresolved']=[qid for qid in s['sourcing_revision']['unresolved'] if index[qid]['stage']!='RETIRED CLUTCH']
s['rigid_belt_revision']=dict(date=DATE,source_sha256=sha,retired_purchase_rows=['M17','M21','H16','H18','H20','H22','S05'],
    new_screw_source=index['H14']['source'],new_screw_pack_price_usd=3.79,purchases_made=False)
write(R/'parts-sources.json',s)
views=read(R/'.local/s18-named-views.json')
write(R/'design/assembly-view-presets.json',dict(schema_version=2,source_model='Roller-300.nbcad',geometry_baseline_sha256=sha,
    native_named_views_supported=True,purpose='Mirror of four persistent native CAD named views; no geometry or occurrence pose changes.',
    apply_sequence=['Open canonical model in native CAD','Recall saved Named View by its exact name'],presets=views))
print(json.dumps(dict(source_sha256=sha,first_stage_usd=subtotal('first_stage_qty'),two_drive_usd=subtotal('vehicle_qty'),
    print_grams=sum(q['grams'] for q in slices['parts']),print_pieces=11)))
