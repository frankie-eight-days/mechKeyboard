"""Retain the base document's FreeCAD view state after a headless solid export."""
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


def restore_view(source, model, face_name, color):
    target = Path(model)
    staged = target.with_suffix('.tmp')
    with zipfile.ZipFile(source) as ref, zipfile.ZipFile(model) as geom:
        gui = ET.fromstring(ref.read('GuiDocument.xml'))
        providers = gui.find('ViewProviderData')
        objects = ET.fromstring(geom.read('Document.xml')).find('ObjectData')
        labels = {item.get('name'): item.find('./Properties/Property[@name="Label"]/String').get('value')
                  for item in objects}
        carrier = next(name for name, label in labels.items() if label.startswith('Shared left OLED'))
        face = deepcopy(providers.find(f'ViewProvider[@name="{carrier}"]'))
        face.set('name',face_name)
        providers.append(face)
        providers.set('Count',str(len(providers)))
        assert set(labels) == {view.get('name') for view in providers}
        artifacts = {item.get('file'): ref.read(item.get('file')) for item in gui.iter() if item.get('file')}
        for name,label in labels.items():
            if name != face_name and not any(v in label for v in ('tray section','rear cover and mounting','Shared left OLED')):
                continue
            blob = providers.find(f'ViewProvider[@name="{name}"]//MaterialList').get('file')
            material = bytearray(artifacts[blob])
            # FreeCAD v1.1 MaterialList v3, one uniform material, packed diffuse RGBA.
            if len(material) == 40 and material[:4] == bytes([1,0,0,0]):
                material[8:12] = bytes([255,*(round(255*v) for v in reversed(color))])
                artifacts[blob]=bytes(material)
        with zipfile.ZipFile(staged,'w',zipfile.ZIP_DEFLATED) as dest:
            for name in geom.namelist():
                if name not in artifacts and name != 'GuiDocument.xml':
                    dest.writestr(name,geom.read(name))
            for name,data in artifacts.items():
                dest.writestr(name,data)
            dest.writestr('GuiDocument.xml',ET.tostring(gui,encoding='utf-8',xml_declaration=True))
    staged.replace(target)
