---
name: design-and-review-circuit
description: Design, audit, or correct an electronic circuit from a product brief, native schematic, netlist, block diagram, or circuit description. Use for architecture and component-function review, power and logic-domain checks, reset and boot sequencing, bus ownership, ratings, timing, protection, safe states, component suitability, netlist intent assertions (must-connect / must-not-connect / must-be-open), circuit bugs, power-up behaviour, or layout-facing electrical constraints.
---

# Circuit Design Reviewer

Treat readability and electrical correctness as separate gates. Default to
review-only unless the user asks to change the authoritative circuit source.

## Establish truth

1. Read repository instructions, product brief, architecture, `DECISIONS.md`,
   sourcing lock, native schematic or generator, netlist, BOM, datasheets,
   firmware-visible behavior, and existing review notes.
2. Identify the electrical source of truth. When a generator owns the
   schematic, modify the generator rather than only generated files.
3. Capture ERC/lint, connectivity, and protected PCB/layout hashes before any
   authorized correction.
4. **Read the datasheet of every IC, module, regulator, and connector before
   designing or reviewing its circuit**, from `pcb/datasheets/`. If an evaluation
   board (EVM/EVK) PDF is there for that part, read it too and treat its schematic,
   BOM, and layout notes as the reference design; record every deliberate
   deviation from it in `DECISIONS.md`. To save tokens, read the table of contents
   first, then only the sections you need: pin table, absolute maximum and
   recommended operating conditions, electrical characteristics at your operating
   point, application/typical circuit, component selection, and layout guidelines.
   If a datasheet is missing, ask the user for it (or for permission to download it
   from the manufacturer) rather than designing from memory.
5. Select the evidence path in
   [references/evidence-adapters.md](references/evidence-adapters.md); never
   claim an edit or verification stronger than the source permits.

## Schematic structure

When drawing a new schematic or sheet, follow
[references/new-schematic-kicad.md](references/new-schematic-kicad.md). For a block
the board contains (STM32, USB-C, CAN, RS-485, Ethernet, battery input, regulators,
motor drive, I2C/LED/MOSFET details), read only that section of
[references/common-circuits.md](references/common-circuits.md); the datasheet and
EVM still take precedence.

- **Large designs** (more than one page, or roughly 40+ components) use
  **hierarchical sheets**: one sheet per functional block, connected through
  hierarchical labels and sheet pins drawn on the parent sheet. Do not use global
  labels for signals between sheets. Power rails may use KiCad power symbols
  (these are global by nature). Small single-page designs may use plain wires and
  local labels.
- **Reference designators for multi-sheet designs only** (single-sheet designs use R1, C1, U1) are page number x 100 + increment: page 1 gives R101,
  R102, C101, U101; page 2 gives R201, C201, U201. In KiCad use Annotate Schematic
  with "Use first free number after sheet number x 100" and sort by sheet. If a
  page needs more than 99 of one prefix, split the page.
- Every symbol carries `MPN` and `LCSC` fields once sourcing has run.

## Audit

Read [references/circuit-audit-checklist.md](references/circuit-audit-checklist.md)
and produce `.pcba-workflow/circuit-review.md` from
[assets/circuit-review.md](assets/circuit-review.md).

- Explain operating principle and data/power/control flow in plain language.
- Build a component-by-component function table, power tree, voltage-domain
  table, operating-state table, and reset/boot/ownership sequence.
- Trace every external interface, power entry, driver, receiver, memory/control
  path, and hardware default. Check partial-power and firmware-not-running states.
- Verify ratings, logic thresholds, enable polarity, unused pins, static ties,
  decoupling, regulator stability/thermal margin, protection, clocks/timing, and
  connector semantics. Run the mandatory-pin sweep and the "pass review, fail on
  the bench" patterns in the checklist.
- **Assert intent against the netlist.** Write `.pcba-workflow/netlist-assertions.json`
  from the design intent (not from the current netlist) and run
  `scripts/assert_netlist.py` on a fresh KiCad XML export, as described in
  [references/netlist-assertions.md](references/netlist-assertions.md). Include
  must-not-connect assertions for every rail pair and switch node.
- Classify each finding as critical, major, minor, or information; distinguish
  proven defect, design risk, and unknown evidence.
- Tag every number VERIFIED, COMPUTED, TARGET, ESTIMATE, or NOT ESTABLISHED
  (definitions in the project `CLAUDE.md`). Record layout constraints with these
  tags, including data/edge rate, topology and stubs, return plane, skew intent,
  current allocation, placement, keepout, and authoritative source where
  applicable.
- Coordinate with `/plan-board-bringup` for boot straps, programming/recovery,
  test pads, and DNP hedges; they belong in the schematic before layout.

## Correct only when authorized

For each change, state the defect and evidence, edit the source of truth, render
the complete schematic, inspect it visually, rerun ERC/lint, re-run the netlist
assertions, compare canonical connectivity, and confirm protected layout files
remain unchanged. A deliberate electrical change must appear explicitly in the
connectivity delta and in `DECISIONS.md`; do not hide it inside presentation
cleanup.

## Gate

Use `PASS` only when no critical/major issue or safety-relevant unknown remains,
the netlist assertions pass, the selected parts match the sourcing lock, and the user has
accepted it (or, if they asked for an `/adversarial-review`, it has no open FATAL/SERIOUS findings). Use
`USER_REVIEW` for explicit engineering decisions and `BLOCKED` for missing
evidence or a failed check.

Hand drawing readability to `/schematic-humanizer`, part risk to
`/qualify-pcba-sourcing`, bring-up provisions to `/plan-board-bringup`, and
placement/routing constraints to `/pcb-layout-review`.
