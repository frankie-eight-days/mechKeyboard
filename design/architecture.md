# Keyboard electrical architecture, first pass

Design brief: 65% US ANSI keyboard, USB-C data and Bluetooth LE, physical two-position output selector, soldered MX switches and RGB shine-through legends. A hand-fitted actuator beneath W provides game feedback. The rear shelf carries a center OLED and a top-right volume potentiometer. The proposed layout has 67 keys. Design for an assembled SMT board from LCSC/JLCPCB, with the builder installing stabilizers, plate, switches and keycaps. The first electrical capture is available in the [KiCad project](../electronics/keyboard.kicad_pro). The power circuits and key geometry have reached schematic and mechanical review. Consult the current subsystem records before using the earlier sizing estimates. Mechanical work and electrical verification will use models, drawings and CAD.

| Design record | What it owns |
|---|---|
| [Revision F assembly stock](assembly-stock.md) | Exact supplier IDs, available order quantities and assembly processes for five boards |
| [Controller and pins](controller-and-pins.md) | Module pads, digital signals, firmware behavior and recovery |
| [Display and volume](display-and-volume.md) | Center I²C OLED, potentiometer sensing, power states and host data |
| [WASD haptics](haptics.md) | SYS-fed driver, bus isolation, actuator wiring and game-feedback power limits |
| [Keybed](keybed.md) | Key positions, switch/diode orientation, matrix and LED order |
| [USB input and transients](usb-input-transient.md) | Receptacle capacitance, protected reservoir, plug-in and live load-release models |
| [Charger input ripple](charger-input-ripple.md) | PMID switching loop, capacitive ripple, branch currents and C602 selection |
| [Cortex debug cable](debug-sourcing.md) | SMT header, preterminated mating cable and stock lookup |
| [USB current limiter](usb-limit.md) | Source tiers, default-host grants and suspend retention |
| [Pack charge control](charge-control.md) | Pack temperature interlock, charge settings and two-hour estimate |
| [RGB power](rgb-power.md) | Five-volt supply, current transients and brightness policy |
| [Mechanical fit](fit.md) | Key travel, LED opening, enclosure sections and assembly reservations |
| [Power budget](power-budget.md) | Charge scenarios, source limits, steady-state and transient loads |
| [Review](review.md) | Independent findings and issues to resolve before schematic sign-off |

## Power and data paths

| From | To | Design contract |
|---|---|---|
| USB-C D+ and D− | BLE/USB controller | One USB 2.0 device. Both plug orientations work. Enumerate on a host in either selector position, send keystrokes only to the selected output. |
| CC1 and CC2 | Sink-only Type-C detector | Read the source's 5 V current advertisement. Keep a safe hardware input limit through dead-battery startup, reset, detach, and changes in advertisement. |
| USB VBUS and protected single-cell pack | Power-path charger | 5 V baseline. Reserve input power for the keyboard, allocate the remainder to charging, obey pack temperature and charge-current limits. Support USB operation with the pack absent. |
| Charger system output | 3.3 V logic supply and independently switched RGB 5 V supply | Keep logic alive when LEDs turn off. Budget the logic regulator over the entire system-output range. Isolate LED data and power when disabled. |
| Charger SYS and controller I²C | DRV2605L and wired linear actuator | The motor takes power from SYS. A separately enabled 1.8 V interface connects the driver to the 3.3 V charger bus. |
| Physical selector | Controller GPIO | GPIO selects report destination. No battery current, USB data or charging current goes through this switch. |
| Key matrix and controller | USB HID or BLE HID | 15 driven columns, 5 sensed rows, one diode per switch. Debounce keys and selector independently. |

## Operating modes

