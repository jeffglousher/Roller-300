"""Shift both native pulleys inboard so the input pulley clears the Y92 post."""
import base64
import json
import struct
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXE = Path.home() / "AppData/Local/nbcad/mcp/nbcad-mcp.exe"
OUT = ROOT / "first-prints" / "drive-unit"
SHIFT_Y = -4.75  # centers the 14.5 mm pulley in the Y74–Y92 gap


def send(proc, message):
    proc.stdin.write((json.dumps(message) + "\n").encode("utf-8"))
    proc.stdin.flush()


def recv(proc):
    line = proc.stdout.readline()
    if not line:
        raise RuntimeError("MCP closed stdout")
    return json.loads(line.decode("utf-8"))


def call(proc, name, arguments, call_id):
    send(
        proc,
        {
            "jsonrpc": "2.0",
            "id": call_id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        },
    )
    while True:
        message = recv(proc)
        if message.get("id") == call_id:
            return message


def unwrap(message):
    result = message.get("result", message)
    if isinstance(result, dict) and result.get("isError"):
        raise SystemExit(json.dumps(result)[:2000])
    if isinstance(result, dict) and "structuredContent" in result:
        return result["structuredContent"]
    return result


def execute(proc, group, operation, arguments, call_id):
    return unwrap(
        call(
            proc,
            "cad_interface",
            {
                "action": "execute",
                "group": group,
                "operation": operation,
                "arguments": arguments,
            },
            call_id,
        )
    )


def stl_bounds(data):
    count = struct.unpack_from("<I", data, 80)[0]
    mins = [1e9, 1e9, 1e9]
    maxs = [-1e9, -1e9, -1e9]
    for index in range(count):
        values = struct.unpack_from("<12fH", data, 84 + 50 * index)
        for corner in range(3):
            for axis in range(3):
                value = values[3 + 3 * corner + axis]
                mins[axis] = min(mins[axis], value)
                maxs[axis] = max(maxs[axis], value)
    return count, mins, maxs


def write_bed(assembly_stl, dest):
    count = struct.unpack_from("<I", assembly_stl, 80)[0]
    points = []
    triangles = []
    for index in range(count):
        values = struct.unpack_from("<12fH", assembly_stl, 84 + 50 * index)
        normal = values[0:3]
        corners = [values[3 + 3 * k : 6 + 3 * k] for k in range(3)]
        # +90 deg about X: shaft axis Y becomes print axis Z. Determinant +1.
        def spin(point):
            x, y, z = point
            return (x, -z, y)

        triangles.append((spin(normal), [spin(corner) for corner in corners]))
        points.extend(triangles[-1][1])
    mins = [min(point[axis] for point in points) for axis in range(3)]
    blob = bytearray(b"drive-unit bore-up".ljust(80, b"\0"))
    blob += struct.pack("<I", len(triangles))
    for normal, corners in triangles:
        shifted = [tuple(corner[axis] - mins[axis] for axis in range(3)) for corner in corners]
        blob += struct.pack("<12fH", *normal, *(value for corner in shifted for value in corner), 0)
    dest.write_bytes(blob)


def main():
    archive = zipfile.ZipFile(ROOT / "Roller-300.nbcad")
    model_text = archive.read("model.json").decode("utf-8")
    model = json.loads(model_text)
    originals = {}
    steps = {}
    for feature in model["body_features"]:
        if feature.get("feature_id") in (9, 10):
            originals[feature["feature_id"]] = feature["data_base64"]
            steps[feature["feature_id"]] = base64.b64decode(feature["data_base64"])

    proc = subprocess.Popen(
        [str(EXE)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    send(
        proc,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "pulley-shift", "version": "0"},
            },
        },
    )
    recv(proc)
    send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})
    call(proc, "cad_new_project", {}, 2)

    names = {10: "input-pulley-24t", 9: "output-pulley-48t"}
    for feature_id, name in ((10, names[10]), (9, names[9])):
        print("import", name)
        execute(
            proc,
            "solid/body",
            "solid_import_step",
            {
                "file_name": f"{name}.step",
                "data_base64": base64.b64encode(steps[feature_id]).decode("ascii"),
            },
            feature_id,
        )

    print("shift Y", SHIFT_Y)
    execute(
        proc,
        "solid/body",
        "solid_move_copy",
        {
            "body_ids": [1, 2],
            "translation": {"x": 0.0, "y": SHIFT_Y, "z": 0.0},
            "pivot": {"x": 0.0, "y": 0.0, "z": 0.0},
            "rotation": [0.0, 0.0, 0.0, 1.0],
            "copy": False,
        },
        20,
    )

    replaced = {}
    for body_id, feature_id in ((1, 10), (2, 9)):
        name = names[feature_id]
        stl_doc = execute(
            proc,
            "document/export",
            "solid_export_stl",
            {"body_ids": [body_id], "linear_deflection": 0.08, "angular_deflection": 0.25},
            30 + body_id,
        )
        stl = base64.b64decode(stl_doc["bytes_base64"])
        count, mins, maxs = stl_bounds(stl)
        print(
            name,
            "tris",
            count,
            "Y",
            round(mins[1], 3),
            round(maxs[1], 3),
            "size",
            [round(maxs[axis] - mins[axis], 3) for axis in range(3)],
        )
        (OUT / f"{name}-assembly.stl").write_bytes(stl)
        write_bed(stl, OUT / f"{name}.stl")
        step_doc = execute(
            proc,
            "document/export",
            "solid_export_step",
            {"body_ids": [body_id]},
            40 + body_id,
        )
        replaced[feature_id] = step_doc["bytes_base64"]
        print("step", name, "b64", len(replaced[feature_id]))

    proc.kill()

    updated = model_text
    for feature_id, new_b64 in replaced.items():
        old_b64 = originals[feature_id]
        count = updated.count(old_b64)
        if count != 1:
            raise SystemExit(f"feature {feature_id} base64 count {count}")
        updated = updated.replace(old_b64, new_b64, 1)
    payload = updated.encode("utf-8")
    source = ROOT / "Roller-300.nbcad"
    temp = source.with_suffix(".nbcad.tmp")
    with zipfile.ZipFile(source, "r") as incoming, zipfile.ZipFile(
        temp, "w", compression=zipfile.ZIP_DEFLATED
    ) as outgoing:
        for info in incoming.infolist():
            data = payload if info.filename == "model.json" else incoming.read(info.filename)
            outgoing.writestr(info, data)
    temp.replace(source)
    print("updated", source.name, source.stat().st_size)


if __name__ == "__main__":
    main()
