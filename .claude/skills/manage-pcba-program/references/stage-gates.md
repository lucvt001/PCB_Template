# Stage gates and invalidation

## Gates

| Stage | Pass condition |
|---|---|
| `product_definition` | Functions, environment, power, interfaces, mechanics, quantity, assembly mode, cost target, hard/soft constraints, and unknowns are recorded; every board-changing question is answered. |
| `sourcing` | Critical MPNs, packages, pinouts, lifecycle, assembly stock, total assembled cost, footprints assigned and checked, and substitution bounds are verified with dated evidence. |
| `circuit` | Locked parts pass architecture, ratings, power, reset, timing, safe-state, power-up audit patterns, netlist intent assertions, and ERC or equivalent review. |
| `schematic_visual` | Functional flow is visibly traceable, visual audit passes, and connectivity is unchanged or limitations are explicit. |
| `placement` | Functional corridors, connectors, decoupling, 2D placement mechanics (courtyards, module bodies, connector mating areas), routability, bring-up test/strap pads, RF, polarity, and package bodies pass logical and visual review. |
| `routing` | No unexplained disconnects or real DRC errors remain; zones are filled as saved; return paths, planes, critical nets, and manufacturing constraints pass. |
| `manufacturing_release` | Gerber, drill, BOM, CPL, constraints, bring-up plan, order-form checklist, and source files share one revision and verified hashes. |
| `assembly_placement` | The user has reviewed JLCPCB's part matching and placement preview (pin 1, polarity, rotation, offset) and approved it; any error was fixed in the source and re-released. |
| `order` | Parts, substitutions, options, price, and shipping address are separately reviewed and explicitly approved; the user has submitted and paid. |

Every technical stage (`product_definition` through `manufacturing_release`) also
needs an `/adversarial-review` report with no open FATAL or SERIOUS findings, listed
in that stage's evidence.

## Invalidation map

- `netlist` or `circuit`: circuit through order.
- `product-definition`: every stage.
- `mpn-package`: sourcing through order.
- `footprint` or `placement`: placement through order.
- `routing`: routing through order.
- `bom`: sourcing, manufacturing release, assembly placement, and order.
- `cpl`: manufacturing release, assembly placement, and order.
- `browser-placement`: manufacturing release, assembly placement, and order;
  mark manual browser edits present. The source CPL and release hash must be
  regenerated before the placement gate can pass again.
- `stock-price`: sourcing and order only unless the chosen part changes.

An invalidated stage is `BLOCKED`, not merely pending, because downstream work
must not proceed until it is repeated.

## Approval transitions

Use one explicit transition; do not collapse technical evidence into user
approval:

1. Complete machine reconciliation and full visual placement review, then set
   `assembly_placement` to `USER_REVIEW` with evidence.
2. Record the user's independent assembly-placement approval, then set that
   stage to `PASS` with the approved evidence.
3. After every prior stage is PASS, set `order` to `USER_REVIEW` with the final
   quote and address evidence.
4. Record final-price approval. Claude stops at the page before final submission.
   The user submits and pays; record the `payment` approval only after the user
   confirms it, with their confirmation as evidence. Payment requires the
   substitution/no-substitution, assembly-placement, and final-price approvals
   already be APPROVED.
5. Set `order` to `PASS` only after all four approval records are APPROVED.

Placement may transition to `USER_REVIEW` or `PASS` only while sourcing is PASS.
A later stock/price-only refresh can block sourcing and order without
invalidating the already-proven physical placement.
