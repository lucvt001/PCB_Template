# Drawing a new schematic in KiCad

Use this when creating a schematic (or a new sheet) rather than reviewing one.

## Before drawing

1. Product brief and architecture exist (or run `/plan-electronic-product`).
2. Datasheets, and EVM PDFs where available, for every IC, module, regulator, and
   connector are in `pcb/datasheets/`, and have been read (see the circuit SKILL).
3. Plan the hierarchy: one sheet per functional block (e.g. power input, regulators,
   MCU, comms, motor drive, sensors, connectors). List each sheet's hierarchical
   signals and their direction before drawing.

## Sheets and connections

- Root sheet: block diagram of hierarchical sheet symbols with their sheet pins
  wired to each other. This is page 1 only if it holds components; otherwise the
  first block sheet's components start at the page number KiCad assigns to it.
- Between sheets: **hierarchical labels and sheet pins**, typed correctly (input,
  output, bidirectional, passive). No global labels for signals.
- Power: KiCad power symbols (`+3V3`, `+5V`, `VBAT`, `GND`), consistent names
  across sheets. Add `PWR_FLAG` only where a rail is really driven by a connector
  or regulator ERC can't see.
- Within a sheet: wires for local connections; local labels only for long or
  repeated connections (buses).
- Net names: give every meaningful net a name (`CAN1_H`, `MOTOR_A`, `I2C1_SDA`) so
  netlist assertions and layout are readable.
- Unused pins: a no-connect flag on every pin deliberately left open (checked
  against the datasheet), so ERC flags the rest.

## Symbols and fields

- **Ask the user about every selectable IC option** (EN, PG, UVLO, mode/config
  pins, connector types, etc.) before drawing; never assume. Don't ask about
  capacitor ratings or other small details.
- **Values:** capacitors as capacitance_voltage (`1u_50V`); resistors from E12
  (or E24); capacitors from standard values.

- Use KiCad's standard symbols when the pinout matches the exact part; otherwise
  create the symbol in the project library `pcb/sym/` from the datasheet pin table,
  with correct pin types (power in/out, input, output, bidirectional, passive, open
  collector) so ERC is meaningful.
- Fields: Value; `MPN` and `LCSC` (filled in the sourcing session); `Datasheet`
  pointing at the file in `pcb/datasheets/`. Footprints may be provisional here; the
  sourcing session assigns and checks the final ones.
- Mark DNP parts (hedges, optional termination) with KiCad's DNP attribute.

## Sheet arrangement

- Place the main IC in the middle of its sheet, support circuitry around it.
- One dashed box (graphic rectangle, titled) per functional sub-circuit, with the
  datasheet/EVM explanation or equation as a text note beside it, tagged with its
  source section/page.
- Box text is minimal: only the equation or datasheet rationale, no part numbers.
  Text 40 mil, box title 70 mil.
- Keep each sub-circuit's wiring to the IC compact and visible; don't spread the
  connections out, so the human can cross-check against the datasheet/EVM.

## Annotation and checks

- Annotate multi-sheet designs with **page number x 100 + increment** (single-sheet designs use plain R1, C1, U1) ("Use first free number after
  sheet number x 100"): R101, C101, U101 on page 1; R201 on page 2.
- Run ERC with all severities and fix or explain every item; don't silence pin-type
  warnings by changing pin types to passive.
- Export the KiCad XML netlist, write `netlist-assertions.json` from the design
  intent, and run `scripts/assert_netlist.py`.
- Export the schematic PDF and check each page is readable (see
  `/schematic-humanizer` if it isn't).
