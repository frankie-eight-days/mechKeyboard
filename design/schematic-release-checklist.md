# Schematic release checklist

Use this at the decision to begin PCB placement. For each ID record the revision, evidence, result, exception and person or discipline that owns closure. Use **verified**, **open**, **deferred to layout/firmware**, **unverified**, or **inapplicable with reason**. Record what a calculation assumes and the condition that would invalidate it. A missing calculation and a demonstrated electrical failure warrant different findings. Revisit affected IDs after an ECO.

## Design intent and drawing

| ID | Check and evidence to retain |
|---|---|
| R01 | Identify the exact project, tool, libraries, assembly variant, sheet manifest and supporting document revisions. Recreate the review outputs from that baseline. |
| R02 | Trace every user-facing requirement to a circuit, quantitative limit or explicit system decision. Include mutually exclusive operating modes and allowed degradation. |
| R03 | Render every sheet. At normal reading size follow power and signals through the hierarchy. Inspect pin names, polarities, junctions, crossings, bus membership, title blocks and clipped or obscured text. |
| R04 | Inspect ERC configuration, downgraded rules, excluded markers and intentional no-connects. Run ERC across the hierarchy. Record tool version, diagnostics and exclusions. |
| R05 | Export an independent machine-readable netlist. Trace critical paths by physical pin, look for net aliases, single-node nets and unintended joins, and verify repetitive channels algorithmically. |
| R06 | Check that design notes, firmware tables, wiring diagrams and BOM agree with the native design. Retire stale values and cite the controlling revision. |

