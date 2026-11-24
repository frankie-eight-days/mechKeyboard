"""Compare visible FreeCAD wire solids and terminal labels to a KiCad XML netlist.

Generate the netlist with kicad-cli sch export netlist --format kicadxml.
Pass the XML and one or more FCStd assemblies to this script in FreeCAD Python.
"""
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import FreeCAD as App
netlist, *models = sys.argv[1:]
electrical = {}
for net in ET.parse(netlist).findall('.//nets/net'):
    for node in net.findall('node'):
        key = node.get('ref') + '.' + node.get('pin')
        electrical[key] = net.get('name').split('/')[-1]
wanted = {f'{ref}.{i}' for ref,pins in [('M1100',2),('J600',3),('J1000',4)] for i in range(1,pins+1)}
for model in models:
    doc = App.openDocument(str(Path(model).resolve()))
    actual = {}
    with zipfile.ZipFile(model) as z:
        assert z.testzip() is None, model
        gui = ET.fromstring(z.read('GuiDocument.xml'))
    for o in doc.Objects:
        if 'FromPin' not in o.PropertiesList:
            continue
        pin = o.FromPin.split()[0]
        assert pin not in actual, pin
        assert o.Net == electrical[pin], (pin,o.Net,electrical[pin])
        assert o.Shape.isValid() and o.Shape.Volume > 0 and len(o.Shape.Solids)==1, pin
        prop = gui.find(f'.//ViewProvider[@name="{o.Name}"]/Properties/Property[@name="Visibility"]/Bool')
        assert prop is not None and prop.get('value')=='true', (pin,model)
        actual[pin] = o.Net
    assert set(actual)==wanted,actual
    print(Path(model).name, len(actual), 'visible wire solids with matching KiCad net assignments',sorted(actual.items()),flush=True)
    App.closeDocument(doc.Name)
