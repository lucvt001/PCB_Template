# Electronic-product intake checklist

## Product and environment

- User problem, success behavior, prohibited behavior, and intended operator.
- Indoor/outdoor, temperature, humidity, vibration, ingress, cable length, and
  expected lifetime.
- Prototype quantity, production quantity, target board and assembled cost,
  schedule, repairability, and component-lifecycle expectations.

## Electrical architecture

- Every power source, connector, nominal range, transient condition, source
  capability, reverse-polarity or back-power risk, and required isolation.
- Rails and modes: off, startup, programming, normal, sleep, reset, fault, and
  partial-power states.
- External and internal interfaces with direction, voltage domain, data rate,
  likely edge rate, topology, loading, hot-plug behavior, and protection.
- Shared buses or memories with one explicit owner per state and hardware-safe
  defaults before firmware starts.

## Physical architecture

- Board outline, mounting, enclosure, connector location, controls, indicators,
  antenna, thermal paths, keepouts, clearances, and assembly side limits.
- Programming, boundary/test access, debug connectors, measurement points, and
  replaceable or field-serviceable elements.

## Asking questions

Ask only when the two answers give a different board. Examples that changed real
boards: one unit or several (at quantity one, assembly fees dominate part prices);
a hard budget vs "cheap"; which packages may be used; whether a feature transmits,
receives, or both; whether a runtime target is with a display on or off. Do not
ask what you can measure (prices, stock, library class) or what is your job
(decoupling placement).

## Evidence tags

Tag every figure (definitions in the project `CLAUDE.md`):

- `VERIFIED`: authoritative requirement, standard, official datasheet, live page,
  or approved measured result - with source and date.
- `COMPUTED`: arithmetic on verified numbers, with the arithmetic shown.
- `TARGET`: project allocation chosen with stated margin.
- `ESTIMATE`: temporary premise or unmeasured value that must be confirmed before
  its gate.
- `NOT ESTABLISHED`: unknown; must be measured or researched.

Every unresolved item needs an owner, affected stage, and the evidence that
will close it.
