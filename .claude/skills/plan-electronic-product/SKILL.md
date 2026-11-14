---
name: plan-electronic-product
description: Turn an electronic product idea, behavior description, reverse-engineering note, or incomplete circuit concept into a decision-ready engineering brief and architecture with numbered hard constraints, ranked soft constraints, and a decision log. Use before schematic design or audit when functions, operating states, power, interfaces, mechanics, production quantity, cost, or measurable requirements are missing or ambiguous.
---

# Electronic Product Planner

Produce `.pcba-workflow/product-brief.yaml`, `.pcba-workflow/architecture.md`, and
start `.pcba-workflow/DECISIONS.md`. Do not invent requirements merely to fill a
template.

## Workflow

1. Read repository instructions and all supplied descriptions, diagrams,
   existing circuits, firmware behavior, mechanics, and commercial constraints.
2. Use [references/intake-checklist.md](references/intake-checklist.md) to
   distinguish known facts, design targets, estimates, and unresolved choices.
3. Copy [assets/product-brief.yaml](assets/product-brief.yaml) into the project
   state directory and complete only supported fields.
4. **Apply the question test:** ask the user a question only when its two answers
   give a different board. Research everything measurable yourself (prices,
   library classes, datasheet facts); decide everything that is your job (e.g.
   decoupling placement). Typical board-changing questions: quantity, hard budget,
   assembly mode, operating environment, interfaces that must exist, power source,
   enclosure limits.
5. Record **hard constraints `H1..Hn`** (never traded away) and **ranked soft
   constraints `S1 > S2 > ...`** with the tie-break written down. A clear ranking
   settles most later decisions without another round-trip.
6. Record the scope boundary: what is out of scope and what "done" means for each
   deliverable.
7. Describe system boundaries, actors, external connectors, major functional
   blocks, data and energy flow, operating modes, startup/shutdown/fault states,
   and ownership of shared resources in `architecture.md`.
8. For every interface, record voltage domains, direction, protocol or bus,
   nominal rate, edge-rate uncertainty, topology, cable/connector environment,
   and protection expectations.
9. Build a provisional power budget by rail and mode with **typical and worst-case
   columns**, labelled as such. Tag every figure VERIFIED, COMPUTED, TARGET,
   ESTIMATE, or NOT ESTABLISHED; typical datasheet current is not a guaranteed
   system maximum.
10. Enumerate candidate architectures and price them **including assembly fees**,
    not only part cost.
11. Record mechanical envelope, user-accessible parts, antenna/enclosure needs,
    programming and test access, expected quantity, target cost, lifecycle, and
    compliance context.
12. Ask the user only for unresolved choices that pass the question test. Record
    the rest as explicit unknowns with an owner and the evidence needed.

## Decision log and standing authority

- Write every ruling to `DECISIONS.md` as `D-<n>` with the measurement behind it.
  The log is **append-only**: a changed decision gets an amendment that
  supersedes the earlier entry, which stays visible.
- If the user grants standing authority ("stop asking, push it through"), record
  it in the brief. Operate it by applying `H1..Hn` and `S1 > S2 ...` only; when two
  options are close, pick the one cheaper to reverse and say so; escalate any
  **constraint** change, not ordinary decisions. Standing authority never covers
  design-critical substitutions, assembly-placement approval, final price,
  credentials, order submission, or payment.

## Gate

Set `status: PASS` only when downstream circuit and sourcing specialists can
work without guessing core behavior, power source, interfaces, physical limits,
assembly mode, or production intent, and every question that changes the board
has an answer on record. Use `USER_REVIEW` for a decision awaiting the owner and
`BLOCKED` for missing evidence that prevents safe progress.

Do not select exact components or approve a circuit in this skill. Hand exact
parts to `/qualify-pcba-sourcing` and electrical implementation to
`/design-and-review-circuit`.
