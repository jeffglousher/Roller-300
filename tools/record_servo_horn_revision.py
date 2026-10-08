"""Record the validated native S19 adapter and current print/BOM provenance."""
from pathlib import Path
import copy,hashlib,json,math,zipfile
R=Path(__file__).resolve().parents[1];DATE='2026-10-06'
OUT=R/'design/servo-horn-adapter-2026-10-06';PRINT=R/'first-prints/servo-horn-fit-2026-10-06';REVIEW=R/'first-prints/bambu-servo-horn-review-2026-10-06'
def read(p):
 data=p.read_bytes()
 try:return json.loads(data.decode('utf-8-sig'))
 except UnicodeDecodeError:return json.loads(data.decode('cp1252'))
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
m=json.loads(zipfile.ZipFile(R/'Roller-300.nbcad').read('model.json'));sha=hashlib.sha256((R/'Roller-300.nbcad').read_bytes()).hexdigest()
assert len(m['document']['history']['features'])==1740
validated=read(R/'.local/s19-servo-horn-model-replayed.json')
assert all(m[k]==validated[k] for k in ['sketches','extrudes','body_features','datum_planes','holes','fillets','chamfers'])
checks=read(OUT/'checks.json');mount=read(OUT/'capture-checks.json');slices=read(PRINT/'slice-checks.json');plate=read(REVIEW/'review-check.json')
assert checks['passed'] and mount['passed'] and slices['passed'] and plate['exit_code']==0
for path in [OUT/'checks.json',OUT/'capture-checks.json',PRINT/'source.json',PRINT/'slice-checks.json',REVIEW/'review-check.json']:
 v=read(path);v['source_sha256']=sha;write(path,v)
stack=read(R/'.local/s19-servo-horn-parts.json')
rev=dict(date=DATE,source='Roller-300.nbcad',source_sha256=sha,features=1740,
 checks='design/servo-horn-adapter-2026-10-06/checks.json',print_candidates='first-prints/servo-horn-fit-2026-10-06',
 physical_test_performed=False,unpowered_coupon_files_ready=True,powered_release=False,horn_adapter_nominal_design_complete=True,
 scope='Unpowered one-drive fit; purchased horn interface defined, physical seating/retention and powered qualification pending',
 validation=dict(connected_valid_watertight_print_bodies=len(checks['bodies']),nominal_clearance_checks=len(checks['checks']),mount_capture_checks=len(mount['checks']),warning_free_individual_slices=len(slices['parts']),warning_free_review_plate_slices=1),
 bambu_review_project='first-prints/bambu-servo-horn-review-2026-10-06/Roller-300-servo-horn-first-fit.3mf',native_named_views=5)
