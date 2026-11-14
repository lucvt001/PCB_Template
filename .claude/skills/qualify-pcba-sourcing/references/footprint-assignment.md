# Footprint assignment (KiCad)

Assign and check a footprint for every symbol once its exact MPN is chosen. Read
the part's datasheet package drawing and recommended land pattern from
`pcb/datasheets/` first.

## Where footprints come from

1. KiCad's standard libraries, when the package matches the datasheet exactly.
2. A manufacturer- or LCSC/JLCPCB-provided footprint, copied into the project
   library under `pcb/fp/<lib>.pretty` (registered in the project's `fp-lib-table`),
   never referenced from a download folder.
3. A footprint drawn from the datasheet's recommended land pattern (IPC-7351
   naming and zero orientation), saved in `pcb/fp/`.

Symbols come the same way into `pcb/sym/`. 3D models are optional; if present
they go in `pcb/step/`, and they are not reviewed.

## Check every assignment

| check | how |
|---|---|
| package matches the MPN suffix | datasheet ordering table vs footprint name |
| land pattern | pad size, pitch, row span, and exposed pad vs the datasheet's recommended land pattern |
| pad numbering | every footprint pad number maps to the symbol pin with the same function (datasheet pin table); mismatches are invisible to ERC and netlist checks |
| pin 1 and polarity | marked on silk **and** Fab; diode/LED/electrolytic/tantalum polarity matches the symbol |
| body outline | Fab outline and courtyard match the drawing's body in plan view |
| exposed pad | pad connected to the right net, paste reduced or windowed as the datasheet says, thermal vias if required |
| origin and rotation | origin at package centre; zero orientation per IPC-7351 (pin 1 top-left for ICs), so JLCPCB CPL rotation corrections stay predictable |
| assembly-tier limits | package size and pitch within the selected JLCPCB PCBA tier |

Record the result in the sourcing lock's `footprint`, `package_verified`, and
`pinout_verified` columns. Any footprint change after placement invalidates
placement and everything after it.

## Confirm in the netlist

After assigning, export a fresh netlist and confirm every component has a
non-empty footprint field that resolves in the project's library tables. Check
from the exported files or `kicad-cli` output, not by looking at the canvas.
