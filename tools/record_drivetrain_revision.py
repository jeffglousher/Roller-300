"""Synchronize manufacturing records with verified native CAD and slice evidence."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
REV='drivetrain-fit-2026-10-03'
CAD=ROOT/'Roller-300.nbcad'
with zipfile.ZipFile(CAD) as z:model=json.loads(z.read('model.json'))
replay=json.loads((ROOT/'.local/s15-carrier-model-replayed.json').read_text())
geometry=['document','sketches','extrudes','revolves','sweeps','lofts','ribs','fillets','chamfers','holes','datum_planes','body_features']
assert all(model[k]==replay[k] for k in geometry), 'Saved CAD differs from validated native replay'
sha=hashlib.sha256(CAD.read_bytes()).hexdigest()
folder=ROOT/'design/drivetrain-revision-2026-10-03'
checks=json.loads((folder/'checks.json').read_text());assert checks['passed']
checks.update(source='Roller-300.nbcad',source_sha256=sha,saved_native_geometry_matches_validated_replay=True)
(folder/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
prints=ROOT/'first-prints'/REV
manifest=json.loads((prints/'source.json').read_text())
slices=json.loads((prints/'slice-checks.json').read_text())
assert manifest['source_sha256']==sha and slices['source_sha256']==sha and slices['passed']
assert len(slices['parts'])==len(manifest['parts'])==13
for row in slices['parts']:
    part=next(p for p in manifest['parts'] if p['name']==row['part'])
    assert row['native_mesh_sha256']==part['native_mesh_sha256']
parts=json.loads((ROOT/'.local/s15-carrier-parts.json').read_text())
parts.update({'L wheel shaft':1,'L mouth608':2,'L wheel collar':3,'L wheel metal hub':4,
    'L input608 pair':5,'L input shaft':6,'L input24T pulley':10,'L belt':11,'L servo case':12,
    'L wheel':13,'L tyre allowance':14,'L wheel3mm shim':224,'L shaft clamp trial':301,
    'L central608':357,'L servo bridge':367,'L input collar':369,'L input1p7mm shim':370,
    'L mouth retainer':376,'L inboard input retainer':377,'L outboard input retainer':378,'L center retainer':383,
    'R wheel shaft':18,'R mouth608':19,'R wheel collar':20,'R wheel metal hub':21,
    'R input608 pair':22,'R input shaft':23,'R input24T pulley':27,'R belt':28,'R servo case':29,
    'R wheel':30,'R tyre allowance':31,'R wheel3mm shim':227,'R shaft clamp trial':309,
    'R central608':358,'R servo bridge':368,'R input collar':371,'R input1p7mm shim':372,
    'R mouth retainer':380,'R inboard input retainer':381,'R outboard input retainer':382,'R center retainer':384})
current=dict(date='2026-10-03',source='Roller-300.nbcad',source_sha256=sha,
             features=len(model['document']['history']['features']),checks=str(folder.relative_to(ROOT)/'checks.json'),
             print_candidates=str(prints.relative_to(ROOT)),shell_body=32,fit_section_body=373,
             carrier_bodies=[437,440],pressure_pad_bodies=[391,442,416,443],
             bearing_retainer_bodies=[376,377,378,380,381,382,383,384],
             physical_test_performed=False,unpowered_coupon_files_ready=True,
             scope='Unpowered roof-open one-drive fit; horn interface, whole vehicle and powered release held',
             save_note='Saved through native CAD File/Save; saved feature geometry exactly matches the validated native engine replay.',
             validation=dict(connected_valid_watertight_print_bodies=len(checks['bodies']),
                             nominal_clearance_checks=len(checks['checks']),warning_free_offline_slices=13))
p=json.loads((ROOT/'parameters.json').read_text())
historical_keys=['native_fit_revision','assembly_parts','caps','native_stage_map','native_naming',
                 'mass_ledger','slicer_estimates','views','wheel_retention','input_cap_travel_detail',
                 'clearance_corrections','known_motion_clearance_bounds']
if p['revision']!=REV:
    p['historical_pre_drivetrain_revision']={k:p.pop(k) for k in historical_keys if k in p}
p.update(revision=REV,status='UNPOWERED ROOF-OPEN FIT FILES READY; HORN AND PHYSICAL FITS PENDING; WHOLE VEHICLE/POWERED HOLD',
         native_fit_revision=current,assembly_parts=parts,caps=current['bearing_retainer_bodies'],
         slicer_estimates=slices['parts'],views=dict(latest='design/drivetrain-revision-2026-10-03/latest-native.png',
                                                   one_drive='design/drivetrain-revision-2026-10-03/left-drive-native.png',
                                                   top='design/drivetrain-revision-2026-10-03/left-drive-top-native.png'))
p['bearings'].update(wheel_centers_y=[-101.5,-11.5,11.5,101.5],wheel_span_each=90,wheel_bearings_per_shaft=2,
    wheel_additional_center_bearings_abs_y=[],
    input_axial_retention='Coupler inner-race land; 6 mm metal collar at89.7..95.7 and1.7 mm metal shim at88..89.7. Nominal cap gap0.2, shaft-end reserve0.3; physical engagement/endplay required.',
    axial_seat_note='Two stationary wheel bearings per shaft at|Y|8..15 and98..105. No wheel-mounted608. Input seats54..61 and81..88 move together with servo/carrier. Existing outer-race shoulders and removable retainers remain.')
p['wheel_retention']=dict(bearings_y_left_mm=[[8,15],[98,105]],shaft_y_left_mm=[8,158],
    inboard_collar_y_left_mm=[85.8,94.8],inboard_metal_spacer_y_left_mm=[94.8,97.8],
    opposing_metal_spacer_y_left_mm=[105,113],opposing_spacer_id_od_length_mm=[8,11,8],
    nominal_endplay_mm=.2,retired_rotating_bearing_and_caps=True,
    physical_gate='Verify received wheel hub has the modeled rear abutment face at113; set measured endplay without bearing preload.')
p['input_stop'].update(left_collar_y_mm=[89.7,95.7],left_inner_race_shims_y_mm=[88,89.7],
                       nominal_cap_gap_mm=.2,nominal_shaft_end_reserve_mm=.3)
p['transmission'].update(available_translation_x=[-2,1],slot_corner_radius=0,
    travel_status='Native clearance checks pass at five positions. Three M4x14 mounts per carrier, washer9x4.3x0.8, M4 AF7/3.2 nut. Belt tension/stretch still requires physical setting.',
    clutch_candidate='Purchased goBILDA1309-0016-0008 metal shaft hub; bolted reaction plate and two radially inserted pressure pads; four spring guide/adjuster screws.',
    clutch_status='Torque path and assembly geometry modeled; physical grip, liner behavior, spring calibration and slip torque HOLD.',
    carriage_mounts_xy_left_mm=[[32.5,12],[60,50],[30.5,79]],carrier_bodies=[437,440])
p['clutch']=dict(hub='goBILDA1309-0016-0008',source='https://www.gobilda.com/1309-series-sonic-hub-8mm-bore/',
    reaction_plate_od_mm=57.5,reaction_plate_y_left_mm=[28.3,32.3],
    rotor_y_left_mm=[32.8,34.8],pressure_pads_y_left_mm=[35.3,38.3],pressure_split_gap_mm=.4,
    pressure_pads_per_drive=2,guide_pcd_mm=48,adjuster='4 x M3x35 ISO4762 + captive M3 nyloc',
    reaction_mount='4 x M4x8 ISO7380-1; nominal thread engagement6.2 mm in purchased hub',
    journal_mount='4 x M3x10 + captive M3 nuts; rear removable flange',
    spring='4 x goBILDA2916-0001-0002; free25 mm, modeled18 mm; minimum guide length16 mm',
    spring_source='https://www.gobilda.com/compression-spring-6mm-id-x-8mm-od-2-3kg-max-load-16-25mm-length-2-pack/',
    maximum_installed_length_mm=18,minimum_installed_length_mm=16,
    spring_guide='Metal OD5, ID3.2, length16 mm; procurement/sample pending',
    liner='Trial0.5 mm front annulus44x27.4; rear two half sheets44x33.4. Supplier/bonding/compressed thickness pending.',
    journal='PETG trial OD26.5/ID8.2,32.8..79.75; friction/wear not qualified',
    release='Unpowered assembly only; no calibrated torque claim')
p['servo']['horn_interface_status']='HOLD: metal horn retained by servo center screw; adapter separately bolted to horn. Actual hole spacing, boss diameter/height and usable screw engagement unknown. No printed PETG spline. Final axial stack may require cradle/coupler revision.'
p['retired_current_prints']=['outer-wheel-bearing-coupon','wheel-bearing-retainer','closed clutch-pressure-plate']
p['whole_frame_service_access']='Existing upper guard blocks the rear carrier straight driver. Roof-open test fixture passes; resolve access in later barrel work before whole-frame printing.'
(ROOT/'parameters.json').write_text(json.dumps(p,indent=2)+'\n')
t=json.loads((ROOT/'test-record.json').read_text())
if t['current_revision']!=REV:
    t['historical_previous_native_fit']=t.get('current_native_fit')
    t['historical_previous_slice_estimates']=t.get('slice_estimates')
t.update(date='2026-10-03',current_revision=REV,status=p['status'],current_native_fit=current,
         slice_estimates=slices['parts'],unpowered_coupon_files_ready=True,
         current_print_release='13 mesh candidates/offline slices for unpowered roof-open fit only; 2 copies of pressure pad. Final horn adapter, whole frame and powered use held.')
t['fit_hardware'].pop('wheel_outer_cap',None)
t['fit_hardware'].update(input_stop='8x25x6 metal collar at89.7..95.7; 1.7 mm metal inner-race shims',
                         wheel_opposing_stop='8x11x8 metal spacer; verify actual wheel hub abutment',
                         carrier='3 M4x14 + 9x4.3x0.8 washers + AF7/height3.2 M4 nuts; outer nut loads from inner side port',
                         clutch=p['clutch'])
t['pending_physical_fit']=['Bearing seats and free rotation after cap tightening; metal inner-race contacts',
    'Metal wheel hub abutment, collar full engagement and measured endplay',
    'M3/M4 nut insertion, screw head seating and driver access; support removal',
    'Carrier motion under clamp loosening; belt installation and measured tension',
    'Radial pressure-pad installation, even spring lengths16..18, actual liner stack',
    'Servo/horn/grommet/cable measurements and final horn-adapter axial stack',
    'Clutch grip/slip calibration, journal friction/wear and load tests before powered operation']
t['historical_records_note']='Older packaging, stage and slice entries are historical. current_native_fit and parameters.revision are the active drivetrain evidence; no physical test or print has been performed.'
(ROOT/'test-record.json').write_text(json.dumps(t,indent=2)+'\n')
print(json.dumps(current))
