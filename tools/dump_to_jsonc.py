#!/usr/bin/env python3
"""Generate design/*.nbcad.jsonc from a native-port dump JSON.

Mirrors the Design Ops patterns used by design_v0_1_input_carriage.nbcad.jsonc.
No invented geometry — sketch entities, extents, flips, combines, patterns,
and mirrors come from the dump only.

Usage:
  tools/dump_to_jsonc.py design/native-port/main_shell-32.json \\
      -o design/design_v0_1_barrel_shell.nbcad.jsonc \\
      --role main_shell --body-id 32 --skip-hatch
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any


def fmt_num(x: float) -> float | int:
    if abs(x - round(x)) < 1e-9:
        return int(round(x))
    return float(f"{x:.10g}")


def diam_text(diameter: float) -> str:
    d = fmt_num(diameter)
    return str(d)


def parse_entities(sk: dict) -> tuple[dict[int, tuple[float, float]], list[dict]]:
    points: dict[int, tuple[float, float]] = {}
    curves: list[dict] = []
    snap = sk.get("snapshot_full") or {}
    ents = snap.get("entities")
    if ents:
        for item in ents:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                eid, e = item
            else:
                e = item
                eid = e.get("id")
            if not isinstance(e, dict):
                continue
            t = e.get("type")
            eid_i = int(eid)
            if t == "point":
                pos = e.get("position") or {}
                points[eid_i] = (
                    float(pos.get("x", pos.get("u", 0.0))),
                    float(pos.get("y", pos.get("v", 0.0))),
                )
            elif t in ("line", "arc", "circle"):
                curves.append({**e, "id": eid_i})
    geo = sk.get("geometry") or {}
    if geo.get("points"):
        for p in geo["points"]:
            points[int(p["id"])] = (float(p["u"]), float(p["v"]))
    if geo.get("curves"):
        byid = {c["id"]: c for c in curves}
        for c in geo["curves"]:
            byid[int(c["id"])] = c
        curves = list(byid.values())
    return points, curves


def is_axis_aligned_rect(
    lines: list[dict], points: dict[int, tuple[float, float]]
) -> tuple[float, float, float, float] | None:
    if len(lines) != 4:
        return None
    corners: set[tuple[float, float]] = set()
    for ln in lines:
        s, e = ln.get("start"), ln.get("end")
        if s not in points or e not in points:
            return None
        corners.add(points[s])
        corners.add(points[e])
    xs = sorted({c[0] for c in corners})
    ys = sorted({c[1] for c in corners})
    if len(xs) != 2 or len(ys) != 2 or len(corners) != 4:
        return None
    return xs[0], ys[0], xs[1], ys[1]


def plane_select(plane_step_id: str) -> dict:
    return {
        "type": "datum_plane",
        "datum_id": {
            "$select": {
                "from": {"$ref": plane_step_id},
                "path": "/planes",
                "pointer": "/datum_id",
                "take": "last",
                "where": {},
            }
        },
    }


def body_ref(name: str) -> dict:
    return {"$ref": name, "pointer": "/id"}


def feat_body_lets(step_id: str, feat_let: str, body_let: str) -> list[dict]:
    return [
        {
            "let": {
                feat_let: {
                    "$select": {
                        "from": {"$ref": step_id},
                        "path": "/document/features",
                        "take": "last",
                        "pointer": "/id",
                    }
                }
            }
        },
        {
            "let": {
                body_let: {
                    "$select": {
                        "from": {"$ref": step_id},
                        "path": "/scene/bodies",
                        "where": {"/feature_id": {"$ref": feat_let}},
                        "take": "one",
                    }
                }
            }
        },
    ]


def multi_body_lets(step_id: str, feat_let: str, body_lets: list[str]) -> list[dict]:
    """Bind N bodies created by one feature (pattern/mirror), ordered by body id."""
    steps: list[dict] = [
        {
            "let": {
                feat_let: {
                    "$select": {
                        "from": {"$ref": step_id},
                        "path": "/document/features",
                        "take": "last",
                        "pointer": "/id",
                    }
                }
            }
        },
        {
            "let": {
                f"{feat_let}__all": {
                    "$select": {
                        "from": {"$ref": step_id},
                        "path": "/scene/bodies",
                        "where": {"/feature_id": {"$ref": feat_let}},
                        "take": "all",
                        "order_by": "/id",
                    }
                }
            }
        },
    ]
    for i, bl in enumerate(body_lets):
        steps.append(
            {
                "let": {
                    bl: {
                        "$ref": f"{feat_let}__all",
                        "pointer": f"/{i}",
                    }
                }
            }
        )
    return steps


def curve_endpoints(
    c: dict, points: dict[int, tuple[float, float]]
) -> tuple[tuple[float, float], tuple[float, float]]:
    t = c["type"]
    if t == "line":
        return points[c["start"]], points[c["end"]]
    if t == "arc":
        center = c["center"]
        cx, cy = float(center["x"]), float(center["y"])
        r = float(c["radius"])
        sa = float(c["start_angle"])
        ea = float(c["end_angle"])
        return (cx + r * math.cos(sa), cy + r * math.sin(sa)), (
            cx + r * math.cos(ea),
            cy + r * math.sin(ea),
        )
    raise ValueError(f"no endpoints for {t}")


def pt_key(p: tuple[float, float], nd: int = 6) -> tuple[float, float]:
    return (round(p[0], nd), round(p[1], nd))


def order_closed_wire(
    curves: list[dict], points: dict[int, tuple[float, float]]
) -> list[tuple[dict, bool]]:
    """Return [(curve, reversed), ...] walking a single closed loop."""
    if not curves:
        return []
    # Map endpoint -> list of (curve_index, at_start)
    buckets: dict[tuple[float, float], list[tuple[int, bool]]] = {}
    ends: list[tuple[tuple[float, float], tuple[float, float]]] = []
    for i, c in enumerate(curves):
        a, b = curve_endpoints(c, points)
        ends.append((a, b))
        buckets.setdefault(pt_key(a), []).append((i, True))
        buckets.setdefault(pt_key(b), []).append((i, False))

    used = [False] * len(curves)
    start_i = 0
    a0, b0 = ends[start_i]
    ordered: list[tuple[dict, bool]] = [(curves[start_i], False)]
    used[start_i] = True
    cur = pt_key(b0)
    for _ in range(len(curves) - 1):
        cands = [x for x in buckets.get(cur, []) if not used[x[0]]]
        if not cands:
            # reopen search — disconnected; fall back to id order
            return [(c, False) for c in sorted(curves, key=lambda c: int(c["id"]))]
        ci, at_start = cands[0]
        # if we arrived at the curve's start, traverse forward; if at end, reverse
        rev = not at_start
        ordered.append((curves[ci], rev))
        used[ci] = True
        a, b = ends[ci]
        cur = pt_key(b if not rev else a)
    return ordered


def emit_sketch_geometry(
    prefix: str, points: dict, curves: list[dict]
) -> list[dict]:
    steps: list[dict] = []
    steps.append(
        {
            "id": f"{prefix}_nosnap",
            "call": {
                "group": "sketch/selection",
                "operation": "sketch_set_grid_snap",
                "arguments": {"enabled": False},
            },
        }
    )
    lines = [c for c in curves if c["type"] == "line"]
    circles = [c for c in curves if c["type"] == "circle"]
    arcs = [c for c in curves if c["type"] == "arc"]

    rect = is_axis_aligned_rect(lines, points) if not arcs and not circles else None
    if rect is not None and not arcs and not circles:
        x0, y0, x1, y1 = rect
        steps.append(
            {
                "id": f"{prefix}_rect",
                "call": {
                    "group": "sketch/draw",
                    "operation": "sketch_add_rectangle_locked",
                    "arguments": {
                        "mode": "two_point",
                        "anchor": {"x": fmt_num(x0), "y": fmt_num(y0)},
                        "corner_hint": {"x": fmt_num(x1), "y": fmt_num(y1)},
                        "width_mm": fmt_num(abs(x1 - x0)),
                        "height_mm": fmt_num(abs(y1 - y0)),
                        "ctrl_held": True,
                    },
                },
            }
        )
    elif circles and not lines and not arcs:
        for i, c in enumerate(sorted(circles, key=lambda c: int(c["id"]))):
            center = c["center"]
            r = float(c["radius"])
            cx, cy = float(center["x"]), float(center["y"])
            steps.append(
                {
                    "id": f"{prefix}_c{i}",
                    "call": {
                        "group": "sketch/draw",
                        "operation": "sketch_add_circle_locked",
                        "arguments": {
                            "mode": "center_diameter",
                            "anchor": {"x": fmt_num(cx), "y": fmt_num(cy)},
                            "edge_hint": {"x": fmt_num(cx + r), "y": fmt_num(cy)},
                            "diameter_text": diam_text(2 * r),
                            "ctrl_held": False,
                        },
                    },
                }
            )
    else:
        # Non-circle profiles: walk closed wire (lines+arcs). Circles rare mixed.
        for i, c in enumerate(sorted(circles, key=lambda c: int(c["id"]))):
            center = c["center"]
            r = float(c["radius"])
            cx, cy = float(center["x"]), float(center["y"])
            steps.append(
                {
                    "id": f"{prefix}_c{i}",
                    "call": {
                        "group": "sketch/draw",
                        "operation": "sketch_add_circle_locked",
                        "arguments": {
                            "mode": "center_diameter",
                            "anchor": {"x": fmt_num(cx), "y": fmt_num(cy)},
                            "edge_hint": {"x": fmt_num(cx + r), "y": fmt_num(cy)},
                            "diameter_text": diam_text(2 * r),
                            "ctrl_held": False,
                        },
                    },
                }
            )
        wire_curves = [c for c in curves if c["type"] in ("line", "arc")]
        ordered = order_closed_wire(wire_curves, points)
        for i, (c, rev) in enumerate(ordered):
            t = c["type"]
            if t == "arc":
                center = c["center"]
                cx, cy = float(center["x"]), float(center["y"])
                r = float(c["radius"])
                sa = float(c["start_angle"])
                ea = float(c["end_angle"])
                if rev:
                    sa, ea = ea, sa
                d = ea - sa
                while d <= -math.pi:
                    d += 2 * math.pi
                while d > math.pi:
                    d -= 2 * math.pi
                mid = sa + d / 2.0
                sx, sy = cx + r * math.cos(sa), cy + r * math.sin(sa)
                mx, my = cx + r * math.cos(mid), cy + r * math.sin(mid)
                ex, ey = cx + r * math.cos(ea), cy + r * math.sin(ea)
                steps.append(
                    {
                        "id": f"{prefix}_arc{i}",
                        "call": {
                            "group": "sketch/draw",
                            "operation": "sketch_add_arc_3pt",
                            "arguments": {
                                "p1": {"x": fmt_num(sx), "y": fmt_num(sy)},
                                "p2": {"x": fmt_num(mx), "y": fmt_num(my)},
                                "p3": {"x": fmt_num(ex), "y": fmt_num(ey)},
                                "ctrl_held": True,
                            },
                        },
                    }
                )
            elif t == "line":
                a, b = curve_endpoints(c, points)
                if rev:
                    a, b = b, a
                steps.append(
                    {
                        "id": f"{prefix}_L{i}",
                        "call": {
                            "group": "sketch/draw",
                            "operation": "sketch_add_line",
                            "arguments": {
                                "ctrl_held": True,
                                "from": {"x": fmt_num(a[0]), "y": fmt_num(a[1])},
                                "to_raw": {"x": fmt_num(b[0]), "y": fmt_num(b[1])},
                            },
                        },
                    }
                )

    steps.append(
        {
            "id": f"{prefix}_snap",
            "call": {
                "group": "sketch/selection",
                "operation": "sketch_set_grid_snap",
                "arguments": {"enabled": True},
            },
        }
    )
    return steps



def slug(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return s[:80] or "x"


class Generator:
    def __init__(
        self,
        dump: dict,
        *,
        role: str,
        primary_body_id: int,
        skip_hatch: bool,
        max_fid: int | None = None,
    ):
        self.dump = dump
        self.role = role
        self.primary_body_id = primary_body_id
        self.skip_hatch = skip_hatch
        self.max_fid = max_fid
        self.steps: list[dict] = []
        self.native_body_let: dict[int, str] = {}  # native body id -> let name
        self.plane_lets: dict[tuple[str, float], str] = {}  # (plane, dist) -> step id
        self.skipped: list[str] = []
        self.verify: list[str] = []

    def add(self, step: dict) -> None:
        self.steps.append(step)

    def chapter(self, title: str, note: str) -> None:
        self.add({"chapter": title, "note": note})

    def ensure_plane(self, datum: dict) -> str:
        src = datum["source"]
        plane = src["reference"]["plane"]
        dist = float(src["distance"])
        key = (plane, dist)
        if key in self.plane_lets:
            return self.plane_lets[key]
        name = datum.get("name") or f"datum_{datum.get('feature_id')}"
        step_id = f"pl_{slug(name)}"
        # uniquify
        base = step_id
        n = 2
        existing = {s.get("id") for s in self.steps}
        while step_id in existing or step_id in self.plane_lets.values():
            step_id = f"{base}_{n}"
            n += 1
        self.add(
            {
                "id": step_id,
                "call": {
                    "group": "solid/reference",
                    "operation": "construction_plane_offset",
                    "arguments": {
                        "name": f"{name} / shared",
                        "distance": fmt_num(dist),
                        "reference": {"type": "origin_plane", "plane": plane},
                    },
                },
            }
        )
        origin = (datum.get("basis") or {}).get("origin")
        self.chapter(
            f"datum {step_id}",
            f"Native basis origin {origin}; source distance {dist} from origin {plane}.",
        )
        self.plane_lets[key] = step_id
        return step_id

    def bind_body(self, native_id: int, step_id: str, let_name: str | None = None) -> str:
        let_name = let_name or f"body_{native_id}"
        feat_let = f"{let_name}_feat"
        for s in feat_body_lets(step_id, feat_let, let_name):
            self.add(s)
        self.native_body_let[native_id] = let_name
        return let_name

    def bind_bodies_multi(
        self, native_ids: list[int], step_id: str, feat_prefix: str
    ) -> list[str]:
        feat_let = f"{feat_prefix}_feat"
        body_lets = [f"body_{nid}" for nid in native_ids]
        for s in multi_body_lets(step_id, feat_let, body_lets):
            self.add(s)
        for nid, bl in zip(native_ids, body_lets):
            self.native_body_let[nid] = bl
        return body_lets

    def resolve_body(self, native_id: int) -> dict:
        if native_id not in self.native_body_let:
            raise KeyError(f"native body {native_id} not bound yet")
        return body_ref(self.native_body_let[native_id])

    def should_skip(self, feat: dict) -> str | None:
        kind = feat["kind"]
        name = feat.get("name", "")
        if not self.skip_hatch:
            return None
        if kind == "move_copy" and name == "MoveCopy5":
            return "hatch-only MoveCopy5 (shell→141); hatch chapter owns body 141"
        if kind == "combine" and name == "Combine8":
            return "needs hatch body 141 (skip; ledge joins without hatch cut)"
        if kind == "combine" and name == "Combine16":
            return "needs hatch body 141 for final shell opening; pre-Combine16 AABB expected"
        # Skip any op that references body 141 as tool/source when hatch skipped
        if kind == "combine":
            tools = feat.get("tool_body_ids") or []
            if 141 in tools:
                return "tool references hatch body 141"
        if kind == "move_copy":
            if 141 in (feat.get("body_ids") or []) or 141 in (
                feat.get("result_body_ids") or []
            ):
                return "references hatch body 141"
        return None

    def emit_extrude(self, feat: dict) -> None:
        name = feat["name"]
        fid = feat["feature_id"]
        sk = feat["sketch"]
        datum = sk["datum"]
        plane_id = self.ensure_plane(datum)
        sketch_name = f"{name}__{sk['name']}"
        points, curves = parse_entities(sk)

        self.chapter(
            f"{name} — {feat['operation']}",
            f"Native fid {fid}; sketch `{sk['name']}`; extent {feat['extent']}; "
            f"flip={feat.get('flip')}; profiles={feat.get('profile_indices')}; "
            f"native targets {feat.get('target_body_ids')}; "
            f"new_body_ids {feat.get('new_body_ids')}.",
        )
        prefix = f"sk_{name}"
        self.add(
            {
                "id": f"{prefix}_begin",
                "call": {
                    "group": "sketch/draw",
                    "operation": "sketch_begin",
                    "arguments": {
                        "name": sketch_name,
                        "plane": plane_select(plane_id),
                    },
                },
            }
        )
        for s in emit_sketch_geometry(prefix, points, curves):
            self.add(s)
        self.add(
            {
                "id": f"{prefix}_finish",
                "call": {
                    "group": "sketch/draw",
                    "operation": "sketch_finish",
                    "arguments": {},
                },
            }
        )

        # Target bodies: only those we've bound (drop foreign timeline bodies)
        raw_targets = list(feat.get("target_body_ids") or [])
        targets: list[dict] = []
        dropped = []
        for tid in raw_targets:
            if tid in self.native_body_let:
                targets.append(self.resolve_body(tid))
            else:
                dropped.append(tid)
        if dropped and feat["operation"] in ("cut", "join"):
            self.verify.append(
                f"{name}: dropped unbound target bodies {dropped} (foreign timeline)"
            )

        ex_id = f"ex_{name}"
        self.add(
            {
                "id": ex_id,
                "call": {
                    "group": "solid/build",
                    "operation": "solid_extrude",
                    "arguments": {
                        "sketch_name": sketch_name,
                        "profile_indices": list(feat.get("profile_indices") or [0]),
                        "operation": feat["operation"],
                        "extent": {
                            "type": feat["extent"]["type"],
                            "distance": fmt_num(float(feat["extent"]["distance"])),
                        },
                        "taper_angle_deg": fmt_num(float(feat.get("taper_angle_deg") or 0)),
                        "flip": bool(feat.get("flip")),
                        "target_body_ids": targets,
                    },
                },
            }
        )

        new_ids = list(feat.get("new_body_ids") or [])
        op = feat["operation"]
        if op == "new_body":
            # Bind each new body. Usually one; if multiple, multi-bind.
            if len(new_ids) == 1:
                nid = new_ids[0]
                let = (
                    "main_shell_body"
                    if nid == self.primary_body_id
                    else f"body_{nid}"
                )
                self.bind_body(nid, ex_id, let)
            elif len(new_ids) > 1:
                self.bind_bodies_multi(new_ids, ex_id, ex_id)
        elif op == "join" and new_ids:
            # Join into existing target — target already bound; transient new ids
            # usually consumed. If join target is a tool body we track (e.g. 155),
            # no rebind needed.
            pass

    def emit_combine(self, feat: dict) -> None:
        name = feat["name"]
        fid = feat["feature_id"]
        tgt = feat["target_body_id"]
        tools = list(feat.get("tool_body_ids") or [])
        self.chapter(
            f"{name} — {feat['operation']}",
            f"Native fid {fid}; tgt [{tgt}]; tools {tools}; keep_tools={feat.get('keep_tools')}.",
        )
        tool_refs = [self.resolve_body(t) for t in tools]
        self.add(
            {
                "id": f"ex_{name}",
                "call": {
                    "group": "solid/body",
                    "operation": "solid_combine",
                    "arguments": {
                        "target_body_id": self.resolve_body(tgt),
                        "tool_body_ids": tool_refs,
                        "operation": feat["operation"],
                        "keep_tools": bool(feat.get("keep_tools")),
                    },
                },
            }
        )

    def emit_pattern(self, feat: dict) -> None:
        name = feat["name"]
        fid = feat["feature_id"]
        src = list(feat.get("body_ids") or [])
        new_ids = list(feat.get("new_body_ids") or [])
        self.chapter(
            f"{name} — rectangular_pattern",
            f"Native fid {fid}; from {src}; new {new_ids}; count {feat['count']}; "
            f"spacing {feat['spacing']}; dir {feat['direction']}.",
        )
        step_id = f"ex_{name}"
        args: dict[str, Any] = {
            "body_ids": [self.resolve_body(b) for b in src],
            "direction": {
                "x": fmt_num(float(feat["direction"]["x"])),
                "y": fmt_num(float(feat["direction"]["y"])),
                "z": fmt_num(float(feat["direction"]["z"])),
            },
            "spacing": fmt_num(float(feat["spacing"])),
            "count": int(feat["count"]),
        }
        if feat.get("second_count") and int(feat["second_count"]) > 1:
            args["second_count"] = int(feat["second_count"])
            args["second_spacing"] = fmt_num(float(feat.get("second_spacing") or 0))
            sd = feat.get("second_direction")
            if sd:
                args["second_direction"] = {
                    "x": fmt_num(float(sd["x"])),
                    "y": fmt_num(float(sd["y"])),
                    "z": fmt_num(float(sd["z"])),
                }
        self.add(
            {
                "id": step_id,
                "call": {
                    "group": "solid/repeat",
                    "operation": "solid_rectangular_pattern",
                    "arguments": args,
                },
            }
        )
        if new_ids:
            self.bind_bodies_multi(new_ids, step_id, step_id)

    def emit_mirror(self, feat: dict) -> None:
        name = feat["name"]
        fid = feat["feature_id"]
        src = list(feat.get("body_ids") or [])
        new_ids = list(feat.get("new_body_ids") or [])
        plane = feat.get("plane") or {"type": "origin_plane", "plane": "xz"}
        self.chapter(
            f"{name} — mirror",
            f"Native fid {fid}; from {src}; new {new_ids}; plane {plane}.",
        )
        step_id = f"ex_{name}"
        self.add(
            {
                "id": step_id,
                "call": {
                    "group": "solid/repeat",
                    "operation": "solid_mirror",
                    "arguments": {
                        "body_ids": [self.resolve_body(b) for b in src],
                        "plane": plane,
                    },
                },
            }
        )
        if new_ids:
            self.bind_bodies_multi(new_ids, step_id, step_id)

    def emit_move_copy(self, feat: dict) -> None:
        name = feat["name"]
        fid = feat["feature_id"]
        src = list(feat.get("body_ids") or [])
        result = list(feat.get("result_body_ids") or [])
        self.chapter(
            f"{name} — move_copy",
            f"Native fid {fid}; from {src}; result {result}; copy={feat.get('copy')}; "
            f"T {feat.get('translation')}; quat {feat.get('rotation')}.",
        )
        step_id = f"ex_{name}"
        self.add(
            {
                "id": step_id,
                "call": {
                    "group": "solid/body",
                    "operation": "solid_move_copy",
                    "arguments": {
                        "body_ids": [self.resolve_body(b) for b in src],
                        "translation": {
                            "x": fmt_num(float(feat["translation"]["x"])),
                            "y": fmt_num(float(feat["translation"]["y"])),
                            "z": fmt_num(float(feat["translation"]["z"])),
                        },
                        "pivot": {
                            "x": fmt_num(float((feat.get("pivot") or {}).get("x", 0))),
                            "y": fmt_num(float((feat.get("pivot") or {}).get("y", 0))),
                            "z": fmt_num(float((feat.get("pivot") or {}).get("z", 0))),
                        },
                        "rotation": [fmt_num(float(x)) for x in (feat.get("rotation") or [0, 0, 0, 1])],
                        "copy": bool(feat.get("copy")),
                    },
                },
            }
        )
        # copy=True creates new bodies; copy=False moves in place (same ids)
        if feat.get("copy"):
            if result:
                if len(result) == 1:
                    self.bind_body(result[0], step_id, f"body_{result[0]}")
                else:
                    self.bind_bodies_multi(result, step_id, step_id)
        else:
            # in-place move — body lets remain valid
            pass

    def build(self) -> dict:
        role = self.role
        primary = self.primary_body_id
        header_notes = [
            f"// Roller-300 design_v0_1_barrel_shell — modular Design Ops chapter (VERSION 0.1)",
            f"// Role noun: {role} (native body {primary})",
            f"// SoT: this .nbcad.jsonc. Replay: blank document only (starting_state empty).",
            f"// Source: design/native-port/main_shell-32.md + .json — dump-only, no invented blocks.",
            f"// Sequence: fid order from dump; hatch-only MoveCopy5/Combine8/Combine16 skipped.",
            f"// Coupons remain under first-prints/coupons/. Shared named refs + $ref/$select.",
            f"// AABB target (with Combine16): 159.95×210×159.98 @ mins (-79.95, -105, 43.01).",
            f"// Generated by tools/dump_to_jsonc.py — do not hand-edit geometry values.",
        ]
        self.header_notes = header_notes

        self.chapter(
            f"Shared refs — {role} (native body {primary})",
            "VERSION 0.1. Ported from design/native-port/main_shell-32.* — no invented blocks. "
            "Datum offsets use native signed distances. Skip hatch-only MoveCopy5 / Combine8 / "
            "Combine16 (body 141). Transient new_body_ids on join/cut are tool solids — not SoT. "
            "Saddle-coupon chapter replaced; print-today coupons remain under first-prints/coupons/.",
        )
        for plane, dist, pid in (
            ("xy", 0.0, "ref_origin_xy"),
            ("xz", 0.0, "ref_origin_xz"),
            ("yz", 0.0, "ref_origin_yz"),
        ):
            self.add(
                {
                    "id": pid,
                    "call": {
                        "group": "solid/reference",
                        "operation": "construction_plane_offset",
                        "arguments": {
                            "name": f"origin_{plane} / shared",
                            "distance": 0.0,
                            "reference": {"type": "origin_plane", "plane": plane},
                        },
                    },
                }
            )
            self.plane_lets[(plane, 0.0)] = pid

        # Walk feature_sequence; skip standalone datum/sketch (emitted with extrude)
        for feat in self.dump["feature_sequence"]:
            kind = feat["kind"]
            if kind in ("datum_plane", "sketch"):
                continue
            if self.max_fid is not None and int(feat.get("feature_id", 0)) > self.max_fid:
                self.chapter(
                    f"PREFIX stop before {feat.get('name')}",
                    f"max_fid={self.max_fid}; remaining dump features not emitted.",
                )
                break
            reason = self.should_skip(feat)
            if reason:
                self.skipped.append(f"{feat.get('name')} (fid {feat.get('feature_id')}): {reason}")
                self.chapter(
                    f"SKIP {feat.get('name')}",
                    reason,
                )
                continue
            try:
                if kind == "extrude":
                    self.emit_extrude(feat)
                elif kind == "combine":
                    self.emit_combine(feat)
                elif kind == "rectangular_pattern":
                    self.emit_pattern(feat)
                elif kind == "mirror":
                    self.emit_mirror(feat)
                elif kind == "move_copy":
                    self.emit_move_copy(feat)
                else:
                    self.verify.append(f"unhandled kind {kind} for {feat.get('name')}")
            except Exception as e:
                self.chapter(
                    f"BLOCKED at {feat.get('name')}",
                    f"Generator error: {e}. Prefix ends before this feature.",
                )
                self.verify.append(f"blocked at {feat.get('name')}: {e}")
                break

        self.verify.extend(self.dump.get("verify_gaps") and [
            g.get("detail") if isinstance(g, dict) else str(g)
            for g in self.dump.get("verify_gaps", [])
        ] or [])

        skip_note = "; ".join(self.skipped) if self.skipped else "none"
        self.chapter(
            "VERIFY — AABB + remaining",
            "Expect review STL AABB 159.95×210×159.98 @ mins (-79.95,-105,43.01) only after "
            "Combine16 (hatch 141). This chapter skips hatch-only ops — compare pre-Combine16 "
            f"shell AABB to dump-without-hatch-cut. Skipped: {skip_note}. "
            f"Extra VERIFY: {' | '.join(self.verify[:12])}",
        )

        doc = {
            "version": 1,
            "name": f"Roller-300 design_v0_1_barrel_shell (VERSION 0.1) — {role} native body {primary}",
            "starting_state": "empty",
            "steps": self.steps,
            "checks": [
                {
                    "id": "final_scene",
                    "call": {
                        "group": "solid/check",
                        "operation": "solid_scene",
                        "arguments": {},
                    },
                    "expect": {"/errors": []},
                }
            ],
        }
        return doc

    def render(self, doc: dict) -> str:
        body = json.dumps(doc, indent=2, ensure_ascii=False)
        return "\n".join(self.header_notes) + "\n" + body + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dump_json")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--role", default="main_shell")
    ap.add_argument("--body-id", type=int, default=32)
    ap.add_argument("--skip-hatch", action="store_true", default=True)
    ap.add_argument("--no-skip-hatch", action="store_true")
    ap.add_argument("--max-fid", type=int, default=None)
    args = ap.parse_args()
    dump = json.loads(Path(args.dump_json).read_text())
    skip = not args.no_skip_hatch
    gen = Generator(
        dump,
        role=args.role,
        primary_body_id=args.body_id,
        skip_hatch=skip,
        max_fid=args.max_fid,
    )
    doc = gen.build()
    text = gen.render(doc)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    n_call = sum(1 for s in doc["steps"] if "call" in s)
    print(
        f"Wrote {out} steps={len(doc['steps'])} calls={n_call} "
        f"skipped={len(gen.skipped)} bound_bodies={len(gen.native_body_let)}"
    )
    for s in gen.skipped:
        print(f"  SKIP {s}")


if __name__ == "__main__":
    main()
