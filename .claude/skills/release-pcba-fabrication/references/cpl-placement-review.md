# CPL rotation and offset check

JLCPCB places each part's package centre at `Mid X`/`Mid Y` and turns it to
`Rotation` relative to **its own** library model's zero angle. KiCad exports the
footprint origin and KiCad's zero angle. Where those differ, parts come out shifted
or rotated - a reversed diode or a 90-degree IC is a dead board. This check runs in
two stages: before upload (Claude) and after upload (the user, with Claude).

## Stage 1 - before upload (`scripts/check_cpl.py`)

```bash
"$K" pcb export pos --format csv --units mm --side both -o ../.pcba-workflow/pos.csv template.kicad_pcb
python ../.claude/skills/release-pcba-fabrication/scripts/check_cpl.py \
  --board template.kicad_pcb --pos ../.pcba-workflow/pos.csv \
  --corrections ../.pcba-workflow/cpl-corrections.json \
  --out ../production/<rev>/cpl-jlcpcb.csv --report ../.pcba-workflow/cpl-check.json
```

It blocks on:

1. **Reference set** - every placeable footprint (not DNP, not excluded from
   position files) appears exactly once; nothing extra.
2. **Export transform** - all rows follow one transform (KiCad flips Y and uses
   the board or aux origin); a mixed or mirrored export blocks.
3. **Origin offset** - footprint origin more than 0.05 mm from the centre of its
   pads (e.g. origin on pin 1, a tab, or a mounting peg). Fix the footprint origin
   to the package centre, or add an `offset_mm` correction.
4. **Rotation unverified** - every polarised or asymmetric part (more than two
   pads, or prefix U, Q, D, LED, J, P, CN, Y, X, SW, K, T, BT, IC, PS) needs a
   correction entry for its footprint **and side**, even if the rotation is 0.

It writes the JLCPCB CPL (`Designator, Mid X, Mid Y, Layer, Rotation`) with only
the approved corrections applied. It cannot see JLCPCB's library models; that is
what Stage 2 is for.

### Corrections file

`.pcba-workflow/cpl-corrections.json`, one entry per footprint and side, each with
evidence. Copy from [../assets/cpl-corrections.example.json](../assets/cpl-corrections.example.json).

```json
{
  "schema": "cpl-corrections-v1",
  "footprints": {
    "Package_TO_SOT_SMD:SOT-23": {
      "top": {"rotation_deg": 180, "evidence": "JLCPCB preview, order rev A, U101 pin 1 checked"}
    },
    "Conn:Pin1Origin": {
      "top": {"rotation_deg": 0, "offset_mm": [1.0, 0.0], "evidence": "datasheet body centre"}
    }
  }
}
```

`offset_mm` is in the footprint's local frame (as in the footprint editor); the
script rotates it into place. Bottom-side parts need their own `bottom` entry: the
same package often needs a different correction on the bottom. Keep the file
across revisions - it is the project's memory of JLCPCB's conventions.

## Stage 2 - after upload (user + Claude)

1. The user uploads the Gerbers, BOM, and `cpl-jlcpcb.csv` and opens JLCPCB's
   placement preview.
2. Check at least three separated, non-collinear, polarised parts per assembled
   side first (anchors), including every package family with a known origin or
   angle exception. If the anchors are wrong by the same amount, suspect a
   whole-board issue (origin, mirroring, units) before per-part fixes.
3. Then check **every** part at useful zoom: each lead/terminal on its pad, pin 1,
   diode/LED/electrolytic polarity, connector mouth direction, exposed/thermal pad,
   and nothing shifted or off-board. Screenshots of both sides (top and bottom
   preview) can be given to Claude for a second look; they are 2D images.
4. If JLCPCB's table can be copied or exported, compare it with what was submitted:

   ```bash
   python ../.claude/skills/release-pcba-fabrication/scripts/reconcile_cpl_import.py \
     --submitted ../production/<rev>/cpl-jlcpcb.csv --imported jlcpcb-imported.csv \
     --report ../.pcba-workflow/cpl-reconcile.json
   ```

   Any nonzero exit blocks.
5. **Fix every mismatch at the source**: add or change the entry in
   `cpl-corrections.json` (with the preview as evidence) or fix the footprint
   origin, regenerate the release, and re-upload. Browser-only nudges in JLCPCB's
   editor are diagnostics, not fixes - they are lost on the next order and leave the
   release wrong.
6. Repeat until every part passes, then the user approves the placement
   (`assembly_placement` approval).

## Record

Write the result into `.pcba-workflow/cpl-check.json` (Stage 1, written by the
script) and note the Stage 2 outcome - anchors checked, per-part result, corrections
added, upload iteration, final CPL SHA-256 - in the release manifest's
`assembly_placement` evidence.
