# CLAUDE.md

Project guidance for Claude Code. Generic workflow, schematic rules, toolchain, and
JLCPCB defaults live in the **`pcb` plugin** (install: see the plugin's README).

## Always-on rules (even if no skill has loaded)

- **Change only what was asked.** Flag other issues; don't fix them unasked. The
  user edits the design too: re-read files before touching them, and never revert
  differences from your last copy.
- **No automatic review.** Never spawn a reviewer agent unless the user asks. Finish
  a task, run cheap checks, stop, and let the user decide.
- Ask the user before assuming anything that changes the board; don't ask about
  small details.
- Don't commit or push unless asked. Never upload, order, or pay on JLCPCB.

## At the start of every session

1. Load **`/pcb:workflow`**. It holds the working principles, the session map, and
   which skills to use; the toolchain was already checked by the plugin's hook. If
   the plugin isn't installed, stop and tell the user.
2. Read the project requirements below (imported from `README.md`): purpose,
   revision, board size, sheets and their relationships, constraints, overrides. If
   it still has `<placeholders>`, ask the user to fill them in before designing.
   When a requirement changes, edit `README.md` (the single source), not this file.

## Project (from README.md)

@README.md

If `pcb/template.*` is still unrenamed, rename it to the project name (ask only for
the name).

## Folder layout

| Path | Contents |
|---|---|
| `pcb/` | KiCad project: `.kicad_pro`, `.kicad_sch`, `.kicad_pcb` (source of truth) |
| `pcb/sym/`, `pcb/project.pretty/`, `pcb/step/` | Project-local symbols, footprints, 3D models. Libraries are registered as `Project` in `pcb/sym-lib-table` / `pcb/fp-lib-table` (`Project:<name>`) |
| `pcb/datasheets/` | Datasheets (`<MPN>.pdf`) and evaluation-board PDFs (`<MPN>_EVM.pdf`) |
| `docs/`, `docs/design_notes/` | Design notes, calculations, user manual |
| `mechanical/` | Enclosure/housing CAD and exported board STEP |
| `production/<rev>/` | Released Gerber/drill, BOM, CPL, 2D plots, order checklist; `production/superseded/<rev>/` for withdrawn releases |
| `.pcba-workflow/` | Skill artifacts: `DECISIONS.md`, product brief, sourcing lock, netlist assertions, reviews, bring-up plan, release manifest. Reviewer work goes in `reviews/<stage>-<n>/` |

`pcb/.history/` and `*.kicad_prl` are local-only and gitignored; don't edit them.
