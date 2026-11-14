#!/usr/bin/env python3
"""Check design-intent assertions against an exported netlist.

Reads a KiCad XML netlist (`kicad-cli sch export netlist --format kicadxml`) or a
`schematic-connectivity-v1` JSON file, plus a `netlist-assertions-v1` JSON file, and
checks:

  must_connect      - pin (ref, pin) is on the named net
  must_not_connect  - two pins are on different nets (catches silent merges)
  must_be_open      - pin has no connection to any other pin
  net_pin_counts    - a named net has exactly N pins (merged nets have more,
                      split nets fewer)

What it cannot see: anything not in the netlist (copper, footprints, pad geometry,
component values in circuit terms). A must-connect *through* a series part fails,
by design - assert each side separately. An assertion file with no must_not_connect
entries is refused unless --allow-no-negative is given: a design never asked a
must-not-connect question has not been checked for shorts.

Exit status: 0 all pass, 1 any assertion fails, 2 bad input.
"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

Pin = tuple  # (ref, pin)


def load_netlist(path: Path) -> dict[str, set]:
    """Return {net_name: {(ref, pin), ...}}."""
    raw = path.read_text(encoding="utf-8-sig")
    nets: dict[str, set] = {}
    if raw.lstrip().startswith("<"):
        root = ET.fromstring(raw)
        nets_el = root.find("nets")
        if nets_el is None:
            raise ValueError(f"{path}: no <nets> element; is this a KiCad XML netlist?")
        for net in nets_el.findall("net"):
            name = net.get("name", "")
            nodes = {(n.get("ref", ""), n.get("pin", "")) for n in net.findall("node")}
            nets.setdefault(name, set()).update(nodes)
    else:
        data = json.loads(raw)
        if data.get("schema") != "schematic-connectivity-v1":
            raise ValueError(f"{path}: expected schema schematic-connectivity-v1")
        for net in data.get("nets", []):
            nodes = {(p["ref"], str(p["pin"])) for p in net.get("pins", [])}
            nets.setdefault(net["name"], set()).update(nodes)
    return nets


def pin_index(nets: dict[str, set]) -> dict[Pin, str]:
    index: dict[Pin, str] = {}
    for name, pins in nets.items():
        for p in pins:
            if p in index and index[p] != name:
                raise ValueError(f"pin {p[0]}.{p[1]} appears on two nets: {index[p]}, {name}")
            index[p] = name
    return index


def _pin(entry: dict, field: str = "") -> Pin:
    try:
        return (str(entry["ref"]), str(entry["pin"]))
    except (KeyError, TypeError):
        raise ValueError(f"assertion {field or entry!r} needs 'ref' and 'pin'")


def check(nets: dict[str, set], assertions: dict, allow_no_negative: bool = False) -> list[str]:
    if assertions.get("schema") != "netlist-assertions-v1":
        raise ValueError("assertions file must have schema netlist-assertions-v1")
    keys = ("must_connect", "must_not_connect", "must_be_open", "net_pin_counts")
    total = sum(len(assertions.get(k, []) or []) for k in keys)
    if total == 0:
        raise ValueError("assertion file is empty; an empty file passes vacuously and proves nothing")
    if not assertions.get("must_not_connect") and not allow_no_negative:
        raise ValueError("no must_not_connect assertions; add them or pass --allow-no-negative")

    index = pin_index(nets)
    failures: list[str] = []

    for a in assertions.get("must_connect", []):
        p = _pin(a, "must_connect")
        want = str(a["net"])
        got = index.get(p)
        if got != want:
            failures.append(f"must_connect {p[0]}.{p[1]} -> {want}: found {got or 'no net'}")

    for a in assertions.get("must_not_connect", []):
        pa, pb = _pin(a["a"], "must_not_connect.a"), _pin(a["b"], "must_not_connect.b")
        na, nb = index.get(pa), index.get(pb)
        if na is not None and na == nb:
            failures.append(f"must_not_connect {pa[0]}.{pa[1]} / {pb[0]}.{pb[1]}: both on {na}")

    for a in assertions.get("must_be_open", []):
        p = _pin(a, "must_be_open")
        name = index.get(p)
        if name is not None and len(nets[name]) > 1:
            others = sorted(f"{r}.{n}" for r, n in nets[name] if (r, n) != p)
            failures.append(f"must_be_open {p[0]}.{p[1]}: on {name} with {', '.join(others[:6])}")

    for name, count in (assertions.get("net_pin_counts") or {}).items():
        got = len(nets.get(name, ()))
        if got != int(count):
            failures.append(f"net_pin_counts {name}: expected {count}, found {got}")

    return failures


def self_test() -> int:
    xml = """<export><nets>
      <net code="1" name="+3V3"><node ref="U1" pin="1"/><node ref="C1" pin="1"/></net>
      <net code="2" name="GND"><node ref="U1" pin="2"/><node ref="C1" pin="2"/><node ref="U1" pin="5"/></net>
      <net code="3" name="unconnected-(U1-Pad4)"><node ref="U1" pin="4"/></net>
    </nets></export>"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "n.xml"
        path.write_text(xml, encoding="utf-8")
        nets = load_netlist(path)
    good = {
        "schema": "netlist-assertions-v1",
        "must_connect": [{"ref": "U1", "pin": "1", "net": "+3V3"}],
        "must_not_connect": [{"a": {"ref": "U1", "pin": "1"}, "b": {"ref": "U1", "pin": "2"}}],
        "must_be_open": [{"ref": "U1", "pin": "4"}],
        "net_pin_counts": {"GND": 3},
    }
    assert check(nets, good) == [], check(nets, good)
    bad = dict(good)
    bad["must_not_connect"] = [{"a": {"ref": "U1", "pin": "2"}, "b": {"ref": "U1", "pin": "5"}}]
    bad["net_pin_counts"] = {"GND": 2}
    bad["must_be_open"] = [{"ref": "U1", "pin": "5"}]
    assert len(check(nets, bad)) == 3, check(nets, bad)
    for empty in ({"schema": "netlist-assertions-v1"},
                  {"schema": "netlist-assertions-v1", "must_connect": good["must_connect"]}):
        try:
            check(nets, empty)
        except ValueError:
            pass
        else:
            raise AssertionError("vacuous or positive-only assertion file was accepted")
    print("self-test PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("netlist", nargs="?", type=Path, help="KiCad XML netlist or schematic-connectivity-v1 JSON")
    parser.add_argument("assertions", nargs="?", type=Path, help="netlist-assertions-v1 JSON")
    parser.add_argument("--allow-no-negative", action="store_true",
                        help="permit a file with no must_not_connect entries")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return self_test()
    if not args.netlist or not args.assertions:
        parser.error("netlist and assertions are required")
    try:
        nets = load_netlist(args.netlist)
        assertions = json.loads(args.assertions.read_text(encoding="utf-8-sig"))
        failures = check(nets, assertions, args.allow_no_negative)
    except (OSError, ValueError, KeyError, json.JSONDecodeError, ET.ParseError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    n = sum(len(assertions.get(k) or []) for k in ("must_connect", "must_not_connect", "must_be_open", "net_pin_counts"))
    print(f"netlist: {args.netlist} ({len(nets)} nets)  assertions: {n}")
    for line in failures:
        print(f"FAIL {line}")
    print("PASS" if not failures else f"BLOCKED: {len(failures)} failing assertion(s)")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
