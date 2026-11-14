# CLAUDE.md

Guidance for Claude Code when working in a PCB project cloned from this template.

> When you clone this template: fill in **Project** below, **automatically
> rename** the `pcb/template.*` files (`.kicad_pro/.kicad_sch/.kicad_pcb/.kicad_prl`)
> to the project name, and update the paths in **Commands** and the project file
> references. Do this at the start of the first session without asking; ask the
> user only for the project name if it isn't known. Rename with `git mv` or
> a plain move while KiCad has the project closed.

## Project

- Name: `<project name>`
- Purpose: `<one-line description of what the board does>`
- Current revision: `<Rev A>`
- Fab / assembly house: JLCPCB (jlcpcb.com, international site)
- **Assembly mode: JLCPCB assembles (PCBA)** unless this project says otherwise.
  - Choose parts from JLCPCB's assembly parts library (LCSC numbers).
    **JLCPCB Basic parts are strongly preferred**; each Extended part type adds a
    loading fee, so use Extended only when no Basic part meets the requirement,
    and record why. Compare the total order cost, not the unit price.
  - **Part size:** use the smallest package available (within the assembly tier's
    minimum, and as a Basic part) for generic components such as pull-ups,
    dividers, decoupling and filter parts. Use larger packages where a part must
    handle power, voltage, or current (resistor dissipation, capacitor voltage and
    DC-bias derating, current-sense parts). Basic outranks size. Details in
    `/qualify-pcba-sourcing`. Check stock in JLCPCB's **assembly** stock
    (separate from LCSC retail stock), and price parts from JLCPCB's
    assembly/BOM match screen.
  - Stay within the assembly service's limits for the selected tier (Economic vs
    Standard): smallest passive size, minimum IC pitch/BGA pitch, one-sided
    vs two-sided placement, and supported board thickness. Read them from
    JLCPCB's current capabilities page; don't assume them.
  - Put SMT parts on the top side by default. Bottom-side placement needs Standard
    PCBA and costs more.
  - JLCPCB may add rails and fiducials and round the board corners for assembly.
    The enclosure/hull fit must tolerate that, or the order must say not to.
  - Hand-solder only the parts JLCPCB can't or shouldn't place (e.g. some
    through-hole connectors, cables, batteries). List them in the BOM as DNP for
    JLCPCB and keep them in a separate hand-assembly list.
- **Ordering is done by the user.** Claude's work ends at a validated release in
  `production/<rev>/`. The user uploads to JLCPCB, checks part matching and the
  placement preview, orders, and pays. If the preview shows a rotation or offset
  error, fix it in the source and regenerate the release. Before release, Claude
  runs the CPL rotation and offset check (`release-pcba-fabrication`,
  `scripts/check_cpl.py`) and the user's preview check follows its Stage 2.

## Sessions: one stage per session, only that stage's skills

