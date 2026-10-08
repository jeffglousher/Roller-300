"""Extract unchanged carrier and its two support blockers for an offline trial."""
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from bambu_project_settings import preserve_process_overrides

R=Path(__file__).resolve().parents[1]
SOURCE=R/'first-prints/corrected-full-fit-2026-10-06/Roller-300-full-fit-corrected.3mf'
OUT=R/'first-prints/carrier-roof-trial-2026-10-06'
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
ET.register_namespace('',NS);ET.register_namespace('p',PROD)
ET.register_namespace('BambuStudio','http://schemas.bambulab.com/package/2021')
tag=lambda x:'{'+NS+'}'+x
sha=lambda data:hashlib.sha256(data).hexdigest()

def mesh_signature(mesh):
    points=[tuple(round(float(v.get(a))*100000) for a in 'xyz') for v in mesh.find(tag('vertices'))]
    faces=sorted(tuple(sorted(points[int(t.get(a))] for a in ['v1','v2','v3'])) for t in mesh.find(tag('triangles')))
    return sha(json.dumps(faces,separators=(',',':')).encode())

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(SOURCE) as z:entries={n:z.read(n) for n in z.namelist()}
    model=ET.fromstring(entries['3D/3dmodel.model'])
    cfg=ET.fromstring(entries['Metadata/model_settings.config'])
    carrier=next(o for o in cfg.findall('object') if any(m.get('key')=='name' and m.get('value')=='input-sliding-carrier' for m in o.findall('metadata')))
    oid=carrier.get('id')
    normal=next(p for p in carrier.findall('part') if p.get('subtype')=='normal_part')
    blockers=[p for p in carrier.findall('part') if p.get('subtype')=='support_blocker']
    assert len(blockers)==2 and len(carrier.findall('part'))==3
    parent=next(o for o in model.find(tag('resources')) if o.get('id')==oid)
    components=parent.find(tag('components'))
    children={c.get('{'+PROD+'}path').lstrip('/') for c in components}
    assert len(children)==1
    childfile=next(iter(children));child=ET.fromstring(entries[childfile])
    original=next(o for o in child.find(tag('resources')) if o.get('id')==normal.get('id')).find(tag('mesh'))
    signature=mesh_signature(original)
    for obj in list(model.find(tag('resources'))):
        if obj.get('id')!=oid:model.find(tag('resources')).remove(obj)
    for item in list(model.find(tag('build'))):
        if item.get('objectid')!=oid:model.find(tag('build')).remove(item)
        else:
            transform=item.get('transform').split();transform[9:11]=['128','128'];item.set('transform',' '.join(transform))
    for obj in list(cfg.findall('object')):
        if obj.get('id')!=oid:cfg.remove(obj)
    for plate in cfg.findall('plate'):
        for md in list(plate):
            if md.get('key') in {'gcode_file','thumbnail_file','thumbnail_no_light_file','top_file','pick_file'}:plate.remove(md)
            elif md.tag=='model_instance':
                # CLI assigns fresh instance ids after extracting resources;
                # do not retain the source plate's instance-index registry.
                plate.remove(md)
    rels=ET.fromstring(entries['3D/_rels/3dmodel.model.rels'])
    for rel in list(rels):
        if rel.get('Target','').lstrip('/')!=childfile:rels.remove(rel)
    assert len(rels)==1
    # Reindex the extracted assembly into a compact single-model package.
    # Sparse source ids can leave an empty source plate in Bambu's CLI importer.
    compact=ET.Element(tag('model'),unit='millimeter')
    ET.SubElement(compact,tag('metadata'),name='BambuStudio:3mfVersion').text='1'
    resources=ET.SubElement(compact,tag('resources'))
    idmap={normal.get('id'):'1',blockers[0].get('id'):'2',blockers[1].get('id'):'3'}
    for obj in child.find(tag('resources')):
        clone=copy.deepcopy(obj);clone.set('id',idmap[obj.get('id')]);resources.append(clone)
    compact_parent=ET.SubElement(resources,tag('object'),id='4',type='model')
    compact_components=ET.SubElement(compact_parent,tag('components'))
    for component in components:
        ET.SubElement(compact_components,tag('component'),objectid=idmap[component.get('objectid')],transform=component.get('transform'))
    build=ET.SubElement(compact,tag('build'))
    item=next(iter(model.find(tag('build'))))
    ET.SubElement(build,tag('item'),objectid='4',transform=item.get('transform'),printable='1')
    carrier.set('id','4')
    for part in carrier.findall('part'):part.set('id',idmap[part.get('id')])
    entries['3D/3dmodel.model']=ET.tostring(compact,encoding='utf-8',xml_declaration=True)
    entries['Metadata/model_settings.config']=ET.tostring(cfg,encoding='utf-8',xml_declaration=True)
    entries['3D/_rels/3dmodel.model.rels']=ET.tostring(rels,encoding='utf-8',xml_declaration=True)
    keep={'[Content_Types].xml','_rels/.rels','3D/3dmodel.model','Metadata/project_settings.config','Metadata/model_settings.config'}
    placement=OUT/'carrier-roof-trial-placement.3mf'
    with zipfile.ZipFile(placement,'w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(keep):z.writestr(name,entries[name])
    settings=R/'first-prints/adversarial-fit-2026-10-06/slicer-check/input-sliding-carrier'
    project='Roller-300-carrier-roof-trial.3mf'
    args=[r'C:\Program Files\Bambu Studio\bambu-studio.exe','--debug','3','--filament-map','1','--filament-map-mode','Manual','--arrange','0',
          '--load-settings',str(settings/'machine.json')+';'+str(settings/'input-sliding-carrier-process.json'),
          '--load-filaments',str(settings/'input-sliding-carrier-filament.json'),'--curr-bed-type','Textured PEI Plate',
          '--slice','0','--export-3mf',project,'--outputdir',str(OUT),str(placement)]
    run=subprocess.run(args,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=0x08000000)
    (OUT/'stdout.log').write_bytes(run.stdout);(OUT/'stderr.log').write_bytes(run.stderr)
    result=json.loads((OUT/'result.json').read_text())
    assert run.returncode==0 and result.get('return_code')==0
    assert all(not p.get('warning_message') for p in result['sliced_plates'])
    final=OUT/project
    preservation=preserve_process_overrides(final,json.loads((settings/'input-sliding-carrier-process.json').read_text()))
    with zipfile.ZipFile(final) as z:
        output_cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
        objs=output_cfg.findall('object');assert len(objs)==1
        out_normal=[p for p in objs[0].findall('part') if p.get('subtype')=='normal_part']
        out_blockers=[p for p in objs[0].findall('part') if p.get('subtype')=='support_blocker']
        assert len(out_normal)==1 and len(out_blockers)==2
        output_model=ET.fromstring(z.read('3D/3dmodel.model'))
        out_parent=next(o for o in output_model.find(tag('resources')) if o.get('id')==objs[0].get('id'))
        comp=next(c for c in out_parent.find(tag('components')) if c.get('objectid')==out_normal[0].get('id'))
        out_child=ET.fromstring(z.read(comp.get('{'+PROD+'}path','3D/3dmodel.model').lstrip('/')))
        out_mesh=next(o for o in out_child.find(tag('resources')) if o.get('id')==out_normal[0].get('id')).find(tag('mesh'))
        assert mesh_signature(out_mesh)==signature,'Native carrier mesh changed'
    report=dict(source_project=str(SOURCE.relative_to(R)),source_project_sha256=sha(SOURCE.read_bytes()),
                project_sha256=sha(final.read_bytes()),native_geometry_changed=False,normal_mesh_count=1,support_blocker_count=2,
                native_mesh_signature_sha256=signature,physical_print=False,powered=False,
                settings_preservation=preservation,slice_result=result)
    (OUT/'slice-check.json').write_text(json.dumps(report,indent=2)+'\n')
    grams=sum(float(f['total_used_g']) for p in result['sliced_plates'] for f in p['filaments'])
    seconds=sum(float(p['total_predication']) for p in result['sliced_plates'])
    (OUT/'README.md').write_text(f'''# Carrier roof trial — unpowered\n\nPrint this carrier separately after the five-part receiving gate passes. This project contains one unchanged native carrier and two nonprinting support blockers, using X2D / PETG / 0.4 mm / 0.2 mm / 5 walls / 15% gyroid. Estimated material: {grams:.2f} g; time: {seconds/3600:.2f} hours.\n\nThe purpose is to prove the unsupported bridge-nut channel roofs at print Z47.8 mm. The corrected full plate has unsupported wall runs approximately 9.12 mm on one post and 16.37 mm on the other. Inspect for sag, clean the accessible supports, and verify nuts insert fully and M3 screws pass through without forcing or cracking the posts. A successful slice is not proof of roof quality, dimensional accuracy, or load-bearing capacity.\n\nUnpowered fit only. No print has been submitted.\n''',encoding='utf-8')
    print(json.dumps(dict(project=str(final),grams=grams,seconds=seconds)))

if __name__=='__main__':main()
