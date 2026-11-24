# Eleven-sheet schematic review · revision F

Open **keyboard.kicad_pro** in KiCad 10.0.8. The root contains ten selectable child-sheet symbols and the physical mode selector. Read the top row from the receptacle through the current limiter and charger to the RGB supply. The next row connects the matrix, controller, 3.3 V regulator and pixels. USB data, CC status, matrix rows and matrix columns use native KiCad buses. The display and volume sheet sits below the controller on a five-signal bus. The haptic sheet beside it takes SYS motor power and interfaces to the controller’s 3V3 bus. Shared control signals are indexed at the bottom. [Review PDF](../electronics/keyboard-schematic.pdf) · [KiCad hierarchical schematics](https://docs.kicad.org/10.0/en/eeschema/eeschema.html#hierarchical-schematics)

## Sheet index

| Page | Circuit | What to follow |
|---|---|---|
| 1 | System overview and mode selector | Power paths, page references and the physical USB/Bluetooth selector contacts. |
| 2 | Key matrix | Follow any column through a switch and steering diode to its row. All 67 keys fit inside the frame. |
| 3 | USB and Bluetooth controller | Supply and bypass at VCC/VCCH, I²C pull-ups, GPIO pulldowns, crystal load capacitors and the Arm debug port. |
| 4 | USB-C receptacle and hot-plug protection | Follow both CC pins into the FUSB303B, both protected data nets, and VBUS through the damping and disconnect circuits. |
| 5 | RGB data and pixels | U300 shifts the MOSI level. R301 and R302 feed LED1. Each row reads left to right in transmission order, with references reversing on alternate physical rows. |
| 6 | Charger and battery | Follow the switching loop to SYS. The two comparators below evaluate the pack thermistor and gate the charge request. |
| 7 | Always-on 3V3 | Input capacitor and enable straps on the left, LX inductor loop beside U700, configuration and output capacitors on the right. |
| 8 | USB current and suspend | The resistor bank selects the default, Type-C and configured-host current tiers. The timing and activity circuits determine which tiers are allowed. |
| 9 | RGB power | Follow SYS through the inductor to the boost output and bulk bank. Trace the feedback divider to FB and the brownout inhibit to EN. |
| 10 | Display and volume | Follow the excitation and wiper to the SAADC, and the switched 3.3 V path through the JST port to the OLED. |
| 11 | WASD haptics | Trace SYS to motor driver U1100 and its local reservoir, then follow the translated I²C signals to the red and blue actuator leads. |

## Capacitors and hot-plug behavior

The table gives nominal external shunt capacitance. Effective ceramic capacitance depends on DC bias, tolerance and temperature. The inrush seen at the connector depends on which stages have turned on. [Hot-plug model and assumptions](usb-input-transient.md) · [Charger ripple and modeled waveforms](charger-input-ripple.md) · [USB suspend budget](usb-limit.md) · [RGB supply design](rgb-power.md)

| Net | Nominal capacitance and location |
|---|---|
| VBUS_CONN | 1 µF at C202 plus 4.7 µF through the 1 Ω damping resistor R204. |
| USB_VBUS | Three 47 µF capacitors in parallel behind R208 (0.10 Ω) plus 10 µF ceramic at C800. The gate ramp controls charging of this 151 µF nominal bank. |
| VBUS_LIMITED | 1 µF C601 at the charger VBUS pin. |
| LOGIC_IN | 22 µF C700 at the logic converter input. |
| 3V3 | 45.7 µF nominal including the new 100 nF bypass at the controller side of the translator. The radio adds 4.7 µF each on VCC and VCCH, both strapped to 3V3. |
| OLED_VIN_SW | 1 µF on the main PCB plus the module input capacitance. U1000 gates the logic supply. The breakout LDO and panel charge-pump headroom are reviewed in [Display and volume](display-and-volume.md#voltage-at-the-connector-and-glass). |
| SYS | 91.1 µF including the 47 µF haptic reservoir and the two 1 µF SYS bypasses for the driver and the interface regulator. |
| LED_5V | 990.8 µF from two 470 µF polarized capacitors, two 22 µF ceramics, 67 pixel bypasses and the translator bypass. |
| Charger-local nets | 10.1 µF at PMID, 4.8 µF at REGN, 10 µF at the battery terminal. |

At cold attach U203 qualifies the source, then slews Q200 and Q201 to charge the protected rail. C602 at the charger was changed to a 1206 50 V X5R capacitor. At 5 V its typical effective capacitance is 7.28 µF. The calculated capacitive ripple is 25 mV p-p at the 1.04 A charge and 150 mA lighting design point. [Transient limits](usb-input-transient.md) · [Charger ripple model](charger-input-ripple.md)

## RGB signaling and programming

SPIM2 at 8 MHz can send a packed 67-pixel frame plus reset in 2.31 ms. R301 is a provisional 33 Ω source-damping resistor and R302 is the 100 kΩ idle pulldown. J100 is a pin-7-keyed 1.27 mm Samtec Arm Cortex Debug header with VTref, SWDIO, SWCLK, nRESET and ground. Its cable clearance and final component placement belong to PCB and case layout. [Pixel timing and electrical details](keybed.md) · [Arm header pinout](controller-and-pins.md) · [Mating cable, inventory and stock lookup](debug-sourcing.md)

## Drawing references and checks

Horowitz and Hill’s figure E3 separates the reference, error amplifier, pass devices, current limit and feedback divider in a voltage regulator. This informed the charger’s comparator ladder and RGB feedback branch. Jim Williams’s figure 101 shows the feedback loop around a 200 mA booster along with its local transistor protection. [Horowitz and Hill, *How to Draw Schematic Diagrams*](https://opencircuitdesign.com/xcircuit/goodschem/goodschem.html) · [Jim Williams, AN47, figure 101](https://www.analog.com/media/en/technical-documentation/application-notes/an47fa.pdf#page=46)

The hierarchy-only conversion preserved all 1,143 original pin-to-net memberships when compared as connected pad sets. Revision D introduced the input MOSFETs, gate drive, sensing and bypass networks. Revision E adds two matrix-column pin reassignments and five display/volume signals. KiCad's integrated ERC and the XML checker cover the 67 switch/diode paths, 67 pixels, Cortex header, power paths and new controls. [Connectivity checker](../electronics/check-netlist.py) · [Display and volume](display-and-volume.md)

Revision F connects the haptic enable to U100 pad 60 and the existing charger bus through a powered-off-high-impedance translator. The [haptic design](haptics.md) gives the physical motor-node mapping and qualification limits.
