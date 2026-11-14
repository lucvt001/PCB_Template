# Canonical connectivity (KiCad)

Use native exporters whenever possible. An adapter is acceptable only when it can repeat the same normalization before and after editing.

## Generated schematic binding guard

When a generator supports variants or separate presentation/placement tables,
record the source module, selected variant, active override table, generator
version, and output hash. Prove that the selected override is consumed with a
deterministic manifest, trace, or harmless sentinel fixture. Reject silent
fallback to default placement even when generation and ERC succeed. After a
binding change, regenerate from a clean state and repeat exact connectivity and
all-sheet visual comparison.

KiCad: export XML netlists before/after with
`kicad-cli sch export netlist --format kicadxml` (the default is S-expression) and
compare with `scripts/compare_connectivity.py`. Run native ERC, export PDF, render
all pages. Preserve references, net names, pin numbers, and PCB bytes; net codes,
coordinates, timestamps, and sheet paths are export metadata. A PDF/image-only
source cannot prove electrical equivalence: trace it into a new native schematic.

## Canonical JSON

Use UTF-8 JSON with this shape:

```json
{
  "schema": "schematic-connectivity-v1",
  "components": [
    {"ref": "R1", "value": "1k", "footprint": "R_0603", "device": "Device:R"}
  ],
  "nets": [
    {"name": "SIGNAL", "pins": [{"ref": "R1", "pin": "1"}, {"ref": "U1", "pin": "4"}]}
  ]
}
```

Sort order is irrelevant. References, pin identifiers, net names, and component identity strings are exact and case-sensitive. Adapters may leave `value`, `footprint`, or `device` empty only when the source does not provide them; use the same policy before and after.
