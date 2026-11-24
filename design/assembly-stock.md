# Revision F assembly stock, November 21, 2026

All **77 supplier codes** in the eleven-sheet KiCad export matched the exact manufacturer part numbers at LCSC and JLCPCB. Each had enough LCSC retail stock and JLCPCB available order quantity for **five keyboards** in the 22:17–22:18 UTC sweep. Each of the 372 supplier-coded parts per keyboard has a footprint and an explicit assembly method. The quantities below include modeled assembly losses. Inventory remains shared with other buyers until parts are allocated. [All line items and reference designators](smt-stock-2026-11-21.csv) · [JLCPCB parts sourcing](https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction)

## Assembly split

| Stage | Per keyboard | Production detail |
|---|---:|---|
| JLCPCB SMT | 370 placements, 75 codes | Use **Standard PCBA**. The 67 reverse-mount SK6812MINI-E LEDs are Standard-only and carry JLC’s review flag. Their optical openings, bottom-side rotation and board outline need the routed PCB and placement file for approval. The single BMD-340 radio is also Standard-only and carries an X-ray flag. [LED listing](https://jlcpcb.com/partdetail/C5149201) · [Radio listing](https://jlcpcb.com/partdetail/C5456944) |
| Volume potentiometer RV1000 | 1 placement | JLC lists the Alps RK09K1130A6S for manual through-hole soldering in both its prototype and batch processes. Include it in the assembly quotation or hand-solder it after reflow. [Alps pot listing](https://jlcpcb.com/partdetail/C209770) |
| Hand-soldered MX switches | 67 | These are Cherry MX2A-L1NB, installed through the plate. Their footprints and references are present in the netlist. Mechanical Keyboards showed **544** of the exact PCB-mount RGB variant at $0.40 each, enough for the 335 switches in five boards. DigiKey US lists the exact MPN as a 450-piece lead-time order. [Retail SKU and live variant](https://mechanicalkeyboards.com/products/cherry-mx2a-red-45g-linear?variant=48020634239276) · [DigiKey](https://www.digikey.com/en/products/detail/cherry-americas-llc/MX2A-L1NB/21738399) · [Keybed](keybed.md) |
| Haptic actuator M1100 | 1 hand-fit | Attach the LEADER motor after reflow, hand-solder its two leads and fit strain relief. Its footprint is excluded from pick and place. [Placement and power](haptics.md) |
| Bare test pad | 1 | TP300 is the last pixel’s data output. The copper feature takes zero purchased parts. |
| Display and cable | 1 module and 1 cable | Mount the OLED in the enclosure and plug in the four-wire cable after assembly. Adafruit displayed **72** of OLED 4440 and the **50 mm preterminated cable 4399** as in stock. The 100 mm cable 4210 showed out of stock. [Display](https://www.adafruit.com/product/4440) · [50 mm cable](https://www.adafruit.com/product/4399) · [100 mm cable](https://www.adafruit.com/product/4210) |

The 77 supplier codes comprise 18 JLC Basic and 59 Extended parts. Fitted parts include R1002 and R1003 on the display bus. The [mechanical and hand-fit BOM](mechanical-bom.csv) lists the case hardware, fabricated steel plate, printed parts and purchased assemblies with quantities per keyboard. It cross-references the motor and potentiometer already in the electronics BOM. Other case hardware and the removable programming cable are separate purchases. [Display and volume design](display-and-volume.md) · [Debug cable](debug-sourcing.md) · [Mechanical fit](fit.md)

## Quantities worth watching

| Part | LCSC retail | JLC displayed stock | JLC available order quantity | Five-board screen |
|---|---:|---:|---:|---:|
| C2760466 · U601 pack-temperature comparator | 22 | 22 | 15 | 6 |
| C427179 · C904/C905 LED bulk capacitors | 25 | 25 | 24 | 11 |
| C5296739 · J100 Cortex debug header | 95 | 95 | 76 | 6 |
| C5456944 · U100 radio | 114 | 229 | 168 | 6 |
| C209770 · RV1000 volume control | 722 | 722 | 145 | 6 |
| C51940130 · J1000 display connector | 17,980 | 17,981 | 17,681 | 6 |

C1591 covers the 100 nF bypasses. C1589 is the 10 nF pot-filter capacitor. Both have stock at both suppliers. The fitted XYECONN connector has a part-specific land pattern. The genuine JST C160404 alternative displayed 4,936 at JLC, but its available order quantity was zero and the rendered listing offered preorder. J100 provides a cross-check in the other direction. Its rendered page showed 95 in stock with 76 available to add to the assembly library. [J1000](https://jlcpcb.com/partdetail/C51940130) · [JST alternative](https://jlcpcb.com/partdetail/C160404) · [J100](https://jlcpcb.com/partdetail/C5296739)

## Reproduce the sweep

From the project root with KiCad CLI and Python 3 available, run the following commands. Individual code lookups still return JSON. Netlist mode writes CSV and returns a nonzero exit status if any required line has a lookup, identity, stock or assembly exception. A completed assembly quote checks the eventual BOM, board outline, copper, placement file, panel, part orientation and feeder allocation. [Lookup CLI](../electronics/check-stock.py) · [JLCPCB BOM matching](https://jlcpcb.com/help/article/common-bom-and-cpl-matching-issues-and-explanations)

```sh
kicad-cli sch export netlist --format kicadxml -o /tmp/keyboard-stock.xml electronics/keyboard.kicad_sch
python3 electronics/check-stock.py --netlist /tmp/keyboard-stock.xml --boards 5 > /tmp/keyboard-stock.csv
python3 electronics/check-stock.py C5296739 C51940130
```

The tool reads LCSC’s exact product record and the public JSON used by JLC’s parts library. For the fitted parts JLC’s in-stock purchasing limit is its `canPresaleNumber` field, displayed as **Available Order Qty**. JLC transitions the order to a preorder when the requested quantity exceeds that threshold. The CLI retains the older single-code JSON key `preorder` as an alias for the supplier field. The CSV also reports minimum placement, minimum quantity, fixed attrition and proportional attrition. For a five-board run it uses the larger of each listed minimum or the placement count plus the larger of the fixed loss or rounded-up proportional loss. This intentionally rounds small fractional losses up to one spare. The stricter of displayed stock and available order quantity must cover that screen. The project CLI uses no account credentials. Both vendors separately offer credentialed developer APIs. [JLC listing and purchasing interface](https://jlcpcb.com/parts/in-stock-parts) · [JLCPCB assembly quantity guidance](https://jlcpcb.com/parts/bom-tool/) · [LCSC Open API](https://www.lcsc.com/agent/) · [JLCPCB Online API](https://jlcpcb.com/help/article/jlcpcb-online-api-available-now)

## Loose mechanical hardware

The mechanical BOM is a separate final-assembly shopping list. Eight fastener lines cover the two tray joints, nine PCB/cover mounts, OLED and dial. For a single keyboard, the BOM gives a metric-fastener source and exact dimensions. A local store can substitute matching stock, especially when the head diameter, point style and countersink angle match. The steel switch plate has its own DXF for a sheet-metal shop.

Order **nine standard M2.5 × 0.45 DIN 934 hex nuts** per keyboard from a metric-fastener supplier. Accu HPN-M2.5-A2 is A2 steel, 5.0 mm across flats (+0/−0.18) and 2.0 mm thick (+0/−0.25). The side pockets fit those dimensions. Buy the M3 seam/dial nuts and M2 OLED nuts in the separate sizes listed in the BOM. Four M2.5 × 6 front screws and five M2.5 × 16 rear screws share the nine M2.5 nuts. [Accu specification and ordering](https://accu-components.com/us/hexagon-nuts/7886-HPN-M2-5-A2)

LCSC also sells loose hardware. Its exact record for XHHD C133377 showed 12,100 M3 nuts and a minimum purchase of 100 on November 22 at 05:11 UTC. That record lacked a drawing proving the pocket-critical 5.5 mm flats and 2.4 mm thickness. The BOM specifies a drawing-backed DIN 934 nut. The other candidate, Shuntian C357432, returned zero LCSC retail stock in the same check. Neither fastener is on the existing board assembly BOM. [Mechanical BOM](mechanical-bom.csv) · [XHHD listing](https://www.lcsc.com/product-detail/C133377.html) · [Shuntian listing](https://www.lcsc.com/product-detail/C357432.html)
