# PCBA cost and stock (JLCPCB assembly)

Adapted from `daishuge/pcb-skill` (MIT, see `../LICENSE-pcb-skill`) for JLCPCB
(jlcpcb.com) machine assembly. **Do not hardcode fees or limits from this file**:
read the live parts library, BOM-match screen, and capabilities page, and tag every
figure VERIFIED (source + date), COMPUTED, or ESTIMATE.

## At low quantity, fees dominate part prices

JLCPCB charges a per-type loading fee for Extended parts (Basic parts have none),
plus order-level setup. On a small prototype run that fee can exceed the price of
the part many times over, so compare **total assembled-order cost**, not unit price:

```
option cost = unit price x placed quantity (incl. attrition)
            + loading fee (if Extended, once per part type)
            + any extra setup the option triggers
```

**Compute the break-even fee before you read the live fee**, so the decision is
arithmetic once the number arrives. Typical outcomes:

- a Basic part at a slightly worse spec often beats an Extended part at the right
  spec - only if the spec still holds (see "physics" below);
- consolidating values (e.g. one capacitor value instead of three Extended ones)
  saves a loading fee per type removed;
- a part JLCPCB doesn't stock may be cheaper to hand-fit afterwards than to
  consign - list it as DNP for JLCPCB and on the hand-fit list.

## Basic first, then smallest size

Project rule (see the sourcing SKILL "Part selection rules"): meet the electrical
requirement with margin, then prefer Basic, then the smallest package within the
assembly tier's limit. Use a larger package where power, voltage, DC-bias
derating, or current demands it. Basic outranks size.

## Basic vs Extended (and "Preferred")

- **Read the library class from the page JLCPCB bills against** (the assembly parts
  library / BOM-match result). A secondary API's class field has been wrong before.
- Absence is proof only after a real search: record the filters used when you
  conclude "no Basic part exists" for a role. Connectors, chargers, and power
  inductors are commonly Extended-only.
- **Resolve every LCSC number to its live product page** and check the MPN, package,
  and value match what you intend. Part numbers carried through documents have
  pointed at the wrong part.

## Two stock pools

JLCPCB **assembly** stock and LCSC **retail** stock are different inventories, and
assembly pricing uses its own price book.

- Price and check stock for machine-placed parts on JLCPCB's assembly side.
- Price and check stock for hand-fit spares on the retail side.
- A part can have millions in assembly stock and none in retail, or the reverse.
- Watch thin lines (low stock relative to order quantity); record the timestamp.

## Quantity the order actually consumes

- Machine assembly adds **attrition** (extra parts consumed per reel change) for
  Extended parts, and may impose a **minimum loading quantity** (tape length per
  feeder). Read the current policy and include it in required quantity and cost.
- Assembly quantity can differ from PCB quantity; assembling fewer boards than you
  fabricate often saves money.
- Hand-fit extras are bought in packs: **budget on line totals**, never unit price x
  quantity needed. Paste needed quantities into the cart and let the vendor round
  them up to reveal the real pack step.

## Sanity-check ratings against physics

Compute what a claim implies and ask whether physics allows it before trusting a
listing: capacity vs volume for cells (Wh/L), dropout vs your actual input range,
switch current vs the inductor's saturation rating, supply range vs your rails. A
basic-library op-amp that needs +/-5 V does not work on a 3.3 V board.

## Package and substitution traps

- "Same function" substitutes can have completely different pinouts in the same
  package. Choose before layout, not after.
- A pin- and land-compatible substitute is the cheapest fix there is; look for one
  first when a part fails a spec.
- Honour the project's assembly rules: check the selected JLCPCB assembly tier's
  minimum package, pitch, and side limits for every part.

## Hand-fit extras and leftover stock

For parts the user fits by hand (connectors, cables, batteries, modules):

- net the need against stock the user already owns; "bought minus used" is an
  **upper bound** (assumes zero scrap) - flag every line with margin 0 or 1 and add
  a small insurance quantity;
- check the mating half of every connector is on the list;
- stage carts but never check out: read the cart back line by line, record the
  item count before and after, and touch nothing that was already in it.

## Labelling prices

A price nobody has read off a live page is an **ESTIMATE**. When documents disagree
(BOM, ledger, cart), the live quote/cart at order time is authoritative. Shipping
and tax are often NOT ESTABLISHED until checkout; give totals both ways.
