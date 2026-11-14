---
name: manage-pcba-program
description: Coordinate an evidence-gated electronic product and PCBA workflow from an idea, circuit description, schematic, netlist, PCB, BOM, or fabrication package through a reviewed order. Use for end-to-end requests, multi-stage hardware projects, workflow recovery, gate tracking, change invalidation, re-opening a released design, or deciding which specialist skill is required next.
---

# PCBA Program Manager

Coordinate specialists; do not replace them. Default shared artifacts to
`.pcba-workflow/` and use only `PASS`, `BLOCKED`, or `USER_REVIEW` for gate
status.

## Start

1. Read repository instructions and inventory available descriptions, native
   EDA sources, generators, netlists, plots, PCB files, BOM/CPL files,
   manufacturing packages, test evidence, `DECISIONS.md`, and approvals.
2. Read [references/stage-gates.md](references/stage-gates.md).
3. Identify which specialist skills are installed. If a required specialist is
   absent, report its exact name and stop that stage; never improvise its
   approval.
4. Initialize or validate `.pcba-workflow/program-state.json` with
   `scripts/program_state.py`.

## Route the work

- Description or incomplete requirements: `/plan-electronic-product`.
- BOM, MPN, stock, package, CAD, lifecycle, assembly cost, or substitution:
  `/qualify-pcba-sourcing`.
- Electrical architecture, ratings, power, reset, timing, safe state, netlist
  intent, or circuit correctness: `/design-and-review-circuit`.
- Programming, recovery, test pads, staged power-up, DNP hedges, runbook:
  `/plan-board-bringup` (before placement freeze, and finished before release).
- Label-heavy, visually floating, overlapping, or netlist-like schematic:
  `/schematic-humanizer` after capturing a connectivity baseline.
- Placement, routability, routing, layers, planes, DRC, SI/PI, RF, mechanics, or
  DFM: `/pcb-layout-review`.
- Gerber, drill, BOM, CPL, 2D assembly plots, and revision-consistent release:
  `/release-pcba-fabrication`.
- JLCPCB upload, part matching, placement preview, and payment are done by the
  user; they are not tracked as stages. Note their outcome in `DECISIONS.md` if a fix was needed.
- Before any stage is set to `PASS`: the user's acceptance, or (when the user asks
  for it) `/adversarial-review` by a fresh, read-only reviewer. Never start a
  review automatically; see `CLAUDE.md`, Human-centric workflow.

Run the humanizer early when presentation blocks review, but never use its
readability result as circuit approval. Require sourcing and circuit gates
before placement freeze.

## Manage evidence and change

- Record every artifact path, revision, SHA-256, gate status, unresolved risk,
  review report, and approval evidence in program state.
- Keep `DECISIONS.md` append-only: every ruling has an id and the measurement
  behind it; a changed decision is an amendment that supersedes, never an edit.
- Operate standing authority, when granted, only by the recorded hard constraints
  and soft-constraint ranking; escalate constraint changes. It never covers
  substitution, placement, or price approvals, credentials, order submission, or
  payment.
- Invalidate downstream gates after controlled data changes. Use
  `scripts/program_state.py invalidate --change ...`; do not manually preserve
  a stale PASS.
- Only the substitution approval is tracked. Payment is always done by the user.
- Respect user intent: review-only requests do not authorize design edits,
  browser mutations, cart changes, or payments.
- Give workers and reviewers **file paths, not pasted content**, and copy
  measured numbers into briefs from the original output, never from memory.
  Parallel workers must not edit the same files; a KiCad document open in the GUI
  with unsaved changes must not be edited on disk.
- Stop on contradictory revisions, missing source-of-truth data, unverifiable
  safety assumptions, or a specialist BLOCKED result.

## Re-opening a released design

It will happen. Move the withdrawn package to `production/superseded/<rev>/` with a
note saying exactly why; a superseded package left next to the current one will
eventually get ordered. Re-run each affected gate from a fresh export, not only
the delta. Fix everything that is free while the board is open.

## Finish

Report current gate, completed evidence, invalidated work, unresolved risks,
required user reviews, and the next specialist. A program is complete only
when the requested terminal gate is PASS and no required work remains. Claude's
work ends at a validated release; the user uploads, reviews the JLCPCB
placement preview, orders, and pays.
