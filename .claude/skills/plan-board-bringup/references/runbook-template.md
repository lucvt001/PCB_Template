# Bring-up runbook template

Adapted from `daishuge/pcb-skill` (MIT, see `../LICENSE`). Write this **during
design**. Mark any step that needs a tool the user does not own as
`[needs <tool>]` - each one is a design finding.

```markdown
# Bring-up runbook - <board> <rev>

Tools assumed: <bench supply with current limit, meter, scope, debug probe, cable ...>

## 0. Before power
a. Visual inspection against the JLCPCB placement-review screenshots: polarity,
   pin 1, rotation of every IC, connector orientation.
b. Set <one-way-door items> (module jumpers, straps) before fitting <part>.
c. Confirm strap population: <R fitted / R DNP>. If <symptom>, swap them.
d. Meter every input rail to GND for shorts: expect > <value>.

## 1. First power, current-limited
Supply <V> at <limit> mA into <connector>, all rail links open.
Expect idle current < <value>. **If higher, stop.**

## 2. Prove each rail unloaded, then close its link
For each rail: measure <TP> vs <GND TP>: expect <V> +/- <tol>. Close <JP>.
Re-measure under load: expect <V>, current <range>.

## 3. Program the main MCU
<probe/connector, tool, command>. Expected ID: <value>.
If it never connects: <recovery gesture: power off -> bridge BOOT<->GND -> power on
-> flash -> remove bridge>.

## 4. Console and basic I/O
<UART pads, baud>. Expected banner: <text>.

## 5. Each subsystem, cheapest first
<sensor / comms / motor driver / RF ...>: stimulus, expected result, pass/fail.

## 6. Settle the open unknowns
<each DNP hedge and arrival test: measurement that decides it, and what to fit>

## 7. Battery / high-energy sources last
Connect <battery> only after everything above passes.
```

## Firmware obligations and accepted defects

Record, in the same file:

- **Accepted defects** with the reason (e.g. a turn-off pop that has no cheap
  hardware fix).
- **Firmware mitigations** for things the board cannot fix (drive strength, clock
  limits, debounce).
- **Firmware obligations created by the hardware** (PWM frequency limits, enable
  timing, sense thresholds that must sit above leakage).
- **Bring-up measurements that are not banked results** (runtime, RF range,
  thermal rise), each with a named fallback.
