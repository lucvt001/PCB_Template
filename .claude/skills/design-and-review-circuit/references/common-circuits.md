# Common circuit blocks

Starting points for the blocks these AUV boards usually contain. Read only the
section you are designing. **The part's datasheet and its EVM/reference design
override everything here**; record deviations from the EVM in `DECISIONS.md`. Values
marked ESTIMATE are typical starting values to confirm.

The bus voltage varies by board: record this board's maximum bus voltage
(including transients and charger/regeneration peaks) in `DECISIONS.md` first, and
size every rating below from it.

## STM32 MCU

Read the device datasheet and ST's "Getting started with hardware development"
application note for the family (e.g. AN4488 for STM32F4, AN5096 for G0, etc.).

| item | typical connection |
|---|---|
| VDD pins | 100 nF per VDD pin, plus one 4.7-10 uF bulk per MCU `[ESTIMATE; use the family app note]` |
| VDDA / VREF+ | 1 uF + 10 nF (or 100 nF) at the pins; optional ferrite from VDD for a cleaner analog supply |
| VCAP pins (F2/F4/F7/H7 etc.) | low-ESR capacitor of the value in the datasheet (often 2.2 uF or 4.7 uF) - required, the core regulator is unstable without it |
| VBAT | to a coin cell / supercap, or to VDD with 100 nF if unused |
| NRST | 100 nF to GND (internal pull-up); reset pad or button; route to the SWD header |
| BOOT0 | 10 kOhm pull-down to boot from flash, with a pad or jumper to pull it high for the system bootloader. Some newer families use an option bit (nBOOT0) - check |
| HSE crystal | load caps `C1 = C2 = 2 x (CL - Cstray)`, Cstray about 2-5 pF `[ESTIMATE]`; check the crystal's ESR and the oscillator's gain margin per AN2867 |
| LSE (32.768 kHz) | low-drive crystal with the CL recommended for the family; layout matters more than value |
| SWD | header with VTref, SWDIO, SWCLK, NRST, GND, and optionally SWO: e.g. 10-pin 1.27 mm Cortex debug or a Tag-Connect footprint |
| unused pins | leave as configured by firmware (analog input default) or tie per the datasheet; don't leave required-pull pins floating |

USB on STM32: check whether the part has internal D+ pull-up and needs a 48 MHz
clock source (crystal or CRS from USB SOF).

## USB-C device (sink, USB 2.0)

- **CC1 and CC2 each get their own 5.1 kOhm pull-down (Rd) to GND.** Do not share one
  resistor between them.
- ESD array on D+/D- at the connector (low capacitance, rated for USB 2.0 HS if used).
- VBUS: TVS rated for VBUS, bulk capacitance within the USB limit, and a fuse or
  current limit if the board can draw a lot.
- Connect both D+ pins and both D- pins of the receptacle (A6/B6, A7/B7).
- Shell: decide its connection to GND/chassis and record it.

## CAN

- Transceiver supplied at the voltage its datasheet requires; logic side at the MCU's
  I/O voltage (or a transceiver with a separate VIO pin).
- **Termination:** 120 Ohm at each physical end of the bus only. Prefer split
  termination (2 x 60 Ohm with about 4.7 nF to GND at the midpoint) for better EMC,
  on DNP footprints or a jumper so only end nodes populate it.
- TVS diode rated for CAN at the connector; optional common-mode choke.
- STB/silent pin tied to a defined state (MCU pin or resistor).
- For long tethers or separate grounds, consider an isolated transceiver.

## RS-485

- Transceiver with fail-safe receivers (preferred), or bias resistors at one node per
  the transceiver datasheet so the idle bus reads a defined state.
- 120 Ohm termination at the two ends only (DNP footprint or jumper).
- TVS at the connector; driver enable (DE/RE) driven by the MCU with a defined default
  (pull-down so the bus isn't driven at reset).
- Consider isolation on long runs.

## Ethernet (10/100)

- PHY with its reference design: crystal or clock, strap resistors (address, mode),
  termination (often 49.9 Ohm per line to a centre-tap capacitor) per the PHY.
- Magnetics or an RJ45 with integrated magnetics; Bob Smith termination (often
  75 Ohm per pair and a 1 nF high-voltage capacitor to chassis) per the magnetics
  datasheet.
- RMII/MII to the STM32: check the 50 MHz reference clock source and the clock
  direction.

## Battery input and power path

In order from the connector:

1. **Fuse** sized for the wire and the board, not just the load.
2. **Reverse-polarity protection:**
   - P-MOSFET in the high side, gate to GND through a resistor, with a Zener
     clamping gate-source if the bus exceeds the MOSFET's VGS(max);
   - or an ideal-diode controller with an N-MOSFET for high currents (lower loss).
3. **TVS:** standoff voltage (VRWM) at or above the maximum normal bus voltage;
   clamping voltage below the absolute maximum of everything it protects.
4. **Bulk capacitance:** voltage rating about 1.5-2x the maximum bus voltage
   `[TARGET]`; check ripple-current rating for motor loads.
5. **Inrush limiting / pre-charge** if large bulk capacitance meets a stiff battery
   (connector arcing, fuse stress): a hot-swap controller or pre-charge resistor.
6. **Monitoring:** voltage divider to the ADC (check the divider's voltage rating
   and that the ADC input stays in range at the maximum bus voltage), and a
   current-sense amplifier with a Kelvin-connected shunt.

## Regulators

- **LDO:** input/output capacitors exactly as the datasheet specifies (value, type,
  ESR); dissipation P = (Vin - Vout) x I against the package's theta_JA at the
  enclosure's internal ambient.
- **Buck/boost:** follow the datasheet design procedure and EVM: inductor value and
  saturation current above peak inductor current with margin, input/output
  capacitors with DC-bias derating, feedback divider (keep its current reasonable),
  enable/UVLO divider from the bus, soft-start.
- Check each rail's worst-case maximum against every load's absolute maximum.

## Motor / ESC drive

- Gate driver suited to the bridge (bootstrap supply sized per datasheet, dead time).
- Gate resistor (typically 2-20 Ohm for power stages `[ESTIMATE]`), and a gate-source
  pull-down so the MOSFET stays off while the driver is unpowered.
- MOSFET VDS rating with margin over the bus plus switching overshoot; RDS(on) at the
  gate voltage you actually drive.
- Bulk + ceramic capacitance across the bridge; TVS or a braking/clamp path for
  regeneration back onto the bus.
- Current sense per phase or in the DC link, with a filter matched to the ADC.
- Brushed motors, solenoids, relays: flyback diode (or TVS for faster decay) across
  the coil.

## Small signals

- **I2C pull-ups:** `Rmin = (VDD - 0.4 V) / 3 mA`; `Rmax = tr / (0.8473 x Cb)`, with
  tr = 1000 ns (100 kHz) or 300 ns (400 kHz) and Cb the total bus capacitance
  (NXP UM10204). One set of pull-ups per bus.
- **LED resistor:** `R = (Vsupply - Vf) / If`, with If well below the LED's maximum;
  check the driving pin's current limit.
- **MOSFET switch from a 3.3 V pin:** logic-level MOSFET with RDS(on) specified at
  2.5-3.3 V VGS, 100 Ohm-1 kOhm gate resistor, 10-100 kOhm gate pull-down.
- **Connector ESD:** a TVS or ESD array on every signal leaving the board, placed at
  the connector, with capacitance low enough for the signal's speed.
