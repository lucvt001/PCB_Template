# Circuit audit checklist

## Architecture and state

- System boundary, sources, sinks, connectors, functional blocks, and data flow.
- Startup, shutdown, reset, programming, normal, sleep, fault, and partial-power
  states.
- Shared bus or memory ownership in every state; hardware-enforced break-before-
  make and safe defaults before firmware.
- Source of truth and consistency among schematic, netlist, BOM, firmware pin
  map, and architecture notes.

## Power and grounding

- Source range/capability, reverse current, OR-ing, inrush, hot plug, fusing,
  surge/ESD, and back-power paths.
- Rail tolerance, sequencing, dropout, transient response, stability capacitor
  requirements, thermal dissipation, and current budget by operating mode.
- Decoupling value and placement intent at every supply pin; bulk storage at
  entries and load steps.
- Ground/reference strategy based on return-current paths. A module with an
  integrated radio still needs the reference and keepout required by its
  manufacturer.

## Digital, memory, and interfaces

- Absolute maximums, VIH/VIL and VOH/VOL margin, tolerance to unpowered inputs,
  bidirectional contention, direction/enable polarity, pulls, and boot straps.
- Clock/access/setup/hold requirements, loading, fanout, topology, stubs, edge
  rate, and any asynchronous-domain crossing.
- Memory address capacity actually used, chip enables, output/write enables,
  unused address or bank pins, data ownership, and retained image assumptions.
- USB, Ethernet, CAN, RS-485, audio, display, sensor, RF, and other interfaces:
  correct connector pins, protection, bias/termination, impedance intent, and
  manufacturer layout requirements.

## Analog and physical concerns

- Input common-mode and range, source impedance, bias, filtering, reference
  quality, noise, gain, bandwidth, ADC drive, and calibration.
- Crystals/oscillators, feedback loops, switch nodes, antennas, current-sense
  paths, thermal pads, exposed interfaces, test points, and programming access.
- Package/pinout and footprint agreement with exact MPN; polarity and pin 1.

## Patterns that pass review and fail on the bench

Adapted from `daishuge/pcb-skill` (MIT, see `../LICENSE-pcb-skill`). Details and
examples in `plan-board-bringup/references/power-up-audit-patterns.md`.

- Every switch, jack, and connector contact traced in **both** states.
- Every current-setting value checked against the package's dissipation limit at
  the enclosure's real internal ambient, not 25 C.
- Every part operated at a point its datasheet tables actually specify; outside
  the tables there is no specification.
- No floating analogue node when switched out.
- Each rail checked against the maximum of everything it feeds, at worst-case
  tolerance.
- Ceramic capacitance derated for DC bias in filter, coupling, and stability
  calculations.
- Cross-rail signals checked for clamp injection in powered, unpowered, and
  partially-powered states.
- Unkeyed power inputs have reverse-polarity protection and visible polarity.
- Mandatory-pin sweep: every IC's datasheet pin table walked, every required
  connection confirmed.

## Evidence and findings

For each finding record reference/net, severity, observed condition, governing
requirement, evidence URL/file, consequence, recommended action, affected gates,
and verification. Use `unknown` instead of an unsupported conclusion.
