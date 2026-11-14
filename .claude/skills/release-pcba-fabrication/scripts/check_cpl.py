#!/usr/bin/env python3
"""Check a KiCad position file for JLCPCB rotation and offset problems, and write
a JLCPCB CPL with only explicitly approved corrections applied.

Inputs:
  --board        the saved .kicad_pcb
  --pos          `kicad-cli pcb export pos --format csv --units mm --side both`
  --corrections  optional cpl-corrections-v1 JSON (per footprint, with evidence)

Checks (each one can block):
  1. reference set: every placeable footprint (not DNP, not excluded from position
     files) is in the pos file exactly once, and nothing extra is there;
  2. export transform: every pos row equals the board position under ONE
     transform (PosX = x - ox, PosY = -(y - oy)) and rotation matches the board;
     a mixed or mirrored export is a blocker;
  3. origin offset: the footprint origin vs the centre of its pads' bounding box.
     JLCPCB places the package centre at Mid X/Mid Y, so an origin on pin 1 or a
     tab shifts the part. Offsets above --offset-warn-mm need a correction entry;
  4. rotation: every polarised or asymmetric part (more than two pads, or a
     polarised reference prefix) needs a correction entry for its footprint and
     side, even if the entry says 0, with evidence from JLCPCB's preview or the
     part's tape/library orientation.

What it cannot see: JLCPCB's own library model for each part. Its zero-angle
convention is only known from their placement preview, which is why rotation
entries need evidence. Through-hole parts are checked too if they are in the
pos file.

Exit status: 0 PASS, 1 BLOCKED (findings listed), 2 bad input.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path

POLARISED_PREFIXES = ("U", "Q", "D", "LED", "J", "P", "CN", "Y", "X", "SW", "K", "T", "BT", "IC", "PS")
TOKEN = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')


# ---------------------------------------------------------------- s-expression
def parse_sexpr(text: str):
    stack, cur = [], []
    for tok in TOKEN.findall(text):
        if tok == "(":
            stack.append(cur)
            cur = []
        elif tok == ")":
            done, cur = cur, stack.pop()
            cur.append(done)
        else:
            cur.append(tok[1:-1].replace('\\"', '"') if tok.startswith('"') else tok)
    return cur[0] if cur else []


def child(node, name):
    for item in node:
        if isinstance(item, list) and item and item[0] == name:
            return item
    return None


def children(node, name):
    return [i for i in node if isinstance(i, list) and i and i[0] == name]


# ---------------------------------------------------------------- board model
def load_board(path: Path) -> dict:
    root = parse_sexpr(path.read_text(encoding="utf-8"))
    if not root or root[0] != "kicad_pcb":
        raise ValueError(f"{path}: not a .kicad_pcb file")
    parts = {}
    for fp in children(root, "footprint"):
        lib = fp[1] if len(fp) > 1 and isinstance(fp[1], str) else ""
        layer = (child(fp, "layer") or [None, "F.Cu"])[1]
        at = child(fp, "at") or ["at", "0", "0"]
        x, y = float(at[1]), float(at[2])
        rot = float(at[3]) if len(at) > 3 else 0.0
        ref = ""
        for prop in children(fp, "property"):
            if len(prop) > 2 and prop[1] == "Reference":
                ref = prop[2]
        if not ref:
            fp_text = [t for t in children(fp, "fp_text") if len(t) > 2 and t[1] == "reference"]
            ref = fp_text[0][2] if fp_text else ""
        attr = child(fp, "attr") or []
        flags = set(a for a in attr[1:] if isinstance(a, str))
        if child(fp, "dnp") is not None:
            flags.add("dnp")
        pads = []
        for pad in children(fp, "pad"):
            pat = child(pad, "at")
            if pat is None:
                continue
            ptype = pad[2] if len(pad) > 2 else ""
            if ptype == "np_thru_hole":
                continue
            pads.append((str(pad[1]), float(pat[1]), float(pat[2])))
        parts[ref] = {"lib": lib, "side": "bottom" if layer.startswith("B.") else "top",
                      "x": x, "y": y, "rot": rot, "flags": flags, "pads": pads}
    return parts


def load_pos(path: Path) -> dict:
    rows = {}
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            ref = row.get("Ref") or row.get("Designator")
            if ref is None:
                raise ValueError(f"{path}: expected KiCad CSV columns Ref,Val,Package,PosX,PosY,Rot,Side")
            if ref in rows:
                rows[ref]["dup"] = True
                continue
            rows[ref] = {"x": float(row["PosX"]), "y": float(row["PosY"]), "rot": float(row["Rot"]),
                         "side": row["Side"].strip().lower(), "package": row.get("Package", ""),
                         "val": row.get("Val", "")}
    return rows


def norm(a: float) -> float:
    a = a % 360.0
    return 0.0 if abs(a - 360.0) < 1e-6 else a


def rotate(dx: float, dy: float, deg: float) -> tuple:
    """Local footprint vector -> board vector (KiCad: Y down, positive angle CCW on screen)."""
    r = math.radians(deg)
    return (dx * math.cos(r) + dy * math.sin(r), -dx * math.sin(r) + dy * math.cos(r))


def pad_centre(pads) -> tuple | None:
    if not pads:
        return None
    xs, ys = [p[1] for p in pads], [p[2] for p in pads]
    return ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)


def needs_rotation_evidence(ref: str, part: dict) -> bool:
    prefix = re.match(r"[A-Za-z]+", ref)
    prefix = prefix.group(0).upper() if prefix else ""
    return len(part["pads"]) > 2 or prefix in POLARISED_PREFIXES


# ---------------------------------------------------------------- check
def check(board: dict, pos: dict, corrections: dict, offset_warn: float, tol: float):
    findings, rows = [], []
    placeable = {r: p for r, p in board.items()
                 if r and not ({"dnp", "exclude_from_pos_files"} & p["flags"])}
    missing = sorted(set(placeable) - set(pos))
    extra = sorted(set(pos) - set(placeable))
    dups = sorted(r for r, v in pos.items() if v.get("dup"))
    if missing:
        findings.append(f"refs on board but not in pos file: {', '.join(missing)}")
    if extra:
        findings.append(f"refs in pos file but not placeable on board: {', '.join(extra)}")
    if dups:
        findings.append(f"duplicate pos rows: {', '.join(dups)}")

    common = sorted(set(placeable) & set(pos))
    if common:
        r0 = common[0]
        ox = board[r0]["x"] - pos[r0]["x"]
        oy = board[r0]["y"] + pos[r0]["y"]
        bad = []
        for r in common:
            b, p = board[r], pos[r]
            if (abs(b["x"] - ox - p["x"]) > tol or abs(-(b["y"] - oy) - p["y"]) > tol
                    or abs(((norm(b["rot"]) - norm(p["rot"]) + 180) % 360) - 180) > 0.01
                    or b["side"] != p["side"]):
                bad.append(r)
        if bad:
            findings.append("pos rows not explained by one export transform "
                            f"(origin {ox:.3f},{oy:.3f}, Y flipped): {', '.join(bad[:20])}")

    fp_corr = corrections.get("footprints", {})
    for r in common:
        b, p = board[r], pos[r]
        key = b["lib"]
        entry = fp_corr.get(key, {}).get(p["side"])
        status, notes = "PASS", []
        mid_x, mid_y, rot = p["x"], p["y"], p["rot"]
        centre = pad_centre(b["pads"])
        local_off = centre if centre else (0.0, 0.0)
        off_len = math.hypot(*local_off)
        if entry:
            if not str(entry.get("evidence", "")).strip():
                findings.append(f"{r}: correction for {key}/{p['side']} has no evidence")
                status = "BLOCKED"
            dx, dy = entry.get("offset_mm", [0.0, 0.0])
            bx, by = rotate(dx, dy, b["rot"])
            mid_x, mid_y = p["x"] + bx, p["y"] - by
            rot = norm(p["rot"] + float(entry.get("rotation_deg", 0.0)))
            notes.append(f"correction applied ({entry.get('rotation_deg', 0)} deg, offset {dx},{dy})")
        else:
            if off_len > offset_warn:
                findings.append(f"{r} ({key}): origin is {off_len:.3f} mm from pad centre "
                                f"(local {local_off[0]:.3f},{local_off[1]:.3f}); add an offset correction "
                                "or move the footprint origin to the package centre")
                status = "BLOCKED"
            if needs_rotation_evidence(r, b):
                findings.append(f"{r} ({key}, {p['side']}): rotation not verified; add a correction "
                                "entry (rotation_deg, even 0) with evidence from JLCPCB's preview")
                status = "BLOCKED"
        rows.append({"Designator": r, "Mid X": f"{mid_x:.4f}mm", "Mid Y": f"{mid_y:.4f}mm",
                     "Layer": "Top" if p["side"] == "top" else "Bottom", "Rotation": f"{norm(rot):g}",
                     "_status": status, "_footprint": key, "_origin_offset_mm": round(off_len, 4),
                     "_notes": "; ".join(notes)})
    return findings, rows


def self_test() -> int:
    board_text = """(kicad_pcb (version 20260206)
      (footprint "Resistor_SMD:R_0603" (layer "F.Cu") (at 10 20 0)
        (property "Reference" "R101") (attr smd)
        (pad "1" smd rect (at -0.8 0 0)) (pad "2" smd rect (at 0.8 0 0)))
      (footprint "Package_TO_SOT_SMD:SOT-23" (layer "F.Cu") (at 30 20 90)
        (property "Reference" "U101") (attr smd)
        (pad "1" smd rect (at -0.95 1.1 90)) (pad "2" smd rect (at 0.95 1.1 90)) (pad "3" smd rect (at 0 -1.1 90)))
      (footprint "Conn:Pin1Origin" (layer "F.Cu") (at 50 20 0)
        (property "Reference" "J101") (attr smd)
        (pad "1" smd rect (at 0 0 0)) (pad "2" smd rect (at 2 0 0)))
      (footprint "Resistor_SMD:R_0603" (layer "F.Cu") (at 70 20 0)
        (property "Reference" "R102") (attr smd dnp)
        (pad "1" smd rect (at -0.8 0 0)) (pad "2" smd rect (at 0.8 0 0))))"""
    board = load_board_text(board_text)
    pos = {"R101": {"x": 10, "y": -20, "rot": 0, "side": "top"},
           "U101": {"x": 30, "y": -20, "rot": 90, "side": "top"},
           "J101": {"x": 50, "y": -20, "rot": 0, "side": "top"}}
    findings, _ = check(board, pos, {}, 0.05, 0.002)
    joined = " | ".join(findings)
    assert "U101" in joined and "rotation not verified" in joined, joined
    assert "J101" in joined and "origin is 1.000 mm" in joined, joined
    assert "R101" not in joined and "R102" not in joined, joined
    corr = {"schema": "cpl-corrections-v1", "footprints": {
        "Package_TO_SOT_SMD:SOT-23": {"top": {"rotation_deg": 180, "evidence": "JLCPCB preview rev A"}},
        "Conn:Pin1Origin": {"top": {"rotation_deg": 0, "offset_mm": [1, 0], "evidence": "drawing"}}}}
    findings, rows = check(board, pos, corr, 0.05, 0.002)
    assert findings == [], findings
    j = next(r for r in rows if r["Designator"] == "J101")
    assert j["Mid X"] == "51.0000mm", j
    u = next(r for r in rows if r["Designator"] == "U101")
    assert u["Rotation"] == "270", u
    bad_pos = dict(pos)
    bad_pos["R101"] = {"x": 10, "y": 20, "rot": 0, "side": "top"}
    findings, _ = check(board, bad_pos, corr, 0.05, 0.002)
    assert any("one export transform" in f for f in findings), findings
    # rotation of a local offset: +X local on a 90 deg part points up the screen (-Y board)
    bx, by = rotate(1, 0, 90)
    assert abs(bx) < 1e-9 and abs(by + 1) < 1e-9
    print("self-test PASS")
    return 0


def load_board_text(text: str) -> dict:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "b.kicad_pcb"
        p.write_text(text, encoding="utf-8")
        return load_board(p)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--board", type=Path)
    ap.add_argument("--pos", type=Path)
    ap.add_argument("--corrections", type=Path)
    ap.add_argument("--out", type=Path, help="JLCPCB CPL CSV to write")
    ap.add_argument("--report", type=Path, help="JSON report to write")
    ap.add_argument("--offset-warn-mm", type=float, default=0.05)
    ap.add_argument("--tolerance-mm", type=float, default=0.002)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return self_test()
    if not args.board or not args.pos:
        ap.error("--board and --pos are required")
    try:
        board = load_board(args.board)
        pos = load_pos(args.pos)
        corrections = json.loads(args.corrections.read_text(encoding="utf-8")) if args.corrections else {}
        if corrections and corrections.get("schema") != "cpl-corrections-v1":
            raise ValueError("corrections file must have schema cpl-corrections-v1")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    findings, rows = check(board, pos, corrections, args.offset_warn_mm, args.tolerance_mm)
    if args.out:
        with args.out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
            w.writeheader()
            for r in rows:
                w.writerow({k: r[k] for k in w.fieldnames})
    status = "PASS" if not findings else "BLOCKED"
    if args.report:
        args.report.write_text(json.dumps({"schema": "cpl-check-v1", "status": status,
                                           "board": str(args.board), "pos": str(args.pos),
                                           "findings": findings, "rows": rows}, indent=2),
                               encoding="utf-8")
    print(f"placed parts checked: {len(rows)}")
    for f in findings:
        print(f"FAIL {f}")
    print(status if not findings else f"BLOCKED: {len(findings)} finding(s)")
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
