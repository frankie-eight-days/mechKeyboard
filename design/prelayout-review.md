# Rev F schematic release review

**Hold the electrical design before PCB placement.** The three first decisions are how the board disconnects a depleted cell, what overvoltage the powered USB input must survive, and how a battery-free keyboard keeps USB alive during suspend. Each can change the power path. The display supply and haptic recovery can also change the parts placed on the board.

Reviewed on November 21, 2026 against the [eleven-sheet schematic](../electronics/keyboard-schematic.pdf). Three independent Sol reviews covered USB/charging, rails/RGB/haptics and controller/interfaces. Integration review covered their shared assumptions, mechanical transfer, parts reconciliation and the native KiCad release checks. The [master checklist](schematic-release-checklist.md) and the coverage record below identify what was actually checked.

## Before placement

Resolve these items while there is still room to change components, footprints or the topology. “Calculated” denotes a result under stated inputs. “Unbounded” means the available evidence allows both passing and failing hardware.

### 01 · Protect the pack at its normal discharge floor

**Power and battery · Specified limits conflict.** CU-J450-V3 uses a cell with a 2.75 V operating discharge floor. Its linked protection module specifies a 2.40 ± 0.10 V emergency trip. U600's battery UVLO can also lie below the operating floor. With no USB source, the pack can continue supplying SYS after optional loads turn off. MCU sleep reduces the rate of discharge. It cannot disconnect every load indefinitely.

