---
name: pcb-layout-review
description: Audit, finish, or port PCB placement and routing using circuit intent, mechanical and enclosure constraints, sourcing evidence, native DRC/connectivity, 2D plots, and manufacturing feedback. Use before routing, after autorouting, before fabrication release, when adapting a proven board to another connector, enclosure, platform, or regional variant, or when reviewing routability, layers, GND references, power distribution, decoupling, buses, controlled interfaces, RF keepouts, vias, 2D placement mechanics, cost-driving features, opens, or DRC findings.
---

# PCB Layout Reviewer

Use the humanized architecture and circuit constraints as placement policy, not
reference-number order or one global wire-length score. Read
[references/layout-review-checklist.md](references/layout-review-checklist.md)
(including its "Proven lessons" section). Record the
gate with [references/layout-review-record.md](references/layout-review-record.md)
and use the KiCad commands in
[references/kicad-adapter.md](references/kicad-adapter.md). Gerber/drill/CPL or
images alone permit DFM and visual review only, not connectivity proof.

Also read, when they apply:

- [references/design-rules.md](references/design-rules.md) - when setting net
  classes, sizing power paths and vias, choosing clearance for higher-voltage nets,
  or routing controlled-impedance pairs;
- [references/layout-patterns.md](references/layout-patterns.md) - the section for
  the block being placed or routed (decoupling, buck/LDO, STM32 crystal, stitching,
  thermal, fiducials, CAN/RS-485, USB, Ethernet, battery path, motor drive);
- [references/placement-mechanics.md](references/placement-mechanics.md) - always
  before placement freeze and before release (courtyards, connector mouths and
  mating areas, module bodies, keep-outs, hand-fit access, enclosure outline);
- [references/connector-stack-and-fanout.md](references/connector-stack-and-fanout.md) -
  modules, card sockets, daughtercards, board-to-board, or dense connector fanout;
- [references/variant-porting.md](references/variant-porting.md) - a derivative of
  a proven board (connector, enclosure, platform, or regional variant).

## Layout workflow (project rules)

1. **Board size first:** ask the user to set the board size/outline before placing
   anything; don't pick one yourself.
2. **Sheet by sheet, placement first:** place one schematic sheet at a time. After
   the initial placement, **stop for the user to check; do no copper pours and no
   routing yet.** Apply the user's corrections, and only after they approve the
   placement do pours and routing, then stop again. Start the next sheet only
   after the user approves the current one.
3. **No automatic review.** Don't spawn a reviewer/Opus agent unless the user asks;
   the review is normally the final check (see `CLAUDE.md`, Human-centric
   workflow). Ignore the `/adversarial-review` steps below until then.
4. Stackup use, via placement, pours, and thermal via rules are in
   `references/design-rules.md` section 1 and `references/layout-patterns.md`
   (GND stitching and planes, Thermal).

## Establish truth

1. Read repository rules, native board/project sources, product brief,
   architecture, `DECISIONS.md`, sourcing lock, circuit review, bring-up plan,
   schematic/netlist, mechanics, enclosure, manufacturer constraints, and
   project-local layout lessons.
2. Identify the board source of truth and supported adapter. KiCad may use
   native CLI/API tooling; other EDA tools require equivalent native exports.
   Gerber or images alone permit review, not safe editable round-trip.
3. Record board/project hashes, layer stack, net classes, rules, placement,
   connectivity, raw DRC, classified DRC, via/drill histogram, and top/bottom
   2D assembly plots before changing anything. **Read the rule set and layer stack actually
   stored in the `.kicad_pro`/`.kicad_dru`/`.kicad_pcb`**, not the one you intended.
4. Record connector maturity and every assembly dimension as measured,
   drawing-derived, inferred, or TBD. Treat a plausible model as visual
   evidence, not mechanical proof.
5. Distinguish hard constraints from negotiable targets. Never trade a short,
   new open, corrupted return path, unsupported pad, keepout violation, unsafe
   ownership state, or fabrication violation for a better score.

## Review in order

1. **Architecture placement:** align external connector pin order with
   functional corridors; place protection, translation, processing, memory,
   and outputs along real flow. Keep ownership and reset controls direct.
2. **Critical locality:** decoupling in the supply-pin escape path, tight
   regulator loops, correct crystals/feedback, connector protection, antenna
   edge/keepout, user access, thermal paths, and enclosure clearance. Place the
   bring-up plan's test pads, strap pads, and rail-isolation links now.
