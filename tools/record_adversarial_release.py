"""Record current S20 dimensions, assembly sequence and validated file provenance."""
from pathlib import Path
import copy,json,zipfile
R=Path(__file__).resolve().parents[1];D=R/'design/adversarial-review-2026-10-06';P=R/'first-prints/adversarial-fit-2026-10-06';B=R/'first-prints/bambu-adversarial-review-2026-10-06';DATE='2026-10-06'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
proof=read(D/'validation-summary.json');assert proof['passed'];sha=proof['source_sha256']
model=json.loads(zipfile.ZipFile(R/'Roller-300.nbcad').read('model.json'));slices=read(P/'slice-checks.json');plate=read(B/'review-check.json')['slice_result']['sliced_plates'][0]
rev=dict(date=DATE,revision='S20',source='Roller-300.nbcad',source_sha256=sha,features=2015,checks='design/adversarial-review-2026-10-06/validation-summary.json',print_candidates='first-prints/adversarial-fit-2026-10-06',physical_test_performed=False,unpowered_coupon_files_ready=True,powered_release=False,whole_barrel_release=False,horn_adapter_nominal_design_complete=True,positive_rex_input=True,scope='Unpowered one-drive roof-open receiving, fit and assembly test. PETG /0.4mm X2D. Powered loads, belt tooth fit and complete barrel service remain open.',validation=dict(connected_valid_watertight_print_bodies=22,nominal_geometry_checks=496,drivetrain_checks=255,adversarial_assembly_checks=109,mount_capture_checks=122,wall_section_checks=10,warning_free_individual_slices=11,warning_free_review_plate_slices=1),bambu_review_project='first-prints/bambu-adversarial-review-2026-10-06/Roller-300-REX-first-fit.3mf',native_named_views=7,save_note='Native CAD File/Save; saved solid geometry exactly equals validated native replay. Seven recalled views preserve geometry.')
pending=['Received608 fit and free rotation after retainer tightening; remove supports without damaging seats','Received H25T spline/pilot seating and low-profile M3 center-screw length; seat without bottoming, nominal head-to-shaft gap1.25mm (conservative vendor STEP0.883mm)','PETG AF7.3 keyed bores on actual REX shaft; clip insertion, pocket fit and retention by hand','Input shaft nominal0.2mm endplay and pulley nominal0.4mm play; stops act on bearing inner races, no bearing preload','Received M3/M4 nuts, screws and driver access; bridge pan-head envelope and four servo ear mounts','Output hub pilot, clamp access, four M4x16 engagements and wheel hub rear abutment; stock6+2mm stop and measured wheel endplay','Carrier motion, belt installation, tooth seating, flange tracking and measured tension','Actual servo boot/cable clearance and full-barrel rear carrier screw access before any full-frame release','Supervised powered torque, reversal, shock and temperature qualification after electrical limits/cutoff established; no mechanical torque limiter']
p=read(R/'parameters.json')
archive_keys=['revision','status','native_fit_revision','assembly_parts','slicer_estimates','views','wheel_retention','input_stop','servo_horn_revision','servo_horn_attachment','shafts','bearings','transmission','servo','measurement_gates','hardware_envelopes']
p.setdefault('historical_s19_before_adversarial',copy.deepcopy({k:p[k] for k in archive_keys if k in p}))
p.update(revision='adversarial-review-'+DATE,status='S20 UNPOWERED ONE-DRIVE FIT FILES READY; RECEIVING FITS AND POWERED QUALIFICATION PENDING',native_fit_revision=rev,adversarial_revision=rev,servo_horn_revision=rev)
p['shafts'].update(input_y_left=[46.5,94.5],input_shaft_stock='2106-4008-0480; stainless8mm REX x48mm, factory Eclip and M4 tapped ends',right='Purchased threaded input/horn references rotate180deg about Z, preserving thread handedness. Printed parts mirror in XZ; wheel shafts remain independent.',retention='Uncut smooth150mm wheel shafts use metal clamp hub/collar stops. Stock48mm REX input uses factory Eclip and M4 end screw; no fabricated shaft grooves or threads.')
p['bearings']['input_axial_retention']='Factory Eclip Y49.8..50.5 in adapter pocket49.5..50.7; rear6mm metal spacer88..94,0.5mm shim94..94.5,1.5mm washer94.5..96 and M4x8 end screw. Nominal shaft play0.2mm; integral pulley inner-race lands61.2..80.8 leave0.4mm total pulley play. Receiving fit/endplay required.'
p['transmission'].update(input_pulley_main_y_left_mm=[62.75,79.5],input_pulley_land_y_left_mm=[61.2,80.8],input_pulley_total_nominal_endplay_mm=.4,input_key_bore_af_mm=7.3,position_note='Belt remains Y68..77; output pulley65.25..79.75. Input bearings54..61 and81..88. Positive AF7.3 keyed adapter and pulley fit nominal D8/AF7 REX. Integral R5.5 lands stop on inner races; rear main flange clearance0.5mm nominal and0.3mm at permitted axial travel.')
p['servo'].update(drawing_case_height_mm=37.5,base_y_left_mm=.5,case_front_y_left_mm=38,spline_tip_y_left_mm=42,ear_y_left_mm=[25.2,27.9],drawing_basis='User supplied INJS035-270 diagram provisionally supplies case/ears for owned INJS035-360; published25T/5.9 spline confirmed. Explicit37.5mm case/41.5mm total heights and24.7mm ear datum used. Nominal40.5mm table conflicts with diagram; physical unpowered fit establishes received geometry. S20 shared datum movement corrected once.',horn_interface_status='Purchased1906-0025-0032 metal H25T horn, fourM4x6 screws and printed positive REX adapter. No printed servo spline. Low-profile M3 center retention length selected on received servo.',ear_fastener_status='Four M3x10 ear screws into AF6 x2.8mm captured-nut pockets. Upper bridge uses twoM3x16 pan screws and side-loaded AF6 pockets atZ128.7..131.5. Nominal drawing slots modeled; actual grommet/eyelet fit untested.')
p['hardware_envelopes']['servo'].update(status='S20 nominal case/ears from supplied drawing plus actual purchased horn STEP. Shared datum corrected. Received360 servo, cable boot and fastener fits remain unmeasured.',case_drawing_height_mm=37.5)
p['input_stop']=dict(stock_shaft='2106-4008-0480',factory_clip_y_left_mm=[49.8,50.5],adapter_clip_pocket_y_left_mm=[49.5,50.7],input_shaft_y_left_mm=[46.5,94.5],rear_spacer=dict(model='1522-0010-0060',nominal_id_od_length_mm=[8,10,6],y_left_mm=[88,94]),rear_shim=dict(model='2807-0811-0500',id_od_thickness_mm=[8,11,.5],y_left_mm=[94,94.5]),rear_washer=dict(model='2801-0004-0011',nominal_id_od_thickness_mm=[4,11,1.5],y_left_mm=[94.5,96]),end_screw=dict(model='2802-0004-0008',thread='M4x0.7',length_mm=8,nominal_engagement_mm=6.5),nominal_shaft_endplay_mm=.2,nominal_pulley_endplay_mm=.4,status='Actual stock STEP in native CAD; positive axial stops checked. No purchased or physical-fit claim.')
p['wheel_retention'].update(opposing_spacer_id_od_length_mm=[8,10,8],opposing_spacer_stock_components=[dict(model='1522-0010-0060',y_left_mm=[105,111]),dict(model='1522-0010-0020',y_left_mm=[111,113])])
p['servo_horn_attachment']['horn_fasteners']['head_seat_y_mm']=45.1
p['servo_horn_attachment']['nominal_axial_stack_left_mm'].update(servo_base=.5,case_top=38,spline_tip=42,horn_thread_boss_back=38.1,horn_spline_entry=39,horn_face=41.6,horn_pilot_end=43.6,center_head_seat=43.6,input_shaft_start=46.5,adapter_race_land_end=53.8,first_bearing_start=54,center_head_to_shaft_nominal_gap=1.25,center_head_to_vendor_STEP_conservative_gap=.883)
p['servo_horn_attachment'].update(input_key_bore_af_mm=7.3,input_retention='Factory Eclip and rear stock retention; pinch clamps retired')
a=p['assembly_parts']
for k in list(a):
 if any(x in k for x in ['input collar','input1p7mm shim','shaft clamp trial','mouth opposing metal spacer']):a.pop(k)
