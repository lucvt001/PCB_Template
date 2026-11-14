# Derivative PCB variant porting

Use this workflow when a proven board is adapted to another connector,
enclosure, platform, regional standard, or mechanically related product. The
goal is controlled reuse: retain verified circuit/layout knowledge without
assuming the parent geometry still satisfies the target.

## 1. Write the delta before layout

Freeze the donor PCB/project and record its hashes. Create a target manifest
covering:

- connector pin order, pitch, contact geometry, mating datum, and insertion
  envelope;
- exact orderable connector MPN, body, locating features, footprint origin,
  mating-card thickness, insertion depth, retention, and sample status;
- removed, added, or reassigned circuit functions and safe-state behavior;
- power, ground, audio, protection, programming, and user-interface changes;
- board outline, thickness, slots, bosses, shell limits, antenna regions, and
  keepouts;
- assembly side, panel/depanel assumptions, finish, edge treatment, and current
  fabrication thresholds.

Do not begin from a cropped or scaled board. A matching pin count does not
prove matching pin semantics, mechanics, return paths, or assembly support.

## 2. Preserve the mating edge

Treat contacts, tongue, bevel, insertion keepouts, and the host datum as hard
geometry. If the target needs more area, extend only in a direction proven by
the host and enclosure. Require a 1:1 fit gate for every nonstandard outline;
a clean board plot is not enclosure proof.

For a socket, module, or board-to-board connector, distinguish intentional
body/mouth overhang from pads or support features that lack substrate. Keep a
conservative courtyard while the exact body or physical sample is unverified.

## 3. Reuse intent, not coordinates

Carry over functional blocks, physical pin-bank direction, decoupler/support
relationships, routing topology, and verified local constraints. Re-run the
humanized signal-flow, source/destination pin-side, power/reference, RF,
mechanical, and sourcing reviews on the target. Optimize family-level routing
metrics only after those checks.

Geometry-lock each candidate: compare outlines, slots, fixed connectors,
keepouts, footprint transforms, pad nets, zones, and the paired project file.
Record every allowed transform or route change.

## 4. Route transactionally

Prefanout power before dense buses and route scarce shared spines early. When a
trapped route requires neighboring lanes to move, preserve the smallest
coherent donor and integrate every changed net atomically. Prove all displaced
nets and compare non-whitelisted route fingerprints before promotion.

When an autorouter produces no target route, inspect the job rather than
guessing from its headline warning:

- confirm the target net and pins in the exported input;
- count fixed and movable wiring scopes;
- inspect the result for target-net route occurrences;
- verify that the minimum physical blocker was allowed to move.

Retry only after the movable window or board conditions materially change.
Board growth counts only if the new geometry creates a measurable corridor;
extra area elsewhere does not resolve a local connector fanout blocker.

## 5. Prove visuals and release together

Plot donor and target 2D outlines (Edge.Cuts + Fab) at the same physical scale;
show explicit dimensions. Inspect both sides, each signal layer, connector support, antenna, contacts, tongue, slots, and enclosure
limits. Then run normalized silk-over-silk, silk-over-copper, and edge-clearance
checks. Preserve pin-1, polarity, and functional labels; classify intentional
connector-body overhang separately and leave unresolved labels at
`USER_REVIEW`.

For multi-board products, put every adapter, daughtercard, and mating connector
in one dimensioned 2D drawing at one scale. Mark dimensions as measured,
drawing-derived, inferred, or TBD.

Release still requires one saved board/project state with zero unexplained raw
disconnects, zero real DRC, zero power disconnects, passing layout gates,
verified reference paths, and visual/mechanical/silkscreen approval.
