# Mac mini handoff · Rev F

**Resume with the battery cutoff, live USB overvoltage and battery-free USB suspend decisions. PCB placement is on hold.** This November 24, 2026 checkpoint preserves the reviewed schematic, the mechanical models, both rounds of review and their supporting evidence. The findings have been recorded. The schematic still represents the circuit the reviewers examined.

## Open the project

Use KiCad 10.0.8 with its standard libraries for the closest match to the electrical baseline, FreeCAD 1.1 for the assembly, and Python 3 for the ledger checks. Run from Terminal on the Mac mini.

```sh
git clone https://github.com/frankie-eight-days/mechKeyboard.git
cd mechKeyboard
open -a KiCad electronics/keyboard.kicad_pro
open -a FreeCAD mechanical/keyboard-placement.FCStd
```

For a review without CAD, open the [schematic PDF](electronics/keyboard-schematic.pdf), [mechanical review](mechanical/mechanical-review.pdf) and [screw-stack sections](mechanical/mounting-sections.pdf). The project library tables resolve custom symbols and footprints relative to the KiCad project. The FreeCAD sources sit alongside the native assemblies. If regenerating models, use FreeCAD's bundled Python and point `KICAD10_3DMODEL_DIR` at the standard KiCad 3D model library if installed outside the default macOS bundle. [Mechanical generator](mechanical/build_fit.py)

## Read the evidence in order

| Record | What you'll find |
|---|---|
| [Architecture](design/architecture.md) · [schematic review](design/schematic-review.md) · [checkpoint review](design/checkpoint-review.md) | Earlier design choices, drawing review and the evolution of the keyboard. For current dispositions use the Rev F audits below. |
| [Release checklist](design/schematic-release-checklist.md) · [19-item issue register and 48-item coverage record](design/prelayout-review.md) · [printable review](design/prelayout-review.pdf) | First pre-layout review. Each item describes the consequence, closure evidence and earliest decision point. The coverage record includes partial and deferred checks. |
| [Frozen evidence ZIP](design/prelayout-review-evidence.zip) | Reviewed XML netlist, ERC output, sheet overview, individual reviewer reports and the contemporary working scripts. |
| [Component and pin audit](design/rev-f-electrical-audit/review.md) · [workbook](design/rev-f-electrical-audit/electrical-audit.xlsx) · [case verdicts](design/rev-f-electrical-audit/case-verdicts.csv) | Second pass by component, pin and operating state. Each case identifies the particular claim, verdict and remaining assumptions. |
| [Independent challenges](design/rev-f-electrical-audit/challenges.md) · [cross-circuit calculations](design/rev-f-electrical-audit/interactions.md) | Where a second reader changed, narrowed or upheld a finding. Includes U803 timing, U700 stress and the haptic/charger bus. |
| [Datasheets](datasheets/README.md) · [supplier index with checksums](datasheets/index.csv) · [stock snapshot](design/smt-stock-2026-11-21.csv) | Supporting part limits and a dated five-board sourcing reconciliation. Recheck inventory and assembly acceptance once there is a board and placement file. |
| [Schematic release skill](.agents/skills/review-schematic-release/SKILL.md) · [drawing skill](.agents/skills/redraw-kicad-schematics/SKILL.md) | Project copies of the review and schematic drawing workflows for the next revision. |

**Verified scope.** KiCad exported eleven sheets, 440 references, 294 nets and 1,250 pin memberships. The configured ERC reported zero violations and zero exclusions. Four rule types were disabled (single global label, four-way junction, SPICE model issues and footprint filters). All 67 matrix positions, 66 inter-pixel links and 351 switch/stabilizer drills reconciled. [Connectivity results](design/prelayout-review.md) · [Mechanical transfer](design/rev-f-electrical-audit/key-placement-check.csv)

The component audit covered 122 capacitors (14 part numbers), 69 fixed resistors, one pot and three inductors. All capacitor nameplate voltages clear their stated screen. DC bias, temperature, pulse current and converter stability retain individual qualifications. Semiconductor coverage includes individual junctions in dual parts. The logic audit covers 270 signal pins in its declared scope, with 317 case rows and **13 explicit static passes**. Coverage counts measure what was examined. An electrical pass applies only to the operating conditions on its row. [Capacitors](design/rev-f-electrical-audit/capacitors.csv) · [Resistors and inductors](design/rev-f-electrical-audit/resistors-inductors.csv) · [Semiconductors](design/rev-f-electrical-audit/semiconductors.csv) · [Supply pins](design/rev-f-electrical-audit/supply-pins.csv) · [Logic margins](design/rev-f-electrical-audit/logic-levels.csv) · [Operating states](design/rev-f-electrical-audit/states.csv)

## Open decisions

The IDs match the [full issue register](design/prelayout-review.md). The actions below include the findings added in the [deeper audit](design/rev-f-electrical-audit/review.md).

