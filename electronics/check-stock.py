#!/usr/bin/env python3
"""Check exact LCSC/JLCPCB part codes or audit a complete KiCad XML netlist."""

import argparse
import csv
import json
import math
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.error import URLError
from urllib.request import Request, urlopen


def read(url):
    request = Request(
        url, headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"}
    )
    with urlopen(request, timeout=12) as response:
        return response.read().decode("utf-8")


def count(record, key):
    value = record[key]
    if type(value) is not int or value < 0:
        raise ValueError(f"Invalid quantity for {key}: {value}")
    return value


def lcsc_info(code):
    url = f"https://www.lcsc.com/product-image/{code}.html?whichImg=0&obs={time.time_ns()}"
    page = read(url)
    for attrs, body in re.findall(r"<script\b([^>]*)>(.*?)</script>", page, re.DOTALL):
        if 'id="__NEXT_DATA__"' in attrs:
            item = json.loads(body)["props"]["pageProps"]["detail"]
            if item and item.get("productCode") == code:
                return {
                    "mpn": item["productModel"],
                    "stock": count(item, "stockNumber"),
                }
    raise ValueError("Exact LCSC part record missing")


def jlc_info(code):
    endpoint = "https://cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail"
    data = json.loads(read(f"{endpoint}?componentCode={code}"))["data"]
    item = data.get("data", data)
    if item.get("componentCode") != code:
        raise ValueError("Exact JLCPCB part record missing")
    stock = count(item, "stockCount")
    threshold = count(item, "canPresaleNumber")
    # JLC's parts library uses this quantity to switch from its in-stock
    # purchase option to preorder at the requested quantity.
    available = threshold
    if item.get("isBuyComponent") == "0" and item.get("allowPostFlag") is True:
        available = count(item, "overseasStockCount")
    return {
        "mpn": item["componentModelEn"],
        "manufacturer": item["componentBrandEn"],
        "stock": stock,
        "in_stock_limit": available,
        "preorder": threshold,
        "preorder_min": count(item, "preMinPurchaseNum"),
        "min_qty": count(item, "leastNumber"),
        "min_placement": count(item, "leastPatchNumber"),
        "loss_qty": count(item, "lossNumber"),
        "loss_ratio": item["largeUsageLossRatio"],
        "library": item["componentLibraryType"],
        "process": item["assemblyProcess"],
        "prototype": item["assemblyMode"],
        "batch": item["assemblyModeBatch"],
        "tier": {
            0: "Economic and Standard",
            1: "Economic only",
            2: "Standard only",
        }.get(item.get("componentProductType"), "Unknown"),
        "listed_status": item.get("componentStatus"),
        "package": item["componentSpecificationEn"],
        "xray": item["xrayFlag"],
        "review": item["needAuditFlag"],
    }


def lookup(code):
    now = datetime.now(timezone.utc)
    result = {"checked_utc": now.isoformat(timespec="seconds"), "part_code": code}
    for supplier, fetch in (("lcsc", lcsc_info), ("jlcpcb", jlc_info)):
        for attempt in range(3):
            try:
                result[supplier] = fetch(code)
                break
            except (
                OSError,
                URLError,
                ValueError,
                KeyError,
                TypeError,
                AttributeError,
            ) as exc:
                result[supplier] = {"error": str(exc)}
                if attempt < 2:
                    time.sleep(0.5 * (attempt + 1))
    return result


def part_groups(path):
    groups = defaultdict(list)
    refs = set()
    for part in ET.parse(path).findall("./components/comp"):
        ref = part.attrib["ref"]
        if ref in refs:
            raise ValueError(f"Duplicate part reference {ref}")
        refs.add(ref)
        fields = {f.get("name"): f.text or "" for f in part.findall("fields/field")}
        flags = {f.get("name") for f in part.findall("property")}
        assembly = fields.get("Assembly", "").lower()
        code = fields.get("LCSC", "")
        if "dnp" in flags or "exclude_from_bom" in flags:
            route = "DNP" if "dnp" in flags else "Excluded from BOM"
        elif "hand solder" in assembly or "through-hole" in assembly:
            route = "Hand fit"
        else:
            route = "Factory"
        identity = code or fields.get("MPN") or part.findtext("value") or ref
        groups[(route, code, identity)].append(
            (ref, fields.get("MPN", ""), part.findtext("footprint", ""))
        )
    if not refs:
        raise ValueError("No components in KiCad XML export")
    return groups


