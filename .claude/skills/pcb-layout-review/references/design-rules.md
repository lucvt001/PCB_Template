# Design rules for the template's 4-layer JLCPCB board

Read this when setting up net classes, sizing power paths, choosing clearances, or
routing controlled-impedance pairs. The fab minimums and default net class live in
`pcb/template.kicad_pro`; this file does not repeat them. Every number here is a
starting point tagged with its basis - confirm against the current JLCPCB pages
and the parts' datasheets before relying on it.

## 1. Stackup and layer assignment

Default assignment for a 4-layer board:

| layer | use |
|---|---|
| F.Cu | components, short signal routing, local power |
| In1.Cu | **solid GND plane** - the reference for F.Cu; no routing except unavoidable short jumps |
| In2.Cu | **solid GND plane** - the reference for B.Cu |
| B.Cu | signal and power routing/pours, referenced to In2.Cu |

**Project rule:** F.Cu and B.Cu carry signal and power; the two middle layers are
both ground. Route power as traces/pours on the outer layers, not on inner layers.

Rules:

- A solid GND plane on In1 is more valuable than a dedicated low-current power plane.
  For boards with mostly low-current rails, consider GND on both In1 and In2 and
  route power as wide traces/pours on outer layers.
- Never route a fast or controlled-impedance signal across a split or void in its
  reference plane. Where a signal changes layer, put a GND stitching via within about
  1-2 mm of the signal via, so the return current can change plane too.
- **Check the stored stackup before any impedance work.** The template board
  currently stores a generic stackup (three 0.48 mm FR4 dielectrics, 35 um copper on
  all four layers). JLCPCB's standard 4-layer stackups (e.g. JLC04161H-7628) have a
  thin prepreg between each outer layer and its inner plane and 0.5 oz inner copper
  `[ESTIMATE - read the real values from jlcpcb.com/impedance]`. Set the KiCad
  stackup to the JLCPCB stackup you will select on the order form, and record which
  one in the order-form checklist.

## 2. Trace width vs current

Use IPC-2152 (or a calculator based on it) for final sizing. IPC-2221's formula below
is conservative for traces near planes, which is why it is a safe first pass.

`I = k x dT^0.44 x A^0.725`, A in mil^2, k = 0.048 (external) or 0.024 (internal);
1 oz copper = 35 um = 1.378 mil. `[COMPUTED from IPC-2221]`

| current (A) | ext 1 oz, +10 C | ext 1 oz, +20 C | ext 2 oz, +10 C | int 0.5 oz, +10 C | int 1 oz, +10 C |
|---|---|---|---|---|---|
| 0.5 | 0.12 mm | 0.08 | 0.06 | 0.60 | 0.30 |
| 1 | 0.30 | 0.20 | 0.15 | 1.56 | 0.78 |
| 2 | 0.78 | 0.51 | 0.39 | 4.07 | 2.03 |
| 3 | 1.37 | 0.90 | 0.68 | 7.11 | 3.56 |
| 5 | 2.77 | 1.82 | 1.38 | 14.4 | 7.19 |
| 10 | 7.19 | 4.72 | 3.60 | 37.4 | 18.7 |
| 15 | 12.6 | 8.26 | 6.29 | 65.5 | 32.7 |
| 20 | 18.7 | 12.3 | 9.36 | 97.4 | 48.7 |

How to use it:

- Size every power path for the **worst-case** current from the power budget, not
  typical. Note the temperature rise you chose.
- Inner layers are thin (0.5 oz on JLCPCB's standard 4-layer) and badly cooled: put
  high current on outer layers or wide pours, and order 2 oz outer copper if a path
  needs it.
- Above a few amps, use pours rather than traces, and check the **narrowest neck**
  (connector pins, fuse pads, between vias). The neck sets the rise.
- Check voltage drop too: R = rho x L / (w x t), rho(Cu) = 1.72e-8 Ohm m at 20 C
  (about 0.5 mOhm per square for 1 oz). `[COMPUTED]`
- For battery and motor paths, also check the connector's and fuse's current rating
  and the pad size they need.

## 3. Vias for current

A via barrel's copper area is about `pi x drill x plating thickness`. For a 0.3 mm
drill, plating of 18-25 um gives roughly 1.4-1.8 A at +10 C by the IPC-2221 external
formula `[COMPUTED; plating thickness is an ESTIMATE - check JLCPCB's spec]`.

- Plan **at least 2 vias per amp** for power layer changes (margin for plating
  variation and current crowding), more under thermal pads.
- Spread power vias along the current path, not clustered in one spot.
- Every via counts toward the drill count; check it against the fab's surcharge
  threshold (see `release-pcba-fabrication/references/jlcpcb-constraints.md`).

## 4. Clearance vs voltage

The bus voltage varies by board, so pick the row for each net pair's **peak**
voltage difference (DC or AC peak, including transients). IPC-2221B Table 6-1
minimum conductor spacing, in mm `[from IPC-2221B as commonly reproduced - confirm
against the standard for anything above 50 V]`:

| voltage (V peak) | B1 internal | B2 external, uncoated (<3050 m) | B4 external, permanent polymer coating | A5 external, conformal-coated assembly | A6 component lead, uncoated |
|---|---|---|---|---|---|
| 0-15 | 0.05 | 0.1 | 0.05 | 0.13 | 0.13 |
| 16-30 | 0.05 | 0.1 | 0.05 | 0.13 | 0.25 |
| 31-50 | 0.1 | 0.6 | 0.13 | 0.13 | 0.4 |
| 51-100 | 0.1 | 0.6 | 0.13 | 0.13 | 0.5 |
| 101-150 | 0.2 | 0.6 | 0.4 | 0.4 | 0.8 |
| 151-170 | 0.2 | 1.25 | 0.4 | 0.4 | 0.8 |
| 171-250 | 0.2 | 1.25 | 0.4 | 0.4 | 0.8 |
| 251-300 | 0.2 | 1.25 | 0.4 | 0.4 | 0.8 |
| 301-500 | 0.25 | 2.5 | 0.8 | 0.8 | 1.5 |

How to use it:

- Treat outer layers as **B2 (uncoated)** unless the board will be conformally
  coated; solder mask alone is not usually counted as a permanent coating.
- Use the **A6** column for exposed pads and component leads.
- The template's default 0.127 mm clearance is fine for low-voltage nets but **not**
  for 31 V and above on outer layers (B2 needs 0.6 mm). Create a net class for the
  battery/motor bus and set its clearance from this table.
- Wet or condensing environments (inside a hull that may leak or sweat) need more
  margin than the table, and safety-rated isolation needs creepage per the relevant
  safety standard, not IPC-2221.

## 5. Controlled impedance

| interface | target | notes |
|---|---|---|
| USB 2.0 FS/HS data | 90 Ohm differential, +/-10 % | FS (12 Mbit/s) tolerates loose control; HS needs it |
| Ethernet 10/100 (PHY to magnetics) | 100 Ohm differential | pairs matched within a pair; keep short |
| CAN, RS-485 | about 120 Ohm differential | on-board length is short; termination matters more than trace geometry |
| RF feed (if any) | 50 Ohm single-ended | follow the module's reference layout exactly |

- Get widths and gaps from **JLCPCB's impedance calculator** for the exact JLCPCB
  stackup and copper weight you will order, then set them in KiCad's net class or
  differential-pair settings. Don't reuse widths from another stackup.
- Select impedance control on the order form if the interface needs it, and name
  the stackup.
- Route each pair over a continuous plane, with no stubs, symmetric spacing, and
  intra-pair length matching to the interface's requirement (tune with small
  serpentines only where needed).