Work is split into three kinds of session. At the start, establish which one this
is (ask the user if it isn't clear), then **use only that session's skills**. Do
not open other skills' `SKILL.md` or reference files, and inside a skill open a
reference file only when the step you are on calls for it. This keeps token use
and memory down.

| Session | Skills to use | Produces |
|---|---|---|
| **1. Schematic design and review** | `/design-and-review-circuit`; `/schematic-humanizer` for readability; `/plan-board-bringup` for straps, programming, test points and DNP hedges in the schematic; `/plan-electronic-product` only if there is no product brief yet | schematic, `circuit-review.md` (with layout handoff constraints), `netlist-assertions.json`, draft `bringup-plan.md` |
| **2. Component sourcing and footprint assignment** | `/qualify-pcba-sourcing` | `sourcing-lock.csv`, `MPN`/`LCSC` fields on symbols, footprints assigned and checked |
| **3. PCB layout** | `/pcb-layout-review`; `/plan-board-bringup` to place test pads and finish the runbook; `/release-pcba-fabrication` at the end | board, `layout-review.json`, release in `production/<rev>/` |

`/adversarial-review` is loaded by the reviewer agent only, and only when the user
asks for a review (see **Human-centric workflow**). `/manage-pcba-program` is used only when the user asks for overall status, gate
tracking, or to re-open a released design.

Sessions hand over through files in `.pcba-workflow/`, not by reading each other's
skills. For example, the layout session reads the "Layout handoff constraints"
section of `circuit-review.md` and the sourcing lock; it does not load the circuit
or sourcing skills.

## Human-centric workflow (speed and tokens first)

**No automatic review.** Never spawn a reviewer agent (Opus or otherwise) on your
own initiative. Review happens only when the user asks for it, typically as the
final check. During design the user is the reviewer: finish a task, stop, show the
result, and let the user decide the next step.

- **Session 1 (schematic):** plan, write the plan down (`circuit-review.md`,
  `DECISIONS.md`), then implement it straight away. When the initial schematic is
  done, run only the cheap self-checks (ERC, netlist assertions) and stop. Ask the
  user to look. The user then either requests changes (send back to the designer),
  or asks for the Opus review.
- **Session 3 (layout):** the user sets the board size first. Place components
  sheet by sheet; for each sheet, do the initial placement only, then stop for the
  user to check. **No copper pour and no routing until the user approves the
  placement.** After approval, do pours and routing, and stop again for the user.
  Only run a review when the user asks.
- **Session 2 (sourcing):** same principle; stop after the sourcing lock and
  footprint assignment for the user's look. The Sonnet double-check runs only on
  request.
- The sheet arrangement rule applies: IC in the middle, a dashed annotated box per
  sub-circuit (see `/schematic-humanizer`).
- Gates stay `USER_REVIEW` until the user accepts them or asks for a review; the
  user's acceptance counts as clearing the gate for work they have looked at.

## Designer and reviewer agents

The main Claude coordinates and talks to the user. It may spawn a **designer**
subagent for the session's work (no need to ask first); it spawns a **reviewer**
only when the user asks.

- **Designer agent** - does the session's work with the session's skills and is
  the only agent that edits design files. Its brief gives the task, the skills to
  load, and input file paths. If it hits a question only the user can answer, it
  **stops and returns the question immediately** instead of guessing.
- **Reviewer agent (on user request only)** - read-only. Loads
  `/adversarial-review`, exports its own copies, and reviews the designer's result.
  Its brief gives file paths only, never the designer's conclusions.

**Models** (pass `model` when spawning each agent):

| Session | Designer agent | Reviewer agent |
|---|---|---|
| 1. Schematic design and review | `sonnet` | `opus` |
| 2. Component sourcing and footprint assignment | `haiku` | `sonnet` - double-checks every selected part (MPN, LCSC number, Basic/Extended, size and ratings, stock) and every footprint assignment (land pattern, pad numbering, pin 1/polarity) |
| 3. PCB layout (including the release and CPL check) | `sonnet` | `opus` |

If a model isn't available, use the next one up and tell the user.

Rules:

1. **Questions go to the user immediately.** Whenever either agent returns a
   question, the coordinator asks the user right away; it doesn't wait for the end
   of the session or answer on the user's behalf.
2. **One feedback cycle, then escalate.** When the user has asked for a review and
   it finds FATAL/SERIOUS issues: the designer fixes those findings once, then the
   reviewer re-checks them from a fresh export. If anything is still unresolved
   after that one cycle, stop and alert the user with the finding, what was tried,
   and the options. Don't start a second cycle without the user.
3. The agents run one after the other, never editing at the same time. Before the
   designer edits KiCad files on disk, ask the user to save and close (or be ready
   to reload) the project in KiCad.
4. Give agents file paths, not pasted content, and copy measured numbers into
   briefs from the original output, never from memory.
5. A gate goes to `PASS` only after a requested reviewer report has no open FATAL
   or SERIOUS findings, or the user explicitly accepts it. Without either it stays
   `USER_REVIEW`. If subagents aren't available when a review is requested, tell
   the user and ask them to run it in a separate session.

## Schematic rules

- **Datasheets first.** Before designing or reviewing any part's circuit, read its
  datasheet in `pcb/datasheets/`. If an evaluation-board (EVM/EVK) PDF for that
  part is there, read it too and use it as the reference design; record any
  deliberate deviation in `DECISIONS.md`. Name files `<MPN>.pdf` and
  `<MPN>_EVM.pdf` where possible. Read the contents page first, then only the
  sections needed (pin table, absolute maximum and recommended operating
  conditions, electrical characteristics, application circuit, component selection,
  layout guidelines). If a datasheet is missing, ask the user for it or for
  permission to download it from the manufacturer.
- **Hierarchy for large designs.** Anything over one page (or roughly 40+ parts)
  uses hierarchical sheets, one per functional block, connected by hierarchical
  labels and sheet pins on the parent sheet. Don't use global labels for signals
  between sheets; power rails may use KiCad power symbols.
- **Reference designators: multi-sheet designs only = page number x 100 +
  increment.** Page 1: R101, R102, C101, U101. Page 2: R201, C201, U201. In KiCad's
  Annotate Schematic, choose "Use first free number after sheet number x 100".
  Split a page that needs more than 99 of one prefix. A single-sheet design uses
  plain numbering (R1, R2, C1, U1).
- **Ask, don't assume, selectable IC options.** When planning, every property of
  an IC that is selectable by the design (EN polarity/tie/divider, PG/open-drain
  usage, UVLO thresholds, mode/config pins, address pins, soft-start, switching
  frequency, connector types and pinouts, etc.) must be asked of the user, with the
  datasheet options listed and a recommendation. Do not assume. Do **not** ask
  about capacitor ratings or other small details; choose those yourself.
- **Capacitor values:** write capacitance followed by voltage rating in the Value
  field for every capacitor, e.g. `1u_50V`, `100n_16V`, `22p_50V`.
- **Standard values:** resistors use E12 or E24 values (prefer E12 unless the
  calculation needs E24; E96 only with a stated reason). Capacitors use standard
  values (E6/E12 series, e.g. 1u, 2.2u, 4.7u, 10u, 22u, 47u, 100n).
- **Dashed-box text is minimal:** only the equation or the datasheet rationale
  (no part numbers, no prose). Text height 40 mil (1.016 mm); box titles 70 mil
  (1.778 mm).
- Each part carries `MPN` and `LCSC` fields once sourcing has run.

## Toolchain

- **KiCad 10** (the project files are `generator_version "10.0"`), including
  `kicad-cli`.
- **Python 3** for the skill scripts under `.claude/skills/*/scripts/`
  (standard library only).
- **Optional:** a KiCad MCP server (`mcp__kicad__*` tools) for live
  board/schematic queries and edits. Use `kicad-cli` for reproducible
  ERC/DRC/exports either way.

### Preflight: check the toolchain before starting work

Tools may be missing, installed somewhere else, or a different version on each
machine. At the start of a session that touches the design, check them before
running any skill. **Do not guess paths or work around a missing tool silently.**

1. **KiCad / `kicad-cli`.** Try `kicad-cli version` on `PATH`, then the default
   install locations:
   - Windows: `C:\Program Files\KiCad\<version>\bin\kicad-cli.exe`
   - macOS: `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`
   - Linux: `/usr/bin/kicad-cli`

   If it's found somewhere else, use that path and tell the user which one.
   If it isn't found, **stop and tell the user**: KiCad 10 is needed, install it
   from https://www.kicad.org/download/ (or give the path to an existing
   install). If it's older than 10.0, warn the user: the project files may not
   open, and CLI options can differ.