Source qualification and report routing are independent. This table sets proposed product behavior. “Qualified power” means the power logic has identified an allowed source current by USB configuration or a valid Type-C advertisement. Presence of 5 V alone does not grant a fast-charge budget. [USB-IF Type-C power overview](https://www.usb.org/sites/default/files/D1T1-2%20-%20USB%20Type-C%20System%20Overview.pdf)

| Selector and connection | Reports | Charging and RGB | Wake / transition |
|---|---|---|---|
| USB, unplugged | None | Battery travel sleep, lights off | Selector to BLE or cable attachment wakes. Keys in a bag do not wake it. |
| BLE, unplugged, connected | BLE only | Battery brightness cap while active. Sleep cuts the RGB supply. | A key wakes scanning from normal idle. Reconnect if the link timed out. |
| BLE, unpaired or host unavailable | None until connected | Use bounded advertising windows. Keep LEDs off during unattended reconnects. | Explicit pairing gesture starts pairing. Preserve existing bonds across selector changes. |
| USB, active data host | USB after configuration | Charge within qualified budget. Allow capped USB lighting after enumeration. | Follow host suspend/resume. |
| BLE, active data host | BLE only, even when BLE host unavailable | USB may enumerate for power. Charge within qualified budget. | Attach/detach preserves BLE selection. |
| Either, wall supply with valid higher-current CC advertisement | USB position sends no reports. BLE position can type over BLE. | Wall-charge target about two hours to full. Lights off when idle, limit charging or RGB to fit available input when active. | Switching to BLE never requires removing the charging cable. |
| Either, powered cable without qualifying data host or higher-current advertisement | Only BLE can type | Default attach budget, charging and RGB initially off. Support for legacy charger identification would need a separate design decision. | Re-evaluate source on configuration or advertisement change. |
| Either, default-current data host suspends | USB reports paused. BLE may run on a valid cell. | Suspend USB charging and cut USB-funded lighting. With no usable cell retain only suspend functions within the USB suspend limit. | Resume or reattach requalifies the budget. Omit USB remote wake from this first pass. |
| Either, powered with no usable cell | USB works once configured, BLE works if sufficient source power is qualified | Charge only a valid pack. Treat absent, disconnected temperature sensor, thermally inhibited, and deeply depleted pack as distinct charger states. | Verify startup from USB with an empty/absent pack, normal precharge for an eligible depleted pack, and that no fault leaves fast charge enabled. |

On a selector change, send an all-keys-released report to the former host when the link is available, clear queued reports and suppress keys already held until released. Release modifiers, consumer controls and mouse buttons as applicable. On a link loss, start the next connection with neutral reports. Expose pairing and recovery through deliberate actions so an unrelated host cannot receive typed text when the selected transport drops.

## Charging target and architecture decision

Target approximately **two hours from normal low-battery cutoff to charge termination** on a suitable USB-C wall supply at room temperature, using an idle keyboard with RGB off. Budget the separate typing-with-RGB case as well. A damaged, deeply discharged, hot or cold pack is outside the timing target. The 1,500 mAh capacity is a sizing assumption pending a protected pack with a compatible temperature sensor, mechanical drawing, permitted charge rate and a documented charge curve.

Lead option: USB-C at 5 V with advertised-current detection and a switching single-cell power-path charger. Keep PD as an alternative if the selected pack and active load exceed that supply or a required adapter needs PD to provide the target power. Any higher-voltage PD design must protect **every** 5 V-only VBUS branch, including the radio module's USB supply/sense, with suitable regulation, detection and fault isolation. A PD contract alone does not establish the pack's allowable current or constant-voltage taper time. [TI Type-C detector](https://www.ti.com/lit/ds/symlink/tusb320lai.pdf) · [ST USB PD sink example](https://www.st.com/resource/en/user_manual/um2398-getting-started-with-the-stevalisc005v1-evaluation-board-for-stusb4500-stmicroelectronics.pdf)

The review caught a detector-selection issue. The TUSB320LAI reports the source tier on attachment. The fast-charge circuit needs to follow a wall adapter that subsequently reduces its advertised current. The onsemi FUSB303B is captured on the USB-C input sheet in GPIO mode. Its two outputs report the observed current tier. The schematic must show how a stale grant is revoked, including with stalled firmware. [TI §7.2.1.2](https://www.ti.com/lit/ds/symlink/tusb320lai.pdf) · [onsemi FUSB303B](https://www.onsemi.com/pdf/datasheet/fusb303b-d.pdf) · [LCSC C895444](https://www.lcsc.com/product-detail/USB-ICs_onsemi-FUSB303BTMX_C895444.html)

## Schematic handoff

1. **Power owner** resolves the pack and charger combination, VBUS protections, default/qualified input limits, USB suspend and total sleep current. Include a pin truth table through reset, CC downgrade, firmware crash and watchdog expiry. Check voltage, tolerance and thermal margins at the connector and pack.
2. **Controller owner** checks the actual module pads, recovery access and antenna geometry, then prepares USB/BLE/selector logic against the mode table. One integrated firmware build must exercise all peripheral allocations concurrently.
3. **Keybed owner** uses the same matrix and key-center map for symbols, footprints and firmware, including rotated bottom-side LED placement. Separate hand-fit and factory components in the BOM. Confirm Standard PCBA eligibility, placement side and orientation for each SMT part.
4. **Integrator** owns the hierarchical KiCad project and system overview, board outline, interfaces and PCB. Import the switch stack, battery, connectors, radio keepout and case into FreeCAD. The 304.8 × 95.25 mm keybed cannot fit flat inside a 220 mm square at any rotation. Even at 45°, its bounding box is about 283 × 283 mm. Plan printable case sections if the printer is the Adventurer 5M; the electronic PCB can remain one piece. [Printer build volume](https://www.flashforge.com/products/adventurer-5m-3d-printer)
5. **Independent reviewers** re-derive current limits, scan polarity, peripheral assignments and part orientations from the integrated schematic, then repeat against board and manufacturing exports. Assembly outputs include Gerbers, drills, SMT BOM with supplier codes, CPL, assembly drawings and a separate builder's BOM. Electrical behavior, RF performance, light output, fit and charge time will remain unmeasured for this digital-only design.
