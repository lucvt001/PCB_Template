# Review brief and report templates

Adapted from `daishuge/pcb-skill` (MIT, see `../LICENSE`).

## Brief (written by the builder before the review starts)

```markdown
# Review brief - <stage> - <n>

Scope: <exactly what to review>
Read only far enough not to duplicate: <earlier reviews / "found correct" lists>
Inputs (paths only): <.kicad_sch / .kicad_pcb / .kicad_pro / sourcing-lock.csv / release dir>
Working directory: .pcba-workflow/reviews/<stage>-<n>/   (write nowhere else)

Termination criterion:
  One pass. Read-only. Produce a ranked finding list and a verdict
  "FIX FIRST: <ids>". Do not iterate; do not re-review your own findings.

Self-check first - reproduce these on your own code path:
  - components: <N>, pads: <N>, nets: <N>
  - min clearance: <mm> (from <source>)
  - drill hits: <N>, outline: <W> x <H> mm
  (if you cannot reproduce them, report that and stop using your model)

Known constraints: <hard constraints H1..Hn, fab limits, enclosure limits>
Out of scope: <...>
```

Checklist for the brief:

```
[ ] scope, and what to read only far enough not to duplicate
[ ] termination criterion, written before the review starts
[ ] read-only; work only inside <dir>; export your own copy
[ ] self-check numbers to reproduce first
[ ] output: ranked findings (id / severity / measurement / failure scenario / cheapest fix)
[ ] output: what was checked and found correct
[ ] output: unverified suspicions, explicitly not findings
[ ] output: verdict "FIX FIRST: <ids>" and fix order with reasons
[ ] one pass - do not iterate on your own findings
```

## Report (written by the reviewer)

```markdown
# Review report - <stage> - <n>

Read-only, one pass, <date>. Nothing outside <working dir> was modified.
Exports used: <commands and output paths, with SHA-256>

## Self-check
<published number> vs <my number> for each; PASS/FAIL.

## Findings
| ID | Severity | Measurement (where from) | Failure scenario | Cheapest fix |
|---|---|---|---|---|

## Checked and found correct (do not re-audit)
- <item> - <evidence>

## Suspicions, unverified - do not act on these without a measurement
- <item> - <what would settle it>

## Verdict
FIX FIRST: <ids>. <fix order and why>. <ids> can ship as they stand.
```

## Severity examples

- **FATAL:** a capacitor lies wholly inside a module body, so the module cannot be
  fitted; a connector mouth faces the wrong way, so the cable cannot be connected;
  pin 1 rotated, putting a high-voltage rail on a ground pin.
- **SERIOUS:** a buried trace carries the whole system current at a width the
  current standard says is too narrow; an antenna keep-out exists only on a
  documentation layer and the ground pour fills it; a current-setting resistor that
  forces the part into thermal regulation inside the enclosure.
- **MINOR:** a passive too close to an IC body for easy rework; a label obscured.
