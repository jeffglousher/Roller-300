"""Offline placement/slice of a fresh native open-face wheel; never prints."""
from pathlib import Path
import hashlib,json,struct,subprocess,sys,zipfile
import xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial import cKDTree
from bambu_project_settings import preserve_process_overrides

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'first-prints/chassis-fit-2026-10-07'
PROFILE=ROOT/'first-prints/adversarial-fit-2026-10-06/slicer-check/left-wheel-axle-vertical'
if not PROFILE.exists():
    PROFILE=ROOT/'first-prints/chassis-fit-2026-10-07'
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
ET.register_namespace('',NS)
tag=lambda x:'{'+NS+'}'+x
sha=lambda b:hashlib.sha256(b).hexdigest()

def signature(triangles):
    return sha(json.dumps(sorted(tuple(sorted(tuple(round(float(x)*10000) for x in p) for p in t)) for t in triangles),separators=(',',':')).encode())

def verify_triangles(actual,expected):
    source=np.array(expected).reshape(-1,3)
    output=np.array(actual).reshape(-1,3)
    vertices,source_indices=np.unique(source,axis=0,return_inverse=True)
    distance,output_indices=cKDTree(vertices).query(output)
    assert distance.max()<=0.00005,'Placed native vertex moved beyond tolerance'
    source_faces=sorted(tuple(sorted(f)) for f in source_indices.reshape(-1,3))
    output_faces=sorted(tuple(sorted(f)) for f in output_indices.reshape(-1,3))
    assert source_faces==output_faces,'Native triangle connectivity changed'
    return float(distance.max())

def transform(value):
    m=np.eye(4)
    if value:m[:3,:]=np.array([float(x) for x in value.split()]).reshape(4,3).T
    return m

def final_triangles(project):
    with zipfile.ZipFile(project) as z:
        def walk(file,oid,parent):
            model=ET.fromstring(z.read(file))
            obj=next(o for o in model.find(tag('resources')) if o.get('id')==oid)
            mesh=obj.find(tag('mesh'))
            if mesh is not None:
                verts=np.array([[float(v.get(k)) for k in 'xyz']+[1.] for v in mesh.find(tag('vertices'))])
                verts=(parent@verts.T).T[:,:3]
                return [verts[[int(t.get(k)) for k in ['v1','v2','v3']]].tolist() for t in mesh.find(tag('triangles'))]
            result=[]
            for c in obj.find(tag('components')):
                child=c.get('{'+PROD+'}path',file).lstrip('/')
                result.extend(walk(child,c.get('objectid'),parent@transform(c.get('transform'))))
            return result
        model=ET.fromstring(z.read('3D/3dmodel.model'))
        result=[]
        for b in model.find(tag('build')):
            if b.get('printable','1')=='1':result.extend(walk('3D/3dmodel.model',b.get('objectid'),transform(b.get('transform'))))
        return result

