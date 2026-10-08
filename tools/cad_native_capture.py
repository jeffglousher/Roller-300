"""Capture the CAD application's own rendered window, through its native MCP API."""
import json
from pathlib import Path
import subprocess
import sys

session_id, destination = sys.argv[1:]
output=Path(destination).resolve()
output.parent.mkdir(parents=True,exist_ok=True)
proc=subprocess.Popen([str(Path.home()/'AppData/Local/nbcad/mcp/nbcad-mcp.exe')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,creationflags=0x08000000)
def send(message):
    proc.stdin.write((json.dumps(message)+'\n').encode());proc.stdin.flush()
def receive(call_id):
    while True:
        line=proc.stdout.readline()
        if not line:raise RuntimeError('CAD MCP closed')
        result=json.loads(line)
        if result.get('id')==call_id:return result
try:
    send({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'native-cad-window-capture','version':'1'}}})
    receive(1)
    send({'jsonrpc':'2.0','method':'notifications/initialized'})
    send({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'cad_interface','arguments':{'action':'inspect','session_id':session_id}}})
    receive(2)
    send({'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'cad_interface','arguments':{'action':'capture','session_id':session_id,'path':str(output),'overwrite':True}}})
    reply=receive(3)
    result=reply.get('result',{})
    if result.get('isError') or 'error' in reply:raise RuntimeError(json.dumps(reply))
    data=result.get('structuredContent',{})
    if data.get('status')=='failed':raise RuntimeError(data.get('message',str(data)[:400]))
    print(json.dumps({'path':str(output),'exists':output.exists(),'status':data.get('status')}))
finally:
    proc.kill();proc.wait()