a.update({'L input shaft':447,'R input shaft':448,'L positive horn REX adapter':301,'R positive horn REX adapter':309,'L input rear6mm spacer':449,'R input rear6mm spacer':450,'L input rear0p5mm shim':451,'R input rear0p5mm shim':452,'L input end washer':453,'R input end washer':454,'L input end M4x8 screw':455,'R input end M4x8 screw':456,'L output6mm spacer':457,'R output6mm spacer':458,'L output2mm spacer':459,'R output2mm spacer':460,'retired smooth input/collar/shim/spacer body IDs':[6,23,369,370,371,372,385,386],'input moving bodies L':[437,5,10,12,301,367,377,378,445,447,449,451,453,455],'input moving bodies R':[440,22,27,29,309,368,381,382,446,448,450,452,454,456]})
p['slicer_estimates']=slices['parts'];p['views']=dict(latest='design/adversarial-review-2026-10-06/drivetrain-stack-native.png',servo='design/adversarial-review-2026-10-06/servo-mounts-native.png',input_section='design/adversarial-review-2026-10-06/rex-stack-section-native.png',servo_section='design/adversarial-review-2026-10-06/servo-captures-section-native.png',native_named_view_names=[v['name'] for v in model['views']])
p['measurement_gates']=list(dict.fromkeys([g for g in p.get('measurement_gates',[]) if not any(x in g.lower() for x in ['613g','shaft/bearing/retainer','25t spline','m4x16'])]+pending))
write(R/'parameters.json',p)
t=read(R/'test-record.json')
for k in ['current_native_fit','current_CAD_checks','drive_article','drive_end_section','fit_hardware','cad_evidence','cad_observations','new_cad_checks','slice_estimates','transmission_check']:
 if k in t:t.setdefault('historical_s19_'+k,copy.deepcopy(t.pop(k)))
