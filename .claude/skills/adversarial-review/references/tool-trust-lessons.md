# Tool-trust lessons

Adapted from `daishuge/pcb-skill` (MIT, see `../LICENSE`). Each lesson is a failure
that passed a check which was not actually checking. Read-the-wrong-thing faults
never look like errors.

## 1. A green board is not a correct board

A schematic passed ERC with zero errors while five nets were silently merged by the
EDA (a switch node into a card supply, an I2S data line and a UART TX into ground).
Only must-connect / must-not-connect / must-be-open assertions against the exported
netlist caught it (see `design-and-review-circuit/references/netlist-assertions.md`).

KiCad analogues to watch: power symbols and global labels with the same name join
nets across sheets; hierarchical pins mis-wired to a different label; a label that
touches a wire end by accident; "power flag" symbols that silence ERC on a rail
that is not actually driven.

## 2. Verify the tool before the result

- **Stale or cached model.** A 3D check measured a cached model of the previous
  release and reported 0 interferences on a board that had three. A footprint's 3D
  model came from its old name and showed a header that was no longer on the board.
  *Guard:* print the size/hash of the exact file being measured every run; a hole
  exists iff it is in the drill file, a pad iff it is in the copper Gerber, a mask
  opening iff it is in the mask Gerber.
- **Bounding box reported as a pad.** A module's "two thermal lands" were the
  footprint author's bounding boxes over 20 small pads. A clearance checker modelled
  obround pads as rectangles and reported eleven phantom violations.
  *Guard:* carry the true pad shape; test checkers on the part whose shape differs
  most from its box.
- **Copper labelled by the wrong owner.** Pour copper attributed by "which zone
  outline contains this point" mislabels where a lower-priority zone fills around a
  higher-priority one. *Guard:* attribute copper by connected component.
- **Mirror validated on a symmetric object.** A bottom-side transform used `x = -x`
  instead of `y = -y` and passed because 148 of 149 pads were symmetric two-terminal
  chips. *Guard:* calibrate every transform against a known asymmetric part.
- **Asynchronous or stale instrument.** A DRC call returned the previous document's
  result on the first read after a change. *Guard:* re-run until the result repeats;
  for KiCad, run `kicad-cli` on the saved file rather than reading a GUI panel, and
  **save, close, reopen, re-measure** before calling a gate.
- **The loaded rule set is not the one you think.** A routability estimate used the
  intended 4-layer rules while the board actually carried a 2-layer profile with
  wider clearance. *Guard:* read the rules from the `.kicad_pro`/`.kicad_dru` you are
  checking, and the layer count/stackup from the `.kicad_pcb`.

## 3. A wait condition must fire on a crash

An autorouter crashed (StackOverflowError) at 00:34; the JVM sat at 0 % CPU without
exiting; the supervisor waited for "output exists or process gone" for 10 h 53 min.
Any wait on a background job must answer: **if this crashed right now, would my
filter emit a line?** Cover: output present (non-empty, log says complete), crash
signature in the log, process gone, wall-clock timeout, and a progress-rate floor.
Not every logged exception is terminal; named fatal errors are. Measure the input
size before feeding an external tool - the fix for that crash was protecting 51
traces instead of 3 326, not more stack.

Applies to Freerouting runs (DSN export -> route -> SES import) and any long
`kicad-cli` job.

## 4. Judge connectivity by islands merged, not edges drawn

A walker that merged any two nodes at the same XY counted a track on an inner layer
and another on the top layer as connected with no via there. Connectivity must be
layer-aware: only a via or plated hole joins layers. A pour that is declared is not
a pour that exists: judge it by its filled copper, not by the refill call's return
value. For KiCad, compare DRC on stored fills with `kicad-cli pcb drc --refill-zones`
(without `--save-board`); a difference means the saved fills are stale.

A via is redundant only if deleting it leaves the net in one piece **and** it is not
the return path for a nearby signal layer change, RF stitching, or thermal path.

## 5. "No legal site" is not an answer while neighbours can move

A fix pass reported two bias resistors had no legal site within 6 mm and left them
undone. Ruling: move the neighbours. Before writing "impossible", state the degrees
of freedom held fixed and the measurement that proves it.

## 6. Reviews disagree, and the disagreement is data

Two reviewers used different rows of the same standard for one clearance; two read
different layers of one differential pair. Name both numbers and say which is right
and why. Quietly disagreeing reports get reconciled badly by the next reader.

## 7. Review the reviewer's tooling too

A verification pass's first eleven violations were all its own bugs. Keep the wrong
versions and the root causes visible. A checker that has never been wrong has never
been tested.