3. **Placement mechanics (2D):** run the checklist in `placement-mechanics.md`:
   courtyard/Fab outlines, nothing under module bodies, connector mouths and
   mating areas, keep-outs on copper, hand-fit access, and enclosure outline.
   Do not render 3D or analyse part heights unless the user asks.
4. **Routability, not just legality:** before routing, run the routability
   section of the checklist - via-lane widths between parts, fine-pitch escape
   arithmetic, parts with no via-capable side, and a legal standard-process
   escape for every dense connector/module power and GND pad. A placement with
   zero courtyard overlaps can still be unroutable. "No legal site" is not an
   answer while neighbouring parts can move.
5. **Layer and reference strategy:** choose layer count from bus density,
   routing channels, return paths, RF, controlled interfaces, power current,
   board size, and fabrication cost. A solid reference plane is normally more
   valuable than a dedicated low-current power plane; never assume four or six
   layers without analysis.
6. **Routing:** preserve continuous return paths, short critical controls,
   sensible topology, no stubs where forbidden, appropriate width/spacing,
   matched pairs/groups only when budgets require them, and legal transitions.
7. **Power and zones:** prove every rail and GND pad reaches the intended
   network. Same net name, overlapping fill, or zero pad-opens is not proof.
   Connectivity is layer-aware; a declared zone is not a filled zone. Compare
   DRC on stored fills with `kicad-cli pcb drc --refill-zones` (without
   `--save-board`); a difference means the saved fills are stale.
8. **Manufacturing:** compare trace/space, annulus, mechanical drill, via type,
   finish, thickness, impedance, drill count, and other cost thresholds with the
   current fabricator quote. Treat premium features as measured DFM feedback, not
   an automatic reason to weaken electrical constraints.
9. **Independent visual pass:** inspect clean 2D views, each signal layer, and
   fresh top/bottom 2D assembly plots (Fab + SilkS + CrtYd + Edge.Cuts). Verify
   body outlines, pin 1, polarity, connector
   overhang, pad support, antenna, outline, keepouts, silkscreen, and mechanics.
   Run silk-over-silk, silk-over-copper, and edge-clearance checks before the
   visual pass; preserve pin-1, polarity, and functional meaning, and leave
   unresolved dense labels at `USER_REVIEW`.

Split placement and routing into separate passes with a **user check** between
them (an `/adversarial-review` only if the user asks): floorplan-level problems
must be found before the copper exists.

## Experiment safely

Use named candidate states and paired project files. Make one coherent change,
then measure raw disconnects, real DRC, power disconnects, layout gates, and
manufacturing defects. Record it with `scripts/score_experiment.py`; write new
project-specific lessons with `scripts/record_lesson.py`. Both default to
`.pcba-workflow/` and never mutate the installed skill.

Freeze the input and compare stackup, outline, via-process, and routing
experiments with the current best safe candidate using the complete gate
vector. A larger board or extra layer is useful only when it removes a measured
blocker without regressing another gate.

Prefer high-scoring applicable methods. Do not repeat a negative method unless
conditions materially changed. An accepted candidate must be a measured net
improvement and may not add opens, real DRC, power disconnects, or verified
manufacturing defects. A successful route for one trapped net is not promotable
when its coupled donor set is incomplete or another lane becomes stranded.

When running an autorouter (e.g. Freerouting via DSN/SES), measure the input size
first, and supervise it so a crash or stall is reported: output present, crash
signature in the log, process gone, wall-clock timeout, and a progress-rate floor.
Judge the result on the board read back into KiCad, never on the session file.

## Release gate

Require zero unexplained raw disconnects, zero real DRC errors, zero power
disconnects, all project layout checks passing, verified planes/critical nets,
and visual/mechanical/silkscreen PASS in the same saved board/project state.
Save, close, reopen, and re-measure before declaring it. If assembly depends on
an unverified connector body, card thickness, insertion depth, retention feature,
or enclosure stack, the result remains `USER_REVIEW` or `BLOCKED` even when DRC is
clean. An `/adversarial-review` of the routed board must have no open FATAL or
SERIOUS findings.

Document only narrow, evidence-backed waivers in
`.pcba-workflow/layout-review.json`. Hand the result to
`/release-pcba-fabrication`. JLCPCB's own placement preview after upload is a
separate check the user does.
