---
name: adversarial-review
description: Run a one-pass, read-only adversarial review of a PCB/PCBA stage result - product brief, schematic, netlist, sourcing lock, placement, routing, mechanical fit, bring-up plan, or fabrication release - by a fresh reviewer that rebuilds its own model from its own export. Use before declaring any gate PASS, when a board "looks finished", when two reports disagree, or before trusting a new checker or script.
---

# Adversarial Review

A builder cannot review its own work: the assumption that produced a fault also
produces the check that misses it. This skill is the protocol for a **fresh,
read-only reviewer** whose only job is to try to break the result, and to say
exactly what it measured.

Run it at the end of every stage gate before setting `PASS`. Its report is
evidence for the gate; it never edits the design.

## Who reviews

- The reviewer must be a **different worker from the builder**: a subagent or
  separate session given **file paths, not pasted content or conclusions**. When
  subagents are available, spawn one per review; otherwise ask the user to open a
  fresh session with the brief.
- The builder writes the brief; the reviewer writes the report. The builder may
  not edit the report.

## Protocol

1. **Write the brief first**, from
   [references/review-brief.md](references/review-brief.md): scope, what to read only
   far enough to avoid duplicating, known numbers for the self-check, and the
   **termination criterion** - normally *"one pass, read-only, ranked findings, a
   `FIX FIRST` verdict; do not iterate or re-review your own findings."* A review
   without a written stop condition finds problems forever.
2. **Read-only means read-only.** Export your own copy into
   `.pcba-workflow/reviews/<stage>-<n>/` and work only there. Never edit the live
   schematic, board, libraries, rules, or another stage's artifacts. If a question
   can only be settled by a write (e.g. refilling zones and saving), report it as an
   instruction to the fix pass, not as a verdict.
3. **Build your own model from your own export.** Do not read the builder's
   intermediate files. For KiCad, re-export from the saved files yourself, e.g.
   `kicad-cli sch export netlist --format kicadxml`, `kicad-cli sch erc`,
   `kicad-cli pcb drc --schematic-parity`, `kicad-cli pcb export gerbers/drill/pos/step`.
   GUI state that has not been saved is not evidence.
4. **Self-check the model before trusting it.** Reproduce numbers the builder
   already published (component and pad counts, net count, min clearance, drill
   count, outline size) on your own code path. If you cannot, report a finding about
   **your model**, not the board, and stop using it for novel numbers.
5. **Rank every finding** and give each one four things:
   - **severity**: FATAL (cannot be assembled or cannot work, or assembling it
     destroys something), SERIOUS (works, but a real failure mode is live or a spec
     is violated), MINOR (record and cost it; do not inflate);
   - **measurement**: numbers, coordinates/references, and which file produced them;
   - **failure scenario**: what a person physically experiences if it ships;
   - **cheapest fix**: the smallest change that closes it, costed in parts, mm, area,
     or re-work.
6. **Quarantine hunches.** End with *"Suspicions, unverified - do not act on these
   without a measurement."* A guess mixed into findings wastes the fix pass.
7. **Record what you checked and found correct**, with evidence, so the next pass
   does not re-audit it.
8. **Deliver a verdict, not a mood:** `FIX FIRST: <ids>`, the fix order and why, and
   which findings can ship as they stand.

Write the report to `.pcba-workflow/reviews/<stage>-<n>/report.md`. A gate may go to
`PASS` only when every FATAL and SERIOUS finding is closed or explicitly waived by
the owner, and the fix has been re-measured from a fresh export.

## What every reviewer must assume

Read [references/tool-trust-lessons.md](references/tool-trust-lessons.md) before
writing or trusting any checker. In short:

- **A green result names an instrument**, and you must be able to say what that
  instrument cannot see. ERC/DRC cannot see a net that consistently resolves to the
  wrong thing; zero unrouted cannot see a pour that was never filled.
- **Verify the tool before the result.** Calibrate every geometric transform
  (mirror, rotation, origin, units) against a known **asymmetric** object.
- **Judge the artifact, not the intention.** Measure the saved file, the Gerber, the
  fresh STEP - not the design you meant or the file you pushed.
- **"No legal site / impossible" is a fact about the search**, not the board, until
  you state which degrees of freedom were held fixed and why.
- **When two reports disagree, say so and name both numbers.**

## Re-review after fixes

After the designer's one fix pass, re-check the fixed findings from a **fresh
export** (not the designer's files), plus anything the fix could have disturbed.
If any FATAL/SERIOUS finding is still open after that one cycle, stop and hand it
to the user with the measurement, what was tried, and the options; do not start a
second cycle on your own. Ask the user any question that only they can answer as
soon as it comes up.
