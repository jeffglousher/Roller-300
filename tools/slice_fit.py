"""Offline X2D slice estimate, using installed vendor profiles. Never sends a print."""
from pathlib import Path
import json,subprocess,sys,struct,zipfile,os,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
PROFILE=Path(r'C:\Program Files\Bambu Studio\resources\profiles\BBL')
PRINT_SET=os.environ.get('ROLLER_PRINT_SET','drive-end-section')
if PRINT_SET not in ['drive-end-section','shell-first-review']:raise SystemExit('Unknown print set')
PARTS=ROOT/'first-prints'/PRINT_SET
OUT=PARTS/'slicer-check'/sys.argv[1];OUT.mkdir(parents=True,exist_ok=True)
index={p.stem:p for p in PROFILE.rglob('*.json')}
def flattened(name):
 p=index[name];own=json.loads(p.read_text(encoding='utf-8-sig'));merged={}
 if own.get('inherits'):merged.update(flattened(own['inherits']))
 for included in own.get('include',[]):merged.update(flattened(included))
 merged.update({k:v for k,v in own.items() if k not in ['inherits','include']})
 return merged
def write(name,data):
 p=OUT/name;p.write_text(json.dumps(data,indent=2));return p
machine=flattened('Bambu Lab X2D 0.4 nozzle')
process=flattened('0.20mm Standard @BBL X2D')
part=sys.argv[1] if len(sys.argv)>1 else 'tpu-tread-246-fit'
is_tpu=part.startswith('tpu')
process.update(wall_loops='3' if is_tpu else '5',sparse_infill_density='15%',sparse_infill_pattern='gyroid',brim_width='3',brim_type='outer_only',enable_support='0' if is_tpu or 'retainer' in part else '1',support_type='normal(auto)',support_on_build_plate_only='1',enable_prime_tower='0')
if PRINT_SET=='shell-first-review':process['support_on_build_plate_only']='0'
material=flattened(('Generic TPU' if is_tpu else 'Generic PETG')+' @BBL X2D 0.4 nozzle')
mp=write('machine.json',machine);pp=write(part+'-process.json',process);fp=write(part+'-filament.json',material)
args=[r'C:\Program Files\Bambu Studio\bambu-studio.exe','--debug','3','--arrange','1','--load-settings',str(mp)+';'+str(pp),'--load-filaments',str(fp),'--curr-bed-type','Textured PEI Plate','--slice','0','--export-3mf',str(OUT/(part+'-estimate.3mf')),'--export-settings',str(OUT/(part+'-used-settings.json')),'--outputdir',str(OUT),str(PARTS/(part+'.stl'))]
args[args.index('--export-3mf')+1]=part+'-estimate.3mf'
# The fully resolved profile and resulting bounds are recorded for review.
args[1:1]=['--filament-map','1','--filament-map-mode','Manual']
if True:  # Fixed center avoids the CLI arranger restricting this part to both nozzles' intersection.
 ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns)
 tag=lambda n:'{'+ns+'}'+n
 model=ET.Element(tag('model'),unit='millimeter');resources=ET.SubElement(model,tag('resources'));obj=ET.SubElement(resources,tag('object'),id='1',type='model');mesh=ET.SubElement(obj,tag('mesh'));vertices=ET.SubElement(mesh,tag('vertices'));triangles=ET.SubElement(mesh,tag('triangles'))
 data=(PARTS/(part+'.stl')).read_bytes();count=struct.unpack_from('<I',data,80)[0]
 for i in range(count):
  v=struct.unpack_from('<12fH',data,84+50*i)
  for k in range(3):ET.SubElement(vertices,tag('vertex'),x=str(v[3+3*k]),y=str(v[4+3*k]),z=str(v[5+3*k]))
  ET.SubElement(triangles,tag('triangle'),v1=str(3*i),v2=str(3*i+1),v3=str(3*i+2))
 build=ET.SubElement(model,tag('build'));ET.SubElement(build,tag('item'),objectid='1',transform='1 0 0 0 1 0 0 0 1 128 128 0')
 fixed=OUT/(part+'-placement.3mf')
 with zipfile.ZipFile(fixed,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
  z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
  z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
 args[-1]=str(fixed);args[args.index('--arrange')+1]='0'
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
result=subprocess.run(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=0x08000000,startupinfo=startup)
(OUT/(part+'-stdout.txt')).write_bytes(result.stdout);(OUT/(part+'-stderr.txt')).write_bytes(result.stderr)
report={'exit_code':result.returncode,'args':args,'output_exists':(OUT/(part+'-estimate.3mf')).exists(),'physical_print':False,'profile_basis':'Installed Bambu Studio 02.08.02.61; generic material, 0.4 mm nozzle, 0.2 mm layer, 15% gyroid. Actual filament/nozzle not confirmed.'}
write(part+'-result.json',report)
if (OUT/'result.json').exists():write(part+'-slice-result.json',json.loads((OUT/'result.json').read_text()))
print(json.dumps(report,indent=2))