t.setdefault('historical_s19_native_fit_revision',copy.deepcopy(t['current_native_fit_revision']));t.setdefault('historical_gates_before_adversarial',copy.deepcopy(t['gates']))
t.update(date=DATE,current_revision=p['revision'],status=p['status'],current_native_fit_revision=rev,current_native_fit=rev,current_CAD_checks=rev,servo_horn_revision=rev,adversarial_revision=rev,cad_evidence=rev['checks'],current_print_release='S20 eleven native pieces ready for unpowered one-drive roof-open fit, PETG /0.4mm X2D. Received hardware/PETG fits required. No print sent or physical test performed.',slice_estimates=slices['parts'],pending_physical_fit=pending,physical_test_performed=False,powered_release=False,fit_hardware='Current parts-sources.json BOM rows and PLAN.md stack; no hardware purchased.')
t['gates'].update(complete_one_side_detail_and_guarding='S20 exact nominal CAD assembly checks pass; receiving fit, full-barrel guarding/service and powered qualification remain open.',printer_slicer_footprint='Current11 native parts and ten-part Bambu review plate pass without warnings; finalproject meshes verified against current native STL exports.',obstacle_normal_torque_and_limiter_selection='No mechanical limiter in S20. Mass, obstacle load and powered torque/reversal/shock tests remain open.',cost_comparison='Current partial one/two-drive priced purchase subtotals in BOM.xlsx; whole-robot parts, tax, shipping, filament and unresolved hardware excluded.',transmission_choice='Rigid24T/48T2:1 belt drive; positive REX input, metal Sonic output hub. No clutch. Physical tooth fit, tension, loads and acoustics remain open.',normal_shock_envelope='UNTESTED: belt isolates some compliance but is not an overload release. Establish actual impulse/load/duty before powered qualification.')
write(R/'test-record.json',t)
sources=read(R/'parts-sources.json');sources['adversarial_revision'].update(rev);sources['servo_horn_revision']=rev;write(R/'parts-sources.json',sources)
small_g=plate['filaments'][0]['total_used_g'];hours=plate['total_predication']/3600;wheel=next(q for q in slices['parts'] if q['part']=='left-wheel-axle-vertical');cost=sources['bom']
old_plan=(R/'PLAN.md').read_text(encoding='utf-8');tail=old_plan[old_plan.index('## Historical mount capture correction'):];tail=tail.replace('current evidence is in the S18 folder above.','current evidence is in `design/adversarial-review-2026-10-06`.')
plan=f'''# Roller-300 — positive REX belt drivetrain, {DATE}

Canonical model: `Roller-300.nbcad`, S20, 2,015 native history features. Saved through installed Limo CAD0.2.2 File/Save. Saved geometry exactly matches the validated native replay. Native exports, exact interference results, assembly probes and application captures are in `design/adversarial-review-2026-10-06`. S19 is preserved in `.local/before-s20-adversarial.nbcad.bak`.

Scope: **unpowered, roof-open, one-drive fit and assembly test**, PETG,0.4mm nozzle on the X2D. Eleven print pieces are ready for this physical test. No physical print, purchase or powered test has occurred. Full barrel and powered operation remain deferred.

## Adversarial corrections

- Restored shared servo/bridge datums once. Repeated datum moves had put servo ears and bridge restraints inside the servo and placed vertical bridge bores outside the bridge.
- Rounded bridge posts and fitted two side-loaded M3 captures. Four servo ear screws now also use captured nuts. Lower pad support and through-driver passages remove the former base obstruction.
- Removed both input pinch joints. The24T pulley's5mm hub could not enclose its M3 nut reliably, and the adapter's rotating pinch ear touched the carrier.
- Replaced the smooth input shaft/custom thin collar/1.7mm shim with stock48mm REX shaft, factory Eclip and catalog rear retention. Positive AF7.3 bores put the torque connection in the printed parts.
- Added integral pulley inner-race lands. A keyed bore alone did not stop axial pulley movement. Lands give0.4mm total nominal play and stop further movement at the bearing inner races.
- Replaced the unsourced8mm output stop with stock6+2mm metal spacers. Purchased horn, REX shaft and threaded end screw on the right use rotation to preserve handedness.

## Input shaft, horn and axial retention

Purchased horn: goBILDA1906-0025-0032 H25T metal servo hub, native manufacturer STEP. INJORA specifies25T/5.9mm for the owned continuous360 servo. The supplied drawing dimensions the case/ears and labels a270 variant. Its explicit37.5mm case height is used provisionally; the40.5mm table conflicts with the diagram. Received360 geometry still needs a fit check.

Left nominal positions in mm:

- Servo baseY0.5, case front38.0, spline tip42.0, ear thickness25.2..27.9.
- Horn spline entry39.0, mounting face41.6, pilot/center-screw head seat43.6. Four M4x6 heads seat at45.1, with2.5mm nominal metal engagement. Pattern16mm square, adapter D14.4/depth2.8 pilot clearance.
- A nominal low-profile M3 center head D5.7 x1.65 ends at45.25. Nominal REX starts46.5:1.25mm gap,0.883mm conservative gap to the imported shaft STEP's thread overshoot. Select actual center-screw length to seat without bottoming. Install it before inserting the input shaft.
- Stock2106-4008-0480 REX shaft spans46.5..94.5, with M4 tapped ends and factory Eclip49.8..50.5. Adapter pocket49.5..50.7 has a radial insertion window. Adapter and pulley have AF7.3 bores for nominal D8/AF7 stock.
- Input608 bearings54..61 and81..88; adapter race land ends53.8. Pulley R5.5 lands extend61.2..80.8, leaving0.4mm total nominal pulley play. Main rear flange ends79.5,0.5mm from stationary housing nominally and0.3mm at allowed travel.
- Rear stock6mm spacer88..94,0.5mm shim94..94.5,1.5mm washer94.5..96, and M4x8 button screw into the shaft end. Nominal screw engagement6.5mm. Rear metal stack and Eclip pocket give0.2mm nominal shaft travel. Check measured endplay/free rotation; do not preload bearing outer races.

The Eclip is a spring part: remove it before sliding the shaft through bearings/pulley, then install it through the adapter's window with its opening facing the shaft. Native probes verify printed access, not clip spring force or fatigue.

## Servo captures and carrier

Each servo uses four M3x10 ear screws. Lower AF6/depth2.8 nut pockets load from the front before installing the servo; upper bridge nuts load from the back. Two vertical M3x16 pan-head bridge screws seat atZ143.25 and terminate127.25. Bridge nuts side-load through extended ports intoZ128.7..131.5 pockets. Nominal M3 nuts are AF5.5/height2.4. Hex flats resist rotation, and installed screws prevent sideways escape. Loose nuts are not snap-retained.

Rounded OD10 posts atX34.1723 and65.1723,Y21.7 support the removable bridge. Lower nut pads have solid backing; lower bolt/head/driver corridors clear the carrier base. A0.95mm local upper nut-pocket lip is backed by4.2mm solid axial material. This revision qualifies nominal fit, not powered plastic joint strength.

Servo, horn, bearings, shaft, pulley and rear retention move together on carriers437/440. Guide keys constrain transverse movement. TravelX-2..+1mm about nominal24/48T center distance49.6723mm permits belt installation/adjustment; it does not prescribe belt stretch or tension.

Three M4x14 carrier screws per drive use9x4.3x0.8mm washers and AF7/height3.2 M4 nuts. Left fixed centers:(32.5,12),(60,50),(30.5,79). Outer nut loads horizontally through its side port; the other nuts load from below with carrier removed. Captures and driver access pass for the roof-open section373. The full-frame rear straight driver remains obstructed by the upper guard; resolve during barrel work.

## Output support and rigid belt

Uncut smooth8x150mm wheel shaft spansY8..158. Two stationary608 bearings at8..15 and98..105 provide90mm center span. Outer races seat against printed shoulders and removable retainers. The redundant rotating wheel bearing is retired.

Wheel axial stops: metal collar85.8..94.8 and3mm inner-race spacer94.8..97.8, opposed by stock1522-0010-0060 spacer105..111 plus1522-0010-0020 spacer111..113 against the wheel hub. Total8mm, nominal D10/ID8. Wheel endplay0.2mm is a receiving setting. Verify the hub's actual rear abutment and free rotation before tightening.

The48T printed output pulley remainsY65.25..79.75,14.5mm long,8.4mm shaft clearance. Purchased1309-0016-0008 Sonic hub mounting face65.25, D14 pilot to67.25; pulley pilot recessD14.2/depth2.2. Four M4x16 button screws use16mm square pattern, D4.5 bores, D8/depth4.7 recesses. Head seat75.05 leaves9.8mm plastic to the hub face and6.2mm nominal metal thread engagement. Bolt hub/pulley together on the bench; rear bearing obstructs installed straight screwdriver access. Tighten shaft clamp with input carrier removed.

Torque path: servo, metal horn, printed positive REX adapter, supported keyed input shaft,24T pulley,210-3M-09 belt, rigid48T pulley, metal Sonic hub, wheel shaft, metal wheel hub and printed wheel. Ratio2:1; belt bandY68..77. Mechanical clutch and all friction/spring/adjuster hardware are retired. No mechanical torque limiter is fitted; a toothed belt is not a calibrated overload release. Powered loads, reversal/shock and temperatures remain unqualified.

## Unpowered assembly order

1. Check small keyed bores, nut captures, head seats and bearing seats with received hardware. Remove supports carefully. Confirm servo center-screw seating before the larger fixture/wheel prints.
2. Load fixed-frame M4 nuts, fit stationary wheel bearings/retainers and leave input carrier out.
3. Bench-bolt48T pulley to Sonic hub with four M4x16 screws; verify pilot/engagement. Place loose belt around the pulley.
4. Lower hub/pulley into roof-open section. Thread wheel shaft through both bearings and hub, placing collar and stock spacers as above. Tighten hub clamp with carrier removed; check hand rotation and measured wheel endplay.
5. Bench-bolt metal horn to positive REX adapter with four M4x6 screws. Fit it to servo and install low-profile center screw through adapter bore. Verify seating and shaft clearance.
6. Load four servo ear nuts and two bridge nuts. Fit servo/bridge to carrier with four M3x10 and two M3x16 screws. Fit input bearings/retainers and loose keyed pulley between them.
7. Remove factory Eclip, slide REX shaft through rear bearing, pulley, front bearing and adapter. Reinstall clip through radial window. Fit rear6mm spacer,0.5mm shim, washer and M4x8 end screw. Check hand rotation, shaft/pulley endplay and inner-race contacts.
8. Offer carrier into frame at reduced center distance, fit belt, then move/clamp carrier with three M4x14 screws/washers. Confirm free hand rotation, tooth seating and flange tracking. Record actual fits; no powered test in this article.

## Evidence, printing and purchasing

`design/adversarial-review-2026-10-06/validation-summary.json`:496 nominal geometry/assembly checks,22 valid connected watertight print bodies, seven persistent native Named Views and0 history errors. Native exact interference checked27 selected bodies per side. Only simplified belt/tooth and nominal servo-spline reference overlaps remain. Dense threaded REX/screw solids were inspected separately with exported native geometry probes; no manufactured spline/thread/belt mesh qualification is claimed.

Native export preflight contains layout warnings because bodies are in assembly positions. It is not the print arrangement. The actual eleven rigidly placed print meshes and ten-part Bambu project were checked separately; every project mesh matches its current native export within0.00005mm after translation.

Print set: `first-prints/adversarial-fit-2026-10-06`,11 pieces including separate wheel. Current ten-part project: `first-prints/bambu-adversarial-review-2026-10-06/Roller-300-REX-first-fit.3mf`, approximately{small_g:.1f}g /{hours:.2f}h. All eleven individual slices and the combined plate pass without warnings: X2D, PETG,0.4mm,0.2mm layers,5 walls,15% gyroid. Wheel remains approximately{wheel['grams']:.1f}g /{wheel['seconds']/3600:.2f}h. Check small hardware fits before spending that material. No print sent.

Seven native Named Views: overall, roof-open fit, drivetrain stack, output hub, horn/adapter, servo captures and positive REX input. `design/assembly-view-presets.json` mirrors them; view recalls preserve solid geometry. The additional `Roller-300-review-cutaway.nbcad` is inspection only: its removed half-sections must never be printed.

`BOM.xlsx` and `parts-sources.json` contain current stock retention and fasteners. Partial priced purchase subtotals:${cost['priced_first_stage_subtotal_usd']:.2f} first drive /${cost['priced_vehicle_purchase_subtotal_usd']:.2f} two drives, crediting confirmed ownership. Excludes tax, shipping, filament, unresolved hardware and final electronics. Exact carrier washer source, wheel fasteners and center-screw length remain receiving/sourcing checks. Other catalog offers retain their original check dates. No orders placed.

Current dimensions, provenance and physical gates are in `parameters.json` and `test-record.json`. Older print/model folders and records are historical.

'''
(R/'PLAN.md').write_text(plan+tail,encoding='utf-8')
(R/'README.md').write_text('''# Roller-300

Two-wheel indoor roller under mechanical development. Current S20 work is the simplified rigid belt drivetrain, ready for an **unpowered one-drive roof-open fit test** using PETG /0.4mm on the X2D. Received hardware fits and powered loads remain untested; the full barrel is deferred.

- [Roller-300.nbcad](Roller-300.nbcad): current native CAD model,2,015 features and seven assembly Named Views.
- [Adversarial review](design/adversarial-review-2026-10-06/README.md): corrected defects, native images and validation scope.
- [PLAN.md](PLAN.md): current dimensions, retention and assembly order.
- [Bambu first-fit project](first-prints/bambu-adversarial-review-2026-10-06/Roller-300-REX-first-fit.3mf): ten smaller pieces. The wheel is a separate print.
- [Print set](first-prints/adversarial-fit-2026-10-06/README.md): all eleven pieces and individual slicer checks.
- [BOM.xlsx](BOM.xlsx) and [parts-sources.json](parts-sources.json): current purchase workbook and source record.
- [parameters.json](parameters.json) and [test-record.json](test-record.json): current nominal values, evidence and pending physical tests.

Geometry is authored/replayed and rendered by the installed native CAD application. STEP-based inspection probes and rigid print placement support validation. No print, powered test or purchase has been made. Historical chapter files and previous print folders are retained for reference.

The public repository is https://github.com/jeffglousher/Roller-300. No hardware/source license has been assigned; linked third-party material retains its own terms.
''',encoding='utf-8')
(D/'README.md').write_text('''# S20 adversarial drivetrain review

S20 corrects assembly defects in the prior nominal model and prepares an unpowered PETG one-drive fit article. [Current model](../../Roller-300.nbcad) and [assembly instructions](../../PLAN.md) are authoritative. No physical validation or powered release is claimed.

## Defects corrected

The earlier shared servo and bridge datums had moved repeatedly. The reference servo ears were12mm from their intended position, bridge bores missed the bridge, and restraints intersected the servo. Native overlap volumes included72.9mm³ with the roof-open fixture,307.8mm³ with its carrier and353.27mm³ with its bridge. Datums/reference ears are now coherent and stationary clearances pass at tested carrier travel.

The bridge lacked valid captures at its actual mounting points. S20 adds rounded posts, side-loaded bridge nuts, four captured ear nuts and lower driver passages. Nut seating, insertion and resistance to rotation are tested against the native solids. Loose nuts require a screw for captivity; a snap fit is not claimed.

The adapter's rotating pinch ear touched its carrier. The24T pulley's5mm clamp hub also could not enclose a conventional M3 nut. Both friction clamps are removed. A stock48mm REX shaft drives AF7.3 printed bores, with factory Eclip and stock rear retention. This simplifies assembly and avoids a fabricated thin collar and1.7mm shim stack.

A positive keyed bore needed a separate axial stop. Integral R5.5 pulley lands now locate it between bearing inner races, leaving0.4mm nominal total play. The shaft uses the Eclip pocket and rear metal stack for0.2mm nominal travel. Native probes verify permitted movement and interference beyond the stops. This establishes nominal geometry, not wear/load capacity.

The output8mm stop now uses stock6+2mm spacers. Right purchased threaded references use rotation, preserving right-hand thread geometry. Printed parts retain their intended mirror geometry.

## Native CAD images

![One-drive stack](drivetrain-stack-native.png)

![REX axial half-section](rex-stack-section-native.png)

![Servo captured-nut section](servo-captures-section-native.png)

All images are native application captures. [Review cutaway model](Roller-300-review-cutaway.nbcad) removes material only for inspection. **Do not print the cutaway.** The canonical model keeps intact parts. These sections show the left drive; subsequent correction of right stock-reference orientation did not change the pictured left geometry.

## Verification and limits

- [Validation summary](validation-summary.json):496 nominal checks,22 valid connected watertight print bodies,2,015 native features with0 errors, seven recalled Named Views preserving geometry.
- [Drivetrain geometry](checks.json):255 checks, including rotating clearances, travel, horn/hub screw positions and current axial dimensions.
- [Assembly probes](adversarial-checks.json):109 checks of actual stock REX/clip geometry, positive torque engagement, axial stops, nut loading/rotation and driver access on both drives.
- [Existing capture checks](capture-checks.json):122 checks of bearing retainers, carrier captures and trimmed envelope roots.
- [Wall sections](wall-section-checks.json):10 continuous-material gauges. Torque lands and horn rims are approximately1.285mm nominal minimum. One upper servo-nut pocket has a0.95mm local lip backed by4.2mm solid axial material; strength remains a physical qualification.
- [Left native interference](left-roof-open-native-interference.json) and [right native interference](right-full-frame-native-interference.json):27 selected bodies each. The only reported volume overlaps are the coarse belt envelope against its two pulleys and the nominal smooth servo spline against the actual25T horn spline. These references cannot qualify physical tooth/spline fit. Dense threaded REX/screw solids are excluded from this broad sweep and checked separately by the assembly probes. Thread fit and belt meshing remain receiving tests.
- Every native STL matches the current print manifest and slice-check hash. The final Bambu project's ten meshes are compared directly to current print STL triangle coordinates. All11 individual slices and the combined plate pass without warnings. Native preflight assembly-layout warnings are superseded by the separate verified print placements.

Actual PETG bearing/key/nut fit, factory Eclip installation, center-screw length, hardware seating, endplay and belt tracking must be recorded during unpowered assembly. Full-barrel rear screw service access remains obstructed by the upper guard and is deferred with barrel work. Powered shock, torque, heat and reversal loads are untested; the belt provides no calibrated torque limiting.
''',encoding='utf-8')
(P/'README.md').write_text('''# S20 one-drive unpowered fit prints

Current native exports for PETG /0.4mm X2D:11 connected pieces,0.2mm layers,5 walls,15% gyroid. `source.json` records native-body and archive hashes; `slice-checks.json` records warning-free individual Bambu slices. Placement applies rigid rotation/translation only.

Use [the ten-part Bambu project](../bambu-adversarial-review-2026-10-06/Roller-300-REX-first-fit.3mf) for smaller parts. `left-wheel-axle-vertical.stl` is separate and costs approximately609g /15.74h in this profile; verify the small hardware fits first.

Parts: roof-open fit section, sliding carrier,48T output pulley, upper servo bridge, positive REX horn adapter,24T keyed pulley, mouth retainer, two input retainers, center retainer and wheel. Do not use old clamp/collar print files or the inspection cutaway. No physical print or test has occurred.

See [PLAN.md](../../PLAN.md) for ordered assembly and [BOM.xlsx](../../BOM.xlsx) for hardware. Physical fits/endplay and powered/full-barrel qualification remain pending.
''',encoding='utf-8')
(B/'README.md').write_text(f'''# S20 Bambu first-fit review

Open `Roller-300-REX-first-fit.3mf` in Bambu Studio. Ten smaller pieces are arranged for X2D /0.4mm /Generic PETG,0.2mm layers,5 walls,15% gyroid. Offline native Bambu slice passes without warnings, approximately{small_g:.1f}g /{hours:.2f}h. The final project meshes match current native export/print meshes. No print sent.

The wheel is separate in [the eleven-piece print set](../adversarial-fit-2026-10-06/README.md). Check small hardware fits before that609g print. Assembly order and retention are in [PLAN.md](../../PLAN.md).
''',encoding='utf-8')
design=R/'design/README.md';text=design.read_text(encoding='utf-8')
if '## Current S20 drivetrain' not in text:
 text=text.replace('# design/\n','# design/\n\n## Current S20 drivetrain\n\n[Adversarial review](adversarial-review-2026-10-06/README.md) contains the current native captures, exact interference and geometry checks. [Canonical CAD](../Roller-300.nbcad) and [PLAN.md](../PLAN.md) define the current assembly. The chapter files below are historical baselines and do not regenerate S20.\n')
 design.write_text(text,encoding='utf-8')
print(json.dumps(dict(revision=rev['revision'],features=rev['features'],checks=rev['validation']['nominal_geometry_checks'],review_plate_grams=small_g,review_plate_hours=hours,records='synchronized')))
