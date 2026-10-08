"""Native CAD MCP transport with bounded console output."""
import json, subprocess, sys
from pathlib import Path

class CAD:
    def __init__(self, executable=None):
        self.seq = 0
        self.p = subprocess.Popen(
            [str(executable or Path.home()/'AppData/Local/limo-cad/bevy/Limo-CAD.exe'), '--headless'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            creationflags=0x08000000)
        self.request('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {},
                                   'clientInfo': {'name': 'roller-native-validation', 'version': '1'}})
        self.p.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
        self.p.stdin.flush()

    def request(self, method, params):
        self.seq += 1
        self.p.stdin.write((json.dumps(dict(jsonrpc='2.0', id=self.seq, method=method, params=params)) + '\n').encode())
        self.p.stdin.flush()
        while True:
            line = self.p.stdout.readline()
            if not line:
                raise RuntimeError(f'Native CAD transport exited ({self.p.poll()})')
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get('id') == self.seq:
                if 'error' in r:
                    raise RuntimeError(r['error'])
                return r['result']

    def call(self, name, arguments):
        r = self.request('tools/call', dict(name=name, arguments=arguments))
        if r.get('isError'):
            raise RuntimeError(str(r)[:2500])
        return r.get('structuredContent') or json.loads(next(c['text'] for c in r['content'] if c['type'] == 'text'))

    def close(self):
        self.p.stdin.close()
        self.p.terminate()

if __name__ == '__main__':
    c = CAD()
    try:
        if sys.argv[1] == 'load':
            path = Path(sys.argv[2])
            c.call('cad_load_project_model', {'model_json': path.read_text()})
            m = json.loads(c.call('cad_project_model', {})['value'])
            out = path.with_name(path.stem + '-replayed.json')
            out.write_text(json.dumps(m))
            bad = [f for f in m['document']['history']['features'] if f['status']['state'] != 'ok']
            pre = c.call('solid_export_preflight', {})
            print(json.dumps({'native_preflight':pre}), flush=True)
            print(json.dumps({'name':m['document']['name'], 'features':len(m['document']['history']['features']), 'failures':bad, 'export':str(out)}), flush=True)
            if len(sys.argv) > 3:
                folder = Path(sys.argv[3]); folder.mkdir(parents=True, exist_ok=True)
                for b in [int(v) for v in sys.argv[4:]]:
                    for fmt,op in [('step','solid_export_step'), ('stl','solid_export_stl')]:
                        args={'body_ids':[b]}
                        if fmt == 'stl':args.update(scope='definition',linear_deflection=0.05,angular_deflection=0.15)
                        result=c.call(op,args)
                        import base64
                        (folder/f'body-{b}.{fmt}').write_bytes(base64.b64decode(result['bytes_base64']))
                    print('Native CAD exported', b, flush=True)
        else:
            raw=sys.argv[2]
            if raw.startswith('@'):raw=Path(raw[1:]).read_text()
            print(json.dumps(c.call(sys.argv[1], json.loads(raw))))
    finally:
        c.close()
