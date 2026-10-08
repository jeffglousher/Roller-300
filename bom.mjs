import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=process.env.BOM_ROOT || path.dirname(fileURLToPath(import.meta.url));
const record=JSON.parse(await fs.readFile(path.join(root,'parts-sources.json'),'utf8'));
const rows=record.bom.rows;
const wb=Workbook.create();const sh=wb.worksheets.add('BOM');
sh.showGridLines=false;
const last=9+rows.length;
sh.getRange(`A1:Q${last+12}`).format.font={name:'Arial',size:10,color:'#203444'};
sh.mergeCells('A1:O1');sh.getRange('A1').values=[['ROLLER-300  |  FIRST INDOOR BUILD']];
sh.getRange('A1:O1').format={fill:'#203F4B',font:{name:'Arial',size:20,bold:true,color:'#FFFFFF'},rowHeight:38};
sh.mergeCells('A2:O2');
sh.getRange('A2').values=[[(record.chassis_access_revision || record.chassis_fit_revision) ? 'S21 chassis fit / positive REX belt | PETG / 0.4 mm X2D | Unpowered ONE-drive fit; received hardware seating and endplay checks remain.' : 'S20 positive REX input / rigid belt | PETG / 0.4 mm X2D | Unpowered ONE-drive fit; received hardware seating and endplay checks remain.']];
sh.getRange('A2:O2').format={fill:'#DFECEC',rowHeight:29,font:{name:'Arial',size:11,color:'#203F4B'}};
sh.mergeCells('A3:D3');sh.getRange('A3').values=[['PRICED FIRST-PURCHASE SUBTOTAL']];
sh.getRange('E3').formulas=[[`=SUM(K10:K${last})`]];
sh.getRange('E3').setNumberFormat('$0.00');
sh.mergeCells('F3:O3');sh.getRange('F3').values=[['USD; partial subtotal excludes tax, shipping, filament and unresolved items. Included-kit rows are charged in H21.']];
sh.getRange('A3:O3').format.rowHeight=28;
sh.getRange('A3:E3').format.fill='#D8EDE4';sh.getRange('E3').format.font={bold:true,size:16,color:'#1D5A44'};
for(const [row,txt] of [[4,'Blue cells are editable quantities/prices. Vehicle quantities are planning counts; blank means unresolved. Owned quantities not confirmed remain blank.'],[5,'Buy qty = max(first-stage target − owned − already ordered, 0). Pack count rounds up. Enter confirmed purchases in Owned / Ordered.'],[6,'Canonical record: parts-sources.json. Return workbook edits there before regeneration. Sources and sizing/hold reasons are alongside each row.'],[7,'Priority: reusable wheel support / servo → rigid belt fit → front sensors / cameras → battery, Pixracer, Pi and retained harness.']]){
 sh.mergeCells(`A${row}:O${row}`);sh.getRange(`A${row}`).values=[[txt]];sh.getRange(`A${row}:O${row}`).format.rowHeight=24;
}
sh.mergeCells('A8:D8');sh.getRange('A8').values=[['PRICED TWO-DRIVE PURCHASE SUBTOTAL']];
sh.getRange('E8').formulas=[[`=SUM(Q10:Q${last})`]];sh.getRange('E8').setNumberFormat('$0.00');
sh.mergeCells('F8:Q8');sh.getRange('F8').values=[['Credits confirmed owned/ordered quantities. Includes one additional servo; unpriced parts, prints and final electronics excluded.']];
sh.getRange('A8:Q8').format={rowHeight:30,fill:'#DFECEC'};
sh.getRange('E8').format.font={bold:true,size:16,color:'#1D5A44'};
sh.getRange('A9:Q9').values=[['ID','Part / exact model','Stage','Vehicle qty','First target','Owned','Ordered','Buy qty','Pack qty','Pack USD','Buy USD','Source','Checked','Reason / sizing / purchase gate','Group','Vehicle buy qty','Vehicle buy USD']];
sh.getRange(`A10:Q${last}`).values=rows.map(q=>[q.id,`${q.item}\n${q.model}`,q.stage,q.vehicle_qty,q.first_stage_qty,q.owned_qty,q.ordered_qty,null,q.pack_qty,q.pack_price_usd,null,q.source,q.checked,q.notes,q.group,null,null]);
sh.getRange(`H10:H${last}`).formulas=rows.map((q,i)=>[`=IF(E${i+10}=0,0,MAX(E${i+10}-F${i+10}-G${i+10},0))`]);
sh.getRange(`K10:K${last}`).formulas=rows.map((q,i)=>[`=IF(H${i+10}=0,0,IF(ISNUMBER(J${i+10}),ROUNDUP(H${i+10}/I${i+10},0)*J${i+10},""))`]);
sh.getRange(`P10:P${last}`).formulas=rows.map((q,i)=>[`=IF(ISNUMBER(D${i+10}),MAX(D${i+10}-F${i+10}-G${i+10},0),"")`]);
sh.getRange(`Q10:Q${last}`).formulas=rows.map((q,i)=>[`=IF(ISNUMBER(P${i+10}),IF(P${i+10}=0,0,IF(ISNUMBER(J${i+10}),ROUNDUP(P${i+10}/I${i+10},0)*J${i+10},"")),"")`]);
const table=sh.tables.add(`A9:Q${last}`,true,'RollerBOM');table.showFilterButton=true;
sh.getRange(`A9:Q9`).format={fill:'#203F4B',font:{bold:true,color:'#FFFFFF'},rowHeight:31,wrapText:true};
sh.getRange(`A10:Q${last}`).format={rowHeight:66,wrapText:true,verticalAlignment:'center'};
for(const [col,width] of Object.entries({A:7,B:43,C:17,D:10,E:10,F:9,G:10,H:9,I:9,J:12,K:12,L:37,M:13,N:66,O:15,P:13,Q:14}))sh.getRange(`${col}1:${col}${last+12}`).format.columnWidth=width;
sh.getRange(`P10:P${last}`).setNumberFormat('0;[Red](0);"-"');
sh.getRange(`Q10:Q${last}`).setNumberFormat('$0.00;[Red]($0.00);"-"');
sh.getRange(`D10:J${last}`).format.font.color='#2166B1';
sh.getRange(`D10:I${last}`).setNumberFormat('0;[Red](0);–');
sh.getRange(`J10:K${last}`).setNumberFormat('$0.00;[Red]($0.00);–');
sh.getRange(`L10:L${last}`).format.font={size:9,color:'#287277'};
sh.getRange(`M10:M${last}`).format.font.size=9;
sh.getRange(`C10:C${last}`).conditionalFormats.add('containsText',{text:'HOLD',format:{fill:'#FCE3C9',font:{color:'#865422',bold:true}}});
sh.getRange(`C10:C${last}`).conditionalFormats.add('containsText',{text:'BUY',format:{fill:'#D8EDE4',font:{color:'#1D5A44',bold:true}}});
sh.getRange(`C10:C${last}`).conditionalFormats.add('containsText',{text:'OWNED',format:{fill:'#E4ECF3'}});
sh.getRange(`E10:G${last}`).dataValidation={rule:{type:'whole',operator:'between',formula1:0,formula2:1000}};
// Keep the existing layout while updating the active build/supplier instructions.
for(const [row,txt] of [[4,'Blue cells are editable quantities/prices. Blank Owned means unconfirmed; quantities are conservative shopping needs, not orders.'],[5,'Buy qty = max(first target - owned - ordered, 0); packs round up. H21 covers H11 nuts. Retired clutch and input clamp rows have zero target quantities.'],[6,'Source URLs are beside each row. Exact catalog sourcing does not qualify physical fit. Historical supplier references remain on retired/deferred rows.'],[7,'ServoCity mechanics + Amazon belt/M3 kit. H08:16 M3x12 bearing screws/drive. H27:4 M3x10 servo-ear screws/drive; source/price check remains.']])sh.getRange(`A${row}`).values=[[txt]];
sh.getRange(`D10:I${last}`).setNumberFormat('0;[Red](0);"-"');
sh.getRange(`J10:K${last}`).setNumberFormat('$0.00;[Red]($0.00);"-"');
const newRow=10+rows.findIndex(q=>q.id==='P06');sh.getRange(`A${newRow}:O${newRow}`).format.rowHeight=100;
const earRow=10+rows.findIndex(q=>q.id==='H27');sh.getRange(`A${earRow}:Q${earRow}`).format.rowHeight=120;
const cost=record.cost_review;
const footer=last+2;
sh.mergeCells(`A${footer}:Q${footer}`);sh.getRange(`A${footer}`).values=[['PRINT MATERIAL ESTIMATE | ONE UNPOWERED DRIVE | CONSUMED MATERIAL, NOT SPOOL PURCHASE COST']];
sh.getRange(`A${footer}:Q${footer}`).format={fill:'#203F4B',font:{bold:true,color:'#FFFFFF'},rowHeight:28};
for(const [offset,label,value] of [[1,'Reference ten-part fit plate incl. supports (kg)',cost.current_fit_set_grams_including_supports/1000],[2,'Current native wheel slice incl. supports (kg)',cost.current_wheel_slice_grams_including_supports/1000],[3,'Filament USD/kg - editable assumption',cost.filament_usd_per_kg_assumption],[4,'Estimated consumed material USD',null]]){
 sh.mergeCells(`A${footer+offset}:D${footer+offset}`);sh.getRange(`A${footer+offset}`).values=[[label]];
 sh.getRange(`E${footer+offset}`).values=[[value]];sh.getRange(`A${footer+offset}:Q${footer+offset}`).format.rowHeight=27;
}
sh.getRange(`E${footer+1}:E${footer+2}`).setNumberFormat('0.000');
sh.getRange(`E${footer+3}:E${footer+4}`).setNumberFormat('$0.00');sh.getRange(`E${footer+3}`).format.font.color='#2166B1';
sh.getRange(`E${footer+4}`).formulas=[[`=SUM(E${footer+1}:E${footer+2})*E${footer+3}`]];
for(const [offset,note] of [[1,'Corrected complete one-drive plate reference. Remove already-printed fit pieces before arranging and reslicing the remaining parts.'],[2,'Current native wheel exported by CAD, placed rigidly and sliced offline in Bambu Studio.'],[3,'$25/kg is a budgeting assumption, not a supplier quote. Own filament is not credited here.'],[4,'Excludes tread, calibration waste, failed prints and electricity. Actual staged support mass depends on final plate layout.']]){
 sh.mergeCells(`F${footer+offset}:Q${footer+offset}`);sh.getRange(`F${footer+offset}`).values=[[note]];
}
for(const [offset,note] of [[6,'FULL ROBOT TOTAL REMAINS UNRESOLVED: partial two-drive subtotal is not a complete vehicle quote.'],[7,'Unresolved: carrier washers, wheel fasteners, servo-ear M3x10 source/price, center-screw length and final tread. Shaft retention uses stock parts.'],[8,'Thermal camera and four ToF modules owned; visible camera, wheel feedback, wiring, power protection and charging hardware remain deferred.'],[9,'Rigid belt drive has no mechanical torque limiter. Verify received horn seating, screw engagement and shaft retention before supervised powered tests.']]){
 sh.mergeCells(`A${footer+offset}:Q${footer+offset}`);sh.getRange(`A${footer+offset}`).values=[[note]];sh.getRange(`A${footer+offset}:Q${footer+offset}`).format.rowHeight=25;
}
sh.freezePanes.freezeRows(9);sh.freezePanes.freezeColumns(2);
wb.recalculate();
const before=Number(sh.getRange('E3').values[0][0]);
const expected=rows.reduce((sum,q)=>sum+(typeof q.pack_price_usd==='number'?Math.ceil(Math.max(q.first_stage_qty-(q.owned_qty||0)-(q.ordered_qty||0),0)/q.pack_qty)*q.pack_price_usd:0),0);
if(Math.abs(before-expected)>0.005)throw Error(`Subtotal ${before} != independent sum ${expected}`);
if(Math.abs(before-record.bom.priced_first_stage_subtotal_usd)>0.005)throw Error('Canonical subtotal mismatch');
const vehicle=Number(sh.getRange('E8').values[0][0]);
const vehicleExpected=rows.reduce((sum,q)=>sum+(typeof q.pack_price_usd==='number'?Math.ceil(Math.max((q.vehicle_qty||0)-(q.owned_qty||0)-(q.ordered_qty||0),0)/q.pack_qty)*q.pack_price_usd:0),0);
if(Math.abs(vehicle-vehicleExpected)>0.005||Math.abs(vehicle-record.bom.priced_vehicle_purchase_subtotal_usd)>0.005)throw Error('Vehicle purchase subtotal mismatch');
const material=Number(sh.getRange(`E${footer+4}`).values[0][0]);
if(Math.abs(material-cost.first_stage_print_kg_including_wheel*cost.filament_usd_per_kg_assumption)>0.005)throw Error('Material subtotal mismatch');
// Meaningful edit check: receiving one belt removes exactly its cost.
const belt=rows.find(q=>q.id==='M03');const beltRow=10+rows.findIndex(q=>q.id==='M03');
sh.getRange(`F${beltRow}`).values=[[(belt.owned_qty||0)+1]];wb.recalculate();
const after=Number(sh.getRange('E3').values[0][0]);
if(Math.abs(before-after-belt.pack_price_usd)>0.005)throw Error('Owned quantity did not reduce purchase subtotal');
sh.getRange(`F${beltRow}`).values=[[belt.owned_qty]];wb.recalculate();
for(const id of ['M04']){
 const q=rows.find(r=>r.id===id);const row=10+rows.indexOf(q);
 if(Number(sh.getRange(`K${row}`).values[0][0])!==7.98)throw Error(`Two-pack rounding failed: ${id}`);
}
for(const id of ['M01','M09','M13','M14','M17','M21','H10','H11','H15','H16','H18','H20','H22']){
 const row=10+rows.findIndex(r=>r.id===id);const cost=sh.getRange(`K${row}`).values[0][0];
 if(cost!==0&&cost!==''&&cost!==null)throw Error(`Owned/retired/included row charged twice: ${id}`);
}
const bearingScrew=rows.find(q=>q.id==='H08');const earScrew=rows.find(q=>q.id==='H27');
if(bearingScrew.first_stage_qty!==16||bearingScrew.vehicle_qty!==32||earScrew.first_stage_qty!==4||earScrew.vehicle_qty!==8||earScrew.pack_price_usd!==null)throw Error('Active bearing/servo-ear screw separation failed');
const inspect=await wb.inspect({kind:'region',sheetId:'BOM',range:'D9:K16',maxChars:3000,tableMaxRows:8,tableMaxCols:8});
const values=sh.getRange(`A1:Q${last+12}`).values;
const errors=values.flat().filter(v=>typeof v==='string'&&/^#(REF!|DIV\/0!|VALUE!|N\/A|NAME\?|NUM!)/.test(v));
if(errors.length)throw Error(errors.join(','));
const sourcingErrors=rows.filter(q=>q.stage.startsWith('BUY')&&!/^https:\/\/(www\.)?(servocity\.com|amazon\.com)\//.test(q.source||''));
if(sourcingErrors.length)throw Error(`Unsupported preferred vendor: ${sourcingErrors.map(q=>q.id)}`);
await fs.writeFile(path.join(root,'checks/bom-check.json'),JSON.stringify({date:cost.date,subtotal_usd:before,independent_subtotal_usd:expected,two_drive_purchase_subtotal_usd:vehicle,independent_two_drive_subtotal_usd:vehicleExpected,material_consumed_estimate_usd:material,owned_quantity_edit_check:true,two_pack_rounding_check:true,kit_charged_once_check:true,preferred_vendor_check:true,bearing_and_servo_ear_screw_separation_check:true,formula_errors:errors,rows:rows.length,unresolved_source_rows:record.sourcing_revision.unresolved,inspect},null,2));
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(path.join(root,'BOM.xlsx'));
const preview=await wb.render({sheetName:'BOM',range:'A1:Q16',scale:1,format:'png'});
await fs.writeFile(path.join(root,'.local/bom-preview.png'),new Uint8Array(await preview.arrayBuffer()));
const changed=await wb.render({sheetName:'BOM',range:`A${last-3}:O${last}`,scale:1,format:'png'});await fs.writeFile(path.join(root,'.local/bom-drive-preview.png'),new Uint8Array(await changed.arrayBuffer()));
const materialPreview=await wb.render({sheetName:'BOM',range:`A${footer}:Q${footer+9}`,scale:1,format:'png'});await fs.writeFile(path.join(root,'.local/bom-material-preview.png'),new Uint8Array(await materialPreview.arrayBuffer()));
const earPreview=await wb.render({sheetName:'BOM',range:`A${earRow}:Q${earRow}`,scale:1,format:'png'});await fs.writeFile(path.join(root,'.local/bom-ear-preview.png'),new Uint8Array(await earPreview.arrayBuffer()));
const bearingRow=10+rows.findIndex(q=>q.id==='H08');const bearingPreview=await wb.render({sheetName:'BOM',range:`A${bearingRow}:Q${bearingRow}`,scale:1,format:'png'});await fs.writeFile(path.join(root,'.local/bom-bearing-preview.png'),new Uint8Array(await bearingPreview.arrayBuffer()));
console.log(JSON.stringify({file:'BOM.xlsx',rows:rows.length,first_purchase_priced_subtotal:before,two_drive_purchase_priced_subtotal:vehicle,material_consumed_estimate:material,checks:'passed'}));
