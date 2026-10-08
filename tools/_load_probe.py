import subprocess
import sys
from pathlib import Path

studio = Path(r"C:\Program Files\Bambu Studio\bambu-studio.exe")
target = Path(sys.argv[1])
log = target.with_suffix(".log")
startup = subprocess.STARTUPINFO()
startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startup.wShowWindow = 0
proc = subprocess.Popen(
    [str(studio), "--debug", "3", str(target)],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    creationflags=0x08000000,
    startupinfo=startup,
)
try:
    out, err = proc.communicate(timeout=12)
except subprocess.TimeoutExpired:
    proc.kill()
    out, err = proc.communicate()
text = out + b"\n" + err
log.write_bytes(text)
print("bytes", len(text), "log", log.name)
# print lines that mention 3mf/config/invalid
for line in text.decode("utf-8", "replace").splitlines():
    low = line.lower()
    if any(word in low for word in ("invalid", "3mf", "config", "bambu lab", "geometry", "error", "warn")):
        print(line[:240])
