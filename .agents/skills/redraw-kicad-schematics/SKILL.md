---
name: redraw-kicad-schematics
description: Redraw and visually review KiCad schematics for readability, including analog and power circuits, controller support circuitry, and hierarchical system overviews. Use when the user wants a clearer existing circuit or a readable first schematic.
---

## Establish the electrical baseline

Record the installed KiCad version and open the project through its root. Before moving symbols, export the complete schematic to PDF and KiCad XML. Preserve symbol UUIDs, reference designators, footprints, pin numbers and assembly fields during a graphical redraw. Track deliberate circuit changes separately so the final comparison can explain each changed pin group.

## Draw the circuit a reader needs to trace

- Pick the question each page answers. On a power stage, follow the source through protection and the switching element to the load. Place the input capacitor where that path begins, and draw the output bank and feedback return where they act. Put a bootstrap capacitor between its two IC pins. Keep each compensation or threshold network physically wired on the page.
- Arrange a controller symbol by function. Place supply pins above, grounds below, and clocks, buses and debug pins in coherent groups. Draw bypass capacitors, crystal loads and pull resistors on short branches from the relevant pins. A project symbol can change graphical pin locations while keeping its physical pad map.
- Use supply and ground symbols for shared rails. PWR_FLAG tells ERC where a supply is driven. Use it at an actual source when ERC needs that information. Show voltage domains explicitly at level translators and connectors.
- Use a single clear rail through repeated circuits. At row wraps, give both ends the same meaningful continuation name. Put a dot at each branching junction and separate adjacent branches enough that dots and component fields remain distinct.
- Give every page a top title. At the root, arrange real child-sheet symbols along the main power and data paths, with names large enough to read at fit-to-page zoom. Put the relevant interface pins on facing edges. Use vector buses for parallel signals and label any shared control nets omitted from the root drawing. Keep the title block and all sheet margins clear.
- Label a relationship when the reader would otherwise have to calculate or infer it. Examples include an active-low inhibit, a current threshold, a pulldown that defines an unpowered state, or the page where a power rail originates. Label a proposed value as provisional when layout or component data still determines it.

## Review the plotted result

Export the integrated project after edits. Inspect every affected page as an image at fit-to-page size, then zoom the densest areas. Trace a current path, a control loop and an off-state path where applicable. Check field collisions, pin names hidden by wires, labels facing into parts, clipped text, four-way junctions, inter-sheet gaps and misleading crossings. Move the actual schematic objects, replot and inspect the revised page.

With a KiCad CLI that supports these commands, use this sequence from the project folder. Replace the example root filename and keep review exports in a working directory.

```sh
kicad-cli sch export pdf -o review.pdf board.kicad_sch
kicad-cli sch export netlist --format kicadxml -o review.xml board.kicad_sch
kicad-cli sch erc --exit-code-violations -o review.rpt board.kicad_sch
```

Compare the sets of connected (reference, pin) pairs before and after. Hierarchy can rename a net while leaving every pin connected. A real split or merge changes those sets. Also verify component count, repeated-sheet instance paths, title blocks, page order and any deliberate schematic-to-footprint pin changes. Report physical or timing assumptions independently of ERC.

Horowitz and Hill’s regulator example shows an effective arrangement for an error amplifier, pass device and feedback ladder. Jim Williams gives a compact example of local protection and amplifier feedback in figure 101 of AN47. [How to Draw Schematic Diagrams](https://opencircuitdesign.com/xcircuit/goodschem/goodschem.html) · [AN47, figure 101](https://www.analog.com/media/en/technical-documentation/application-notes/an47fa.pdf#page=46)
