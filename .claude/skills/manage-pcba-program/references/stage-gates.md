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

Ordering is manual and outside this state file: the user checks JLCPCB's part
matching and placement preview, orders, and pays. A stage is `PASS` when the user
has accepted it or, if the user asked for one, an `/adversarial-review` report has
no open FATAL or SERIOUS findings (listed in that stage's evidence). Otherwise it
stays `USER_REVIEW`.

## Invalidation map

- `netlist` or `circuit`: circuit through manufacturing release.
- `product-definition`: every stage.
- `mpn-package`: sourcing through manufacturing release.
- `footprint` or `placement`: placement through manufacturing release.
- `routing`: routing through manufacturing release.
- `bom`: sourcing and manufacturing release.
- `cpl`: manufacturing release.
- `browser-placement`: manufacturing release; mark manual browser edits present.
  The source CPL and release hash must be regenerated before the release can pass
  again.
- `stock-price`: sourcing only unless the chosen part changes.

An invalidated stage is `BLOCKED`, not merely pending, because downstream work
must not proceed until it is repeated.

## Approval transitions

Only `design_critical_substitution` is tracked (substitution or no-substitution
decision, with the user's confirmation as evidence). Final price, JLCPCB placement
preview, and payment are the user's own manual steps and are not recorded here.

Placement may transition to `USER_REVIEW` or `PASS` only while sourcing is PASS.
A later stock/price-only refresh can block sourcing without
invalidating the already-proven physical placement.
