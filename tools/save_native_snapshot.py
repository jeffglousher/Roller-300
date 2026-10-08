"""Package an unchanged CAD-application model export when native Save fails."""
from pathlib import Path
import json
import zipfile

root=Path(__file__).resolve().parents[1]
source=root/'Roller-300.nbcad'
export=root/'design/native-fixes-2026-10-03/live-model.json'
model=json.loads(export.read_text())
assert model['document']['name']=='Roller-300'
assert not any(f['status']['state']!='ok' for f in model['document']['history']['features'])
with zipfile.ZipFile(source) as old:
    entries={n:old.read(n) for n in old.namelist()}
backup=root/'.local/2026-10-03-before-native-fixes.nbcad.bak'
backup.parent.mkdir(exist_ok=True)
if not backup.exists():backup.write_bytes(source.read_bytes())
entries['model.json']=export.read_bytes()
temporary=source.with_suffix('.nbcad.tmp')
with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED) as out:
    for name,data in entries.items():out.writestr(name,data)
temporary.replace(source)
print('Packaged unchanged application export;',len(model['document']['history']['features']),'features; original preserved in .local')
