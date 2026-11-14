---
name: qualify-pcba-sourcing
description: Verify a PCBA BOM and proposed components before circuit or placement freeze, including exact manufacturer part numbers, LCSC/JLCPCB assembly parts, pin semantics, packages, footprints, CAD and 3D models, lifecycle, live assembly and retail stock, MOQ, Basic/Extended class, loading fees, attrition, price, approved substitutes, and KiCad footprint assignment and checking. Use for sourcing locks, unavailable or expensive parts, JLCPCB/LCSC matching, BOM risk, low-quantity cost decisions, or cost-aware substitution.
---

# PCBA Sourcing Qualifier

Create `.pcba-workflow/sourcing-lock.csv` from
[assets/sourcing-lock.csv](assets/sourcing-lock.csv). Stock and price are
time-sensitive: browse current primary manufacturer and supplier sources rather
than relying on model memory. Read each part's datasheet (and EVM PDF, if one is in
`pcb/datasheets/`) before qualifying it. The default assembly mode is JLCPCB PCBA (see the
project `CLAUDE.md`); read [references/pcba-cost-and-stock.md](references/pcba-cost-and-stock.md)
before comparing parts.

## Part selection rules

**JLCPCB Basic parts are strongly preferred.** Every Extended part type adds a
loading fee to the order. Choose an Extended part only when no Basic part meets the
requirement, and record why in `DECISIONS.md` with the Basic options that were
rejected.

Pick each part in this order:

1. **Meets the electrical requirement with margin** - value, tolerance, voltage,
   current, and power, at the real operating point and temperature.
2. **JLCPCB Basic** and in assembly stock.
3. **Smallest package** that satisfies 1 and 2, within the selected JLCPCB
   assembly tier's minimum size. For generic parts (pull-ups, dividers, decoupling,
   filters, LED resistors) this is normally the smallest Basic size offered.

Basic outranks size: if a value is Basic only in a larger package, use the larger
Basic part. Go **larger** whenever the part must handle power or stress:

- **Resistors:** keep dissipation P = I^2 R (or V^2/R) at or below about half the
  part's rated power, from its datasheet (tag VERIFIED; typical ratings rise from
  0402 to 0603, 0805, 1206, 2512). Check the maximum working voltage too, for
  dividers on high rails. Current-sense and shunt resistors are sized by power and
  pulse rating.
- **Capacitors:** voltage rating about 1.5-2x the working voltage, and derate
  ceramic capacitance for DC bias; bulk and high-voltage capacitors usually need a
  larger case to keep their effective capacitance.
- **Inductors, ferrites, fuses, diodes, MOSFETs:** sized by saturation/rated
  current, power dissipation, and thermal path, not by footprint size.
- **Connectors and mechanical parts:** sized by mating, current, and strength.

## Workflow

1. Read the product brief, architecture, `DECISIONS.md`, schematic/netlist, BOM,
   layout, and production quantity. Derive the actual requirement before comparing
   parts.
2. For every populated reference, record the exact manufacturer, orderable MPN,
   supplier (LCSC) part number, package drawing, footprint, physical pin semantics,
   voltage/current/timing requirements, lifecycle, and CAD status.
   Resolve every LCSC/MPN to its live page and confirm it is the part you mean.
3. Record JLCPCB **assembly** stock, timestamp, MOQ, price break used,
   Basic/Extended class (as shown on the page JLCPCB bills against), per-board and
   assembled quantities, attrition and minimum loading quantity, order quantity,
   parts cost, setup/loading charges, and reconciled line/total assembled-order
   cost. For hand-fit parts, use **retail** stock and pack-rounded line totals.
4. Apply the part selection rules above to every line. Compare options on total
   assembled-order cost: compute the break-even loading fee before reading the live
   fee, and consolidate values onto Basic parts where the design allows.
5. Sanity-check every rating claim against physics and against the real operating
   point (supply range, dropout, saturation current, temperature).
6. Treat memories, programmable devices, modules, regulators, translators,
   connectors, sensors, protection, and timing-critical parts as design-critical
   unless project evidence says otherwise.
7. For an alternate, read
   [references/substitution-gate.md](references/substitution-gate.md). Compare
   every physical pin and package dimension; similar family names or pin counts
   are not evidence. Look for a pin- and land-compatible part first. Record both
   the requested and selected MPN; a different selected MPN must be listed,
   explicitly approved, and tied to approval evidence in the sourcing lock.
8. Check every part against the selected JLCPCB assembly tier's package, pitch,
   and side limits, and check every connector's mating half is sourced.
9. **Assign and check footprints** for every symbol, following
   [references/footprint-assignment.md](references/footprint-assignment.md): land
   pattern and pad numbering against the datasheet, pin-1/polarity marking, body
   outline, exposed pad, and origin/rotation. Write `MPN` and `LCSC` fields onto
   each symbol.
10. Classify each line `PASS`, `BLOCKED`, or `USER_REVIEW`. A critical alternate
   always requires explicit design-owner approval.
11. Run `scripts/validate_sourcing_lock.py` with a suitable live-data age limit.

## Gate

Do not freeze the circuit or placement while a critical MPN, pinout, package,
footprint, CAD model, lifecycle, or current availability remains unresolved.
Any selected MPN/package change invalidates the circuit and all downstream
artifacts. A stock/price-only refresh invalidates sourcing and order approval;
it does not invalidate the circuit when the selected part is unchanged.

Report dated evidence, line and total cost (each figure tagged VERIFIED or
ESTIMATE), risk, substitution class, and every unresolved item. Never silently
change a released BOM or website match. Run `/adversarial-review` on the sourcing
lock only when the user asks; otherwise leave `USER_REVIEW` until they accept.
