# Bring-up design rules

Adapted from `daishuge/pcb-skill` (MIT, see `../LICENSE`).

## Programming path

- **Use what the user owns.** If they own a debug probe, give the MCU a standard
  debug header (SWD/JTAG) or a pad pattern for a pogo cable, with VTREF, GND, and
  reset. If they own nothing, the product's own connector (e.g. USB with a built-in
  ROM bootloader or USB-serial/JTAG peripheral) must be the programming interface.
- **Establish bootloader behaviour from the silicon vendor's documentation**, tag it
  VERIFIED with the source, and record which straps select which mode. Where vendor
  docs have gaps, settle them from a second source (module vendor guide, flashing
  tool docs) and write the gap down.
- **Strapping pins get real resistors.** Never rely on a weak internal pull on a long
  trace next to an exposed pad - that is the classic intermittent "boots into the
  wrong mode". An external 10 kOhm on a high-Z input costs no standby current.
- **Verify every pin you spend from the live schematic**, not an architecture table,
  and check none of them is a strapping pin.

## Recovery from bad firmware

Firmware that reconfigures the programming pins, disables the USB peripheral, or
sleeps immediately can lock you out. Recovery needs a forced boot mode **and** a
reset while it is held.

- **Reset:** find or provide a real hard reset - a reset pin on a pad/header, or a
  power switch/enable that actually removes the rail (verify from the schematic,
  including battery and every other power source).
- **Boot strap:** a test pad, and **a GND pad directly next to it** (pad-edge gap
  around 0.4 mm, deliberately bridgeable with tweezers or a solder blob). A strap
  pad 8 mm from the nearest GND with signal pads in between makes the recovery
  attempt fail silently.
- **A button is often the wrong answer** inside an enclosure or hull; a pad pair
  works with the case open, which is the only time you need it.
- **An in-band update path (OTA, CAN bootloader) is a convenience, never the
  recovery path.** Recovery must not depend on the thing that broke.

## Co-processors without their own programming port

Options, decided by numbers: (a) bridge its UART/boot/reset through spare pins of
the main MCU with series resistors (about 1 kOhm, between the main MCU pin and the
co-processor pad, so an external adapter on the test pads always wins and contention
is current-limited); (b) add a dedicated USB-serial bridge (costs area, parts, and a
re-layout); (c) its own debug header. Confirm the firmware side exists before
committing copper.

## Test pads

- A row along an edge on a known pitch, labelled in silk: every rail, GND, reset,
  boot straps, debug pins, UART TX/RX.
- Include a rail and a GND in every group so a probe has a reference.
- Keep them clear of mechanical corridors, mounting hardware, and anything grounded
  that could press on them in the enclosure.
- Keep a probe point on any line a jumper or bridge takes over.
- For JLCPCB PCBA, test pads are bare pads with no part; make sure they are not in
  the CPL and are not covered by conformal coating if you coat the board.

## Staged power-up with machine assembly

- Put a solder jumper or DNP 0 Ohm link between each regulator output and its loads,
  or a jumper on each module's supply, so a rail can be measured unloaded first.
- Size the link for the rail current; a 0402 0 Ohm is not a 2 A link.
- Consider ordering two assembled boards with the most expensive part DNP for the
  first power-up, if JLCPCB pricing makes that cheap.

## DNP hedges

| unknown | hedge |
|---|---|
| a datasheet leaves a strap choice open (pull-up or pull-down) | both footprints, one fitted |
| a module's supply floor may exceed a discharged battery | DNP 0 Ohm from a regulated rail |
| whether two grounds are bonded inside a module | DNP link + continuity test on arrival |
| unused interface lanes may need termination | DNP pads to GND/rail + probe pads |
| a filter or damping value is uncertain | footprint for series R / shunt C, fitted 0 Ohm / DNP |

## Configure before assembly

Walk the BOM and ask of every part: does it have programmable memory, a config
register, OTP, or a physical jumper, and can it still be reached after assembly and
enclosure? JLCPCB will not set a module's jumper for you. Record every one-way door
in the build checklist, and in the order notes when it changes what JLCPCB places.
