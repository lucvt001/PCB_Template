# PCB Template

This is a PCB folder template for new projects. Clone this, rename the files, and start cooking!

## Directories

- `docs`: datasheets, and user manual if have
- `mechanical`: 3D step files of the components and final board, and any additional mechanical housing
- `pcb`: schematics and layout files; the templates already contain presets for a 4-layer board for JLCPCB manufacturing
  - `pcb/sym/`: project-local symbols; `pcb/project.pretty/`: project-local footprints (both registered as library `Project` in `sym-lib-table` / `fp-lib-table`)
  - `pcb/step/`: 3D models; `pcb/datasheets/`: datasheets and evaluation-board PDFs
- `.pcba-workflow`: workflow artifacts (decisions, sourcing lock, reviews). Commit it; generated exports (`*.svg`, `erc.json`, `drc*.json`, `netlist*.xml`, `pos.csv`) are gitignored
- `production`: BOM, pick-and-place files, and gerbers; you should have subfolders under here, renamed to version number or iterations

Optional folders to add:

- `firmware`: code for your MCU