2. **Python 3.** Check `python --version` (or `python3`). If it's missing, tell
   the user to install Python 3 before using the skill scripts. Skills can still
   be read and followed manually, but their validators won't run.
3. **KiCad MCP server.** Check whether `mcp__kicad__*` tools exist in this
   session. If they don't, say so once and carry on with `kicad-cli` plus
   direct file inspection. If the user expects MCP, point them to their MCP
   server's install instructions and to adding it to Claude Code
   (`claude mcp add ...`, or the project's `.mcp.json`). Don't block on it.
   If the tools exist but fail (wrong KiCad path, server not running), report
   the error to the user rather than retrying blindly.
4. **Project files.** Confirm the `.kicad_pro`, `.kicad_sch` and `.kicad_pcb`
   exist under `pcb/` and match the names in **Commands**. If they're missing or
   still called `template.*` on a real project, tell the user before going on.

Record what was found (tool paths and versions, MCP yes/no) in your first
report, so the user knows which evidence paths are available.

## Folder layout

| Path | Contents |
|---|---|
| `pcb/` | KiCad project: `.kicad_pro`, `.kicad_sch`, `.kicad_pcb` (source of truth) |
| `pcb/sym/`, `pcb/fp/`, `pcb/step/` | Project-local symbols, footprints (`.pretty`), and optional 3D models |
| `pcb/datasheets/` | Datasheets (`<MPN>.pdf`) and evaluation-board PDFs (`<MPN>_EVM.pdf`) |
| `docs/`, `docs/design_notes/` | Design notes, calculations, user manual |
| `mechanical/` | Enclosure/housing CAD and exported board STEP |
| `production/<rev>/` | Released Gerber/drill, BOM, CPL, 2D assembly plots, order-form checklist - one subfolder per revision |
| `production/superseded/<rev>/` | Withdrawn releases, each with a note saying why |
| `.pcba-workflow/` | Skill artifacts: product brief, `DECISIONS.md`, sourcing lock, netlist assertions, circuit/layout reviews, bring-up plan, release manifest, program state |
| `.pcba-workflow/reviews/<stage>-<n>/` | Reviewer briefs, the reviewer's own exports, and reports |
| `.claude/skills/` | PCBA design skills (see below) |

`pcb/.history/` and `*.kicad_prl` are local-only and gitignored; never rely on or edit them.

## Board defaults (from `pcb/template.kicad_pro` / `.kicad_pcb`)

- 4 copper layers (F.Cu / In1.Cu / In2.Cu / B.Cu), with the stackup and
  constraints preset for JLCPCB 4-layer fabrication. Read the actual stackup
  from the board file, not from this summary.
- Default net class: 0.254 mm track, 0.127 mm clearance, via 0.6858/0.3302 mm.
- Board minimums: track 0.0889 mm, via diameter 0.45 mm, annular ring 0.1 mm,
  through-hole 0.2 mm, hole-to-hole 0.25 mm, copper-to-edge 0.5 mm,
  silk text height 0.8 mm.
- Treat these as a starting point. Before release, check them against the
  **current** JLCPCB capabilities page and live quote; anything below
  standard-process limits raises the price.

## Skills

Installed at `.claude/skills/`. Invoke with `/skill-name`. See **Sessions** for
which ones each session may use.

| Skill | Use when |
|---|---|
| `/design-and-review-circuit` | Designing or auditing the schematic electrically; netlist intent assertions |
| `/schematic-humanizer` | Making a schematic readable without changing connectivity |
| `/plan-board-bringup` | Programming/recovery, test pads, staged power-up, DNP hedges, bring-up runbook |
| `/plan-electronic-product` | Requirements are vague; need a product brief, constraints, and architecture |
| `/qualify-pcba-sourcing` | Exact MPNs, LCSC parts, assembly stock, cost, substitutes, footprint assignment |
| `/pcb-layout-review` | Placement, routability, stackup, routing, planes, DRC, DFM, 2D placement mechanics |
| `/release-pcba-fabrication` | Generating and independently verifying Gerber/drill/BOM/CPL for one revision |
| `/adversarial-review` | The reviewer agent's protocol, before any gate is set to `PASS` |
| `/manage-pcba-program` | Only on request: overall status, gate tracking, re-opening a release |

Gate statuses are only `PASS`, `BLOCKED`, or `USER_REVIEW`. A change to the
netlist, parts, footprints, placement, routing, BOM, or CPL invalidates the
downstream gates; rerun them rather than keeping a stale `PASS`.

No 3D renders or part-height collision checks by default: placement mechanics are
checked in 2D (courtyards, Fab outlines, Edge.Cuts, copper layers). Do 3D work only
if the user asks.

## Evidence tags

Tag every number and claim that a decision rests on:

| Tag | Meaning |
|---|---|
| `VERIFIED` | Read from an authoritative source (datasheet, standard, live supplier/fab page, measurement), with the source and date |
| `COMPUTED` | Arithmetic on verified numbers, with the arithmetic shown |
| `TARGET` | A design allocation chosen with stated margin (not a measurement) |
| `ESTIMATE` | Unmeasured or assumed; must be confirmed before the gate that depends on it |
| `NOT ESTABLISHED` | Unknown; needs measurement or research, with an owner and the evidence that will close it |

"X probably doesn't support Y" is not a finding. If a claim decides whether work
continues, prove it.

## Decisions

Record every design ruling in `.pcba-workflow/DECISIONS.md` as `D-<n>` with the
measurement behind it. The log is append-only: a changed decision gets an
amendment that supersedes the old entry, which stays visible. Ask the user only
when the two answers would give a different board.

## Working rules

- Edit the native KiCad source (or its generator), never only an exported file.
- KiCad may have the project open. Before editing files on disk, ask the user to
  save/close or be ready to reload, and never overwrite unsaved GUI work.
- Before changing a schematic for readability, export a connectivity baseline and
  prove it is unchanged afterwards (`schematic-humanizer/scripts/compare_connectivity.py`).
- ERC/DRC passing is necessary, not sufficient: also inspect the schematic PDF
  pages and the 2D board plots of both sides.
- Zero unrouted pads is not a release gate on its own: check real DRC, power/GND
  zone connectivity, and same-net zone islands too.
- Judge the saved file, not the running session: save, close, reopen, and
  re-export before calling a gate. Check results against the rule set and layer
  stack actually stored in the project.
- Gate the schematic on netlist intent assertions
  (`design-and-review-circuit/scripts/assert_netlist.py`), not on ERC alone.
- Use current datasheets and live supplier data; don't trust memory for stock,
  price, or fab limits. Save the datasheets you use to `pcb/datasheets/`.
- Releases go to `production/<rev>/` and must come from one saved, committed
  revision of the schematic and board.
- Do not commit or push unless asked. Never upload, order, or pay on JLCPCB.

## Commands

Run from `pcb/`. Set `K` to the `kicad-cli` path found in the preflight, e.g.
`K="/c/Program Files/KiCad/10.0/bin/kicad-cli.exe"` in Git Bash, or call it with
`& "<path>\kicad-cli.exe"` in PowerShell.

```bash
# Electrical / design rule checks (JSON for machine review)
"$K" sch erc --format json --severity-all -o ../.pcba-workflow/erc.json template.kicad_sch
"$K" pcb drc --format json --severity-all --schematic-parity -o ../.pcba-workflow/drc.json template.kicad_pcb

# Netlist export + intent assertions (circuit gate)
"$K" sch export netlist --format kicadxml -o ../.pcba-workflow/netlist.xml template.kicad_sch
python ../.claude/skills/design-and-review-circuit/scripts/assert_netlist.py ../.pcba-workflow/netlist.xml ../.pcba-workflow/netlist-assertions.json

# Connectivity baseline for schematic-humanizer
"$K" sch export netlist --format kicadxml -o ../.pcba-workflow/netlist-before.xml template.kicad_sch

# DRC against freshly refilled zones (does not save the board)
"$K" pcb drc --format json --severity-all --schematic-parity --refill-zones -o ../.pcba-workflow/drc-refilled.json template.kicad_pcb

# Schematic PDF
"$K" sch export pdf -o ../docs/schematic.pdf template.kicad_sch

# 2D assembly plots for visual review (top, and bottom mirrored)
"$K" pcb export svg --mode-single -l F.Fab,F.SilkS,F.CrtYd,Edge.Cuts --page-size-mode 2 --exclude-drawing-sheet -o ../.pcba-workflow/assembly-top.svg template.kicad_pcb
"$K" pcb export svg --mode-single -m -l B.Fab,B.SilkS,B.CrtYd,Edge.Cuts --page-size-mode 2 --exclude-drawing-sheet -o ../.pcba-workflow/assembly-bottom.svg template.kicad_pcb

# Fabrication outputs (use the plot settings stored in the board)
"$K" pcb export gerbers --board-plot-params -o ../production/<rev>/gerber/ template.kicad_pcb
"$K" pcb export drill -o ../production/<rev>/gerber/ template.kicad_pcb
"$K" pcb export pos --format csv --units mm --side both -o ../.pcba-workflow/pos.csv template.kicad_pcb

# CPL rotation/offset check -> JLCPCB CPL with approved corrections (upload this one)
python ../.claude/skills/release-pcba-fabrication/scripts/check_cpl.py --board template.kicad_pcb --pos ../.pcba-workflow/pos.csv --corrections ../.pcba-workflow/cpl-corrections.json --out ../production/<rev>/cpl-jlcpcb.csv --report ../.pcba-workflow/cpl-check.json

# Optional: STEP for the enclosure CAD (export only; not reviewed)
"$K" pcb export step -o ../mechanical/board.step template.kicad_pcb
```

JLCPCB's CPL needs columns `Designator, Mid X, Mid Y, Layer, Rotation` (written
by `check_cpl.py`), and its BOM needs `Comment, Designator, Footprint, LCSC`.
Per-package rotation and offset corrections live in
`.pcba-workflow/cpl-corrections.json`, each with evidence; keep it across
revisions.