p=read(R/'parameters.json');p.setdefault('historical_s18_native_fit_revision',copy.deepcopy(p['native_fit_revision']));p['native_fit_revision']=rev
p.update(revision='servo-horn-adapter-'+DATE,status='UNPOWERED H25T HORN FIT FILES READY; RECEIVING FITS AND POWERED QUALIFICATION PENDING',servo_horn_revision=rev,servo_horn_attachment=stack)
p['servo']['horn_interface_status']='Nominal CAD interface complete: purchased H25T metal 1906-0025-0032 horn, four M4x6 mounting screws, printed integrated shaft clamp. Low-profile M3 center retention screw required; verify length/seating by hand on receipt. No printed spline.'
p['servo']['drawing_basis']='User supplied INJS035-270 diagram provisionally supplies case/ear geometry for owned INJS035-360; INJORA confirms 25T/5.9 spline and continuous rotation. S19 uses the explicit 37.5 case height, 41.5 total height, 24.7 ear datum and 2.7 ear thickness. Published nominal40.5 table conflicts with diagram heights; unpowered fit tests establish the received geometry.'
p['assembly_parts'].update({'L metal H25T horn':445,'R metal H25T horn':446,'L integrated horn shaft adapter':301,'R integrated horn shaft adapter':309})
p['measurement_gates']=[x for x in p['measurement_gates'] if 'servo' not in x.lower() and 'horn' not in x.lower()]+['Received 25T spline seating, cable clearance and low-profile M3 center-screw engagement; nominal interface defined in CAD']
p['slicer_estimates']=slices['parts'];p['views']={'latest':'design/servo-horn-adapter-2026-10-06/drivetrain-stack-native.png','servo':'design/servo-horn-adapter-2026-10-06/servo-horn-native.png'}
write(R/'parameters.json',p)
t=read(R/'test-record.json');t.update(date=DATE,current_revision=p['revision'],status=p['status'],current_native_fit_revision=rev,servo_horn_revision=rev,current_print_release='11 native print pieces, unpowered one-drive fit. Horn interface designed to purchased H25T metal horn; receiving fit and power tests pending.')
t['pending_physical_fit']=[x for x in t['pending_physical_fit'] if 'servo' not in x.lower() and 'horn' not in x.lower()]+['Received H25T horn seating, cable clearance and low-profile M3 center-screw length without bottoming. Check nominal0.25mm head-to-shaft gap before shaft clamp tightening.']
if 'gates' in t and 'complete_one_side_detail_and_guarding' in t['gates']:t['gates']['complete_one_side_detail_and_guarding']='Unpowered drivetrain CAD complete with purchased H25T horn; receiving fit, full-barrel guarding and powered qualification pending.'
t.setdefault('historical_gates_before_servo_horn',copy.deepcopy(t['gates']))
for key in ['supplier_clutch_data','independent_bidirectional_clutch_calibration','new_clutch_retention_packaging']:t['gates'][key]='RETIRED: rigid belt drive has no mechanical clutch.'
t['gates']['servo_model_and_permissible_envelope']='Nominal owned INJORA360/H25T interface defined from manufacturer spline specification and supplied case drawing; receiving fit and load qualification untested.'
write(R/'test-record.json',t)
s=read(R/'parts-sources.json');s.setdefault('historical_bom_before_servo_horn',copy.deepcopy(s['bom']));s.update(current_packaging_revision='servo-horn-adapter-'+DATE,servo_horn_revision=rev)
rows=s['bom']['rows'];idx={q['id']:q for q in rows}
idx['M11'].update(stage='PRINT FIT',checked=DATE,model='Integrated adapter to metal H25T 1906-0025-0032 horn',notes='Native S19 adapter includes 16mm-square M4 bolt pattern, center pilot clearance, accessible center screw bore and captive M3 shaft pinch nut. Case/ear locations revised together; both input bearings and belt alignment unchanged.')
idx['M01']['notes']='Owned continuous-rotation INJORA for first fit. Published25T/5.9mm spline; native case/ears use supplied drawing. Verify received seating and cable clearance. No external feedback. One additional servo needed for two drives; price retains its recorded offer date.'
idx['M15'].update(checked=DATE,stage='BUY FIT',notes='Official STEP integrated into both drives. Nominal H25T/5.9mm INJORA interface; verify seating and retaining screw by hand. Manufacturer drawing and STEP have differing pilot dimensions: adapter clearance accommodates both.')
idx['P01']['notes']='Native 24T input clamp and rigid48T output pulley, PETG/.4mm. S19 integrated horn clamp replaces former coupling trial; no printed servo spline.'
idx['P06'].update(model='Carrier, roof-open section,4 retainers,servo bridge and integrated horn adapter',checked=DATE,notes='11 connected current print pieces per drive. Shaft clamp and horn mounting flange form one print; wheel separate. S19 servo axial location updated to supplied drawing and vendor horn STEP.')
idx['H23'].update(item='Servo center retention screw',model='M3 low-profile button head, D5.7 x1.65mm; length verified on servo',first_stage_qty=1,vehicle_qty=2,checked=DATE,stage='RECEIVING FIT',supplier='Owned supplied screw / matching M3 hardware',notes='Use a compatible low-profile M3 screw. Supplied screw may be reused if it seats without bottoming and fits the D8.2 adapter bore. Nominal head-to-input-shaft gap0.25mm. Do not guess usable internal gear thread depth.',source='https://www.injora.com/products/injora-injs035-360-35kg-waterproof-digital-servo-360-steering-winch-wheel-for-rc')
new=dict(id='H24',group='Drivetrain',item='Horn-to-adapter mounting screws',model='2802-0004-0006; M4x0.7 button head,6mm',first_stage_qty=4,vehicle_qty=8,owned_qty=0,ordered_qty=0,pack_qty=25,pack_price_usd=2.99,stage='BUY FIT',supplier='ServoCity',source='https://www.servocity.com/2802-series-zinc-plated-steel-button-head-screw-m4-x-0-7mm-6mm-length-25-pack/',checked=DATE,notes='Four per drive,16mm square pattern. D8/depth2.2 head seats; nominal2.5mm thread engagement in metal horn. Bench bolt horn to adapter, retain horn on servo through center bore, then insert and clamp input shaft.')
if 'H24' in idx:idx['H24'].update(new)
else:rows.insert(rows.index(idx['H23'])+1,new)
def subtotal(field,credit=True):return round(sum(math.ceil(max((q.get(field) or 0)-((q.get('owned_qty') or 0)+(q.get('ordered_qty') or 0) if credit else 0),0)/q['pack_qty'])*q['pack_price_usd'] for q in rows if isinstance(q.get('pack_price_usd'),(int,float))),2)
s['bom'].update(priced_first_stage_subtotal_usd=subtotal('first_stage_qty'),priced_vehicle_purchase_subtotal_usd=subtotal('vehicle_qty'),priced_vehicle_purchase_without_owned_credit_usd=subtotal('vehicle_qty',False),sourcing_checked=DATE,sourcing_status='H25T horn and M4x6 screw catalog checked '+DATE+'; other offers retain prior dates. Center screw length and other unpriced hardware require receiving/source checks.')
s.setdefault('historical_other_parts_before_servo_horn',copy.deepcopy(s['other_parts']))
s['other_parts']=[dict(item=q['item'],quantity=q.get('vehicle_qty'),model=q['model'],classification=q['stage'],source=q['source'],action=q['notes']) for q in rows]
unresolved=s['sourcing_revision']['unresolved']
if 'H23' not in unresolved:unresolved.append('H23')
mass=sum(q['grams']*next(x['quantity'] for x in read(PRINT/'source.json')['parts'] if x['name']==q['part']) for q in slices['parts'])
wheel=next(q['grams'] for q in slices['parts'] if q['part']=='left-wheel-axle-vertical')
s['cost_review'].update(date=DATE,priced_first_stage_purchase_usd=subtotal('first_stage_qty'),priced_two_drive_purchase_usd=subtotal('vehicle_qty'),first_stage_print_kg_including_wheel=mass/1000,current_fit_set_grams_including_supports=mass-wheel,current_wheel_slice_grams_including_supports=wheel,print_mass_scope='11 native S19 print pieces with warning-free individual vendor slices, including wheel and integrated horn adapter. Supports included; tread excluded.')
write(R/'parts-sources.json',s)
v=read(R/'design/vendor/servo-horn-1906-0025-0032/source.json');v.update(checked_date_local=DATE,status='INTEGRATED NOMINAL FIT DESIGN; receiving seating/retention untested')
v['manufacturer_step_interface_dimensions_mm']={'disc_mounting_face_y':2.6,'front_pilot_end_y':4.6,'pilot_projection_from_mounting_face':2,'thread_boss_back_y':-.9,'tapped_pattern':'Four M4 holes at11.3137 radius, rotated45deg in assembly','spline_entry_y':0,'spline_depth':3,'front_center_screw_head_seat_y':4.6}
v['dimension_reconciliation']='Drawing indicates2.6mm projection; official STEP gives2.0mm pilot projection from outer mounting face. Adapter recess is2.8mm to clear both. Assembled axial datum follows STEP; verify on receipt.'
v['remaining']=['Physical 25T seating, actual case/ear height variant, center screw length without bottoming and cable clearance','Hand rotation and bearing endplay before any powered qualification'];write(R/'design/vendor/servo-horn-1906-0025-0032/source.json',v)
presets=read(R/'design/assembly-view-presets.json');presets.update(geometry_baseline_sha256=sha,purpose='Mirror of five native saved views, including servo horn detail.',presets=m['views']);write(R/'design/assembly-view-presets.json',presets)
plan=(R/'PLAN.md').read_text()
plan=plan.replace('# Roller-300 — rigid belt drivetrain, 2026-10-05','# Roller-300 — rigid belt drive with H25T horn, 2026-10-06').replace('1,657 native history features','1,740 native history features')
plan=plan.replace('`design/rigid-belt-drive-2026-10-05`','`design/servo-horn-adapter-2026-10-06`')
plan=plan.replace('The final horn interface, full-barrel print and powered operation remain held.','The purchased horn interface is defined in CAD. Received hardware fit, full-barrel print and powered operation remain unqualified.')
plan=plan.replace('servo -> purchased metal horn/final adapter','servo -> purchased metal H25T horn/integrated adapter')
plan=plan.replace('5. Fit input carrier, bearings, shaft clamps, servo and removable bridge. Fit belt at reduced center distance, then adjust and clamp carrier. Verify rotation and screw access. Servo-to-horn-to-adapter connection remains pending.','5. On the bench, bolt the purchased metal horn to the integrated printed adapter with four M4x6 screws. Fit the horn to the servo and retain it with a compatible low-profile M3 center screw through the adapter bore. Verify seating and engagement before inserting the input shaft.\n6. Fit input bearings, pulley, metal collar/shims and shaft to the carrier; clamp the shaft in the adapter and fit the servo/removable bridge. Check hand rotation. Fit belt at reduced center distance, then adjust and clamp the carrier. The entire module moves together.')
start=plan.index('## Servo interface');end=plan.index('## Evidence and print files')
plan=plan[:start]+'''## Servo interface

Use the purchased **goBILDA1906-0025-0032 H25T metal horn**, official STEP imported into both drives (445/446). INJORA confirms diameter5.9/25T for the continuous360 servo; the user-supplied drawing establishes nominal case/ear locations. Do not print a PETG spline.

Adapters301/309 retain the shaft clamp and add an integral horn flange. Four M4x6 button heads use the16mm square tapped pattern; D4.5 bores and D8/depth2.2 head seats. Nominal metal engagement2.5mm. A D14.4/depth2.8 pilot recess accommodates the vendor drawing/STEP envelope. The raised M3 pinch screw is separated from the horn screws, with a captive AF6/depth2.8 nut pocket.

Left servo baseY1.0, explicit case top38.5, nominal spline tip42.5; horn mounting face42.1 and front pilot/retention head seat44.1. A low-profile M3 button head (D5.7,height1.65) ends45.75, leaving nominal0.25mm before the unchanged input shaft starts46. Adapter inner-race land still ends53.8, ahead of the first bearing54. Servo ear/bridge mounts were relocated together; belt plane, both input bearings and purchased50mm shaft remain unchanged.

Install the center screw through the adapter before inserting the independent shaft. Actual M3 screw length must seat without bottoming in the received servo; no internal thread depth is invented. Nominal3mm spline engagement and all small axial margins need an unpowered fit check. The diagram identifies a270 variant and conflicts with its nominal40.5 table; the owned360 version remains the actuator. No further supplied-horn measurements are needed to continue this purchased-horn design.

''' +plan[end:]
start=plan.index('## Evidence and print files');end=plan.index('## Historical mount capture correction')
pg=plate['slice_result']['sliced_plates'];grams=sum(float(f['total_used_g']) for q in pg for f in q['filaments']);seconds=sum(float(q['total_predication']) for q in pg)
plan=plan[:start]+f'''## Evidence and print files

`design/servo-horn-adapter-2026-10-06/checks.json` records22 valid connected watertight print bodies and{len(checks['checks'])} nominal drivetrain checks. The accompanying capture-checks.json passes{len(mount['checks'])} mounting/nut checks. Both mirrored horn solids, tapped centers, pilot/head/shaft clearance, screw access, clamp hardware and carrier travel are checked. These checks do not qualify physical fits or loads.

Current print set: `first-prints/servo-horn-fit-2026-10-06`,11 pieces including the separate wheel. PETG,0.4mm X2D,0.2mm layers,5 walls,15% gyroid. All11 individual slices pass without warnings. Current ten-part review plate: `first-prints/bambu-servo-horn-review-2026-10-06/Roller-300-servo-horn-first-fit.3mf`, approximately{grams:.1f}g /{seconds/3600:.2f}hours. No physical print or purchase was made. Older folders are historical.

Five persistent native Named Views: overall, roof-open one-drive fit, drivetrain stack, output hub detail and servo horn/adapter detail. `design/assembly-view-presets.json` mirrors them; recalling a view changes presentation only.

`BOM.xlsx` and `parts-sources.json` include the purchased horn and four M4x6 screws per drive. Partial priced purchase subtotal:${subtotal('first_stage_qty'):.2f} one drive and${subtotal('vehicle_qty'):.2f} two drives, crediting confirmed ownership. Excludes tax, shipping, filament and unresolved hardware. Input collar/shims, opposing wheel spacer, carrier washers, wheel fasteners and center-screw length still require sourcing or receiving checks. No orders placed.

Current dimensions, evidence hashes and physical gates are recorded in `parameters.json` and `test-record.json`.

''' +plan[end:]
(R/'PLAN.md').write_text(plan)
print(json.dumps({'source_sha256':sha,'geometry_checks':len(checks['checks'])+len(mount['checks']),'print_parts':len(slices['parts']),'priced_one_drive_usd':subtotal('first_stage_qty'),'priced_two_drive_usd':subtotal('vehicle_qty')}))
