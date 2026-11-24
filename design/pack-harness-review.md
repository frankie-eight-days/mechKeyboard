# J600 and the three battery conductors

The battery is the BatterySpace CU-J450-V3 revision. The supplier specifies 42 mm, 24 AWG leads terminated in Molex 502351-0300 with three 0561618081 or 5600850101 contacts. Pin 1 connects to PACK_POS, pin 2 to PACK_NTC and pin 3 to GND. This agrees with the exported KiCad schematic. The V3 page gives no insulation color assignment. Red, ivory and charcoal distinguish the three nets in the model. The pack comes precrimped. [BatterySpace CU-J450-V3](https://www.batteryspace.com/Polymer-Li-Ion-battery-3.7V-1500mAh-5.55Wh-3A-rate-703562-2C-2.aspx)

## Connector and route

Molex drawings SD-502352-001 and SD-502351-001 give the 2 mm pitch, 10 × 9.4 × 6.4 mm three-position board-header envelope, 8.1 mm plug width and 11 mm mated length along the insertion axis. The modeled connector bodies, keyed chamber, simplified SMT contacts and latch form approximate these interfaces. The actual vendor drawings govern the PCB and detailed plastic features. [J600 header](https://www.molex.com/en-us/products/part-detail/5023520300) · [Pack housing](https://www.molex.com/en-us/products/part-detail/5023510300)

J600 opens toward the pack along assembly vector (−0.8660, +0.5000, 0), avoiding the neighboring LED during straight withdrawal. For the stock KiCad footprint the datum maps to FreeCAD X = 148.6855, Y = −40.2825, on the PCB underside. Map the footprint's local positive X toward (+0.5000, +0.8660), and its local positive Y toward (−0.8660, +0.5000) in assembly coordinates. The wire exit at the plug is X = 143.0, Y = −37.0, Z = −4.7 for the center NTC contact. On this underside mounting, facing the plug opening with the latch downward, pin 1 is toward the front of the keyboard. The previous 3-mm-high coarse envelope is superseded.

The CAD uses three 42.00 mm circular-arc centerlines, a nominal 1.40 mm insulation diameter and a centerline bend radius of at least 6.25 mm across the sampled postures. The nominal wire exits at the open east side of the pack, X = 109, Y = −46/−44/−42, Z = −8.5 mm. The first 1.5 mm of each lead crosses the lateral expansion envelope at this intentional exit. The route clears the pouch proper and guide walls after that. The nominal pack now spans X 41–109 mm and Y −75 to −40 mm. Its guide walls, expansion volume, strap slots and strap recess move together, 2 mm right and 4 mm toward the spacebar. The J600 header and printed tray seam keep their original coordinates. The 1.25 mm vertical expansion reserve clears switch features by 1.25 mm, stabilizers by 4.00 mm and LEDs by 2.31 mm.

| Nominal clearance | Measured in CAD |
|---|---:|
| Seated header to switch parts / LED | 0.897 / 0.833 mm |
| Seated plug to switch parts / LED | 1.967 / 0.876 mm |
| Seated wire jacket to tray / PCB / switch parts / LED | 2.836 / 2.400 / 1.997 / 3.208 mm |
| Seated adjacent wire jackets | 0.600 mm |
| Entire 6 mm straight withdrawal corridor to switch parts / LED / PCB | 1.570 / 0.865 / 0.520 mm |
| Minimum wire jacket to floor through lift, fore/aft shift and withdrawal | 2.133 mm |

The final solid-model audit checks the three cable jackets, connector pair, expanded battery envelope, tray, PCB, switch features and LEDs at ten seated, front-high and withdrawal poses. A second check uses 39 poses in 0.5° lift increments up to 12°, board translation and 0.5 mm increments over the 6 mm plug withdrawal. It also checks 42.00 mm centerline length for each lead. A conservative solid swept envelope separately bounds the plug housing over the full straight 6 mm pull relative to the neighboring LEDs, switch features and board. At 12° front-high and 2 mm toward the spacebar, the underside of the plug is about 18.84 mm above the tray floor. Support the loosened cover and keyboard, release the latch and pull by the housing along the indicated axis. The longest distance in a straight line from a pack exit to its still-mated socket is 39.13 mm across the sampled service poses. The 42 mm nominal lead therefore has 2.87 mm of geometric length beyond that straight line in the most extended pose.

These are design clearances. The finished pack's lead-exit location, usable free-length datum and tolerance, jacket diameter, minimum bend radius, actual solder fillets, movable latch travel, and access with real fingers still need supplier or physical confirmation.
