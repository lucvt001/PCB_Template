# 2D placement mechanics

Adapted from `daishuge/pcb-skill` (MIT, see `../LICENSE-pcb-skill`). A board that
passes DRC can still be impossible to connect, fit, or hand-finish. Every check
here works in **plan view** (courtyards, Fab outlines, Edge.Cuts, copper layers,
Gerbers); no 3D rendering or height analysis is required.

Use alongside [connector-stack-and-fanout.md](connector-stack-and-fanout.md) for
connector maturity and dense power/GND escape.

## 1. Courtyards and Fab outlines are the 2D body

- Every footprint has a courtyard and an F.Fab/B.Fab body outline that match the
  exact MPN drawing's body in plan view. A footprint with no body outline, or one
  copied from a different part, makes every clearance check blind on that side.
- Run KiCad's courtyard checks as errors (`courtyards_overlap`,
  `missing_courtyard`) and read every violation; do not waive them in bulk.

## 2. Connectors: mouth, mating area, mating half

For every connector, establish from the manufacturer's drawing (not from silk):

1. **Which way does the mouth face?** Mouth direction and pin-1 end can be rigidly
   coupled; rotating a connector without renumbering pads can put a supply on a
   ground pin. Rotation fix and pad renumber are one change, never two.
2. **What area does the mating plug, latch, and cable bend need in plan view?**
   For side-entry connectors the plug sits outside the footprint. Draw that area as
   a courtyard extension or a keep-out on a user layer, and keep parts out of it.
3. **Does the mating half exist, is it in the BOM or hand-fit list, and can the
   user join the two?**
4. **Board-edge openings:** list every connector, switch, LED, and button at an
   edge with its offset from the edge; make sure no two collide on one face and
   that each lines up with the enclosure opening.

## 3. Nothing under module bodies

- No part may sit inside any module, shield can, or connector body outline.
  Courtyard overlap must be checked for **every** part, including small passives,
  against every module courtyard.
- Under a castellated or LGA module, keep non-ground top copper and via drills out
  of the module's exposed underside lands plus a margin, using the module's real
  pad map from its datasheet (not the footprint author's bounding boxes).

## 4. Keep-outs must be on copper layers

A keep-out drawn on a user/documentation layer does not constrain a zone fill. The
reference board's antenna keep-out had 93.8 % ground pour on all four layers plus
stitching vias inside it. In KiCad, use **rule areas (keep-out zones) on every
relevant copper layer**, then confirm from the Gerbers (or a copper-layer SVG
plot) that the region is empty on each layer.

## 5. Through-hole parts and the opposite face

- Through-hole joints protrude on the opposite face. Keep them out of areas that
  rest on a battery, bracket, or hull rail, and list the regions in the layout
  review.
- JLCPCB PCBA places SMT on one side by default; through-hole parts are either
  hand-soldered or a separate service. List which.
- Flag every via barrel inside an SMT pad: machine assembly needs filled/capped
  vias there (usually a premium process).

## 6. Hand-fit access

List every hand-fitted part (through-hole connectors, cables, batteries, modules
fitted later). For each pad, measure the 2D distance to the nearest neighbouring
courtyard; flag anything closer than about 0.8 mm as needing a fitting-order note.
Write the fitting order and every configure-before-fitting item into the build
checklist.

## 7. Enclosure and hull outline

From the enclosure CAD (exported as DXF to a user layer, or given as dimensions):

- board outline vs the enclosure's internal 2D profile, with clearance;
- mounting holes, standoff pads, rails, and their keep-outs;
- connector/penetrator positions and the cable routing space to them;
- regions that must stay uncoated if the board is conformally coated
  (connectors, test pads, switches);
- JLCPCB's added rails/fiducials and corner rounding (if not disabled in the order).

Height and 3D interference are out of scope for routine reviews. If a specific
part is known to be tall near a lid or hull wall, ask the user to check it in their
mechanical CAD.

## Checklist

```
[ ] every footprint has a courtyard and Fab outline matching its MPN drawing
[ ] courtyard checks run as errors; every violation read
[ ] every connector: mouth from the drawing, mating area kept clear in plan view
[ ] every connector: mating half sourced and joinable
[ ] pin-1 marker, footprint numbering, and fitted part agree
[ ] no part inside any module/shield/connector courtyard
[ ] no non-ground top copper or via drills under a module's exposed lands
[ ] every keep-out on the copper layers it must constrain, verified in Gerbers
[ ] through-hole joints clear of resting faces; via-in-pad flagged
[ ] hand-fit parts listed with access distances and fitting order
[ ] board outline, mounting, connector positions, coating keep-outs vs enclosure
```
