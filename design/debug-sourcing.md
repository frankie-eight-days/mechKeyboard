# Sourcing the Cortex SWD header and cable

J100 takes a straight-through, 2 × 5 position, 1.27 mm socket-to-socket Cortex Debug ribbon. The keyboard needs one SMT header per board. One reusable bench cable serves any number of boards. Align the ribbon’s pin-1 stripe with the footprint’s pin-1 mark. The Samtec header has a keying notch and position 7 omitted. Power the target through USB or the battery so the probe can sense 3.3 V on VTref. [Arm connector specification](https://www.keil.com/support/man/docs/jlink/jlink_connectors.asp) · [Samtec’s recommended cable mates](https://kineticlive.samtec.com/standards/jtag/) · [Keyboard SWD pinout](controller-and-pins.md#programming-connector)

| Item | Exact orderable part | Supplier availability on 21 November 2026 |
|---|---|---|
| J100, keyboard PCB | Samtec **FTSH-105-01-L-DV-007-K**, LCSC **C5296739** | At 21:07 UTC, **95** at LCSC. JLCPCB listed it for SMT assembly with **95** displayed in stock and **76** available to add to the assembly library. The separate preorder minimum is **4**. Assembly allocation is determined at quotation. [LCSC](https://www.lcsc.com/product-image/C5296739.html?whichImg=0) · [JLCPCB](https://jlcpcb.com/partdetail/C5296739) |
| Samtec mating cable | **FFSD-05-D-06.00-01-N**, LCSC **C17954924** | The 152.4 mm cable comes terminated at both ends. At 21:07 UTC, **0** at LCSC and **0** available to add to the JLCPCB assembly library. DigiKey also lists this exact assembly as **SAM8218-ND**. [LCSC](https://www.lcsc.com/product-image/C17954924.html?whichImg=0) · [Samtec](https://www.samtec.com/products/ffsd-05-d-06.00-01-n) · [DigiKey](https://www.digikey.com/en/products/detail/samtec-inc/FFSD-05-D-06-00-01-N/1106577) |
| Available mating cable | Adafruit **1675** | The supplier’s own page showed **in stock at US$2.95** at 21:05 UTC. This preterminated, 150 mm ribbon has 1.27 mm 2 × 5 SWD sockets at both ends. [Adafruit](https://www.adafruit.com/product/1675) |

A probe with a native 1.27 mm Cortex Debug port uses the ribbon directly. For a SEGGER J-Link with the older 20-pin, 2.54 mm Arm port, SEGGER **8.06.02** adapts that port to J100 and includes the mating nine-pin cable. An existing probe and this adapter kit are a complete connection. [SEGGER adapter and kit contents](https://shop.segger.com/debug-trace-probes/debug-probes/adapters/9-pin-cortex-m-adapter)

## Repeat the stock check

From the project root, run the read-only lookup with Python 3. It uses the public supplier data, requires no package installation or login, and emits timestamped JSON for each exact supplier code. A site error or an unfamiliar page format produces an error field and a nonzero exit status. Each supplier can change its page format. [Project stock lookup](../electronics/check-stock.py)

```sh
python3 electronics/check-stock.py C5296739 C17954924
```

For a supported integration, LCSC offers the Products API for live inventory. The project also supports a complete [netlist stock audit](assembly-stock.md). Official LCSC API access requires an LCSC account, an application and credentials issued after review. JLCPCB independently offers a Components API for availability, specifications and pricing. It requires a developer account, application approval and a registered app. The published setup instructions for both services describe HTTP APIs. I found no vendor-published installable inventory CLI in those instructions. [LCSC API access](https://www.lcsc.com/agent/) · [LCSC product API list](https://www.lcsc.com/agent/list?urlKey=list) · [JLCPCB API access](https://jlcpcb.com/help/article/jlcpcb-online-api-available-now) · [JLCPCB developer portal](https://api.jlcpcb.com/)
