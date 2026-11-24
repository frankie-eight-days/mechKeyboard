---
name: review-schematic-release
description: Audit an electronic schematic for release into PCB placement or routing. Use for a design sign-off, independent electrical review, or evidence-backed pre-layout issue register. Use the drawing-focused workflow for requests limited to redrawing a schematic.
---

# Review a schematic for PCB layout

Establish the requested gate and exact revision. Inventory the native design, BOM/variants, local libraries, firmware assumptions, power calculations and mechanical constraints. Respect the user's boundary on physical builds, external purchasing and design changes. Keep review outputs outside the native design until fixes are authorized.

Apply all IDs in [the release checklist](references/checklist.md). Record one outcome per ID or group IDs only when they share the same evidence and disposition. State the fit and limits of each check. Use project-local primary sources where their revisions are known. Verify current vendor or standard information when the answer depends on it. Fit all limits to the exact fitted suffix and operating conditions.

For KiCad, use an unmodified snapshot with its project file and local libraries. Export ERC including exclusions, XML connectivity, and a multipage plot. Inspect ignored rules as well as returned diagnostics. Render the plot, view every page, zoom dense areas as needed, and cross-probe critical physical pin numbers. Inspect footprint copper, numbering, mirror and land dimensions separately. A stored BOM or passing connectivity script establishes only the conditions it actually checks.

Exercise boundary states on the exported design. Examples include blank firmware, dead or absent battery, low source, cold startup, plug-in to an empty bank, overvoltage applied to an already powered bank, watchdog reset and one interface powered while another is off. For timing, try an actual clock/divider/encoding and compute its guaranteed margin. For recovery, check what EN, reset, isolation and power removal do on the exact chip. Convert typical curves and unknowns into explicit assumptions and sensitivity calculations. If a physical measurement is outside scope, offer a file-based way to close the question or preserve the residual uncertainty.

When independent review is requested or authorized, assign distinct circuits plus their shared interfaces. Give all reviewers the same export and checklist. Have a second pass challenge claimed defects against the exact data sheet, initial conditions and real board wiring. Merge common causes, retain contrary evidence and distinguish an observed mismatch from an unbounded corner.

Deliver one ranked register with location, consequence, evidence, owner, earliest blocked stage and measurable closure for each item. Separate known-good checks and deferred board/firmware verification. State whether placement, routing or production can proceed at the requested gate. Include the coverage ledger and any unverified areas. After an authorized ECO repeat affected checks and record the new baseline.
