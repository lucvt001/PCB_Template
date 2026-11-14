# Visual audit checklist

This checklist is mandatory after every meaningful schematic rearrangement and
again after adding comments or layout guidance. Passing ERC does not pass the
visual audit.

## Routing and buses

- Do not maximize wire count. Prefer direct local wiring where it clarifies a
  relationship, and matched labels where a long wire would create a loop or
  spaghetti.
- Keep every bus spine outside symbol bodies, values, references, notes, and
  unrelated labels. Large MCUs and modules need extra clearance.
- Never place two different bus spines collinearly on top of one another.
- Avoid wire-through-pin paths that can look connected or create accidental
  connectivity. Make branches and junctions explicit.
- Use the native grid and snap bus entries to it. Keep entry pitch and direction
  consistent.
- In tools where wires are two-point segments, emit a separate segment for each
  bend. Split bus backbones at T-tap endpoints when the format requires explicit
  junction geometry.
- Move pulls, termination parts, decouplers, and interface passives near the
  circuit they support when this makes the function readable.

## Full-page inspection

Render every page to PNG at a resolution where pin labels remain readable.
Inspect:

- dominant left-to-right signal flow;
- functional grouping and sheet titles;
- apparent floating connectors, MCU support logic, power chains, and controls;
- long loops, excessive labels, clipped text, title-block collisions, and empty
  areas that hide a broken flow;
- each page edge and every cross-sheet endpoint.

## Dense-area crops

Inspect enlarged crops around:

- large MCUs, FPGAs, modules, and memories;
- USB, Ethernet, RF, clock, and external connectors;
- bus entries and places where multiple spines pass;
- power OR-ing, regulators, reset/boot, glue logic, and ownership controls;
- any area changed after the previous render.

## Annotation gate

After comments or layout callouts are added, render again. Reject the result if
any note hides a wire, bus, pin, reference, value, or functional heading; if a
URL is clipped; if the callout interrupts the visual signal path; or if the
annotation density makes the sheet harder to scan. Move detailed tables and full
links into a companion document and leave only concise pointers on-sheet.

## Acceptance

Completion requires all of the following:

1. Full-page inspection passed for every sheet.
2. Dense crops passed for every relevant interface and edited region.
3. No visible overlap, ambiguous junction, or apparent floating local function.
4. Connectivity comparison and ERC/lint also pass independently.
5. Final snapshots are shown or linked in the completion report.
