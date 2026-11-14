# Netlist intent assertions

Adapted from `daishuge/pcb-skill` (MIT, see `../LICENSE-pcb-skill`).

ERC can pass with zero errors on a schematic whose nets resolve consistently to the
wrong thing. On the reference project five nets were silently merged (a switch node
into a card supply; I2S data and UART TX into ground) and only assertions against
the EDA's own exported netlist caught it. Gate the schematic on **intent**, not only
on ERC.

## What to assert

| class | meaning | catches |
|---|---|---|
| `must_connect` | pin (ref, pin) is on net N | missing or mis-labelled connections |
| `must_not_connect` | pin A and pin B are on different nets | silent merges and shorts |
| `must_be_open` | pin has no connection to any other pin | stray labels on NC pins |
| `net_pin_counts` | net N has exactly k pins | merged nets (too many) and split nets (too few) |

Write the negative assertions too: a design that has never been asked a
must-not-connect question has not been checked for shorts. Good candidates: every
rail against GND and against every other rail, every switch node against its
input and output, each data line of a bus against its neighbours, any pin tied to a
connector that carries a different voltage domain.

Write assertions from the **design intent** (architecture, datasheet pin tables,
connector pinouts), not by copying the current netlist; copying turns a wrong
netlist into the expected answer.

## File format

`.pcba-workflow/netlist-assertions.json`:

```json
{
  "schema": "netlist-assertions-v1",
  "must_connect": [
    {"ref": "U1", "pin": "1", "net": "+3V3"},
    {"ref": "J1", "pin": "A6", "net": "USB_DP"}
  ],
  "must_not_connect": [
    {"a": {"ref": "U1", "pin": "1"}, "b": {"ref": "U1", "pin": "8"}}
  ],
  "must_be_open": [
    {"ref": "U3", "pin": "7"}
  ],
  "net_pin_counts": {"+3V3": 14, "USB_DP": 3}
}
```

Pin identifiers are the pad numbers in the netlist (e.g. `A6` on a USB-C footprint),
not pin names. Net names are as KiCad exports them: in a hierarchical design a net
driven by a hierarchical label is named with its sheet path (e.g. `/Power/VBAT`),
and power-symbol nets keep their plain name (`+3V3`, `GND`). References follow the
page x 100 scheme (`U101`, `R203`).

## Running it

```bash
"$K" sch export netlist --format kicadxml -o ../.pcba-workflow/netlist.xml template.kicad_sch
python ../.claude/skills/design-and-review-circuit/scripts/assert_netlist.py \
  ../.pcba-workflow/netlist.xml ../.pcba-workflow/netlist-assertions.json
```

Exit 0 = all pass, 1 = an assertion failed (gate BLOCKED), 2 = bad input. The
script refuses an empty file and a file with no `must_not_connect` entries unless
`--allow-no-negative` is given. It also accepts `schematic-connectivity-v1` JSON.

Limits: it sees only the netlist. A must-connect through a series part correctly
fails - assert each side. Footprint pad numbering that does not match the symbol's
pin numbering is invisible here; that needs a pad-by-pad check against the
footprint/datasheet.

## Also part of the schematic gate

- every footprint resolves (no missing library entries), checked from the exported
  netlist or `kicad-cli` output, not by looking at the canvas;
- the BOM reconciles against the sourcing lock, with every deliberate substitution
  written down with a reason;
- save, close KiCad, reopen, and re-export before calling the gate: results from
  the running session are not evidence about the saved file.
