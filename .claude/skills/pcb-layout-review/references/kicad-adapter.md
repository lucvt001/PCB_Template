# KiCad 10 adapter: CLI commands and matching MCP tools

Tested with `kicad-cli` 10.0.6 on Windows against the template (2026-11-14); all
commands below ran without error. Run from `pcb/`; `$K` is the `kicad-cli` path
from the preflight. `<name>` is the renamed project. Use `kicad-cli` for anything
that must be reproducible; use the `mcp__kicad__*` tools for live queries and
edits (they act on the open session, so they are not evidence on their own).

| Task | `kicad-cli` | MCP tool (live) |
|---|---|---|
| ERC | `sch erc --format json --severity-all -o X <name>.kicad_sch` | `run_erc` |
| DRC + parity | `pcb drc --format json --severity-all --schematic-parity -o X <name>.kicad_pcb` | `run_drc`, `get_drc_violations` |
| DRC on fresh fills | add `--refill-zones` (does not save the board) | `refill_zones` |
| Netlist (XML) | `sch export netlist --format kicadxml -o X <name>.kicad_sch` | `export_netlist` |
| Schematic PDF | `sch export pdf -o X <name>.kicad_sch` | `export_sch_pdf` |
| 2D plots | `pcb export svg --mode-single [-m for bottom] -l <layers> --page-size-mode 2 --exclude-drawing-sheet -o X <name>.kicad_pcb` | `export_pcb_svg`, `get_board_2d_view` |
| Gerbers | `pcb export gerbers --board-plot-params -o <dir>/ <name>.kicad_pcb` | `export_gerbers` |
| Drill | `pcb export drill -o <dir>/ <name>.kicad_pcb` | `export_drill` |
| Position (CPL source) | `pcb export pos --format csv --units mm --side both -o X <name>.kicad_pcb` | `export_pos` |
| BOM for JLCPCB | netlist XML, then `release-pcba-fabrication/scripts/export_jlcpcb_bom.py` | `export_bom` |
| STEP | `pcb export step -o X <name>.kicad_pcb` | `export_3d_cli` |

Notes:

- Give `gerbers`/`drill` an existing output directory ending in `/`.
- `kicad-cli sch export netlist` defaults to the S-expression format; always pass
  `--format kicadxml` (the scripts parse XML).
- An empty schematic/board gives 0 violations; that proves the command works, not
  that a design is clean.
- JLCPCB BOM: `python .claude/skills/release-pcba-fabrication/scripts/export_jlcpcb_bom.py netlist.xml --out production/<rev>/bom-jlcpcb.csv --hand production/<rev>/hand-assembly.csv`
  (columns `Comment, Designator, Footprint, LCSC`; DNP and LCSC-less parts go to
  the hand-assembly list and are reported). Tested on a synthetic netlist only;
  check it against the first real netlist.
