#!/usr/bin/env python3
"""Dump native feature chain for one body from Roller-300.nbcad model.json."""
from __future__ import annotations

import argparse
import json
import struct
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_model(nbcad: Path) -> dict:
    with zipfile.ZipFile(nbcad) as z:
        with z.open("model.json") as f:
            return json.load(f)


def stl_aabb(path: Path) -> dict | None:
    if not path.exists():
        return None
    data = path.read_bytes()
    if len(data) < 84:
        return None
    # binary STL: 80 header + uint32 tri count + 50*n
    n = struct.unpack_from("<I", data, 80)[0]
    expected = 84 + n * 50
    xmin = ymin = zmin = float("inf")
    xmax = ymax = zmax = float("-inf")
    if expected == len(data) or abs(expected - len(data)) < 100:
        off = 84
        for _ in range(n):
            # normal 12 + 3 verts 36 + attr 2
            for i in range(3):
                x, y, z = struct.unpack_from("<fff", data, off + 12 + i * 12)
                xmin, xmax = min(xmin, x), max(xmax, x)
                ymin, ymax = min(ymin, y), max(ymax, y)
                zmin, zmax = min(zmin, z), max(zmax, z)
            off += 50
        return {
            "xmin": xmin,
            "xmax": xmax,
            "ymin": ymin,
            "ymax": ymax,
            "zmin": zmin,
            "zmax": zmax,
            "dx": xmax - xmin,
            "dy": ymax - ymin,
            "dz": zmax - zmin,
            "tri_count": n,
            "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        }
    # ASCII fallback
    text = data.decode("utf-8", errors="ignore")
    import re

    coords = [tuple(map(float, m.groups())) for m in re.finditer(r"vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)", text)]
    if not coords:
        return None
    xs, ys, zs = zip(*coords)
    return {
        "xmin": min(xs),
        "xmax": max(xs),
        "ymin": min(ys),
        "ymax": max(ys),
        "zmin": min(zs),
        "zmax": max(zs),
        "dx": max(xs) - min(xs),
        "dy": max(ys) - min(ys),
        "dz": max(zs) - min(zs),
        "tri_count": len(coords) // 3,
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
    }


def sketch_geometry(snapshot: dict) -> dict:
    entities = snapshot.get("entities") or []
    types: Counter = Counter()
    points = []
    curves = []
    for eid, ent in entities:
        t = ent.get("type")
        types[t] += 1
        if t == "point":
            p = ent.get("position") or {}
            points.append((p.get("x"), p.get("y")))
        elif t in ("line", "arc", "circle", "rectangle", "spline"):
            curves.append({"id": eid, **ent})
    bbox = None
    if points:
        xs = [p[0] for p in points if p[0] is not None]
        ys = [p[1] for p in points if p[1] is not None]
        if xs and ys:
            bbox = {
                "umin": min(xs),
                "umax": max(xs),
                "vmin": min(ys),
                "vmax": max(ys),
                "du": max(xs) - min(xs),
                "dv": max(ys) - min(ys),
            }
    # also circles/arcs centers for bbox
    for c in curves:
        if c.get("type") == "circle":
            cx = c.get("center", {}).get("x")
            cy = c.get("center", {}).get("y")
            r = c.get("radius") or 0
            if cx is not None and cy is not None:
                pts = [(cx - r, cy), (cx + r, cy), (cx, cy - r), (cx, cy + r)]
                for x, y in pts:
                    points.append((x, y))
        elif c.get("type") == "arc":
            cx = c.get("center", {}).get("x")
            cy = c.get("center", {}).get("y")
            r = c.get("radius") or 0
            if cx is not None and cy is not None:
                points.append((cx - r, cy))
                points.append((cx + r, cy))
                points.append((cx, cy - r))
                points.append((cx, cy + r))
        elif c.get("type") == "rectangle":
            # various representations
            pass
    if points and (bbox is None or True):
        xs = [p[0] for p in points if p[0] is not None]
        ys = [p[1] for p in points if p[1] is not None]
        if xs and ys:
            bbox = {
                "umin": min(xs),
                "umax": max(xs),
                "vmin": min(ys),
                "vmax": max(ys),
                "du": max(xs) - min(xs),
                "dv": max(ys) - min(ys),
            }
    return {
        "entity_count": len(entities),
        "entity_types": dict(types),
        "point_bbox_uv": bbox,
        "curves": curves,
    }


def enrich_sketch(sk: dict, datums_by_fid: dict, datums_by_id: dict) -> dict:
    snap = sk.get("snapshot") or {}
    plane = sk.get("plane") or {}
    plane_datum_id = plane.get("datum_id")
    # Match chain datum by feature_id proximity: sketch.feature_id - 1 often
    chain = datums_by_fid.get(sk["feature_id"] - 1)
    by_plane = datums_by_id.get(plane_datum_id)
    datum_info = None
    chosen = chain or by_plane
    if chosen:
        note = None
        if chain and by_plane and chain.get("datum_id") != by_plane.get("datum_id"):
            # stale plane.datum_id check via basis origin
            bo = (sk.get("basis") or {}).get("origin")
            co = (chain.get("basis") or {}).get("origin")
            po = (by_plane.get("basis") or {}).get("origin")
            if bo is not None and co is not None and bo == co and po != bo:
                note = (
                    f"Chain datum {chain['feature_id']}; sketch.basis.origin matches. "
                    f"Prefer sketch.basis + datum {chain['feature_id']} if plane.datum_id stale "
                    f"(plane.datum_id={plane_datum_id})."
                )
            elif bo is not None and po is not None and bo == po:
                note = f"plane.datum_id={plane_datum_id} matches sketch.basis."
            else:
                note = (
                    f"Chain datum feature_id={chain['feature_id'] if chain else None}; "
                    f"plane.datum_id={plane_datum_id}."
                )
            chosen = chain  # prefer chain when mismatch
        datum_info = {
            "datum_id": chosen.get("feature_id"),  # history fid used as chain id in hatch dumps
            "name": chosen.get("name"),
            "feature_id": chosen.get("feature_id"),
            "basis": chosen.get("basis"),
            "source": chosen.get("source"),
        }
        # Also keep native datum_id field
        datum_info["native_datum_id"] = chosen.get("datum_id")
        if note:
            datum_info["note"] = note
        # hatch used datum_id = feature_id for chain; keep both
        if chain:
            datum_info["datum_id"] = chain["feature_id"]
    geom = sketch_geometry(snap)
    return {
        "name": sk["name"],
        "feature_id": sk["feature_id"],
        "plane": plane,
        "basis": sk.get("basis"),
        "datum": datum_info,
        "geometry": geom,
        "constraint_count": len(snap.get("constraints") or []),
        "constraints": snap.get("constraints") or [],
        "snapshot_full": snap,
        "grid_snap": sk.get("grid_snap"),
        "dimension_style": sk.get("dimension_style"),
        "plane_datum_id_field": plane_datum_id,
    }


def feature_touches_bodies(payload: dict, bodies: set[int]) -> bool:
    t = payload.get("type") or payload.get("kind")
    if t == "extrude" or "operation" in payload and "sketch_name" in payload:
        tids = set(payload.get("target_body_ids") or [])
        nids = set(payload.get("new_body_ids") or [])
        return bool(tids & bodies or nids & bodies)
    if t == "combine":
        if payload.get("target_body_id") in bodies:
            return True
        if set(payload.get("tool_body_ids") or []) & bodies:
            return True
        return False
    if t == "move_copy":
        return bool(set(payload.get("body_ids") or []) & bodies or set(payload.get("result_body_ids") or []) & bodies)
    if t == "mirror":
        return bool(
            set(payload.get("body_ids") or []) & bodies
            or set(payload.get("new_body_ids") or []) & bodies
            or set(payload.get("result_body_ids") or []) & bodies
        )
    if t == "rectangular_pattern":
        return bool(
            set(payload.get("body_ids") or []) & bodies
            or set(payload.get("new_body_ids") or []) & bodies
            or set(payload.get("result_body_ids") or []) & bodies
        )
    if t == "revolve":
        tids = set(payload.get("target_body_ids") or [])
        nids = set(payload.get("new_body_ids") or [])
        return bool(tids & bodies or nids & bodies)
    return False


def collect_produced_bodies(payload: dict) -> set[int]:
    out: set[int] = set()
    t = payload.get("type")
    if t == "extrude" or ("sketch_name" in payload and "operation" in payload):
        if payload.get("operation") == "new_body":
            out.update(payload.get("new_body_ids") or [])
        # join/cut also list new_body_ids as transient tools
        out.update(payload.get("new_body_ids") or [])
    elif t == "combine":
        pass
    elif t == "move_copy":
        if payload.get("copy"):
            out.update(payload.get("result_body_ids") or [])
        else:
            out.update(payload.get("result_body_ids") or [])
    elif t == "mirror":
        out.update(payload.get("new_body_ids") or [])
    elif t == "rectangular_pattern":
        out.update(payload.get("new_body_ids") or [])
    elif t == "revolve":
        out.update(payload.get("new_body_ids") or [])
    return out


def summarize_feature(kind: str, payload: dict) -> dict:
    s = {
        "feature_id": payload.get("feature_id"),
        "name": payload.get("name"),
        "kind": kind,
        "operation": payload.get("operation"),
        "sketch_name": payload.get("sketch_name"),
        "extent": payload.get("extent"),
        "angle_deg": payload.get("angle_deg") or payload.get("angle"),
        "flip": payload.get("flip"),
        "target_body_ids": payload.get("target_body_ids"),
        "tool_body_ids": payload.get("tool_body_ids"),
        "new_body_ids": payload.get("new_body_ids") or payload.get("result_body_ids"),
        "body_ids": payload.get("body_ids"),
        "copy": payload.get("copy"),
        "translation": payload.get("translation"),
        "rotation": payload.get("rotation"),
        "pivot": payload.get("pivot"),
        "count": payload.get("count"),
        "spacing": payload.get("spacing"),
        "direction": payload.get("direction"),
        "plane": payload.get("plane"),
        "axis_origin": payload.get("axis_origin"),
        "axis_direction": payload.get("axis_direction") or payload.get("axis_dir"),
        "target_body_id": payload.get("target_body_id"),
        "keep_tools": payload.get("keep_tools"),
        "profile_indices": payload.get("profile_indices"),
        "taper_angle_deg": payload.get("taper_angle_deg"),
    }
    return {k: v for k, v in s.items() if v is not None}


def dump_body(
    model: dict,
    body_id: int,
    role: str,
    review_stl: Path | None,
    review_stl_alt: Path | None,
    exclude_bodies: set[int] | None = None,
) -> dict:
    exclude_bodies = exclude_bodies or set()
    hist = model["document"]["history"]["features"]
    extrudes_by_fid = {e["feature_id"]: e for e in model["extrudes"]}
    sketches_by_fid = {s["feature_id"]: s for s in model["sketches"]}
    sketches_by_name = {s["name"]: s for s in model["sketches"]}
    datums_by_fid = {d["feature_id"]: d for d in model["datum_planes"]}
    datums_by_id = {d["datum_id"]: d for d in model["datum_planes"]}
    bf_by_fid = {bf["feature_id"]: bf for bf in model["body_features"]}
    revolves_by_fid = {r["feature_id"]: r for r in model.get("revolves") or []}

    appearance = next((a for a in model["body_appearances"] if a.get("body_id") == body_id), None)

    # Seed interesting bodies
    interesting = {body_id}
    # Expand tool bodies from combines targeting body_id (but skip excluded like hatch 141 full chain)
    for bf in model["body_features"]:
        if bf.get("type") == "combine" and bf.get("target_body_id") == body_id:
            for t in bf.get("tool_body_ids") or []:
                if t not in exclude_bodies:
                    interesting.add(t)

    # Transitive closure: bodies produced that feed into interesting set via combines/patterns
    # Also: if a combine targets interesting and tools not excluded, add tools
    changed = True
    while changed:
        changed = False
        for bf in model["body_features"]:
            t = bf.get("type")
            if t == "combine":
                tgt = bf.get("target_body_id")
                tools = set(bf.get("tool_body_ids") or [])
                if tgt in interesting:
                    for tb in tools:
                        if tb not in interesting and tb not in exclude_bodies:
                            interesting.add(tb)
                            changed = True
                # if tools intersect and keep_tools modifying? skip
            elif t in ("move_copy", "mirror", "rectangular_pattern"):
                produced = set(bf.get("new_body_ids") or []) | set(bf.get("result_body_ids") or [])
                sources = set(bf.get("body_ids") or [])
                if produced & interesting:
                    # need sources
                    for s in sources:
                        if s not in interesting and s not in exclude_bodies:
                            interesting.add(s)
                            changed = True
                if sources & interesting:
                    for p in produced:
                        if p not in interesting and p not in exclude_bodies:
                            interesting.add(p)
                            changed = True
        for e in model["extrudes"]:
            nids = set(e.get("new_body_ids") or [])
            tids = set(e.get("target_body_ids") or [])
            if nids & interesting or tids & interesting:
                # already
                pass
            # if new_body creates something in interesting
            if e.get("operation") == "new_body" and nids & interesting:
                pass

    # Build payload index by history id
    def payload_for(hf: dict) -> tuple[str, dict] | None:
        fid = hf["id"]
        kind = hf["kind"]
        if kind == "extrude":
            return "extrude", extrudes_by_fid[fid]
        if kind == "construction_plane":
            return "datum_plane", datums_by_fid[fid]
        if kind == "sketch":
            return "sketch", sketches_by_fid[fid]
        if kind == "combine":
            return "combine", bf_by_fid[fid]
        if kind in ("move_copy", "mirror", "rectangular_pattern"):
            return kind, bf_by_fid[fid]
        if kind == "revolve":
            return "revolve", revolves_by_fid[fid]
        if kind == "import_step":
            return None  # skip imports for shell native dump
        return None

    # Determine which history fids to include
    include_fids: set[int] = set()
    sketch_names_needed: set[str] = set()

    for hf in hist:
        got = payload_for(hf)
        if not got:
            continue
        kind, payload = got
        if kind == "extrude":
            tids = set(payload.get("target_body_ids") or [])
            nids = set(payload.get("new_body_ids") or [])
            if tids & interesting or nids & interesting:
                include_fids.add(hf["id"])
                if payload.get("sketch_name"):
                    sketch_names_needed.add(payload["sketch_name"])
        elif kind == "combine":
            tgt = payload.get("target_body_id")
            tools = set(payload.get("tool_body_ids") or [])
            if tgt in interesting or tools & interesting:
                # Prefer combines that target our body or produce/consume our tools
                if tgt == body_id or (tgt in interesting and tools & interesting) or (
                    tgt in interesting and body_id in tools
                ):
                    include_fids.add(hf["id"])
                elif tgt in interesting or (body_id in tools):
                    include_fids.add(hf["id"])
                elif tools & interesting and tgt in interesting:
                    include_fids.add(hf["id"])
        elif kind == "move_copy":
            src = set(payload.get("body_ids") or [])
            res = set(payload.get("result_body_ids") or [])
            if src & interesting or res & interesting:
                # Include if creates tools for our combines OR moves our body
                # Skip pure hatch create MoveCopy5 copy of shell→141 unless body is 141
                if body_id in src or body_id in res or (res & interesting - {body_id}) or (src & interesting):
                    if payload.get("copy") and body_id in src and body_id not in res:
                        # copy FROM our body to something else — note but include for timeline
                        include_fids.add(hf["id"])
                    else:
                        include_fids.add(hf["id"])
        elif kind in ("mirror", "rectangular_pattern"):
            src = set(payload.get("body_ids") or [])
            res = set(payload.get("new_body_ids") or []) | set(payload.get("result_body_ids") or [])
            if src & interesting or res & interesting:
                include_fids.add(hf["id"])
        elif kind == "revolve":
            tids = set(payload.get("target_body_ids") or [])
            nids = set(payload.get("new_body_ids") or [])
            if tids & interesting or nids & interesting:
                include_fids.add(hf["id"])
                if payload.get("sketch_name"):
                    sketch_names_needed.add(payload["sketch_name"])

    # Add datum+sketch fids for needed sketches
    for name in list(sketch_names_needed):
        sk = sketches_by_name.get(name)
        if not sk:
            continue
        include_fids.add(sk["feature_id"])
        # typically datum is fid-1
        if sk["feature_id"] - 1 in datums_by_fid:
            include_fids.add(sk["feature_id"] - 1)
        # also match by plane datum
        plane_id = (sk.get("plane") or {}).get("datum_id")
        if plane_id in datums_by_id:
            include_fids.add(datums_by_id[plane_id]["feature_id"])

    # Also include datums/sketches that sit between included extrudes if they're the extrude's own
    # (already handled)

    # Build ordered feature_sequence
    feature_sequence = []
    feature_sequence_summary = []
    sketches_used = []
    sketches_dict = {}

    for hf in hist:
        if hf["id"] not in include_fids:
            continue
        got = payload_for(hf)
        if not got:
            continue
        kind, payload = got
        if kind == "datum_plane":
            entry = {
                "kind": "datum_plane",
                "name": payload["name"],
                "feature_id": payload["feature_id"],
                "basis": payload.get("basis"),
                "source": payload.get("source"),
                "payload_full": payload,
            }
            feature_sequence.append(entry)
            feature_sequence_summary.append(
                summarize_feature("datum_plane", {**payload, "feature_id": payload["feature_id"]})
            )
        elif kind == "sketch":
            enriched = enrich_sketch(payload, datums_by_fid, datums_by_id)
            entry = {"kind": "sketch", "name": payload["name"], "feature_id": payload["feature_id"], "sketch": enriched}
            feature_sequence.append(entry)
            feature_sequence_summary.append(
                {
                    "feature_id": payload["feature_id"],
                    "name": payload["name"],
                    "kind": "sketch",
                    "entity_count": enriched["geometry"]["entity_count"],
                    "entity_types": enriched["geometry"]["entity_types"],
                    "point_bbox_uv": enriched["geometry"]["point_bbox_uv"],
                    "plane_datum_id_field": enriched["plane_datum_id_field"],
                    "basis_origin": (payload.get("basis") or {}).get("origin"),
                }
            )
            sketches_used.append(payload["name"])
            sketches_dict[payload["name"]] = enriched
        elif kind == "extrude":
            sk_name = payload.get("sketch_name")
            sk_embed = None
            if sk_name and sk_name in sketches_by_name:
                sk_embed = enrich_sketch(sketches_by_name[sk_name], datums_by_fid, datums_by_id)
                sketches_dict.setdefault(sk_name, sk_embed)
                if sk_name not in sketches_used:
                    sketches_used.append(sk_name)
            entry = {
                "kind": "extrude",
                "name": payload["name"],
                "feature_id": payload["feature_id"],
                "operation": payload.get("operation"),
                "extent": payload.get("extent"),
                "flip": payload.get("flip"),
                "taper_angle_deg": payload.get("taper_angle_deg"),
                "profile_indices": payload.get("profile_indices"),
                "sketch_name": sk_name,
                "target_body_ids": payload.get("target_body_ids"),
                "new_body_ids": payload.get("new_body_ids"),
                "source_face": payload.get("source_face"),
                "source_face_key": payload.get("source_face_key"),
                "source_face_basis": payload.get("source_face_basis"),
                "to_face_basis": payload.get("to_face_basis"),
                "sketch": sk_embed,
            }
            feature_sequence.append(entry)
            feature_sequence_summary.append(summarize_feature("extrude", payload))
        elif kind == "combine":
            entry = {
                "kind": "combine",
                "name": payload["name"],
                "feature_id": payload["feature_id"],
                "operation": payload.get("operation"),
                "target_body_id": payload.get("target_body_id"),
                "tool_body_ids": payload.get("tool_body_ids"),
                "keep_tools": payload.get("keep_tools"),
                "type": "combine",
            }
            feature_sequence.append(entry)
            feature_sequence_summary.append(summarize_feature("combine", payload))
        elif kind in ("move_copy", "mirror", "rectangular_pattern"):
            entry = {"kind": kind, **{k: v for k, v in payload.items() if k != "data_base64"}}
            feature_sequence.append(entry)
            feature_sequence_summary.append(summarize_feature(kind, payload))
        elif kind == "revolve":
            sk_name = payload.get("sketch_name")
            sk_embed = None
            if sk_name and sk_name in sketches_by_name:
                sk_embed = enrich_sketch(sketches_by_name[sk_name], datums_by_fid, datums_by_id)
            entry = {"kind": "revolve", **{k: v for k, v in payload.items()}, "sketch": sk_embed}
            feature_sequence.append(entry)
            feature_sequence_summary.append(summarize_feature("revolve", payload))

    # Body ownership
    as_owner = []
    as_tool = []
    for bf in model["body_features"]:
        if bf.get("type") != "combine":
            continue
        if bf.get("target_body_id") == body_id:
            as_owner.append(
                {
                    "name": bf["name"],
                    "feature_id": bf["feature_id"],
                    "operation": bf.get("operation"),
                    "tool_body_ids": bf.get("tool_body_ids"),
                    "keep_tools": bf.get("keep_tools"),
                }
            )
        if body_id in (bf.get("tool_body_ids") or []):
            as_tool.append(
                {
                    "name": bf["name"],
                    "feature_id": bf["feature_id"],
                    "target_body_id": bf.get("target_body_id"),
                    "operation": bf.get("operation"),
                    "keep_tools": bf.get("keep_tools"),
                }
            )

    creator = None
    for e in model["extrudes"]:
        if e.get("operation") == "new_body" and body_id in (e.get("new_body_ids") or []):
            creator = f"{e['name']} (new_body)"
            break
    if creator is None:
        for bf in model["body_features"]:
            if bf.get("type") == "move_copy" and bf.get("copy") and body_id in (bf.get("result_body_ids") or []):
                creator = f"{bf['name']} (copy of body {bf.get('body_ids')} → {body_id})"
                break

    # VERIFY gaps: stale datum ids
    verify_gaps = []
    for name, sk in sketches_dict.items():
        plane_id = sk.get("plane_datum_id_field")
        datum = sk.get("datum") or {}
        basis_origin = (sk.get("basis") or {}).get("origin")
        chain_origin = (datum.get("basis") or {}).get("origin")
        native = datums_by_id.get(plane_id)
        native_origin = (native.get("basis") or {}).get("origin") if native else None
        if native_origin is not None and basis_origin is not None and native_origin != basis_origin:
            verify_gaps.append(
                {
                    "topic": "stale_sketch_plane_datum_id",
                    "feature": name,
                    "detail": (
                        f"Native sketch.plane.datum_id={plane_id} origin={native_origin} but "
                        f"sketch.basis.origin={basis_origin} matches chain datum "
                        f"{datum.get('feature_id')}. JSONC must use chain datum / basis origin."
                    ),
                }
            )

    # AABB
    aabb = {
        "review_stl_assembly_coordinates": stl_aabb(review_stl) if review_stl else None,
        "review_stl_alt": stl_aabb(review_stl_alt) if review_stl_alt else None,
        "match": {"blank_doc_replay_aabb": None, "status": "pending_jsonc_rebuild"},
    }
    # seed sketch bbox if Extrude1 present
    seed_sk = sketches_dict.get("S02 A continuous exoskeleton 160OD 152ID 210L")
    if seed_sk:
        aabb["seed_sketch_bbox_uv"] = seed_sk["geometry"]["point_bbox_uv"]

    # Counts
    kind_counts = Counter(f["kind"] for f in feature_sequence)

    out = {
        "generated_from": "Roller-300.nbcad / model.json",
        "schema_version": model.get("schema_version"),
        "body": {
            "body_id": body_id,
            "role": role,
            "appearance": appearance,
            "created_by": creator,
            "body_features_as_owner": as_owner or None,
            "used_as_tool_on": as_tool or None,
            "interesting_bodies_in_dump": sorted(interesting),
            "excluded_bodies": sorted(exclude_bodies),
            "note": (
                f"Body {body_id} ({role}) dump includes create/modify features plus tool-body "
                f"prerequisites (excluding {sorted(exclude_bodies) if exclude_bodies else 'none'}). "
                "Do not invent geometry — port from this dump only."
            ),
        },
        "feature_sequence": feature_sequence,
        "feature_sequence_summary": feature_sequence_summary,
        "feature_counts": dict(kind_counts),
        "feature_sequence_length": len(feature_sequence),
        "sketches_used_in_order": sketches_used,
        "sketches": sketches_dict,
        "verify_gaps": verify_gaps,
        "aabb_comparison": aabb,
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--body", type=int, default=32)
    ap.add_argument("--role", default="main_shell")
    ap.add_argument("--exclude", type=int, nargs="*", default=[141], help="Bodies to not transitively expand")
    ap.add_argument("--out-json", type=Path, default=None)
    ap.add_argument("--out-md", type=Path, default=None)
    args = ap.parse_args()

    model = load_model(ROOT / "Roller-300.nbcad")
    review = ROOT / "first-prints/shell-first-review/main-shell-assembly-coordinates.stl"
    review_alt = ROOT / "first-prints/shell-first-review/main-shell-axle-vertical.stl"
    dump = dump_body(model, args.body, args.role, review, review_alt, set(args.exclude or []))

    # Guidance for shell
    dump["timeline_context"] = {
        "seed": "Extrude1 new_body from S02 A (OD160/ID152 × 210L)",
        "hatch_dependency": {
            "note": "MoveCopy5 copies body 32 → 141 (identity). Hatch chapter blocked until this shell dump is JSONC-ported.",
            "combine16": "Combine16 cut tgt=32 tools=[141] keep_tools=true — shell opening for hatch; tool 141 is hatch chapter (excluded from transitive expand).",
        },
        "excluded_hatch_chain": (
            "Body 141 and its local Extrude88/Combine4/fastener patterns are in hatch-141 dump; "
            "shell dump records Combine16 reference only."
        ),
    }
    dump["jsonc_rebuild_guidance"] = {
        "do_not_invent": True,
        "chapter_suggestion": "design/design_v0_1_barrel_shell.nbcad.jsonc",
        "order": [
            "Port Extrude1 seed tube (S02 A) exactly — OD160/ID152, extent 210, flip true",
            "Replay all join/cut extrudes targeting body 32 in fid order with exact sketch entities",
            "Replay combines targeting 32 with tool bodies created in-chapter (or retained)",
            "S03 shell-side features (lap ledge / radial cuts) after hatch copy timing — see fids in summary",
            "Combine16 needs hatch body 141 (keep_tools) — coordinate with hatch chapter or retain solid",
            "Blank-doc replay; AABB vs first-prints/shell-first-review/main-shell-assembly-coordinates.stl",
        ],
        "partial_port_ok": (
            "Dump is SoT this pass. JSONC rebuild is follow-up — do not invent blocks; "
            "may stage seed Extrude1 only as scaffold if dump is complete."
        ),
        "assemble_coordination": "barrel_shell before structural_hatch. Hatch MoveCopy5 requires shell solid.",
        "next_after_dump": "shell JSONC chapter from this dump; then finish hatch blank-doc replay",
    }

    # Extra VERIFY for shell
    dump["verify_gaps"].extend(
        [
            {
                "topic": "hatch_tool_dependency",
                "feature": "Combine16",
                "detail": (
                    "Combine16 cuts shell 32 with hatch body 141 (keep_tools). "
                    "Full final shell AABB matching review STL needs hatch solid or hatch chapter first. "
                    "Early shell port may compare pre-Combine16 AABB separately."
                ),
            },
            {
                "topic": "transient_new_body_ids",
                "feature": "join/cut extrudes",
                "detail": (
                    "Join/cut extrudes list transient new_body_ids auto-booleaned into 32. "
                    "Do not keep as SoT bodies unless visibility says so."
                ),
            },
            {
                "topic": "no_fillet_chamfer_hole_features",
                "feature": "document",
                "detail": "Native file has zero fillet/chamfer/hole features — all detail is sketch+extrude(+combine/pattern).",
            },
        ]
    )

    out_json = args.out_json or ROOT / f"design/native-port/{args.role}-{args.body}.json"
    out_md = args.out_md or ROOT / f"design/native-port/{args.role}-{args.body}.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(dump, indent=2) + "\n")
    print(f"Wrote {out_json} ({out_json.stat().st_size} bytes)")
    print(f"features={dump['feature_sequence_length']} counts={dump['feature_counts']}")
    aabb = dump["aabb_comparison"].get("review_stl_assembly_coordinates")
    if aabb:
        print(
            f"AABB {aabb['dx']:.4f}x{aabb['dy']:.4f}x{aabb['dz']:.4f} "
            f"@ ({aabb['xmin']:.4f},{aabb['ymin']:.4f},{aabb['zmin']:.4f})"
        )

    # Markdown
    md = render_md(dump, args.role, args.body)
    out_md.write_text(md)
    print(f"Wrote {out_md} ({out_md.stat().st_size} bytes)")


def render_md(dump: dict, role: str, body_id: int) -> str:
    body = dump["body"]
    aabb = dump["aabb_comparison"]
    stl = aabb.get("review_stl_assembly_coordinates") or {}
    lines = []
    lines.append(f"# {role} (body {body_id}) — native feature dump")
    lines.append("")
    lines.append("Source: `Roller-300.nbcad` → `model.json` (schema 7). "
                 f"Structured twin: `{role}-{body_id}.json`.")
    lines.append("**This pass is dump-only — no invented JSONC geometry.**")
    lines.append("")
    lines.append("## Creation")
    lines.append(f"- **{body.get('created_by')}**")
    if body.get("body_features_as_owner"):
        owners = ", ".join(
            f"**{c['name']}** ({c['operation']} tools {c['tool_body_ids']})"
            for c in body["body_features_as_owner"]
        )
        lines.append(f"- Owning combines: {owners}")
    if body.get("used_as_tool_on"):
        tools = ", ".join(
            f"**{c['name']}**→{c['target_body_id']}" for c in body["used_as_tool_on"]
        )
        lines.append(f"- Used as tool: {tools}")
    lines.append(f"- Interesting bodies in dump: `{body.get('interesting_bodies_in_dump')}`")
    lines.append(f"- Excluded from transitive expand: `{body.get('excluded_bodies')}`")
    lines.append("")
    lines.append(f"## Feature sequence ({dump['feature_sequence_length']} features)")
    lines.append("")
    lines.append("| fid | Feature | Kind | Notes |")
    lines.append("|-----|---------|------|-------|")
    for s in dump["feature_sequence_summary"]:
        kind = s.get("kind")
        notes = []
        if s.get("operation"):
            notes.append(str(s["operation"]))
        if s.get("extent"):
            notes.append(f"extent {s['extent']}")
        if s.get("sketch_name"):
            notes.append(s["sketch_name"])
        if s.get("target_body_ids"):
            notes.append(f"tgt {s['target_body_ids']}")
        if s.get("target_body_id") is not None:
            notes.append(f"tgt [{s['target_body_id']}]")
        if s.get("tool_body_ids"):
            notes.append(f"tools {s['tool_body_ids']}")
        if s.get("new_body_ids"):
            notes.append(f"new {s['new_body_ids']}")
        if s.get("body_ids") is not None and kind in ("move_copy", "mirror", "rectangular_pattern"):
            notes.append(f"from {s['body_ids']}")
        if s.get("copy") is not None:
            notes.append(f"copy={s['copy']}")
        if s.get("translation"):
            notes.append(f"T {s['translation']}")
        if s.get("rotation") and s["rotation"] != [0.0, 0.0, 0.0, 1.0]:
            notes.append(f"quat {s['rotation']}")
        if s.get("count"):
            notes.append(f"count {s['count']} spacing {s.get('spacing')}")
        if s.get("entity_count") is not None:
            notes.append(f"ents {s['entity_count']} {s.get('entity_types')}")
        if s.get("point_bbox_uv"):
            b = s["point_bbox_uv"]
            notes.append(f"UV {b['du']:.3g}×{b['dv']:.3g}")
        if kind == "datum_plane":
            # pull basis from full sequence
            pass
        note_s = " · ".join(notes) if notes else ""
        # escape pipes
        note_s = note_s.replace("|", "/")
        lines.append(f"| {s.get('feature_id')} | {s.get('name')} | {kind} | {note_s} |")
    lines.append("")
    lines.append("## Feature counts")
    lines.append("")
    for k, v in sorted(dump["feature_counts"].items()):
        lines.append(f"- **{k}**: {v}")
    lines.append("")
    lines.append("## AABB check")
    lines.append("")
    lines.append("| Source | AABB (mm) |")
    lines.append("|--------|-----------|")
    if aabb.get("seed_sketch_bbox_uv"):
        b = aabb["seed_sketch_bbox_uv"]
        lines.append(
            f"| Seed sketch S02 A UV | U[{b['umin']},{b['umax']}] V[{b['vmin']},{b['vmax']}] → "
            f"**{b['du']} × {b['dv']}** |"
        )
    if stl:
        lines.append(
            f"| `{stl['path']}` | X[{stl['xmin']:.4f},{stl['xmax']:.4f}] "
            f"Y[{stl['ymin']:.4f},{stl['ymax']:.4f}] Z[{stl['zmin']:.4f},{stl['zmax']:.4f}] → "
            f"**{stl['dx']:.4f} × {stl['dy']:.4f} × {stl['dz']:.4f}** (tris {stl['tri_count']}) |"
        )
    alt = aabb.get("review_stl_alt")
    if alt:
        lines.append(
            f"| `{alt['path']}` | X[{alt['xmin']:.4f},{alt['xmax']:.4f}] "
            f"Y[{alt['ymin']:.4f},{alt['ymax']:.4f}] Z[{alt['zmin']:.4f},{alt['zmax']:.4f}] → "
            f"**{alt['dx']:.4f} × {alt['dy']:.4f} × {alt['dz']:.4f}** (tris {alt['tri_count']}) |"
        )
    lines.append("| Blank-doc JSONC replay | **PENDING** — dump-only this pass |")
    lines.append("")
    lines.append("## VERIFY gaps (before JSONC rebuild)")
    for i, g in enumerate(dump["verify_gaps"], 1):
        lines.append(f"{i}. **{g['topic']}** ({g.get('feature')}): {g['detail']}")
    lines.append("")
    lines.append("## How the JSONC chapter should be rebuilt")
    for i, step in enumerate(dump["jsonc_rebuild_guidance"]["order"], 1):
        lines.append(f"{i}. {step}")
    lines.append("")
    lines.append(f"See `{role}-{body_id}.json` for full sketch entities, datums, and payloads.")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