def main():
    global OUT
    # The selected outboard-down pose is the default; the baseline is explicit.
    outboard_down='--inboard-down' not in sys.argv
    if outboard_down:OUT=OUT/'outboard-down'
    native=Path(sys.argv[1]).resolve()
    source=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else ROOT/'Roller-300.nbcad'
    OUT.mkdir(parents=True,exist_ok=True)
    data=native.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*n,'Requires native binary STL'
    native_triangles=[];local=[]
    for i in range(n):
        row=struct.unpack_from('<12fH',data,84+50*i)
        points=[row[3+3*k:6+3*k] for k in range(3)]
        native_triangles.append(points)
        local.append([(x,z-123,150-y) if outboard_down else (x,123-z,y-110) for x,y,z in points])
    expected=[[(x+128,y+128,z) for x,y,z in t] for t in local]
    assert max(abs(z) for t in local for _,_,z in t)<=40.0001
    model=ET.Element(tag('model'),unit='millimeter')
    resources=ET.SubElement(model,tag('resources'))
    obj=ET.SubElement(resources,tag('object'),id='1',type='model',name='left-wheel-open-fit')
    mesh=ET.SubElement(obj,tag('mesh'));vertices=ET.SubElement(mesh,tag('vertices'));triangles=ET.SubElement(mesh,tag('triangles'))
    index={}
    for triangle in local:
        ids=[]
        for point in triangle:
            if point not in index:
                index[point]=len(index)
                ET.SubElement(vertices,tag('vertex'),x=str(point[0]),y=str(point[1]),z=str(point[2]))
            ids.append(index[point])
        ET.SubElement(triangles,tag('triangle'),v1=str(ids[0]),v2=str(ids[1]),v3=str(ids[2]))
    build=ET.SubElement(model,tag('build'))
    ET.SubElement(build,tag('item'),objectid='1',transform='1 0 0 0 1 0 0 0 1 128 128 0',printable='1')
    placement=OUT/'wheel-open-fit-placement.3mf'
    with zipfile.ZipFile(placement,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
    process=json.loads((PROFILE/'left-wheel-axle-vertical-process.json').read_text())
    assert process['wall_loops']=='5' and process['sparse_infill_density']=='15%' and process['sparse_infill_pattern']=='gyroid'
    assert process['enable_support']=='1' and process['support_on_build_plate_only']=='0'
    for filename in ['machine.json','left-wheel-axle-vertical-process.json','left-wheel-axle-vertical-filament.json']:
        (OUT/filename).write_bytes((PROFILE/filename).read_bytes())
    name='Roller-300-wheel-open-fit.3mf'
    args=[r'C:\Program Files\Bambu Studio\bambu-studio.exe','--debug','3','--filament-map','1','--filament-map-mode','Manual','--arrange','0','--load-settings',str(OUT/'machine.json')+';'+str(OUT/'left-wheel-axle-vertical-process.json'),'--load-filaments',str(OUT/'left-wheel-axle-vertical-filament.json'),'--curr-bed-type','Textured PEI Plate','--slice','0','--export-3mf',name,'--outputdir',str(OUT),str(placement)]
    if '--reuse-slice' not in sys.argv:
        run=subprocess.run(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=0x08000000)
        (OUT/'wheel-stdout.log').write_bytes(run.stdout);(OUT/'wheel-stderr.log').write_bytes(run.stderr)
        assert run.returncode==0
    result=json.loads((OUT/'result.json').read_text())
    assert result.get('return_code')==0
    assert all(not p.get('warning_message') for p in result['sliced_plates'])
    final=OUT/name
    preservation=preserve_process_overrides(final,process)
    with zipfile.ZipFile(final) as z:
        config=ET.fromstring(z.read('Metadata/model_settings.config'))
        objects=config.findall('object')
        assert len(objects)==1
        parts=objects[0].findall('part')
        assert len(parts)==1 and parts[0].get('subtype')=='normal_part'
        assert all(int(parts[0].find('mesh_stat').get(k,'0'))==0 for k in ['edges_fixed','degenerate_facets','facets_removed','facets_reversed','backwards_edges'])
    actual=final_triangles(final)
    assert len(actual)==len(expected)
    maximum_vertex_error=verify_triangles(actual,expected)
    grams=sum(float(f['total_used_g']) for p in result['sliced_plates'] for f in p['filaments'])
    seconds=sum(float(p['total_predication']) for p in result['sliced_plates'])
    report=dict(date='2026-10-07',native_source_project=str(source.relative_to(ROOT)),native_source_project_sha256=sha(source.read_bytes()),native_body_id=13,native_stl=str(native.relative_to(ROOT)),native_stl_sha256=sha(data),project=str(final.relative_to(ROOT)),project_sha256=sha(final.read_bytes()),geometry_changed=False,triangle_count=n,maximum_placed_vertex_error_mm=maximum_vertex_error,native_triangle_connectivity_preserved=True,placed_geometry_signature_tolerance_mm=0.0001,placed_geometry_signature_sha256=signature(expected),normal_mesh_count=1,support_blocker_count=0,print_pose='outboard_face_down' if outboard_down else 'inboard_face_down',retained_hub_web_bed_z_mm=[12.5,16.5] if outboard_down else [23.5,27.5],native_to_bed_map='bed=(nativeX+128,nativeZ+5,150-nativeY); rigid -90deg X rotation and translation only' if outboard_down else 'bed=(nativeX+128,251-nativeZ,nativeY-110); rigid +90deg X rotation and translation only',release='HOLD until receiving hardware fits and support cleanup/driver access review',physical_print=False,powered=False,settings_preservation=preservation,slice_result=result,mass_grams=grams,time_seconds=seconds)
    (OUT/'wheel-slice-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    (OUT/'README.md').write_text(f'''# Open-face wheel — held fit candidate\n\nFresh native wheel body13, open on both faces, placed by rigid rotation/translation only. X2D main nozzle, PETG,0.4 mm,0.2 mm layers,5 walls,15% gyroid, normal auto supports. Estimated {grams:.2f} g /{seconds/3600:.2f} h. No print submitted.\n\nUse the five-piece receiving gate and carrier trial first. This larger wheel remains HOLD until the received Hyper Hub, M4x10 screws and actual wheel/retainer running clearance are checked. Remove supports through the two D216 face openings, inspect the4 mm mounting web and all four D4.4 screw passages, and verify screw/head/driver access before assembly. The old609 g wheel estimate uses superseded closed-face geometry.\n\nThis project is an unpowered fit trial. A warning-free slice and open cleanup path do not qualify dimensional accuracy, support removal quality or load-bearing behavior.\n''',encoding='utf8')
    print(json.dumps(dict(project=str(final),grams=grams,seconds=seconds,triangle_count=n)))

if __name__=='__main__':main()
