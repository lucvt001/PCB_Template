# Prompt templates

Replace bracketed text before use.

## English

```text
Use /schematic-humanizer to improve the human readability of the schematic in [repository/path]. The source format is [KiCad/Altium/EasyEDA/EAGLE/Fusion/gEDA/Lepton/SPICE/PDF/image/unknown].

First detect the EDA format and authoritative source. If a generator owns the schematic, edit the generator rather than only its output. Before editing, export connectivity and normalize it to a component-reference, pin, and named-net model. Save the ERC/lint baseline and proof that protected PCB/layout files are unchanged. If the available format cannot prove connectivity, tell me exactly what is unverifiable before proceeding with visual-only work.

Reorganize the drawing into functional sheets and show signal flow with visible native wires, buses, and entries. Directly connect nearby connectors, USB, MCU support, memory, level shifters, glue logic, reset/boot, pulls, LEDs, and power paths. Reserve labels mainly for cross-sheet or genuinely long connections. Rotate connectors toward the circuits they serve. Do not route wires or buses under symbols or text, leave visually floating logic, or accept any overlap.

If I request layout guidance, or the circuit clearly exposes clocks, buses, power rails, high-current paths, controlled interfaces, RF/antenna constraints, or vendor placement rules, add concise layout callouts. Tag each value `[VERIFIED]`, `[COMPUTED]`, `[TARGET]`, `[ESTIMATE]`, or `[NOT ESTABLISHED]`; never guess an unknown. Put calculations and authoritative URLs in a companion document. Render again after adding comments and reject any text/wire/bus overlap.

Export every final sheet to PDF, render every page to PNG, inspect them yourself, and iterate until the diagram is clear. Normalize post-edit connectivity with the same adapter and compare it exactly with the baseline. Require no new ERC/lint findings and no protected-file changes. Show the final snapshot and report the adapter, equivalence result, visual inspection, and every remaining limitation separately from any circuit-design audit.
```