Drawing and review practice draws on [Altium’s schematic review checklist](https://resources.altium.com/p/schematic-review-checklist), [Andrew Zonenberg’s hardware checklist](https://github.com/azonenberg/pcb-checklist/blob/master/schematic-checklist.md) and [the KiCad schematic editor manual](https://docs.kicad.org/10.0/en/eeschema/eeschema.html).

## Parts, footprints and production

| ID | Check and evidence to retain |
|---|---|
| L01 | Resolve every fitted reference to an exact MPN, package and footprint. Check embedded symbol pins against physical pad numbers, including duplicated grounds, mounting tabs, exposed pads and NCs. |
| L02 | Compare high-risk land patterns to dimensioned manufacturer drawings. Check top/bottom view, pin 1, polarity, tolerances, shell stakes, paste apertures and mating direction. A pad-number match alone cannot establish orientation. |
| L03 | Reconcile quantities by refdes across schematic, assembly BOM, DNP, variants, off-board items and hand-fitted parts. Document polarity and cable pin order at both ends. |
| L04 | Check the exact order code, lifecycle, supplier quantity and assembler orderable quantity for the intended run. Record the date. Qualify substitutions that change an electrical or mechanical limit. |
| L05 | Identify special fab and assembly operations such as internal routes, nonplated slots, via-in-pad, bottom-side placements and parts sharing the same space. Record supplier capability and leave actual CAM/CPL verification at the appropriate gate. |
| L06 | Check component height, enclosure tolerances, tooling access, mating/unmating envelopes, wire bend and solder access against an explicitly named coordinate frame. |

Manufacturing checks draw on the [Jitter production review checklist](https://jitter.nl/en/pcb-checklist/) and [JLCPCB assembly file guidance](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad).

## Power architecture and faults

| ID | Check and evidence to retain |
|---|---|
| P01 | Map each source, rail, load and return path. Trace normal, insertion, removal, suspend, shutdown, battery-only, absent-pack and mixed-source states. Include capacitor discharge and connector back-voltage after unplug with the battery live. |
| P02 | Budget continuous, startup, transient, stall and combined loads per source tier. Reflect conversion efficiency, available source current, battery supplement, limiter tolerances and quiescent loads. Compare synchronized PWM peak current with the frame average. |
| P03 | Check recommended supply ranges, absolute limits, logic thresholds and voltage headroom at cold/hot corners. Include diode and switch drops, cable loss, regulator dropout and UVLO hysteresis. |
| P04 | Validate each converter’s feedback, passives, operating mode and stability. Compute effective capacitance at bias, ESR, ripple ratings, inductor saturation and startup into the actual load. Qualify the maximum installed distributed capacitance as well as the regulator’s local minimum. |
| P05 | Analyze plug-in, inrush, disconnect and load release. Locate capacitance on each side of limiting/isolation, and document cable L/R, damping, source tolerance and peak stress against ratings. |
| P06 | Trace overvoltage, undervoltage, shorts and reverse connection through protection devices, including detection delay, off-state leakage and FET body diodes. Quantify fault energy or dissipation where relevant. |
| P07 | Calculate component and board thermal margins for worst sustained and pulsed dissipation. Carry any copper-area, thermal-pad and via assumptions into layout. |
| P08 | Establish behavior at power-on, brownout, watchdog, host reset and firmware crash. Check enable defaults, strap sampling and reset order. Distinguish logic disable, software reset and true supply removal. Trace retained rails, stored charge, effective reset and an independent exit from each sleep or ship state. Check minimum recovery slew. Read status/default register values from the exact device revision. |
| P09 | For each power-domain crossing check high/low levels, partial-power-down limits, direction, clamps, pull-ups and sneak current with each side unpowered. |
| P10 | Check bypass values, pin returns and high-di/dt loops against vendor guidance. Give layout a named placement or geometry constraint for every sensitive loop. |

Use the selected IC data sheets for limits. [Analog Devices AN-136](https://www.analog.com/en/resources/app-notes/an-136.html) illustrates why converter current-loop geometry belongs in the handoff.

## Rechargeable battery and external power

| ID | Check and evidence to retain |
|---|---|
| B01 | Match the exact cell, protection board, connector and harness to chemistry, charge voltage, maximum charge/discharge rate, operating floor, polarity, temperature and physical expansion allowance. |
| B02 | Audit charger register defaults and external programming pins, including which limit wins. Check watchdog reversion and sequencing before loads or high-current charging are enabled. |
| B03 | Derive charge time from CC, CV taper, termination and available source power under explicit load and temperature assumptions. State which performance targets remain estimates. |
| B04 | Calculate temperature trips, tolerance, hysteresis and deglitch. Examine sensor open, short, unplug and pin faults for both charging and discharging. |
| B05 | Trace pack removal, deep discharge, protection cutoff/recovery, depleted startup and pack fault independently of normal firmware. Distinguish the normal operating floor from the emergency protection trip. Establish what the exact pack guarantees. |
| B06 | For USB or another negotiated source, distinguish attach, advertised current, enumeration, suspend/resume and high-voltage contracts. Exercise detach and downgrade. Check allowed bus draw in every state. |

Charger-specific manufacturer checklists can suggest failure cases. Apply the limits of the fitted cell and IC. Examples include [TI charger design review guidance](https://www.ti.com/lit/an/slua585/slua585.pdf) and the [USB-IF document library](https://www.usb.org/documents).

## Controller, analog and interfaces

| ID | Check and evidence to retain |
|---|---|
| I01 | Verify controller supply topology, clock source and loading, boot straps, reset, reserved pins, special-function GPIOs, and alternate mappings. Check errata for the actual part or silicon class. |
| I02 | Allocate peripheral instances, pins, clocks, channels, DMA buffers and interrupt resources concurrently. Prove an achievable timing tuple at peripheral resolution for a full transaction with the selected driver’s actual encoding and buffer limits. Include framing, latch time, chain length and CPU/radio contention where applicable. |
| I03 | Trace programming and recovery from a blank or misconfigured board. Verify connector pin order, keyed orientation, VTref, target power, reset, cable and enclosure access. |
| I04 | Verify protocol wiring, data polarity, terminations, levels and idle states. Check external transients, shield returns, ESD device orientation and electrically permissible stubs. |
| I05 | Compute pull-up/down ranges from leakage, sink current, rise time, parasitic capacitance and connected modules. Check address conflicts, clock stretching and stuck-bus recovery. |
| I06 | Analyze ADC/input range, reference, bias, source impedance, acquisition time, RC settling, noise and tolerance across endpoints. |
| I07 | Verify LED, relay, transducer, motor and similar outputs against RMS and peak drive, polarity, dynamics, calibration, safe-off state and load disconnect. |
| I08 | For keyboards, multiplexers or other arrays, verify every element, diode direction, unused locations, rollover/ghost behavior and signal order against its physical coordinate or channel. |
| I09 | Check the RF module's approved supply, ground pattern, antenna orientation, keepout on every layer, separation from metal/enclosure and any host integration conditions. |
| I10 | Check optional modules, switches and external signals during hot insertion, power loss and boot. Verify connector mating view, signal order, pull defaults and any firmware ordering dependency. |
| I11 | Capture the hardware/firmware contract for addresses, polarities, boot states, fault action, timeouts, feature exclusions and safe settings. Assign ownership to timing guarantees. |

## Layout transfer and sign-off

| ID | Check and evidence to retain |
|---|---|
| H01 | Give placement the outline, fixed datums, handedness, board side, mount/copper keepouts, edge ports, RF and mechanical exclusion volumes. Check their coordinate conversion with a second independent point. |
| H02 | List classes and constraints for current, voltage, impedance, return-plane continuity, sensitive nodes, Kelvin sense, differential routing and thermal copper. Distinguish design targets from values that depend on the fab stackup. |
| H03 | Identify accessible observations for each rail, reset, buses, programming and critical faults, including a nearby ground return for each high-speed probe and access at the far end of distributed rails. Record which checks can be made from files and which require assembled hardware. |
| H04 | For each finding record evidence, consequence, disposition, priority, owner, closure proof and earliest stage it blocks. Consolidate duplicate causes and document challenged or dismissed hypotheses. |
| H05 | Reconcile after ECO by repeating relevant pin checks, ERC, netlist assertions and render inspection. Schedule physical DRC, CAM outlines, paste, BOM/CPL orientation and final assembly preview for when those files exist. |

## Mission profile and external exposure

| ID | Check and evidence to retain |
|---|---|
| E01 | Identify the intended ambient, enclosure heating, operating lifetime, humidity and handling. Compare component grade, derating, polarity and endurance to the worst combined conditions. |
| E02 | Define interface exposure and credible fault stimulus separately from normal operation. For hot-plug or shorts include initial rail charge, fault amplitude, duration, protection response and absolute-maximum headroom. |
| E03 | Identify target markets and any applicable product, EMC, radio, battery transport or isolation requirements. For hazardous voltages, establish insulation boundaries, creepage, clearance, fusing and accessible energy from the applicable specification. Assign downstream evidence to its release stage. |
| E04 | Consider a stuck output, lost bus, failed component and interrupted supply during critical operations. Trace an independent path to a safe state and a recovery sequence the available hardware can actually execute. |

For each review, attach the completed coverage record and one issue register. Explicitly identify any check that a desk review could not establish.
