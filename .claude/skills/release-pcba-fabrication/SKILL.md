---
name: release-pcba-fabrication
description: Build and verify a vendor-neutral PCB/PCBA manufacturing release from one frozen design revision. Use when generating or auditing Gerber, drill, IPC-2581/ODB++, BOM, CPL/pick-and-place with JLCPCB rotation and offset checks, assembly drawings, 2D assembly plots, constraints, DFM evidence, hashes, or release manifests, and when preventing mixed-revision fabrication or assembly uploads.
---

# PCBA Fabrication Release

Release artifacts; do not redesign the circuit or layout inside this stage.
Read [references/release-checklist.md](references/release-checklist.md) and
the KiCad export commands in
[../pcb-layout-review/references/kicad-adapter.md](../pcb-layout-review/references/kicad-adapter.md).
Record tool/version, source revision, origin, units, and every command used. If
only derived fabrication files exist, mark native-source traceability BLOCKED or
USER_REVIEW; never reconstruct a revision from filenames.

## Preflight

1. Read repository rules, sourcing lock, circuit/layout gate results, approved
   waivers, native board/project files, fabrication constraints, quantities,
   and target manufacturer capabilities.
2. Freeze one named source revision and record board/project hashes. Stop if
   schematic, PCB, BOM, CPL source, sourcing lock, or constraints disagree.
3. Require circuit and layout gates to be PASS. Zero opens alone is not enough:
   raw connectivity, real DRC, power connectivity, planes, critical nets,
   mechanical and visual review must all be resolved.

## Generate

Use the authoritative EDA tool to export all applicable layers, solder mask,
paste, silkscreen, outline/cutouts, mechanical information, plated/non-plated
drill, drill map/report, BOM, CPL, assembly drawings, stackup/impedance notes,
and top/bottom **2D assembly plots** (SVG of Fab + SilkS + CrtYd + Edge.Cuts per
side; these are the `render_top`/`render_bottom` manifest artifacts). Do not
produce raytraced 3D renders. Preserve units, origin, side convention, rotation
convention, DNP policy, polarity, and pin-1 evidence.

**Verify the package independently of the EDA that produced it.** Inspect the
generated files in an independent Gerber/assembly viewer (e.g. KiCad's GerbView
or another reader) and re-derive: outline and dimensions, copper layer count
**and** that each copper file has copper, drill census, mask opening per pad,
nothing outside the outline (measure hole edges, not centres), keep-outs empty on
every copper layer, text, apertures, edge treatments, panel/depanel needs, and
assembly side. Where two code paths give the same number (EDA DRC and the viewer
or a checker), record both; that agreement is what "verified" means.

**Check CPL rotation and offset before release.** Follow
[references/cpl-placement-review.md](references/cpl-placement-review.md): run
`scripts/check_cpl.py` on the saved board and KiCad position file. It blocks on a
reference-set mismatch, an inconsistent export transform, footprint origins away
from the package centre, and polarised parts without an approved rotation entry in
`.pcba-workflow/cpl-corrections.json`, and it writes `cpl-jlcpcb.csv` with only the
approved corrections applied. Upload that file, not KiCad's raw position file.

Count drills correctly: one drill file can be a strict subset of another; count
unique drilled features including slots, and cross-check the drill report.
Export a via/drill histogram and identify every feature below the current
standard-cost process threshold.

Write the **order-form checklist** for every setting the files cannot carry
(layer count, JLCPCB stackup selection, thickness, copper weights, finish, via
treatment, impedance, rails/fiducials and corner rounding, PCBA tier and side);
see [references/jlcpcb-constraints.md](references/jlcpcb-constraints.md). Include the
bring-up plan (`.pcba-workflow/bringup-plan.md`) and the hand-fit parts list.

## Manifest

Build `.pcba-workflow/release-manifest.json` with
`scripts/build_release_manifest.py`. Supply an explicit revision for every
artifact; the script rejects mixed revisions. Record:

- source and derived artifact SHA-256, size, role, and revision;
- board dimensions, layers, thickness, finish, stackup, controlled options,
  quantities, assembly side, and DNP policy;
- ERC, raw connectivity, classified DRC, power, layout, DFM, and visual results;
- approved waivers and the sourcing-lock hash/time;
- substitution, placement, final-price, and payment approval state.

Run `scripts/validate_release_manifest.py` after moving or packaging the
release. A missing file, hash drift, mixed revision, stale sourcing lock, or
failed required check blocks release. When the user asks, run `/adversarial-review` on the final
package; release requires no open FATAL or SERIOUS findings from it.

Put the release in `production/<rev>/`. If a released package is withdrawn, move
it to `production/superseded/<rev>/` with a note saying why, and regenerate the
whole release rather than patching files.

## Handoff

Deliver an immutable release directory containing the manifest, manufacturing
files, assembly files, constraints, and review evidence. State the exact upload
Gerber/archive, BOM, and CPL, and the order-form checklist. The user uploads to
JLCPCB and checks its part matching and placement preview using Stage 2 of
`cpl-placement-review.md` (anchors per side, then every part; screenshots and any
exported placement table can come back to Claude for `scripts/reconcile_cpl_import.py`
and a second look). If the preview shows a rotation or offset error, fix it in the
source (footprint origin or `cpl-corrections.json`, with the preview as evidence)
and regenerate the release; never patch only in the browser.
