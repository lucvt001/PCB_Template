# JLCPCB order constraints that the design must respect

Adapted from `daishuge/pcb-skill` (MIT, see `../LICENSE-pcb-skill`), which was
measured on JLC's Chinese site (jlc.com). The **international site (jlcpcb.com)
does not share its fee schedule or coupon rules**. Treat every item below as a
question to check on the live jlcpcb.com pages, and tag each answer VERIFIED
(URL + date) or NOT ESTABLISHED. Read this before fixing the outline, stackup, or
rules - every constraint is free at the sketch stage and expensive at the Gerber
stage.

## Assembly-tier limits (DFM gate, not a fee)

Read the current PCBA capabilities page for the tier you will order (Economic vs
Standard) and record: smallest chip package, minimum IC pin pitch, minimum BGA
pitch, one- or two-sided placement, supported board thicknesses and layer counts,
order quantity range, and excluded part classes (e.g. moisture-sensitive or
low-temperature parts). On the CN site, Economic assembly was single-sided with
0402 minimum and roughly 0.4 mm IC pitch - verify the current jlcpcb.com values.

## JLCPCB may change the outline for assembly

JLC states it may add process rails or fiducials and round the outline corners for
SMT orders without separate notice. If the enclosure or hull fit depends on exact
corners or edges, either design for that tolerance or record the order option /
remark that prevents it, and confirm it on the order page.

## Drill count, slots, and fees

- The CN site charges an uncapped excess-drilling fee above a holes-per-area
  threshold. **Whether jlcpcb.com has an equivalent is NOT ESTABLISHED** - check
  the current "extra charges" help article and compare quotes before relying on a
  dense via field.
- **Count holes correctly.** One drill file can be a strict subset of another
  (e.g. a vias-only file inside the full PTH file); summing them double-counts.
  Count unique drilled features, include slots (`G85` in Excellon), and cross-check
  against the drill report.
- Small drills and tight via annulus can trigger premium processes. Compare two live
  quotes with different drill settings rather than reasoning about it.

## Settings the design files cannot carry

Some order parameters live only on the order form. Write each into the release's
order checklist:

- layer count and the **stackup selection** (KiCad's stackup does not select
  JLCPCB's laminate; choose the matching JLCPCB stackup on the form, especially for
  impedance control);
- board thickness, copper weights (outer/inner), surface finish, mask and silk colour;
- impedance control on/off and which stackup it refers to;
- via treatment (tented/plugged/filled). On a Gerber upload the file's mask
  openings normally govern tenting - make sure the design tents what you intend;
- panelisation / rails / fiducials, and the corner-rounding remark above;
- PCBA tier, assembly side, quantity, and any parts to be left unplaced;
- stencil, if one is wanted.

**Set the layer count first** before reading any other option list on the form; the
available finishes and options change with it.

## Quote sanity

- Capture the itemised quote; compare against the expected price and investigate
  any line you did not expect.
- If a free or promotional price is expected, confirm the total actually shows it
  before going further; if it does not, stop - a condition is not what you think.
- Do not publish the design publicly before ordering if a coupon or promotion
  excludes open-source designs.
