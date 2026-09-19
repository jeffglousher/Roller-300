"""Read-only CAD inspection; --write refreshes a derived Git-review snapshot."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
source = root / 'Roller-300.nbcad'
target = root / 'checks/model-review.json'
with zipfile.ZipFile(source) as archive:
    model = json.loads(archive.read('model.json'))
result = {'generated_from': source.name,
          'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'warning': 'Generated review snapshot. Edit the native CAD document, never this file.',
          'model': model}
text = json.dumps(result, indent=2, sort_keys=True) + '\n'
if sys.argv[1:] == ['--write']:
    target.parent.mkdir(exist_ok=True)
    target.write_text(text, encoding='utf-8')
elif sys.argv[1:]:
    raise SystemExit('Usage: python tools/cad_snapshot.py [--write]')
elif not target.exists() or target.read_text(encoding='utf-8') != text:
    raise SystemExit('CAD review snapshot is stale: run with --write after saving native CAD.')
print('CAD snapshot matches saved native source; schema', model['schema_version'])
