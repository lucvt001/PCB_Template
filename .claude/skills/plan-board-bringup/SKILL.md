---
name: plan-board-bringup
description: Design a PCB so first power-up, programming, recovery, and debugging are possible with the tools the user actually owns, and write the bring-up runbook during design. Use before placement freeze and again before fabrication release for boot straps, programming/debug access, test pads, rail isolation, recovery paths, DNP hedge footprints, configure-before-assembly items, a pre-fabrication power-up audit, and firmware obligations.
---

# Board Bring-up Planner

Bring-up is a design constraint, not a phase that happens later. Almost everything
here costs nothing and a few square millimetres while the layout is open, and is
impossible once the board is fabricated and assembled.

Produce `.pcba-workflow/bringup-plan.md` (runbook plus open items). Default to
review-only; hand schematic changes to `/design-and-review-circuit` and placement to
`/pcb-layout-review`.

## Workflow

1. **List the tools the user owns.** Ask once: programmer/debug probe (e.g. ST-Link,
   J-Link, CMSIS-DAP), USB-serial adapter, bench supply with current limit, scope,
   meter, hot air. Every runbook step that needs a missing tool is a **design
   finding**, not a bring-up problem.
2. **Inventory everything programmable or configurable** in the BOM: MCUs,
   co-processors, modules, PMICs/chargers with OTP or registers, EEPROMs, solder
   jumpers on modules, DIP straps. For each, record how it is programmed, how it is
   recovered from bad firmware, and whether it can still be reached after assembly
   and enclosure.
3. **Design the programming and recovery path.** Follow
   [references/bringup-design-rules.md](references/bringup-design-rules.md):
   programming header or the product's own connector, boot/strap resistors, a GND
   pad next to every strap pad, a real hard-reset path, and a recovery path that
   does not depend on the thing that broke.
4. **Make staged power-up possible.** JLCPCB assembles the board, so you cannot
   "fit the power section first" by hand. Instead add solder jumpers or DNP 0 Ohm
   links between each regulator and its loads, or order a few boards with the
   expensive module DNP, so a rail can be proven before it feeds anything costly.
5. **Place test pads** for every rail, GND, programming/debug pins, UART console,
   reset, and boot straps - in a row on a known pitch, out of mechanical corridors
   and enclosure contact.
6. **List configure-before-assembly items** ("one-way doors"): module jumpers, OTP,
   anything unreachable after the enclosure closes. These go in the build checklist,
   and into the JLCPCB order notes if they affect placement.
7. **Hedge every unknown with a footprint.** If a question can only be answered with
   the part in hand, put the answer's implementation on the board now - DNP resistor,
   0 Ohm link, alternate strap footprint - and write the arrival test that decides it.
8. **Run the pre-fabrication power-up audit** in
   [references/power-up-audit-patterns.md](references/power-up-audit-patterns.md)
   and hand each finding to `/design-and-review-circuit`.
9. **Write the runbook** from
   [references/runbook-template.md](references/runbook-template.md): prove the cheap
   thing before risking the expensive thing (rails before loads, current-limited
   supply before battery, module last), with expected values and pass/fail per step.
10. **Record firmware obligations and accepted defects** - things the board cannot
    fix and firmware must, and known behaviour accepted rather than fixed.

## Gate

`PASS` when every runbook step uses only tools the user owns, every rail and
programming pin has a test pad, every one-way door and DNP hedge is listed with its
arrival test, recovery from bad firmware is possible, and, if the user
asked for an `/adversarial-review`, it has no open FATAL/SERIOUS findings. `USER_REVIEW` for a tool or access
decision only the user can make; `BLOCKED` when programming or recovery is not
possible as designed.

Placement freeze needs the test-pad and strap list; fabrication release needs the
finished plan.
