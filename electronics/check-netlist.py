"""Check the integrated KiCad XML export against the intended keyboard wiring.

Run kicad-cli sch export netlist --format kicadxml -o board.xml keyboard.kicad_sch
then python3 check-netlist.py board.xml from the electronics directory.
"""
import argparse
import xml.etree.ElementTree as ET


def check(path):
    xml = ET.parse(path)
    nets = {}
    net_by_pad = {}
    for net in xml.findall("nets/net"):
        name = net.attrib["name"]
        pads = {(node.attrib["ref"], node.attrib["pin"]) for node in net.findall("node")}
        nets[name] = pads
        for pad in pads:
            if pad in net_by_pad:
                raise ValueError(f"{pad} appears on two nets")
            net_by_pad[pad] = name

    def expect_net(name, *pads):
        if name not in nets and "/" not in name:
            matches = [net for net in nets if net.rsplit("/", 1)[-1] == name]
            if len(matches) != 1:
                raise ValueError(f"Expected one net named {name}, found {matches}")
            name = matches[0]
        missing = set(pads) - nets.get(name, set())
        if missing:
            raise ValueError(f"{name} missing {sorted(missing)}")

    def expect_link(first, second):
        name = net_by_pad.get(first)
        if nets.get(name) != {first, second}:
            raise ValueError(f"Expected isolated link between {first} and {second}, found {name}")

    row_pads = [32, 31, 34, 33, 35]
    column_pads = [8, 7, 20, 21, 22, 23, 24, 51, 52, 27, 28, 10, 11, 38, 41]
    for column, pad in enumerate(column_pads):
        expect_net(f"C{column}", ("U100", str(pad)))
    key = 0
    for row, width in enumerate([15, 15, 14, 14, 9]):
        expect_net(f"R{row}", ("U100", str(row_pads[row])))
        for column in range(width):
            key += 1
            switch, diode = f"SW{key}", f"D{key}"
            expect_net(f"C{column}", (switch, "1"))
            expect_link((switch, "2"), (diode, "2"))
            expect_net(f"R{row}", (diode, "1"))

    expect_net("UI_EN", ("U100", "12"), ("U1000", "3"), ("R1000", "1"))
    expect_net("UI_SCL", ("U100", "37"), ("R1003", "2"), ("J1000", "4"))
    expect_net("UI_SDA", ("U100", "36"), ("R1002", "2"), ("J1000", "3"))
    expect_link(("U100", "48"), ("RV1000", "3"))
    expect_link(("RV1000", "2"), ("R1001", "1"))
    expect_net("VOLUME_ADC", ("U100", "9"), ("R1001", "2"), ("C1002", "1"))
    expect_net("3V3", ("U1000", "1"), ("C1000", "1"))
    expect_link(("U1000", "5"), ("R1004", "1"))
    expect_net("OLED_VIN_SW", ("U1000", "6"), ("R1004", "2"), ("C1001", "1"),
               ("R1002", "1"), ("R1003", "1"), ("J1000", "2"))
    expect_net("GND", ("RV1000", "1"), ("RV1000", "MP"), ("U1000", "2"),
               ("J1000", "1"), ("J1000", "MP"), ("R1000", "2"),
               ("C1000", "2"), ("C1001", "2"), ("C1002", "2"))

    # Haptic drive and bus isolation. Net membership also checks the motor
    # polarity, regulator support capacitor and the default-low enable.
    expect_net("SYS", ("U1100", "6"), ("U1100", "10"), ("U1101", "1"),
               ("C1100", "1"), ("C1101", "1"), ("C1104", "1"))
    expect_net("3V3", ("U1102", "7"))
    expect_net("HAPTIC_EN", ("U100", "60"), ("U1101", "3"), ("R1100", "1"))
    expect_net("HAPTIC_1V8", ("U1100", "5"), ("U1101", "5"), ("U1102", "3"),
               ("R1101", "2"), ("C1105", "1"), ("C1107", "1"))
    expect_net(net_by_pad[("U1102", "2")], ("R1101", "1"), ("C1108", "1"))
    expect_net("PMIC_SCL", ("U1102", "8"))
    expect_net("PMIC_SDA", ("U1102", "5"))
    expect_link(("U1102", "1"), ("U1100", "2"))
    expect_link(("U1102", "4"), ("U1100", "3"))
    expect_link(("U1100", "1"), ("C1103", "1"))
    expect_link(("U1100", "7"), ("M1100", "1"))
    expect_link(("U1100", "9"), ("M1100", "2"))
    expect_net("GND", ("U1100", "4"), ("U1100", "8"), ("U1101", "2"),
               ("U1102", "6"), ("R1100", "2"),
               *((ref, "2") for ref in ("C1100", "C1101", "C1103", "C1104",
                                          "C1105", "C1106", "C1107", "C1108")))

    chain = [*range(1, 16), *range(30, 15, -1), *range(31, 45),
             *range(58, 44, -1), *range(59, 68)]
    for led in chain:
        expect_net("LED_5V", (f"LED{led}", "3"), (f"C{300+led}", "2"))
        expect_net("GND", (f"LED{led}", "1"), (f"C{300+led}", "1"))
    for left, right in zip(chain, chain[1:]):
        expect_link((f"LED{left}", "4"), (f"LED{right}", "2"))
    expect_link(("LED67", "4"), ("TP300", "1"))
    expect_net("/RGB lighting/DIN_FIRST", ("R301", "2"), ("LED1", "2"))
    expect_net("RGB_DATA", ("U100", "42"), ("U300", "3"))
    expect_net("/RGB lighting/DIN_FIRST", ("R302", "1"))
    expect_link(("U300", "4"), ("R301", "1"))
    expect_net("GND", ("R300", "1"), ("R302", "2"), ("SW400", "1"), ("R400", "2"))
    expect_net("3V3", ("U300", "1"), ("U300", "5"), ("R401", "2"), ("J100", "1"))
    expect_link(("R401", "1"), ("SW400", "3"))
    for pin in ("3", "5", "9"):
        expect_net("GND", ("J100", pin))
    expect_link(("J100", "2"), ("U100", "44"))
    expect_link(("J100", "4"), ("U100", "43"))
    expect_link(("J100", "10"), ("U100", "39"))
    expect_net("MODE_SEL", ("SW400", "2"), ("U100", "53"))
    expect_net("USB_DP", ("J200", "A6"), ("J200", "B6"), ("U100", "68"))
    expect_net("USB_DM", ("J200", "A7"), ("J200", "B7"), ("U100", "67"))
    expect_net("CC_OUT1", ("U200", "7"), ("U100", "62"))
    expect_net("CC_OUT2", ("U200", "8"), ("U100", "19"))
    expect_net("PMIC_SCL", ("U600", "13"), ("U100", "40"))
    expect_net("PMIC_SDA", ("U600", "12"), ("U100", "56"))
    expect_net("SYS", ("U600", "9"), ("L900", "1"), ("U900", "8"),
               ("U901", "3"), ("U901", "5"), ("U901", "6"))
    expect_net("LOGIC_IN", ("U700", "10"), ("U700", "1"), ("U700", "2"))
    expect_net("3V3", ("U700", "6"), ("U100", "17"), ("U100", "65"), ("U200", "12"))
    pack_sheet = "/Charger and pack/"
    expect_net(pack_sheet + "PACK_POS", ("J600", "1"), ("U600", "8"))
    expect_net(pack_sheet + "PACK_NTC", ("J600", "2"), ("U600", "6"),
               ("U601", "2"), ("U601", "5"), ("R602", "2"), ("R603", "1"))
    expect_net(pack_sheet + "COLD_REF", ("U601", "3"), ("R607", "2"), ("R608", "1"))
    expect_net(pack_sheet + "HOT_REF", ("U601", "6"), ("R608", "2"), ("R609", "1"))
    expect_net(pack_sheet + "REGN", ("U600", "2"), ("U601", "8"), ("R602", "1"))
    expect_net(pack_sheet + "TEMP_OK", ("Q600", "1"), ("U601", "1"), ("U601", "7"))
    expect_net(pack_sheet + "CHARGE_INHIBIT", ("U600", "14"), ("Q600", "3"))
    expect_link(("Q600", "2"), ("Q601", "3"))
    expect_net("CHG_REQUEST", ("Q601", "1"), ("U100", "63"), ("R606", "1"))
    expect_net("GND", ("J600", "3"), ("U600", "15"), ("U700", "8"), ("U700", "11"))
    expect_net("LED_5V", ("U900", "2"), ("C904", "1"), ("C905", "1"))
    expect_net("RGB_PG", ("U900", "5"), ("U100", "57"))
    expect_net("RGB_EN", ("U100", "64"), ("R904", "1"))
    expect_net("/RGB supply/LED_GATE", ("U900", "6"), ("U901", "1"))
    expect_link(("L900", "2"), ("U900", "7"))
    expect_net("USB_VBUS", ("U800", "2"), ("R801", "1"), ("U100", "66"))
    connector_net = "/USB-C input/VBUS_CONN"
    expect_net(connector_net, *(("J200", pad) for pad in ("A4", "A9", "B4", "B9")),
               ("U200", "4"), ("Q200", "5"), ("R204", "1"), ("C202", "1"),
               ("R205", "1"), ("U203", "1"), ("R214", "1"), ("R212", "1"))
    expect_link(("R204", "2"), ("C201", "1"))
    for resistor, mosfet in (("R209", "Q200"), ("R210", "Q201")):
        expect_link((resistor, "1"), (mosfet, "4"))
    for pads in (
            [(part, pin) for part in ("Q200", "Q201") for pin in ("1", "2", "3")],
            [("U203", "8"), ("R209", "2"), ("R210", "2"), ("R211", "1")],
            [("R208", "2"), ("C204", "1"), ("C206", "1"), ("C208", "1")],
            [("U203", "2"), ("R212", "2"), ("R213", "1")]):
        net_name = net_by_pad.get(pads[0])
        if nets.get(net_name) != set(pads):
            raise ValueError(f"Expected isolated connection {pads}, found {net_name}")
    expect_link(("R214", "2"), ("U203", "5"))
    gate_caps = {("R211", "2"), ("C205", "1"), ("C207", "1"), ("C209", "1")}
    if nets.get(net_by_pad.get(("R211", "2"))) != gate_caps:
        raise ValueError("Gate ramp capacitors must connect only through R211")
    expect_net("USB_VBUS", ("Q201", "5"), ("U203", "7"), ("C800", "1"),
               ("R800", "1"), ("R208", "1"))
    expect_net("GND", ("C201", "2"), ("C202", "2"), ("C203", "2"), ("R207", "2"),
               *((f"C{i}", "2") for i in range(204, 210)), ("R213", "2"))
    expect_net("VBUS_LIMITED", ("U800", "5"), ("U600", "18"), ("D801", "1"), ("D801", "2"))
    expect_net("LOGIC_IN", ("D800", "3"), ("D801", "3"))
    expect_net("SYS", ("D800", "1"))
    expect_link(("R801", "2"), ("D800", "2"))
    expect_net("CC_OUT1", ("U801", "2"))
    expect_net("CC_OUT2", ("U801", "1"))
    expect_net("HOST_500_OK", ("U803", "10"), ("U100", "54"))
    expect_net("USB_SUSPEND", ("U100", "59"), ("Q808", "1"))
    expect_net("USB_DP", ("R810", "1"), ("R817", "1"))
    expect_link(("R817", "2"), ("U803", "2"))
    expect_net("USB_DM", ("R807", "1"))
    for key in range(1, 68):
        for ref, library in [(f"SW{key}", "Keyboard_MX:"), (f"LED{key}", "Keyboard_LED:")]:
            footprint = xml.findtext(f"components/comp[@ref='{ref}']/footprint", "")
            if not footprint.startswith(library):
                raise ValueError(f"{ref} requires the routed LED opening and matching silkscreen")
    print("Verified 67 key paths, 67 RGB pixels, USB data, mode selector, CC reporting, Cortex SWD pinout,")
    print("charger control bus, battery polarity, temperature interlocks, USB input protection, RGB and core power, OLED I²C, volume ADC and isolated haptic drive.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("netlist", help="KiCad XML netlist")
    check(parser.parse_args().netlist)
