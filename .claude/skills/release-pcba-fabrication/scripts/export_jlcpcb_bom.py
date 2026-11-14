#!/usr/bin/env python3
"""Make a JLCPCB BOM (Comment, Designator, Footprint, LCSC) from a KiCad XML netlist.

  kicad-cli sch export netlist --format kicadxml -o netlist.xml <name>.kicad_sch
  python export_jlcpcb_bom.py netlist.xml --out bom-jlcpcb.csv [--hand hand-assembly.csv]

Parts are grouped by (value, footprint, LCSC). DNP/excluded parts and parts with
no LCSC number are not put in the JLCPCB BOM: they are written to --hand (if
given) and listed on stderr so nothing is dropped silently. Exit 1 if a non-DNP
part lacks an LCSC number.
"""
import argparse, csv, re, sys
import xml.etree.ElementTree as ET


def natural(ref):
    m = re.match(r"([A-Za-z]+)(\d+)", ref)
    return (m.group(1), int(m.group(2))) if m else (ref, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("netlist")
    ap.add_argument("--out", required=True)
    ap.add_argument("--hand")
    a = ap.parse_args()
    groups, hand, missing = {}, [], []
    for c in ET.parse(a.netlist).getroot().iter("comp"):
        ref = c.get("ref")
        if ref.startswith("#"):
            continue
        value = (c.findtext("value") or "").strip()
        fp = (c.findtext("footprint") or "").strip()
        fields = {f.get("name"): (f.text or "").strip() for f in c.iter("field")}
        props = {p.get("name") for p in c.iter("property")}
        lcsc = fields.get("LCSC", "")
        if props & {"dnp", "exclude_from_board", "exclude_from_bom"}:
            hand.append((ref, value, fp, lcsc, "DNP/excluded"))
            continue
        if not lcsc:
            missing.append(ref)
            hand.append((ref, value, fp, lcsc, "no LCSC"))
            continue
        groups.setdefault((value, fp.split(":")[-1], lcsc), []).append(ref)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC"])
        for (v, fp, l), refs in sorted(groups.items(), key=lambda kv: natural(min(kv[1], key=natural))):
            w.writerow([v, ",".join(sorted(refs, key=natural)), fp, l])
    if a.hand:
        with open(a.hand, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Designator", "Value", "Footprint", "LCSC", "Reason"])
            w.writerows(sorted(hand, key=lambda r: natural(r[0])))
    for ref, v, fp, l, why in hand:
        print(f"not in JLCPCB BOM: {ref} ({v}) - {why}", file=sys.stderr)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
