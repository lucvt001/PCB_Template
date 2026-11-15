# <Project name>

<One-line description of what the board does.> Revision: `<Rev A>`.

Claude Code reads this file at the start of every session (imported by
`CLAUDE.md`), so keep it short and accurate; put long rationale in
`docs/design_notes/` and link it.

## Design requirements

- **Board:** `<size, e.g. 60 x 40 mm>`, `<layers>`, `<enclosure / mounting limits>`
- **Sheets** (one line each: function, and what it feeds or receives):
  - `<Sheet 1: name - function; feeds / fed by ...>`
  - `<Sheet 2: ...>`
- **Interfaces and connectors:** `<fill in>`
- **Power:** `<input range, rails, current budget>`
- **Hard constraints:** `<voltage/current limits, cost target, parts to use or avoid>`
- **Assembly:** JLCPCB PCBA by default; overrides: `<none>`
- **More detail:** `<link to .pcba-workflow/product-brief.md or docs/design_notes/...>`

## Template notes (delete this section after cloning)

Clone this template, fill in the sections above, and rename `pcb/template.*` to the
project name.

- `docs`: design notes, datasheets, user manual
- `mechanical`: 3D step files of components and the board, and any housing
- `pcb`: schematics and layout; presets for a 4-layer JLCPCB board
  - `pcb/sym/`: project-local symbols; `pcb/project.pretty/`: project-local footprints (both registered as library `Project` in `sym-lib-table` / `fp-lib-table`)
  - `pcb/step/`: 3D models; `pcb/datasheets/`: datasheets and evaluation-board PDFs
- `.pcba-workflow`: workflow artifacts (decisions, sourcing lock, reviews). Commit it; generated exports (`*.svg`, `erc.json`, `drc*.json`, `netlist*.xml`, `pos.csv`) are gitignored
- `production`: BOM, pick-and-place files and gerbers, in one subfolder per revision
- Optional: `firmware` for your MCU code
- The design skills, workflow rules, toolchain check and JLCPCB defaults come from the `pcb` plugin; `CLAUDE.md` holds only Claude-specific rules.
