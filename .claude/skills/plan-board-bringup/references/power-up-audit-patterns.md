# Pre-fabrication power-up audit patterns

Adapted from `daishuge/pcb-skill` (MIT, see `../LICENSE`).

Run a sceptical electrical audit before the release is final, scoped to what the
routing, placement, and mechanical reviews did not cover: power-up sequencing and
straps, every IC's mandatory pins against its own datasheet, recomputation of every
value that sets behaviour, thermal, battery safety, and ratings against actual use.
On the reference board this found nine serious issues on a design everyone believed
was finished; each was a value or part change that was free before fabrication.

## Patterns that pass review and fail on the bench

- **Trace mechanical contacts in both states.** A jack's detect pin tied to a
  normally-closed blade became the amplifier output whenever no plug was inserted,
  driving it below its absolute maximum every audio cycle. Check every switch,
  jack, and connector contact open and closed.
- **Check current-setting values against package dissipation in the real
  enclosure.** A charger programmed for the datasheet's 500 mA could only dissipate
  enough for about 170-260 mA at its package's thermal resistance, so it sat in
  thermal regulation and heated the case and cell. Compute
  `P = (Vin - Vout) x I` against `(Tj_max - T_ambient_in_enclosure) / theta_JA`.
  A sealed AUV hull's internal ambient is not 25 C.
- **If the datasheet table does not contain your operating point, you have no
  specification.** A mux specified at 5 V was run at 3.3 V. The fix was a
  pin- and land-compatible part specified at 3.3 V - a free BOM change.
- **Nothing analogue may float.** Every node needs a DC path when switched out.
- **Check each rail against the maximum of what it feeds, at worst-case
  tolerance** (reference, feedback resistors, load regulation).
- **Ceramic capacitors lose capacitance under DC bias.** Recompute filter corners,
  coupling bandwidth, and regulator stability with the derated value.
- **A signal from a device on a different rail can exceed your MCU's rail** and
  inject current into its clamp diodes. Check powered-down and partially-powered
  states too. Before adding a divider, check the low end of the range still meets
  VIH.
- **Unkeyed power inputs need protection you can see**: reverse-polarity protection
  in the circuit, `+`/`-` silk, and different pad shapes.
- **Mandatory-pin sweep:** for every IC, walk its datasheet pin table and confirm
  every pin's required connection (enable, mode, exposed pad, NC vs DNC, required
  capacitors) is satisfied.
- **Things only settled with the part in hand** get a written 60-second arrival
  test.

Record what you checked and found **correct**, with evidence, so the next pass does
not redo it.
