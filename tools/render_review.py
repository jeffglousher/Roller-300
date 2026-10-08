"""Recompute the saved master in an isolated native kernel; write review evidence only."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile
import sys
import base64

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'design' / 'review-2026-10-03'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'Roller-300.nbcad'

def unwrap(reply):
    result = reply.get('result', reply)
    if result.get('isError') or 'error' in reply:
        raise RuntimeError(json.dumps(reply)[:3000])
    if 'structuredContent' in result:
        return result['structuredContent']
    for item in result.get('content', []):
        if item.get('type') == 'text':
            return json.loads(item['text'])
    return result

def extract():
    with zipfile.ZipFile(SOURCE) as archive:
        model_json = archive.read('model.json').decode('utf-8')
    model = json.loads(model_json)
    stderr = (OUT / 'kernel-stderr.txt').open('w')
    proc = subprocess.Popen([str(Path.home() / 'AppData/Local/nbcad/mcp/nbcad-mcp.exe')],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr,
        creationflags=0x08000000)
    next_id = 0
    def rpc(method, params):
        nonlocal next_id
        next_id += 1
        proc.stdin.write((json.dumps({'jsonrpc':'2.0','id':next_id,'method':method,'params':params})+'\n').encode())
        proc.stdin.flush()
        while True:
            line = proc.stdout.readline()
            if not line:
                raise RuntimeError('Native kernel stopped; inspect kernel-stderr.txt')
            reply = json.loads(line)
            if reply.get('id') == next_id:
                return reply
    def call(name, arguments=None):
        return unwrap(rpc('tools/call', {'name':name,'arguments':arguments or {}}))
    try:
        rpc('initialize', {'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'roller-read-only-review','version':'1'}})
        proc.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
        proc.stdin.flush()
        print('Recomputing saved Roller-300 master...', flush=True)
        loaded = call('cad_load_project_model', {'model_json':model_json})
        loaded_summary={k:v for k,v in loaded.items() if k not in {'scene','document'}}
        if 'document' in loaded:
            loaded_summary['document_name']=loaded['document'].get('name')
            loaded_summary['feature_count']=len(loaded['document'].get('features',[]))
        (OUT / 'recompute.json').write_text(json.dumps(loaded_summary, indent=2))
        print('Recompute complete. Extracting native meshes...', flush=True)
        scene = call('solid_scene')
        (OUT / 'scene.json').write_text(json.dumps(scene))
        preflight = call('solid_export_preflight')
        (OUT / 'preflight.json').write_text(json.dumps(preflight, indent=2))
        catalog = call('cad_interface', {'action':'catalog'})
        selected = [o for o in catalog['operations'] if o['name'] in ['solid_export_step','solid_export_stl','assembly_interference_check']]
        (OUT / 'operation-schemas.json').write_text(json.dumps(selected, indent=2))
        (OUT / 'source.json').write_text(json.dumps({'source':SOURCE.name,'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_modified_ns':SOURCE.stat().st_mtime_ns,'render_basis':'fresh native kernel recomputation','model_saved_or_modified':False,'feature_count':len(model['document']['history']['features'])}, indent=2))
        print('Scene keys:', list(scene), flush=True)
        for b in scene.get('bodies', []):
            mesh=b.get('mesh', {})
            p=mesh.get('positions', [])
            mn=[round(min(p[i::3]),3) for i in range(3)] if p else []
            mx=[round(max(p[i::3]),3) for i in range(3)] if p else []
            print(b['id'], b.get('name'), 'bbox',mn,mx,'triangles',len(mesh.get('indices',[]))//3, flush=True)
        print('PREFLIGHT',json.dumps(preflight)[:3500],flush=True)
        if '--exact' in sys.argv:
            for bid in [1,2,5,9,10,13,19,22,30,32,224,227,300,301,316,356,357,358,359,360]:
                reply=call('solid_export_step',{'body_ids':[bid]})
                (OUT/f'body-{bid}.step').write_bytes(base64.b64decode(reply['bytes_base64']))
            for bid in [13,30,32,356]:
                reply=call('solid_export_stl',{'body_ids':[bid],'linear_deflection':0.05,'angular_deflection':0.15})
                (OUT/f'body-{bid}-review.stl').write_bytes(base64.b64decode(reply['bytes_base64']))
            print('Native STEP and refined STL exported for exact structural checks.',flush=True)
    finally:
        proc.kill()
        proc.wait()
        stderr.close()

def render():
    import numpy as np
    import pyvista as pv
    import trimesh
    scene=json.loads((OUT/'scene.json').read_text())
    bodies={b['id']:b for b in scene['bodies']}
    meshes={}
    report=[]
    for bid,b in bodies.items():
        points=np.array(b['mesh']['positions']).reshape(-1,3)
        faces=np.array(b['mesh']['indices']).reshape(-1,3)
        meshes[bid]=pv.PolyData(points,np.c_[np.full(len(faces),3),faces].ravel())
        t=trimesh.Trimesh(points,faces,process=True)
        components=t.split(only_watertight=False)
        report.append({'body_id':bid,'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'connected_components':len(components),'volume_mm3':float(t.volume),'bbox_min':points.min(0).tolist(),'bbox_max':points.max(0).tolist(),'components':[{'watertight':bool(c.is_watertight),'volume_mm3':float(c.volume),'bounds':c.bounds.tolist()} for c in components]})
    (OUT/'mesh-checks.json').write_text(json.dumps(report,indent=2))
    wheel_ids={13,14,30,31}
    printed_ids={9,10,13,26,27,30,32,300,301,307,308,309,315,316,317,356}
    def color(bid):
        if bid==32:return '#b8c8d2'
        if bid in {14,31}:return '#253341'
        if bid in {13,30}:return '#718495'
        if bid in {9,10,26,27,301,309,307,315}:return '#dc9635'
        if bid in {300,308,316,317}:return '#d8b681'
        if bid==356:return '#b7758b'
        if bid in {12,29}:return '#578b9e'
        if bid in {344,345,346,347}:return '#ac7750'
        return '#9ba6ae'
    def view(name,ids,camera,title,cut_shell=False,focus=None,clip=None):
        p=pv.Plotter(off_screen=True,window_size=(1600,1200))
        p.set_background('#f6f7f8')
        p.enable_anti_aliasing('ssaa')
        for bid in ids:
            mesh=meshes[bid]
            if bid==32 and cut_shell:
                mesh=mesh.clip(normal=(0,0,1),origin=(0,0,123),invert=True)
            if clip:
                mesh=mesh.clip(normal=clip[0],origin=clip[1],invert=clip[2])
            if mesh.n_cells:
                p.add_mesh(mesh,color=color(bid),smooth_shading=True,split_sharp_edges=True,
                    ambient=0.30,diffuse=0.70,specular=0.20,specular_power=25)
        p.camera_position=camera
        p.enable_parallel_projection()
        p.reset_camera()
        if focus:
            p.camera.focal_point=focus[0]
            p.camera.parallel_scale=focus[1]
        p.add_text(title,position='upper_left',font_size=17,color='#1f3345')
        p.add_text('Fresh native recompute | mm | 03 Oct 2026 | Review geometry, not a print release',position='lower_left',font_size=10,color='#50616e')
        p.show(screenshot=str(OUT/(name+'.png')),auto_close=True)
        print('Rendered',name,flush=True)
    all_ids=list(bodies)
    drive_ids=[i for i in bodies if i not in wheel_ids]
    view('assembly-isometric',all_ids,[(430,510,410),(0,0,123),(0,0,1)],'Roller-300 | Complete active assembly')
    view('assembly-front',all_ids,[(500,0,123),(0,0,123),(0,0,1)],'Roller-300 | Front elevation (looking along X)')
    view('interior-cutaway',drive_ids,[(330,390,390),(0,0,123),(0,0,1)],'Roller-300 | Interior; upper shell and wheels hidden',cut_shell=True)
    view('drive-side',drive_ids,[(0,500,135),(0,0,123),(0,0,1)],'Roller-300 | Drive plane; wheels hidden',cut_shell=True)
    view('drive-top',drive_ids,[(0,0,650),(0,0,123),(1,0,0)],'Roller-300 | Top; upper shell and wheels hidden',cut_shell=True)
    view('center-support-close',[32,1,18,356,357,358],[(110,190,180),(0,0,93),(0,0,1)],'Roller-300 | New center-bearing support',cut_shell=True,focus=((0,0,93),65))
    view('left-drive-close',[i for i in drive_ids if i not in {18,19,20,21,22,23,26,27,28,29,227,228,229,308,309,315,317,339,341,343,345,347,349,358,360}],[(170,200,200),(28,65,123),(0,0,1)],'Roller-300 | Left drive; upper shell and wheels hidden',cut_shell=True,focus=((25,65,123),65))
    p=pv.Plotter(off_screen=True,window_size=(1800,1100),shape=(1,2))
    p.set_background('#f6f7f8')
    p.enable_anti_aliasing('ssaa')
    p.subplot(0,0)
    b=bodies[32]
    t=trimesh.Trimesh(np.array(b['mesh']['positions']).reshape(-1,3),np.array(b['mesh']['indices']).reshape(-1,3),process=True)
    for c in sorted(t.split(only_watertight=False),key=lambda x:abs(x.volume),reverse=True):
        poly=pv.PolyData(c.vertices,np.c_[np.full(len(c.faces),3),c.faces].ravel())
        if abs(c.volume)>10000:
            poly=poly.clip(normal=(0,0,1),origin=(0,0,123),invert=True)
            col='#b8c8d2'
        else:col='#ba4e4e'
        p.add_mesh(poly,color=col,smooth_shading=True,ambient=0.3)
    p.camera_position=[(290,390,320),(0,0,105),(0,0,1)]
    p.enable_parallel_projection();p.reset_camera()
    p.add_text('Shell: 5 separate native solids',position='upper_left',font_size=17,color='#243846')
    p.add_text('Red: 2 input-bearing bosses + 2 bridge blocks\nNeed real connections to the shell load path.',position='lower_left',font_size=13,color='#763b3b')
    p.subplot(0,1)
    b=bodies[13]
    t=trimesh.Trimesh(np.array(b['mesh']['positions']).reshape(-1,3),np.array(b['mesh']['indices']).reshape(-1,3),process=True)
    for c in t.split(only_watertight=False):
        poly=pv.PolyData(c.vertices,np.c_[np.full(len(c.faces),3),c.faces].ravel())
        poly=poly.clip(normal=(1,0,0),origin=(0,0,123),invert=True)
        p.add_mesh(poly,color='#718495' if abs(c.volume)>10000 else '#ba4e4e',smooth_shading=True,ambient=0.3)
    p.add_mesh(meshes[1],color='#9ba6ae',smooth_shading=True)
    for bid,col in [(2,'#ddaa56'),(359,'#8a659d')]:
        poly=meshes[bid].clip(normal=(1,0,0),origin=(0,0,123),invert=True)
        p.add_mesh(poly,color=col,smooth_shading=True,ambient=0.3)
    p.camera_position=[(280,280,220),(0,142,123),(0,0,1)]
    p.enable_parallel_projection();p.reset_camera()
    p.camera.focal_point=(0,143,123);p.camera.parallel_scale=42
    p.add_text('Wheel: detached outer-bearing boss',position='upper_left',font_size=17,color='#243846')
    p.add_text('Red boss begins at Y151; wheel ends at Y150.\nOld + new bearing references overlap by 2 mm.',position='lower_left',font_size=13,color='#763b3b')
    p.show(screenshot=str(OUT/'print-blockers.png'),auto_close=True)
    print('Rendered print-blockers',flush=True)
    for r in report:
        if r['body_id'] in printed_ids or r['connected_components']>1 or not r['watertight']:
            print('MESH',r['body_id'],'closed',r['watertight'],'components',r['connected_components'],'volume',round(r['volume_mm3'],1),flush=True)
    print('Meshes and review evidence written to',OUT,flush=True)

if __name__ == '__main__':
    if '--render' in sys.argv:
        render()
    else:
        extract()
