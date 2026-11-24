# Sculpted case print sets

Choose Alpine Pass (forest) or Elevated City. Each uses six printed parts and the fasteners in the [mechanical BOM](../../design/mechanical-bom.csv).

| Quantity | File | Supplied print orientation |
|---:|---|---|
| 2 | Left and right tray STLs in the theme folder | Floor down, each on its own bed |
| 1 | Left art face in the theme folder | Flat mating face down, relief up |
| 1 | [Shared left OLED carrier](shared-left-carrier.stl) | Flat mating face down, sleeves up |
| 1 | Right cover in the theme folder | Long rear edge down |
| 1 | [Common volume dial](../tray-fit-meshes/volume-knob.stl) | Outer face down, shaft opening up |

The carrier, art face, right cover and dial share the third 220 × 220 mm bed. Preserve the imported orientations. Slicer checks used an Adventurer 5M, 0.4 mm nozzle, 0.20 mm layers, PLA and supports disabled. Use four wall loops for the trays. Slide nine M2.5 DIN 934 steel hex nuts into the inward-facing slots before fitting electronics. Keep the trays level until the screws engage. Use a 5 mm outer brim for Alpine or a 7 mm brim for City. The 33 mm exterior bridge in the original left cover was eliminated by cutting at Z = 7.55 mm. The four M2 OLED screws and three left M2.5 screws clamp both pieces. The remaining 0.85 mm art face needs to be supported while handling. Print finish, adhesion, nut-pocket durability and bridge sag remain physical checks.

| Complete edition | PLA including brim | Estimated time, all three jobs |
|---|---:|---:|
| Alpine Pass | 61.96 m | 10 h 15 min |
| Elevated City | 63.71 m | 11 h 08 min |

Both native design files include the rest of the keyboard assembly. Run build.py with forest or city in FreeCAD’s bundled Python to regenerate that edition from the current primary FreeCAD assembly. The [render gallery](../sculpted-cases.pdf), [steel plate files](../switch-plate), and [assembly guide](../assembly-guide.pdf) accompany these print sets.
