# Layout patterns

Read the section for the block you are placing or routing; you don't need the whole
file. The part's own datasheet layout guidelines and its EVM layout override
anything here.

## Decoupling

- Order along the current path: **supply pin -> capacitor -> via to GND plane**, with
  the smallest capacitor closest to the pin. The capacitor's GND via goes right at its
  pad, not shared through a long trace.
- One small capacitor (typically 100 nF) per supply pin or pin pair, on the same side
  as the IC where possible; bulk capacitance (e.g. 4.7-10 uF) per rail near the IC
  group.
- Don't put a via between the pin and its capacitor unless the capacitor is on the
  other side directly under the pin.
- Two vias on each capacitor pad for low inductance on fast or high-current rails.

## Switching regulators (buck, boost)

- Identify the **hot loop** from the datasheet (buck: input capacitor -> high-side
  switch -> low-side switch/diode -> back to input capacitor GND). Make that loop as
  small as possible on one layer, with the input capacitor's GND and the IC's GND
  next to each other.
- Keep the switch node (SW) copper area as small as the current allows; keep it away
  from feedback, analog, and sensitive signals, and don't run anything under it on the
  adjacent layer except GND.
- Route the feedback trace from the **output capacitor**, away from SW and the
  inductor, with the divider close to the FB pin.
- Inductor close to SW; output capacitors close to the inductor and load. Copy the
  EVM's placement when one exists.
- Thermal pad: solid connection to GND with the via count the datasheet asks for.

## LDOs

- Input and output capacitors at the pins, of the type and ESR the datasheet requires
  for stability.
- Thermal: compute P = (Vin - Vout) x I and give the tab/pad the copper and vias it
  needs.

## STM32 clock (HSE/LSE crystals)

- Crystal and its two load capacitors as close to the OSC pins as possible, on the
  same side, with short symmetric traces.
- GND plane solid under the crystal; a GND guard ring around it tied to the plane with
  vias; no other signals routed under or next to it.
- Keep switching nodes, clocks, and high-current paths away. Follow ST's crystal
  layout guidance (AN2867) for the device family.

## GND stitching and planes

- Stitch outer-layer GND pours to the GND plane with vias every few millimetres along
  edges and around pour islands; delete GND islands that can't be stitched.
- A GND via next to every signal via on fast or sensitive nets (return path for the
  layer change).
- A row of GND vias along the board edge helps contain noise on boards with motor or
  switching stages.
- **Non-ground vias (power/signal stitching or layer changes) go along the edge of
  a copper pour, never in the middle of it**, so the ground layers underneath stay
  uninterrupted.
- **Pair every non-ground via with a ground via directly across the pour/trace from
  it** to cancel EMI and give the return current a path.
- **Fill the leftover board area with ground pour.** Where a pour spans several
  layers (e.g. the GND pour on both inner layers), draw **one** zone and tick
  multiple layers, instead of one zone per layer.

## Thermal

- Power components (regulators, MOSFETs, shunts, drivers) get copper area on the
  outer layer and an array of thermal vias into the planes under their thermal pads.
- **No via-in-pad (it is expensive).** Use the standard 0.64/0.30 mm via
  (diameter/drill) for thermal vias and make room for them *between* the solder
  paste regions of the thermal pad: split the paste into windows so the vias sit in
  the gaps, and check the gap is at least via diameter plus mask/clearance rules
  (`COMPUTED`). Follow the part's datasheet for the pad and via pattern; if the gaps
  can't fit vias, place them in a copper area adjacent to the pad connected by
  wide copper, and flag it for the user rather than falling back to via-in-pad.
- Spread hot parts apart; a sealed hull has poor airflow.

## Fiducials, test points, mounting

- JLCPCB adds fiducials on its rails for assembly. Add 2-3 board-level fiducials
  (1 mm copper dot, 2 mm mask opening) on non-collinear corners if the board will be
  assembled without rails or has fine-pitch parts. Confirm current JLCPCB guidance.
- Test points per the bring-up plan: rails, GND, programming, UART, reset, straps.
- Mounting holes: plated or not as the mechanics need, with a copper and component
  keep-out ring for the screw head and washer; connect plated holes to GND (or
  chassis) deliberately, not by accident.

## CAN and RS-485

- Transceiver close to the connector. TVS/ESD protection **at the connector**, then
  the optional common-mode choke, then the transceiver.
- Termination (120 Ohm, or split 2 x 60 Ohm with a capacitor to GND) at the connector
  end, populated only on boards at the ends of the bus - use a DNP footprint or a
  jumper.
- Route the pair together, short, over continuous GND; no stubs to test points.

## USB

- ESD array right at the connector; D+/D- as a 90 Ohm differential pair to the MCU with
  no stubs, matched lengths, and no layer changes if possible (if unavoidable, add GND
  stitching vias next to the pair's vias).
- VBUS protection and bulk capacitance at the connector.
- Connector shell to GND per the design decision (direct, RC, or ferrite), consistent
  with the enclosure grounding.

## Ethernet

- PHY close to the magnetics/RJ45; 100 Ohm differential pairs between them, short and
  matched within each pair.
- Keep the isolation gap under the magnetics free of copper on all layers (no planes
  crossing it), per the magnetics datasheet.
- Termination, bias, and Bob Smith network per the PHY and magnetics datasheets and
  the PHY's reference design.

## High-current battery paths

- Battery input -> fuse -> reverse-polarity protection -> TVS -> bulk capacitors ->
  loads, in that physical order, all close to the input connector.
- Wide pours sized from `design-rules.md` section 2, with the vias from section 3 at
  every layer change. Check the narrowest neck.
- Current-sense shunts: Kelvin connections (separate sense traces from the inner edges
  of the shunt pads to the amplifier, routed as a pair away from the power path).
- Use a net class with battery-bus clearance from `design-rules.md` section 4.

## Motor / ESC drive

- Power stage (half-bridges, bulk and ceramic capacitors) as a tight loop like a buck
  hot loop: high-frequency ceramics directly across each half-bridge.
- Gate drive loop small: driver -> gate resistor -> gate, and the return to the
  driver's source/ground pin, kept short and together.
- Separate the power ground and the logic/analog ground paths, joined at one point
  near the bulk capacitors / current shunt; keep the logic and sensors away from the
  motor phase traces.
- Motor phase outputs straight to the connector; no sensitive signals alongside them.
