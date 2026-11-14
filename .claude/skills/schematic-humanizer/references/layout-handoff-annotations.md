# Layout handoff annotations

Add layout annotations when the user explicitly requests them or when the source
clearly exposes placement-sensitive interfaces. Do not guess hidden electrical
requirements. Ask the user only when the missing choice would materially change
the design; otherwise mark it for measurement or engineering review.

## Evidence classes

Use the project evidence tags (defined in `CLAUDE.md`):

- `[VERIFIED]`: manufacturer datasheet, interface standard, approved project
  requirement, or verified measured value. Include the source in the companion
  document.
- `[COMPUTED]`: derived from verified values; put the arithmetic in the companion
  document.
- `[TARGET]`: conservative project routing allocation chosen for this revision,
  such as loose group skew, firmware-rate ceiling, current capacity, or layer
  preference. Explain that it is not certified timing or measured current.
- `[ESTIMATE]`: an unmeasured working value that must be confirmed before its gate.
- `[NOT ESTABLISHED]`: source capability, thermal rise, real current, unknown
  clock, enclosure RF performance, or another item that cannot be proven from the
  schematic.

## What to capture

For each meaningful interface or rail, capture only applicable items:

1. Clock, data rate, or access cadence, plus the warning that edge rate can set
   signal-integrity risk even when the clock is slow.
2. Required topology and stub rule: source → buffer/termination → receiver,
   point-to-point, daisy chain, star, or explicitly forbidden branches.
3. Reference plane, layer preference, controlled impedance, spacing, and return
   transition guidance.
4. Group skew or pair mismatch target. Avoid meanders when the timing budget
   does not require them.
5. Provisional current allocation, shared-trunk capacity, trace/pour and via
   intent, voltage-drop/thermal signoff, and measurement state.
6. Component placement: decoupling escape path, regulator loop, crystal, antenna
   keepout, connector ESD, exposed-interface protection, and mechanical keepouts.
7. Authoritative manufacturer or standards URL in a companion layout guide.

## Presentation

- Put short, local callouts near the relevant functional region, but outside
  wires, buses, symbols, labels, and the dominant visual flow.
- Keep full calculations, current-budget tables, URLs, assumptions, and signoff
  checklists in a companion Markdown/PDF document. Link it with a short on-sheet
  note.
- Do not label an entire design with one clock when domains differ. Separate CPU,
  memory, loader, RF, USB, and other interfaces.
- Do not add a generic impedance width/gap before the final fabricator stackup is
  known. State the impedance and reference plane, then require stackup-derived
  geometry.
- Treat a vendor module with an integrated antenna as a placement/keepout problem;
  do not invent an RF feed trace that is not in the circuit.

## Required final gate

Annotations can introduce new overlaps. After adding them, follow the complete
[visual audit checklist](visual-audit-checklist.md), including every full page
and dense crops around the annotated regions. Then repeat connectivity comparison
and ERC/lint. A clean netlist does not excuse a visually obscured schematic.