**Close when** the owner traces normal shutdown, blank or stalled MCU, continued off-state drain and recovery on USB. Specify the cutoff tolerance under load, hysteresis, residual current and restart behavior. Provide a qualified pack or circuit that meets the cell floor under the claimed conditions. [Cell and pack evidence](charge-control.md) · [Pack protection module](https://www.batteryspace.com/protection-circuit-module-pcb-for-3-6v-3-7v-li-ion-battery-3a-limit.aspx) · [Charger](https://www.ti.com/lit/ds/symlink/bq25622.pdf)

### 02 · Bound USB overvoltage with the pass FETs already on

**USB input · Calculated fault case.** J200 has 5.7 µF nominal at first contact and 141 µF behind Q200/Q201. The existing sampled disturbance with source voltage at or below 5.50 V peaks at 5.760 V on USB_VBUS. U100's recommended maximum is 5.50 V and its absolute maximum is 5.80 V. A separate room-value screen starts at 5.50 V with the switches conducting. A step to 6.0 V gives about 5.824 V at the protected node when the filtered monitor first reaches its high-trip corner, before turn-off. A step to 9 V gives about 6.69 V at that instant. These stimuli model a source fault. The keyboard requests 5 V and has no 9 V PD contract.

**Close when** the owner defines the powered-source fault envelope and runs a bounded step/load-release analysis with cable impedance, C203 delay, comparator tolerance, FET turn-off, leakage and radio VBUS rating. If the selected envelope exceeds the limit, change the clamp, sensing or PHY-supply path and rerun. Preserve inrush and USB low-line operating headroom as separate checks. [Reproduce the powered-fault screen](usb-live-ov-check.py) · [Input transient model and passive values](usb-input-transient.md) · [u-blox power limits](https://content.u-blox.com/sites/default/files/BMD-340_DataSheet_UBX-19033353.pdf)

### 03 · Prove USB-only startup, suspend and wake

**USB power and controller · Unbounded requirement.** On a quiet default-current host, U803 and Q805–Q807 can turn U800 off. Without a usable cell, the 3.32 kΩ R801/D800 retention path must then sustain the controller. The project estimates about 0.31 mA at 3.3 V under one low-line condition. Its separate 2.5 mA connector budget leaves about 30 µA after using the radio's *typical* suspended PHY draw. Those are two different constraints. No simultaneous worst-case proof covers both. A pull-up/timeout race during initial enumeration could also restart the board repeatedly.

**Close when** there is a worst-case current and timing table for unconfigured attach, host debounce, suspend, resume, default and advertised sources, with blank/restarting firmware and absent/depleted pack. Show both the retention load line and maximum connector current, or choose an architecture with more margin. A second screen at 4.35 V, 0.38 V diode drop and 80% efficiency gives only 0.285 mA at 3.3 V even at the best retention load point. Include CC detection, logic thresholds, regulator efficiency, reservoir leakage, SOF watchdog and expiry at temperature. [USB limiter and retention](usb-limit.md) · [Connector budget](usb-input-transient.md)

### 04 · Rate the logic-rail OR diodes for insertion and restart

**Core power · Unbounded surge.** On battery insertion D800 pin 1 supplies LOGIC_IN, including C700 at 22 µF and U700 starting into two more 22 µF capacitors. The BAS40-05 is rated at 120 mA forward and 200 mA nonrepetitive surge under the cited pulse conditions. The unlimited-startup strap on TPS63900 permits a substantially higher switch-current peak. The switch limit alone does not establish current through D800. Equal pulse-current sharing between the paralleled D801 sections also lacks a guarantee.

**Close when** the owner bounds diode current, pulse length, repetition, temperature and voltage drop for pack insertion, reconnect, USB takeover and OLED turn-on, and qualifies the installed parts or selects replacements. Keep the retention budget in issue 03 when changing forward drop. [Diode ratings](../datasheets/active/BAS40-05.pdf) · [TPS63900](../datasheets/active/TPS63900.pdf)

### 05 · Resolve the display module's supply limits

**Display and power · Unbounded operating range.** U1000 is a load switch. The AP2112 regulator is on the Adafruit 4440 breakout. The connector can be at about 3.231 V in the project calculation, before the module regulator's drop. The glass specifies a 3.3 V minimum for VBAT and a 3.3 V maximum for VDD. The breakout ties those supplies together. The vendor's nominal 3.3 V input support is useful evidence for typical operation but leaves the corner unresolved.

**Close when** the selected module vendor supports the complete connector range and intended conditions, or the design uses a display/power arrangement with an overlapping guaranteed range. Check I²C levels and powered-off behavior for any change. Raising VIN alone still leaves the common regulator output and its tolerance to qualify. [Board-level calculation and display drawings](display-and-volume.md)

### 06 · Give the haptic driver a recoverable power state

**Haptics · Datasheet recovery condition missing.** U1100 VDD supply pins 6 and 10 are hard-wired to SYS. HAPTIC_EN controls its enable and isolates its I²C branch. TI documents a REG brownout followed by a slow VDD recovery that can leave the driver in an unknown state. TI also documents interrupted I²C in standby as a case that can require a supply cycle. EN preserves registers. Bus isolation protects charger access but does not cycle the driver.

**Close when** the circuit can discharge and reapply U1100 power independently with a recovery ramp faster than 3.6 kV/s, or an all-source analysis establishes reachable recovery with the existing circuit. Include C1101, isolation order, inrush, and a failed device on the charger bus. [DRV2605L §§8.3.11, 8.3.12.4 and 8.4.1.3](https://www.ti.com/lit/ds/symlink/drv2605l.pdf) · [Haptic circuit](haptics.md)

### 07 · Bound the key matrix at the weakest input-high corner

**Matrix and controller · Unbounded logic margin.** All 67 switch/diode paths connect in the intended direction. C11 and C12 require standard GPIO drive. At 3.2505 V, row VIH is about 2.275 V. C11/C12 have four populated rows and demand about 0.827 mA at that threshold with 11 kΩ pull-downs. The five-row columns demand 1.034 mA under the same initial standard-drive plan. Using the 2.8505 V output-high test bound leaves about 0.575 V for the diode. The fitted 1N4148W's 0.715 V maximum at 1 mA and 25 °C does not establish its drop at the actual lower branch current across temperature. This arithmetic identifies missing margin evidence. It does not predict missing keys in a particular board.

**Close when** the owner supplies a guaranteed load-line and scan-settling budget for the weakest column with the maximum populated keys, or changes pull-downs, diode or pin allocation and recalculates. [Keybed](keybed.md) · [Fitted diode](../datasheets/active/JSCJ-1N4148W.pdf) · [Controller allocation](controller-and-pins.md)

### 08 · Qualify the RGB boost converter with the fitted capacitor bank

**Lighting power · Unbounded stability and frame envelope.** U900 sees two 470 µF polymer capacitors plus ceramic bypasses. TI gives a minimum effective output capacitance and a much smaller reference bank. The project’s 150 mA animation budget is a frame average. A synchronized PWM transient at the design's aged-bank assumptions leaves about 28 mV before the most sensitive PG trip in a 1 kHz screen. The same conservative charge-balance screen fails at 500 Hz. The pixel specifies typical PWM frequency. Neither screen establishes converter instability.

**Close when** the owner validates startup, PFM/PWM operation, load release, PG behavior and stability for this bank, and chooses a guaranteed frame-current policy. If evidence only supports the sparse mode, document that product limit. If alternate capacitance or damping may be needed, reserve it before placement. [RGB power calculations](rgb-power.md) · [TPS61252 application guidance](https://www.ti.com/lit/ds/symlink/tps61252.pdf)

### 09 · Verify cold USB attach timing and source-current grants

**USB input and limiter · Unbounded attach interval.** U203 ramps the protected bank before U100 pin 66 reaches its 4.35 V operating minimum. The existing slow gate screen estimates about 120 ms to that voltage after conduction begins, using pump and timing data characterized at 12 V. This can consume the applicable 100 ms USB attach/current interval. It affects a charged or battery-free board as well as the weak-battery use case. At 4.40 V at J200, the PHY has only 50 mV for all series losses. Separate from that, U800's estimated maximum current at each custom ILIM resistor is extrapolated from characterized points.

**Close when** the owner bounds cold inrush, D+ assertion and current against the applicable USB timing case at 5 V. Include a live change between default, 1.5 A and 3 A advertisement, both plug orientations, FUSB detection delay, GPIO skew, total bypass draw and the lowest usable connector voltage. If the PHY needs an earlier feed than the bulk bank, decide before placement. [USB input](usb-input-transient.md) · [Tier circuit](usb-limit.md) · [USB 2.0 specification and ECNs](https://www.usb.org/document-library/usb-20-specification)

### 10 · Decide USB data termination and local radio bypass

**Controller and USB · Confirmed departure from reference.** J200 D+/D− connect directly to U100. u-blox Figure 8 shows 27 Ω series elements. Rev F also branches each line through 1 kΩ to U803 and D+ through 100 kΩ to Q805. The USB logic can be powered while the 3V3 sensing rail collapses. The HC input clamp can then carry injection current. Sheet 3 has crystal capacitors but no designated external local 4.7 µF bypass like the module reference. C800 serves U800 and its distance from the PHY is unresolved.

**Close when** the owner chooses series tuning sites or justifies their omission, allocates local module/PHY bypass and documents rail-safe sensing. Use the fab stackup for 90 Ω differential routing, keep tap branches short, and check return continuity, ESD and the full-speed end-of-packet detection window. USB eye quality remains a physical uncertainty. [BMD-340 Figure 8](https://content.u-blox.com/sites/default/files/BMD-340_DataSheet_UBX-19033353.pdf) · [Input limiter](usb-limit.md)

### 11 · Qualify the USB receptacle, CC controller and transport switch footprints

**Libraries and assembly · Two measured footprint differences and one missing switch qualification.** U200's generic Texas X2QFN lands extend 0.15 mm farther out than onsemi Case 722AG. With 1:1 paste, nominal area increases 21–30%. J200’s near-mouth plated slots are 0.60 × 1.20 mm against HRO's 0.60 × 1.40 mm recommendation. Electrical pad numbering passed. SW400's archive describes one throw, while the design uses two maintained throws. Its cited contact test is 5 V/10 mA and the high position operates near 30 µA. Its four SH anchor lands have no assigned electrical net.

**Close when** the library owner compares copper, paste, finished slots and plug datum to the exact production drawings and resolves each difference with a part-specific footprint or documented assembler acceptance. Confirm SW400’s two detents, low-current switching, shell treatment, slider direction and case labeling. Keep MCU input pulls off so the high position reaches VIH. [onsemi package drawing](https://www.onsemi.com/pdf/datasheet/fusb303b-d.pdf) · [HRO drawing](../datasheets/mechanical/TYPE-C-31-M-12.pdf) · [Switch document](https://datasheet.lcsc.com/datasheet/pdf/5162155576bfd231c35aa9a893d25c8c.pdf?productCode=C431540)

## Firmware, routing and production decisions

| ID and owner | Issue and consequence | Closure and earliest gate |
|---|---|---|
| 12 · Charger firmware | R600 at 24.9 kΩ sets about 100.4 mA nominal. U600 REG0x19[2] EN_EXTILIM defaults on and can return on watchdog. Raising ICHG and IINDPM alone cannot deliver the intended 1.04 A charge. A frozen high CHG_REQUEST can keep CE active when temperature is valid. | **Firmware contract.** Keep CE inhibited during qualification. Set and read back EN_EXTILIM, IINDPM, ICHG, VREG, ITERM, TS, watchdog and OTG under the correct source grant. Preserve independent U800 limiting. U600 QON is NC. Reserve ship mode for a USB-wake workflow, and account for the parallel USB feed when promising a full-system reset. Define requalification and safe fallback after reset, downgrade and stuck request. [TI BQ25622](https://www.ti.com/lit/ds/symlink/bq25622.pdf) |
| 13 · Battery and firmware | Near-two-hour charging is a target on a 5 V/3 A source. 1.50 Ah / 1.04 A = 87 minutes before taper. Haptics-on profiles of 0.80/0.88 A leave less time for taper. A valid NTC does not establish BAT+ continuity. | **Before a charge-time claim.** Define start voltage, attached loads, endpoint and temperature. Demonstrate pack presence through open-wire cases, valid NTC calibration, precharge, CC/CV taper and termination using supplier data or retain an estimate. Open and short NTC nominally inhibit CE. [Charge control](charge-control.md) · [Power budget](power-budget.md) |
| 14 · Power and product | The detached travel target of 50 µA lacks a closed budget. One FUSB-related 150 kΩ path alone accounts for about 22 µA. Haptic shutdown, translator, reservoir leakage, RGB supervisor, core logic and conversion losses consume more. Room-temperature limits quoted at different voltages cannot simply be added as guaranteed board current. | **Before placement if 50 µA is a firm requirement.** Budget battery-side current by source, state, voltage and temperature. Include deep-sleep and held-key wake states. Choose isolation or agree a revised runtime target if the bound is insufficient. [Controller and pins](controller-and-pins.md) · [Power budget](power-budget.md) |
| 15 · Controller and firmware | The Rev F pin-budget text lists pad 60 as available although the netlist assigns it to HAPTIC_EN. The 8 MHz SPIM2 custom 10-bit RGB encoding fits. Its shortest timing margin is about 25 ns. A stock driver limited to eight bits per symbol cannot reproduce it at 8 MHz. | **Before pin-map freeze.** Mark 60 occupied and distinguish free pads 49/50 from reserved NCs. Keep the custom EasyDMA encoder, 2,010 payload bytes and 300 latch bytes. Check uninterrupted transfer, LF clock, SOF heartbeat, both TWIMs, ADC, selector transitions and HID state releases under concurrent USB/BLE. [Controller allocation](controller-and-pins.md) · [Keybed timing](keybed.md) |
| 16 · Layout and RF | The KiCad project has only its default netclass and no net-class assignments. Critical routing targets currently live in prose. RF clearance and connector access can be lost during board transfer. | **At placement and before routing.** Import the fixed datums, nine Ø8 mm boss exclusions, 67 LED windows, underside battery/header/haptics routes, OLED underside and switch plate. Top-side U100 needs 180° to put the antenna at the modeled edge. Verify two datums and keep all copper, metal and fasteners clear. Set per-net constraints for USB, high-current/quiet returns and charger loops. Check the 10 mΩ assumed LED round-trip resistance including cutouts. [Fit and coordinates](fit.md) · [J600 transfer](pack-harness-review.md) · [Charger loop placement](charger-input-ripple.md) |
| 17 · Controller and layout | The two 18 pF caps on Y100 assume specific pin/board parasitics. Each leg needs about 3 pF of board parasitic with the cited 4 pF typical pin value to reach nominal 12.5 pF load. Incoming radio silicon revision also determines applicable errata. | **Before routing.** Keep XL routes symmetric and quiet, check the crystal land exclusion and extract load/startup margins. Establish the module type and errata policy. Confirm J100’s keyed cable fits and retain reset recovery with the selected UICR settings. [Controller and pins](controller-and-pins.md) · [u-blox data sheet](https://content.u-blox.com/sites/default/files/BMD-340_DataSheet_UBX-19033353.pdf) |
| 18 · Layout and power | Charger ripple, thermal and transient calculations use biased capacitance, modeled ESL and selected temperatures. On the haptic bus, a 0.4 V host VOL bound leaves only 20 mV to the charger's 0.42 V threshold before return noise. An isolated driver and a powerless charger present different bus loads. | **During routing.** Confirm effective local capacitance and worst junction temperature. Route C603/C602 directly at PMID/GND, keep switch-node loops compact, and balance reservoir branches. Check translator power order, sink/rise margin, stuck bus and driven pins during brownout. Reserve paired signal/ground access to USB power nodes, SYS, 3V3, near/far RGB, TEMP_OK/CE and haptic REG/I²C. Provide a way to observe standby current. [Charger ripple](charger-input-ripple.md) · [Haptic bus](haptics.md) |
| 19 · Assembly and release | The quantity/MPN match covers the recorded five-board sourcing run. Rotations, reverse-LED internal routes, actual stackup and thermal copper depend on the finished PCB. The 50 mm OLED harness and 42 mm battery leads have small modeled service clearances. | **Before fabrication or shipment claims.** Check DRC, Gerbers/drills, route and copper setback on all 67 apertures, paste and CPL, bottom-side pin 1, hand-fit exclusions, mated cable clearance and the superseding pack location. Recheck vendor available-order quantities and procurement status for the exact radio type. Confirm the RV1000 manual/THT assembly route. Define intended market and evidence needed for radio/EMC and pack shipment. Physical performance, charging time, haptic feel and radio range remain unverified. [Assembly split](assembly-stock.md) · [Fit study](fit.md) · [JLC KiCad assembly-file guidance](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad) |

## Checks that passed

- **Connectivity.** KiCad 10.0.8 exported 11 sheets, 440 references, 294 nets and 1,250 pin memberships. ERC returned zero violations and zero exclusions. Four checks were configured to be ignored: single global label, four-way junction, SPICE model issues and footprint filters. All 33 one-node nets were explicit no-connects. The native [project assertions](../electronics/check-netlist.py) also passed.
- **Keybed and lighting.** Every occupied matrix cell matched the physical key map. All 67 LED power/ground connections, all 67 bypasses and the 66 isolated inter-pixel links matched the serpentine chain. The planned 8 MHz encoder sends a 1.25 µs symbol and a 300 µs low latch. One complete frame takes 2.310 ms. U300 is a level translator. The output series resistor serves as source damping, with a separate weak pull-down.
- **Controller and wiring.** U100 pad numbering, normal-voltage supply wiring and the all-layer antenna keepout matched the module documentation. J100 pins 1/2/4/10 are VTref/SWDIO/SWCLK/reset, with ground on 3/5/9 and missing key pin 7. J600 pins 1/2/3 are pack positive, NTC and ground. J1000 pins 1/2/3/4 are ground, switched supply, SDA and SCL. The volume input's worst screened source resistance is 4 kΩ with nominal RC time constant 40 µs against a 2 ms excitation interval.
- **Parts and assembly.** All 43 unique footprints resolved. Every schematic symbol pin had a numbered copper pad. The only extra named copper pad number was the SW400 shell anchor SH, repeated four times. The November 21 stock CSV reconciled to all 440 refs with zero order-code or MPN differences on coded parts. The split is 370 factory SMT, one manual/THT potentiometer, 67 hand-soldered switches, one hand-fitted actuator and one BOM-excluded test point. The 77 supplier codes are a dated sourcing snapshot for five boards. [Stock ledger](smt-stock-2026-11-21.csv)
- **Power components.** The USB CC strap, source-tier truth table, USB ESD pin assignments, opposed pass FETs and charger pin map checked out. The 1 µH L600 part fits the assigned land dimensions. Screened peak is about 1.97 A against its 4.8 A saturation figure at 10% inductance loss. C602 is modeled near 7.28 µF effective at 5 V. The existing ripple and insertion calculations remain useful within their modeled envelopes. [Charger ripple and placement](charger-input-ripple.md)

## Checklist coverage

Each result refers to this desk review. “Open” means a decision, correction or stronger evidence is required. “Deferred” identifies work whose evidence first exists in layout, firmware or an assembled unit. Mixed results state which portion passed. Issue numbers refer to the single register above.

| ID | Result | Evidence or outstanding decision |
|---|---|---|
| R01 | Verified | Fresh isolated copy of native project and libraries. Root, controller and haptics carry F, eight unchanged children carry E. All eleven appear in the plot and XML. |
| R02 | Open | USB-only operation, pack floor, display range, RGB envelope and runtime still have provisions or assumptions. 01–09, 13–14. |
| R03 | Verified for sheet extents and hierarchy | All 11 sheets rendered and inspected. Root flow, matrix bounds, power section grouping and controls/haptic pages are legible in the vector plot on zoom. No sheet ran outside the page frame. |
| R04 | Verified | Zero errors, warnings or excluded markers under the recorded settings. Four ignored rule types are listed above. |
| R05 | Verified for traced topology | Project checker, independent matrix and LED traversal, singleton classification and physical pin cross-checks passed. |
| R06 | Open | Pad 60 contradicts the spare-pin table. Older charge profiles are identified as sizing comparisons. 15. |
| L01 | Verified for pin coverage | 440 refs across 43 resolved footprints. SW400's extra shell anchors need a mechanical/electrical disposition. 11. |
| L02 | Open | BMD, Cortex header, L600 and selected J600 lands checked. U200 and J200 differ from vendor land guidance. The OLED connector drawing is preliminary. 11, 19. |
| L03 | Verified for count and intended wiring | 439 fitted parts plus TP300 excluded. Hand-fit exceptions and cable pin maps reconcile. Orientation in manufactured placements is deferred. 19. |
| L04 | Verified for dated run | Exact netlist against the five-board stock export. Quantity allocation, incoming lot and lifecycle at order remain open. 17, 19. |
| L05 | Deferred to CAM | Review internal route radii/copper setback, plated shell slots, paste, bottom-side CPL, thermal pads and plate-first switch assembly. 11, 19. |
| L06 | Open at board transfer | Existing CAD establishes nominal envelopes and a service trajectory. Check the nine mounts, battery withdrawal, display, debug plug and actuator leads against final placement. 16, 17, 19. |
| P01 | Open | Power paths traced in normal, no-battery and sleep modes. Battery cutoff, USB retention, reverse discharge after unplug and ship/reset reachability need closure. 01–04, 09, 12. |
| P02 | Open | Per-tier average budgets exist. Peak load, source changes, inrush and travel draw remain conditional. 03, 04, 08, 09, 14. |
| P03 | Open | PHY 4.35 V floor, matrix VIH, display VBAT and diode drop were evaluated. 02–05, 07, 09. |
| P04 | Open | Charger C602 and L600 screen support selection. Bound actual local core capacitance after bias/aging and the maximum distributed U900 bank. 08, 18. |
| P05 | Open | Cold, powered, initial rail charge and sustained-source cases distinguished. 02–04, 08, 09. |
| P06 | Open | Opposed FET orientation and input isolation checked. Define powered OV, reverse/miswire and CC exposure, short and cutoff margins. 01, 02, 04, 09. |
| P07 | Open | Normal U800 loss screens near 91 mW at 1.3 A and 54 mΩ. Short-circuit retry, diode surge, reservoir sharing and actual board thermal path remain open. 04, 08, 18. |
| P08 | Open | Default-off controls and temperature interlock traced. Review rail brownout, EN retention, ship exit and charger watchdog fallback. 01, 03, 06, 09, 12. |
| P09 | Open | RGB translator direction and powered-off isolation checked. Review U803 input injection, PMIC pull-ups and haptic interface as each rail falls. 06, 10, 18. |
| P10 | Deferred to placement | C603 at U600 pins 17/15, short paths for U700/U900, module bypass and clock return. 10, 16–18. |
| B01 | Open | Harness polarity and nominal pack clearance agree. Operating floor and proof of full pack limits remain. 01, 13, 19. |
| B02 | Open | R600 and POR/watchdog external-limit priority confirmed. 12. |
| B03 | Open | 87 min ideal CC baseline at 1.04 A. Source budget includes accessory profiles. Taper and elapsed time unverified. 13. |
| B04 | Open | Nominal reference ratios reproduce 69.9%/49.9% trips, 85.2% open and 0% short. Final sensor/window tolerances and partial harness faults remain. 13. |
| B05 | Open | Cell normal floor and emergency PCM trip compared. Pack recovery and QON/ship exit traced. 01, 12. |
| B06 | Open | CC encoding and physical USB grant logic checked. Bound cold connect, downgrade, suspend and resume. 03, 09, 12. |
| I01 | Open | Normal radio topology and crystal part verified. Exact module-revision errata, external bypass and LF load still require resolution. 10, 17. |
| I02 | Verified timing arithmetic, deferred implementation | Custom SPIM2 tuple fits. Concurrent SOF, BLE, two TWIMs, ADC and DMA remain firmware work. 15. |
| I03 | Verified pinout, deferred access | Cable/key and target reference agree. Blank-board flash, programmed reset, recovery and case clearance remain. 17. |
| I04 | Open | USB polarity/ESD correct. Decide series tuning and partial-rail taps. 10. |
| I05 | Open | OLED 10 kΩ parallel 10 kΩ gives ~0.424 µs rise at 100 pF, nominal 100 kHz. PMIC bus fault recovery, noise and thresholds need 06 and 18. |
| I06 | Verified first-order design | RV1000 endpoints and 4 kΩ source match the 2 ms pulse screen. ADC acquisition, endpoint calibration and noise remain firmware/layout tasks. 15, 18. |
| I07 | Open | Haptic load is 1.8 Vrms rated, 1.9 Vrms operating ceiling. Mounted calibration, RMS current, braking and audio/rattle remain unverified. RGB synchronized load and fault recovery are open. 06, 08. |
| I08 | Verified topology | 67 cells, eight unused positions, diode direction and 66 inter-pixel connections match. Key-down threshold margin and real scan settling remain open. 07. |
| I09 | Verified land and keepout, deferred RF performance | Preserve module rotation, ground counterpoise, edge clearance and plate relief. 16, 17, 19. |
| I10 | Open | SW400 action, display range and service state, haptic rail order and controlled pack reconnect. 01, 05, 06, 11. |
| I11 | Open | Fast-charge, sleep/wake, RGB encoder and GPIO ownership require firmware contract updates. 03, 06, 12–15. |
| H01 | Deferred to placement | Handedness and fixed datums are recorded. Overlay all mechanical and electrical exclusions on the PCB. 16, 19. |
| H02 | Open | The project has only Default routing rules. Translate USB, RGB return, quiet sense, converter loop and case constraints. 10, 16–18. |
| H03 | Deferred to placement | Cortex header and final RGB data TP exist. Plan accessible rail, fault and local ground observations with the case/plate in place. 17, 18. |
| H04 | Verified | Independent reviewer findings were challenged, consolidated by cause and assigned stage, owner and closure evidence in 01–19. |
| H05 | Deferred to ECO and physical design | Repeat ERC/netlist/render after corrections. Check board update, DRC, CAM and assembly outputs against the same revision. 19. |
| E01 | Open | PLA room-temperature use is assumed. Normal/fault heating, battery temperatures and capacitor aging/leakage at temperature still affect electrical margins. 02, 04, 08, 13, 14, 18. |
| E02 | Open | Source strength, rise time and initial rail state matter. 5 V source disturbances and a failed source with conducting FETs have different results. 02, 09. |
| E03 | Deferred to product release | USB and RF technical constraints identified. Target markets, host integration, EMC/ESD, pack transport and release evidence remain decisions. Board is a low-voltage USB/1S design. 19. |
| E04 | Open | MCU-stuck charge request, retained haptic state, PMIC ship exit and a stuck shared bus each require a reachable recovery state. 01, 06, 12, 18. |

## Reproducing the review

Use KiCad 10.0.8 on a copy containing the project file and its local libraries. From the project root run the commands below. The Python fault screen requires NumPy. The PDF is a desk-review record. Performance in an assembled keyboard remains unmeasured.

```sh
kicad-cli sch erc --severity-all --format json --exit-code-violations -o /tmp/keyboard-review-erc.json electronics/keyboard.kicad_sch
kicad-cli sch export netlist --format kicadxml -o /tmp/keyboard-review.xml electronics/keyboard.kicad_sch
python3 electronics/check-netlist.py /tmp/keyboard-review.xml
kicad-cli sch export pdf -o /tmp/keyboard-review-sch.pdf electronics/keyboard.kicad_sch
python3 design/usb-live-ov-check.py
```

Baseline fingerprint for the 34 native schematic, project, local symbol, library-table and footprint files is `fc8c5f02b26380020e7fbfe725abb3f66d2b5875c6a8d9d18683cb44a8d5de5b`. It is SHA-256 over sorted electronics-relative paths, each followed by a zero byte and the raw 32-byte SHA-256 digest of its contents.