def audit(groups, suppliers, boards):
    for (route, code, _), parts in sorted(groups.items()):
        record = suppliers.get(code, {})
        jlc, lcsc = record.get("jlcpcb", {}), record.get("lcsc", {})
        checks = []
        refs = sorted(
            (p[0] for p in parts),
            key=lambda v: (v.rstrip("0123456789"), int(re.search(r"\d+$", v)[0])),
        )
        mpns = sorted({p[1] for p in parts if p[1]})
        footprints = sorted({p[2] for p in parts})
        fitted = len(parts) if route in ("Factory", "Hand fit") else 0
        placed = fitted * boards
        screened = None
        if code and fitted:
            if not jlc or not lcsc or "error" in jlc or "error" in lcsc:
                checks.append("LOOKUP FAILED")
            else:
                if jlc["mpn"] != lcsc["mpn"] or any(m != jlc["mpn"] for m in mpns):
                    checks.append("MPN MISMATCH")
                if not all(footprints):
                    checks.append("MISSING FOOTPRINT")
                screened = max(
                    jlc["min_qty"],
                    jlc["min_placement"],
                    placed
                    + max(jlc["loss_qty"], math.ceil(placed * jlc["loss_ratio"])),
                )
                if lcsc["stock"] < placed:
                    checks.append("LOW LCSC STOCK")
                if min(jlc["stock"], jlc["in_stock_limit"]) < screened:
                    checks.append("LOW JLC STOCK")
                if jlc["listed_status"] != "yes" or jlc["tier"] == "Unknown":
                    checks.append("CHECK LISTING")
                if route == "Factory" and (
                    jlc["process"] not in ("SMT", "THT") or not jlc["prototype"]
                ):
                    checks.append("CHECK ASSEMBLY")
        elif route == "Factory":
            checks.append("MISSING LCSC CODE")
        if not checks:
            checks.append("Stock covers run" if code and fitted else route)
        yield {
            "route": route,
            "refs": " ".join(refs),
            "fitted_per_board": fitted,
            "boards": boards,
            "placed_quantity": placed,
            "screened_factory_quantity": screened,
            "LCSC": code,
            "schematic_mpn": " | ".join(mpns),
            "without_mpn_field": sum(not p[1] for p in parts),
            "footprints": " | ".join(footprints),
            "lcsc_mpn": lcsc.get("mpn"),
            "lcsc_retail": lcsc.get("stock"),
            "jlc_mpn": jlc.get("mpn"),
            "jlc_brand": jlc.get("manufacturer"),
            "jlc_package": jlc.get("package"),
            "jlc_display_stock": jlc.get("stock"),
            "jlc_in_stock_limit": jlc.get("in_stock_limit"),
            "jlc_canPresaleNumber": jlc.get("preorder"),
            "jlc_preorder_min": jlc.get("preorder_min"),
            "jlc_min_qty": jlc.get("min_qty"),
            "jlc_min_placement": jlc.get("min_placement"),
            "jlc_loss_qty": jlc.get("loss_qty"),
            "jlc_large_usage_loss_ratio": jlc.get("loss_ratio"),
            "jlc_process": jlc.get("process"),
            "jlc_prototype": jlc.get("prototype"),
            "jlc_batch": jlc.get("batch"),
            "jlc_tier": jlc.get("tier"),
            "jlc_library": jlc.get("library"),
            "jlc_xray": jlc.get("xray"),
            "jlc_review": jlc.get("review"),
            "status": " | ".join(checks),
            "error": " | ".join(x["error"] for x in [lcsc, jlc] if "error" in x),
            "checked_utc": record.get("checked_utc"),
            "lcsc_url": f"https://www.lcsc.com/product-detail/{code}.html"
            if code
            else "",
            "jlc_url": f"https://jlcpcb.com/partdetail/{code}" if code else "",
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("codes", nargs="*", metavar="CNUMBER")
    parser.add_argument(
        "--netlist", help="Read all parts from a KiCad XML netlist and print CSV."
    )
    parser.add_argument(
        "--boards",
        type=int,
        default=1,
        help="Number of boards for the inventory screen.",
    )
    args = parser.parse_args()
    if args.boards < 1 or bool(args.netlist) == bool(args.codes):
        parser.error("Use exact C codes or one --netlist, and a positive board count.")
    groups = part_groups(args.netlist) if args.netlist else {}
    codes = (
        sorted(
            {
                code
                for route, code, _ in groups
                if code and route in ("Factory", "Hand fit")
            }
        )
        if groups
        else args.codes
    )
    if any(not re.fullmatch(r"C[1-9][0-9]{0,11}", code) for code in codes):
        parser.error("Supply valid LCSC codes, such as C5296739.")
    with ThreadPoolExecutor(max_workers=4) as pool:
        suppliers = {record["part_code"]: record for record in pool.map(lookup, codes)}
    if args.netlist:
        rows = list(audit(groups, suppliers, args.boards))
        writer = csv.DictWriter(sys.stdout, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        return int(
            any(
                row["status"]
                not in {"Stock covers run", "Hand fit", "Excluded from BOM", "DNP"}
                for row in rows
            )
        )
    for code in codes:
        print(json.dumps(suppliers[code]))
    return int(
        any(
            "error" in rec[supplier]
            for rec in suppliers.values()
            for supplier in ("lcsc", "jlcpcb")
        )
    )


if __name__ == "__main__":
    sys.exit(main())