| ID | Circuit | Where to resume |
|---|---|---|
| **01** | **Battery cutoff** | The cell's normal discharge floor is 2.75 V. The pack protection trip is 2.40 ±0.10 V. Choose a qualified independent cutoff or pack, then bound hysteresis, residual drain and USB restart with a blank or stalled MCU. |
| **02** | **Powered USB overvoltage** | With the pass FETs already on, the 6.0 V source-fault model reached 5.824 V at a PHY rated 5.80 V absolute maximum. Define the required source fault and choose protection that stays within limits across turn-off and recovery. |
| **03** | **USB without a battery** | One low-line retention screen gives at most 0.285 mA at 3.3 V. Reconcile the loads with suspend current and wake timing. Check the FUSB GPIO open-drain status lines at their actual pull-up and fanout. |
| 04 | Logic supply OR | Bound D800 insertion surge, D801 sharing and the voltage at U700. A modeled upstream 5.760 V needs at least 260 mV attenuation to respect U700's 5.5 V recommended maximum. |
| 05 | OLED supply | The 3.231 V low input already misses the bare panel VBAT minimum by 69 mV with an ideal series regulator. Qualify the exact breakout, its reset, and the panel-side I²C timing, or change the interface. |
| 06 | Haptic recovery | Provide a way to recover U1100 from a latched fault. Check its local pull-ups, rail sequencing and a stuck shared bus while preserving charger access. |
| 07 | Key scanning | Bound diode forward drop at the actual cold branch current, five simultaneous rows, driver strength, reverse leakage and settling. Normal diode reverse-voltage and connectivity checks passed. |
| 08 | RGB power | Qualify the boost converter with its reservoir, load release and local short current. U901 reset and U900 EN-low both reach 0.40 V at their stated limits, leaving zero forced-off noise margin. |
| 09 | USB attach and current grant | Bound cold attach, source-tier changes and retained state. Resolve U803 CEXT pins 6/14 against the manufacturer's ground-return guidance. Bound U801 peak current when D802/D803 discharge the gate capacitors. |
| 10 | USB data and radio bypass | Decide on USB series sites, timer-tap loading, input clamp current, local bypass and a return path before routing. |
| 11 | Footprints and controls | Disposition U200 copper/paste, J200 plated slots and SW400's dry-contact rating, throws, anchors and case labeling. |
| 12 | Charger control | R600 selects about 100 mA by default. Specify a source-qualified register sequence, readback, watchdog/reset response and safe fallback. |
| 13 | Charge-time target | Define load, pack presence, thermal conditions and CC/CV termination for a near-two-hour charge on 5 V/3 A. The target remains an estimate. |
| 14 | Detached current | Close the 50 µA travel budget at the battery across temperature and wake states. |
| 15 | Firmware pin map and RGB | Mark pad 60 occupied by HAPTIC_EN. The proposed custom 8 MHz encoding takes 2.310 ms per frame on paper. Pixel DOUT limits and firmware concurrency remain open. |
| 16 | PCB constraints | Transfer switch datums, boss, battery and RF clearances, USB geometry and net classes before routing. |
| 17 | Controller | Check crystal load with board parasitics, incoming module revision, reset configuration and probe access. |
| 18 | Power loops and shared bus | Close charger ripple/thermal/layout assumptions and remaining I²C ground, rise-time and sink-current margins. Allocate observation points. |
| 19 | Manufacturing | Check DRC, apertures, CAM, BOM/CPL rotation and assembly preview once layout exists. Recheck sourcing and the hand-fit operations. |

Start the next electrical revision on a branch. Record the topology or operating-envelope decision against each affected issue, update the native schematic, regenerate its netlist and repeat the affected calculations. Keep the Rev F evidence identifiable when saving the next review.

## Mechanical position at handoff

The chosen pack bay moved **2 mm right and 4 mm toward the spacebar**, keeping the J600 position and 42 mm harness. The service-motion model gives 2.13 mm minimum wire-to-floor clearance over its sampled poses. The assembled model includes the OLED, the WASD actuator and modeled wiring. Check the plug extraction motion before changing the board datum. [Battery options](mechanical/battery-position-options.pdf) · [J600 and harness](design/pack-harness-review.md) · [Wiring inspection model](mechanical/wiring-inspection.FCStd)

The Alpine Pass and Elevated City editions each use six PLA pieces over three Adventurer 5M beds, plus a separate steel switch plate. Nine captive M2.5 hex nuts serve the tray/stack joints. The assembly guide covers the remaining fasteners. Print orientations and clearances were studied digitally. Physical fit, print finish, cable handling and haptic feel remain unverified. [Print sets](mechanical/sculpted-cases/README.md) · [Plate files](mechanical/switch-plate/plate-fabrication.md) · [Assembly guide](mechanical/assembly-guide.pdf) · [Fastener BOM](design/mechanical-bom.csv)

## Reproduce the desk checks

Run these from the repository root. The first command checks the saved ledgers against the archived Rev F netlist. The second reproduces selected component corners.

```sh
python3 design/rev-f-electrical-audit/verify-ledgers.py
python3 design/rev-f-electrical-audit/check-corners.py
```

Export the schematic independently, run its wiring assertions, match the ledgers against that export and run the project's configured ERC. Temporary outputs preserve the archived baseline.

```sh
audit_dir="$(mktemp -d)"
kicad_cli="/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
"$kicad_cli" sch export netlist --format kicadxml -o "$audit_dir/net.xml" electronics/keyboard.kicad_sch
python3 electronics/check-netlist.py "$audit_dir/net.xml"
python3 design/rev-f-electrical-audit/verify-ledgers.py "$audit_dir/net.xml"
"$kicad_cli" sch erc --severity-all --format json --exit-code-violations -o "$audit_dir/erc.json" electronics/keyboard.kicad_sch
```

Further electrical work can build on the [USB hot-plug analysis](design/usb-input-transient.md), [powered overvoltage model](design/usb-live-ov-check.py), [charger ripple analysis](design/charger-input-ripple.md) and [system power budget](design/power-budget.md). PCB fabrication outputs, firmware, physical measurements and a current assembly quote still require their respective design stages.
