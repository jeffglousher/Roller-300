"""Run offline vendor slicer checks for the native unpowered fit set."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
PARTS=ROOT/'first-prints'/os.environ.get('ROLLER_PRINT_SET','drivetrain-fit-2026-10-03')
manifest=json.loads((PARTS/'source.json').read_text())
selected=set(sys.argv[1:] or [row['name'] for row in manifest['parts']])
assert selected <= {row['name'] for row in manifest['parts']}, 'Unknown fit part'
def run(row):
    name=row['name'];env=os.environ.copy();env['ROLLER_PRINT_SET']=PARTS.name
    p=subprocess.run([sys.executable,str(ROOT/'tools/slice_fit.py'),name],env=env,cwd=ROOT,
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=0x08000000)
    folder=PARTS/'slicer-check'/name
    (folder/'runner-stdout.txt').write_bytes(p.stdout);(folder/'runner-stderr.txt').write_bytes(p.stderr)
    result=json.loads((folder/f'{name}-slice-result.json').read_text()) if (folder/f'{name}-slice-result.json').exists() else {}
    plates=result.get('sliced_plates',[])
    estimate=dict(part=name,exit_code=p.returncode,return_code=result.get('return_code'),
                  seconds=sum(float(x.get('total_predication',0)) for x in plates),
                  grams=sum(float(f.get('total_used_g',0)) for x in plates for f in x.get('filaments',[])),
                  warnings=[x.get('warning_message') for x in plates if x.get('warning_message')])
    estimate['native_mesh_sha256']=row['native_mesh_sha256']
    estimate['passed']=p.returncode==0 and result.get('return_code')==0 and bool(plates) and not estimate['warnings'] and estimate['seconds']>0 and estimate['grams']>0
    return estimate
rows=[]
if sys.argv[1:]:
    previous=json.loads((PARTS/'slice-checks.json').read_text())
    current={row['name']:row for row in manifest['parts']}
    for row in previous['parts']:
        if row['part'] not in current:continue
        if row['part'] in selected:continue
        assert row.get('native_mesh_sha256')==current[row['part']]['native_mesh_sha256'], 'Changed native mesh requires a new slice: '+row['part']
        rows.append(row)
with ThreadPoolExecutor(max_workers=int(os.environ.get('ROLLER_SLICE_WORKERS','2'))) as pool:
    jobs=[pool.submit(run,row) for row in manifest['parts'] if row['name'] in selected]
    for job in as_completed(jobs):
        row=job.result();rows.append(row);print(json.dumps(row),flush=True)
rows.sort(key=lambda x:x['part'])
report=dict(source_sha256=manifest['source_sha256'],material='PETG',nozzle_mm=.4,
            layer_height_mm=.2,wall_loops=5,infill='15% gyroid',physical_print=False,
            passed=all(x['passed'] for x in rows),parts=rows)
(PARTS/'slice-checks.json').write_text(json.dumps(report,indent=2)+'\n')
assert report['passed'], 'One or more vendor slices failed; inspect slicer-check'
