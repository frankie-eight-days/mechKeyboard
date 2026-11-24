# Controller, USB data and GPIO allocation

This is the revision F pin budget for a 67-key, 5 × 15 electrical matrix. The pad numbers below are the manufacturer's module pads. Signal assignments and the firmware port are proposed. The integrated schematic verifies the electrical connections. Firmware and physical hardware remain unverified.

## Controller and assembly

Use the **u-blox BMD-340-A-R** open-CPU nRF52840 module with integrated PCB antenna. On 17 November 2026, LCSC listed 206 units of **C5456944** and JLCPCB marked the exact part in stock. Confirm allocation at quote time. A separate USB MCU and BLE HID module would also work, with an interprocessor link for key reports, pairing, wake and reconnect. This module can run the key scanner, wired USB device and BLE HID on one processor. [Manufacturer datasheet](https://content.u-blox.com/sites/default/files/BMD-340_DataSheet_UBX-19033353.pdf) · [LCSC inventory](https://www.lcsc.com/product-detail/C5456944.html) · [JLCPCB assembly listing](https://jlcpcb.com/partdetail/C5456944)

## Pin budget

Of 48 GPIOs, reserve five for the LF crystal, nRESET and NFC. Allocate 20 of the remaining 43 to the matrix, 15 to the existing interface and power functions including reservations, and five to the display and potentiometer. P1.04 controls the haptic interface. Two GPIOs remain unallocated. USB and SWD have dedicated pads outside this count. The rows below list ascending logical indices from left to right. [BMD-340 pin table, §2.1](https://content.u-blox.com/sites/default/files/BMD-340_DataSheet_UBX-19033353.pdf)

| Signal | nRF GPIO, in signal order | Module pad, in signal order |
|---|---|---|
| R0–R4 | P0.14, P0.13, P0.16, P0.15, P0.17 | 32, 31, 34, 33, 35 |
| C0–C4 | P0.27, P0.26, P0.04, P0.05, P0.06 | 8, 7, 20, 21, 22 |
| C5–C9 | P0.07, P0.08, P1.08, P1.09, P0.11 | 23, 24, 51, 52, 27 |
| C10–C14 | P0.12, P0.29, P0.30, P0.20, P0.23 | 28, 10, 11, 38, 41 |

Use active-high column scan, row pulldowns and diode cathodes facing the rows (ZMK col2row). In Bluetooth idle, hold columns active and arm row interrupts or sense for wake. In unplugged USB travel mode, disable row wake, put columns inactive, then arm selector change and USB VBUS rise. Use normal drive and disable parallel trace and QSPI functions on shared pads. [ZMK keyboard scan configuration](https://zmk.dev/docs/config/kscan) · [Nordic power and wake sources](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html)

| Signal | GPIO | Pad | Purpose and reset behavior |
|---|---|---:|---|
| MODE_SEL | P1.10 | 53 | Level input. Proposed low = USB, high = Bluetooth. A break-before-make selector and defined weak bias avoid a floating input during movement. Allow hardware wake on a transition. |
| HOST_500_OK | P1.11 | 54 | Pulse once per accepted start-of-frame (SOF) while configured for 500 mA. Stop on deconfiguration, reset, detach or suspend. The input limiter expires stale pulses. |
| CHG_INT_N | P1.12 | 61 | Charger open-drain interrupt. Pull up to valid MCU logic domain. |
| CC_OUT1 | P1.13 | 62 | First CC advertisement-status input. Hardware qualification and firmware sense both use this signal. |
| CHG_REQUEST | P1.14 | 63 | Active-high charge request, with external pulldown. The thermistor window and request must both permit charging. |
| RGB_PG | P1.01 | 57 | LED power-good input. Disable the GPIO pull. Clear RGB_EN on timeout or loss of power-good. |
| USB_SUSPEND | P1.03 | 59 | Active-high default USB suspend request to the input limiter. |
| RGB_EN | P1.15 | 64 | Active high request, external pulldown. Power circuit enforces limits and isolates data when off. |
| CC_OUT2 | P0.03 | 19 | Second CC advertisement-status input. Sample both inputs after either changes. |
| BAT_ADC | P0.02 / AIN0 | 15 | Reserve only. Prefer PMIC ADC. Any populated divider must tolerate full pack voltage and meet sleep-leakage budget. |
| PMIC_SCL | P0.22 | 40 | TWIM0 clock for the charger and haptic interface. Pull up to 3.3 V, disable QSPI pin ownership. |
| PMIC_SDA | P1.00 | 56 | TWIM0 data shared by the charger and haptic interface. Disable trace on this pad. |
| RGB_DATA | P0.24 | 42 | SPIM MOSI to power-off-tolerant 3.3 V-to-LED-domain buffer. Hold low until the LED rail and buffer are valid. |
| RGB_SCK_RSVD | P0.25 | 6 | Reserve as SPIM clock if required by the pinned Zephyr driver. Leave copper unconnected. |
| VBAT_DIV_EN | P1.02 | 58 | Optional gated-divider control. Leave free if the charger ADC suffices. |
| UI_SCL | P0.19 | 37 | Dedicated 100 kHz TWIM1 clock to the display. |
| UI_SDA | P0.21 | 36 | Dedicated TWIM1 data to the display. Release both pins with pull-ups disabled before switching display power off. |
| UI_EN | P0.31 | 12 | Enables the display supply. Keep low during reset, suspend and unqualified startup. |
| VOLUME_ADC | P0.28 / AIN4 | 9 | Potentiometer wiper to SAADC, single ended. |
| POT_EXC | P1.05 | 48 | Energize the potentiometer briefly before each sample. Drive low at rest. |
| HAPTIC_EN | P1.04 | 60 | Active high. Enables the SYS-fed 1.8 V interface and releases the haptic driver from shutdown. R1100 holds it low through reset. |

P1.10–P1.15 are RF-adjacent, low-frequency-only pins. Use these for slow controls and interrupts. The two I²C buses and the pixel SPI assignments use unrestricted pins. Use TWIM0 for the charger and haptic driver, TWIM1 for the display and SPIM2 for the pixels. C11 and C12 moved to standard-drive, low-frequency pads. Limit each column to one scan pulse per 1 ms frame or slower (1 kHz at the pin), with valid row settling before sampling. Record actual pixel encoding, achievable SPIM clock and latch delay against the exact LED timing spec and the Zephyr revision selected with ZMK. [BMD-340 pin functions, §2](https://content.u-blox.com/sites/default/files/BMD-340_DataSheet_UBX-19033353.pdf) · [Zephyr LED strip SPI binding](https://docs.zephyrproject.org/latest/build/dts/api/bindings/led_strip/worldsemi%2Cws2812-spi.html)

A feasible custom SPI encoder uses an 8 MHz bit clock and ten clock ticks per LED data bit. Send three high ticks for zero (0.375 µs high, 0.875 µs low) and seven high ticks for one (0.875 µs high, 0.375 µs low). Each symbol lasts 1.250 µs. Pack all 67 × 24 symbols into one 2,010-byte RAM transfer, append 300 zero bytes for a 300 µs latch interval, and keep MOSI low afterward. The current stock Zephyr SPI binding accepts at most eight ticks per symbol, so this version needs a small packed-frame driver. Verify worst-case transfer continuity and logic translator delay before releasing firmware. [OPSCO timing table](https://datasheet.lcsc.com/datasheet/pdf/0907a34a701b4aef568078003f6e9eae.pdf?productCode=C5149201) · [Zephyr SPI binding](https://docs.zephyrproject.org/latest/build/dts/api/bindings/led_strip/worldsemi%2Cws2812-spi.html) · [Nordic EasyDMA widths](https://docs.nordicsemi.com/r/bundle/struct_nrf52/page/struct/nrf52.html)

## Power, USB, clocks and recovery

| Function | Module pads | Schematic contract |
|---|---|---|
| Logic and ground | 17 VCC, 65 VCCH, 1–5/16/18/29/30/45–47/55 GND | Tie VCC and VCCH to the regulated 3.3 V rail in normal-voltage mode and connect all designated ground pads. Figure 8 gives the LV-mode USB circuit. Size any external decoupling for the actual regulator and layout. |
| USB power sense and PHY | 66 VBUS, 67 USB-D−, 68 USB-D+ | Feed the dedicated PHY pin from protected 5 V USB VBUS (4.35–5.5 V at the module). Keep core power on 3.3 V. Power owns CC and the connector. Join the mirrored receptacle pins by polarity, route the pair over continuous ground and fit low-capacitance ESD protection at the connector. Include all directly attached VBUS capacitance in the inrush budget. |
| LF clock | 13 P0.00/XL1, 14 P0.01/XL2 | Fit a 32.768 kHz crystal for the BLE sleep clock. Select load capacitors for the crystal's specified load and PCB stray capacitance. Configure firmware for the external oscillator. |
| Programming | 44 SWDIO, 43 SWCLK, 39 P0.18/nRESET | J100 accepts a standard 1.27 mm Arm Cortex Debug cable for flashing a blank module and recovery over SWD. The probe reads the target supply on VTref. Configure the physical reset function in the boot image. |
| NFC | 25 P0.09/NFC1, 26 P0.10/NFC2 | Reserve both and leave unconnected. |
| Available GPIO | 49, 50, 60 | Three spare pads, all subject to the manufacturer's standard-drive, low-frequency rule. |

Use the full BMD-340 footprint for USB and port 1. Match the numbered land pattern and RF clearance in the manufacturer drawings to the symbol; the ordering catalog’s package label alone is insufficient. Place the antenna end at the board edge and keep copper, plate metal, battery foil and enclosure fasteners clear of the antenna region. Check the footprint and 3D model together. [BMD-340 mechanical and RF guidance](https://content.u-blox.com/sites/default/files/BMD-340_DataSheet_UBX-19033353.pdf)

## Programming connector

J100 is the Samtec **FTSH-105-01-L-DV-007-K**, a vertical surface-mount header with a missing pin at position 7. It accepts a keyed, 2 × 5 position Cortex Debug ribbon. On 21 November 2026 LCSC reported 95 pieces of **C5296739**, and JLCPCB’s extended SMT listing showed 76 available to order. The dated assembly sweep records minimums and the quantity screened for five boards. Quantities depend on the assembly quote. [Arm connector specification](https://www.keil.com/support/man/docs/jlink/jlink_connectors.asp) · [Samtec part drawing and options](https://www.samtec.com/products/ftsh-105-01-l-dv-007-k) · [LCSC](https://www.lcsc.com/product-image/C5296739.html?whichImg=0) · [JLCPCB](https://jlcpcb.com/partdetail/C5296739)

| J100 pin | Connection | J100 pin | Connection |
|---|---|---|---|
| 1 | Target 3.3 V reference | 2 | U100 pad 44, SWDIO |
| 3 | Ground | 4 | U100 pad 43, SWCLK |
| 5 | Ground | 6 | SWO unused |
| 7 | Mechanical key, terminal absent | 8 | TDI unused |
| 9 | Ground detect, tied to ground | 10 | U100 pad 39, nRESET |

Power the keyboard from USB or the battery during programming. Place J100 where the debug cable can seat fully with the case open. In board-top view the footprint has pin 1 at lower left and pin 2 directly above it. Its 0.74 × 2.79 mm lands use 1.27 mm pitch along each row and 4.07 mm between row centers. Position 7 has no land. The pin-1 silk mark and asymmetric pin pattern identify cable orientation. [Samtec recommended land pattern, figure 1](https://suddendocs.samtec.com/prints/ftsh-1xx-xx-xxx-dv-xxx-footprint.pdf)

## Firmware ownership

Port ZMK to a custom nRF52840 board. Sample MODE_SEL at startup and wake, debounce both transitions, release held keys on the previous transport when reachable, clear report state, then arm the newly selected transport. Require key release before re-reporting across a transition. An unavailable selected host silences reports. Keep USB enumeration and its power authorization independent of HID report routing, including when Bluetooth is selected with a USB cable attached. ZMK's built-in output commands express endpoint preference, so implement and review a strict selector policy at report dispatch and reconnection. Disable boot-time logging on a shared UART. [ZMK output selection](https://zmk.dev/docs/keymaps/behaviors/outputs) · [ZMK persistent settings](https://zmk.dev/docs/config/settings)

The USB-C sheet uses FUSB303BTMX in sink-only GPIO mode. CC_OUT1 and CC_OUT2 (in that order) read H/L on detach, H/H on default-current attach, L/H for 1.5 A and L/L for 3 A. This encoding supersedes the earlier TI detector proposal. Treat the bits as observations until a circuit independently enforces the allowed current and handles power-up, invalid signals, USB suspend and changing advertisements. [onsemi FUSB303B, tables 1 and 8](https://www.onsemi.com/pdf/datasheet/fusb303b-d.pdf)

Use the CC controller's qualified current advertisement and the USB stack's configured/suspend state as separate power-policy inputs. Send charge settings over TWIM and verify readback before asserting charge enable. On source downgrades, attachment changes, or unreliable communication, return to the conservative hardware limit. USB reset, suspend and detach must revoke a previous legacy-host grant. Hardware defaults must also protect a battery-depleted or firmware-blank board before any I²C command. The power sheet owns the hardware mechanism and worst-case timing for that guarantee. [TI BQ25622](https://www.ti.com/product/BQ25622) · [onsemi FUSB303B](https://www.onsemi.com/pdf/datasheet/fusb303b-d.pdf)

The next schematic review should independently match the symbol pad numbers to the BMD-340 pin table, check the power-off behavior of every cross-domain control, and derive the matrix and power-control devicetree from the actual netlist. The firmware pass should compile that board definition and cover held keys, reconnects, bus suspend and stuck-low I²C with digital tests.

## Game feedback

The host companion uses the same game integration as the OLED. A damage event carries an intensity and an event sequence number over the selected USB vendor HID or bonded BLE GATT connection. Discard repeated events, coalesce rapid hits, cancel on disconnect or power downgrade, and honor a local intensity and mute setting. Schedule motor I²C transactions behind charger fault handling. The power profiles, enable sequence and actuator limits are in the [haptic design](haptics.md). This describes the firmware interface for the firmware stage.
