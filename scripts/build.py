#!/usr/bin/env python3
"""Merge data/records/*.json into the MMD catalog.

Outputs:
  data/mmd.json       - merged, de-duplicated catalog (list of records)
  data/mmd.csv        - flat summary table
  site/data/mmd.js    - catalog embedded for the static gallery (works from file://)
  site/index.html     - gallery page (loads data/mmd.js); open locally or serve via GitHub Pages
  site/mmd-gallery.html - single-file gallery fragment with data inlined, for sharing as one file

Usage: python3 scripts/build.py [--strict]
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECORDS = ROOT / "data" / "records"
REQUIRED = ["id", "title", "material_class", "material", "techniques", "references"]
CLASSES = {
    "Ti alloy", "Ni superalloy", "Steel", "Al alloy", "Mg alloy", "Cu alloy",
    "Co alloy", "Zr alloy", "Cast iron", "HEA/MPEA", "Composite", "Other",
}
RELEVANCE = {"High", "Medium", "Low"}


def norm_doi(doi):
    if not doi:
        return None
    doi = doi.strip().lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    return doi or None


def primary_key(rec):
    """Records describing the same dataset share a dataset DOI or first paper DOI."""
    da = rec.get("data_availability") or {}
    if norm_doi(da.get("doi")):
        return "data:" + norm_doi(da["doi"])
    for ref in rec.get("references") or []:
        if norm_doi(ref.get("doi")):
            return "ref:" + norm_doi(ref["doi"])
    return "id:" + rec["id"]


def merge_into(base, extra):
    """Fill gaps in `base` with values from `extra` (no overwrites)."""
    for k, v in extra.items():
        if k not in base or base[k] in (None, "", [], {}):
            base[k] = v
        elif isinstance(base[k], dict) and isinstance(v, dict):
            merge_into(base[k], v)
        elif isinstance(base[k], list) and isinstance(v, list):
            for item in v:
                if item not in base[k]:
                    base[k].append(item)
    return base


def validate(rec, src):
    problems = []
    for f in REQUIRED:
        if not rec.get(f):
            problems.append(f"missing '{f}'")
    if rec.get("material_class") not in CLASSES:
        problems.append(f"material_class '{rec.get('material_class')}' not in vocabulary")
    rel = rec.get("fatigue_initiation_relevance")
    if rel and rel not in RELEVANCE:
        problems.append(f"fatigue_initiation_relevance '{rel}' invalid")
    refs = rec.get("references") or []
    if not any(r.get("doi") or r.get("url") for r in refs) and not (rec.get("data_availability") or {}).get("doi"):
        problems.append("no reference or dataset DOI/URL")
    return [f"{src}:{rec.get('id', '?')}: {p}" for p in problems]


def flat(rec):
    mp = rec.get("mechanical_properties") or {}
    fat = rec.get("fatigue") or {}
    da = rec.get("data_availability") or {}
    acq = rec.get("acquisition") or {}
    proc = rec.get("processing") or {}
    refs = rec.get("references") or []
    return {
        "id": rec["id"],
        "title": rec.get("title"),
        "material_class": rec.get("material_class"),
        "material": rec.get("material"),
        "route": proc.get("route"),
        "techniques": "; ".join(rec.get("techniques") or []),
        "voxel_size_um": acq.get("voxel_size_um"),
        "in_situ": acq.get("in_situ"),
        "yield_MPa": mp.get("yield_strength_MPa"),
        "uts_MPa": mp.get("uts_MPa"),
        "elongation_pct": mp.get("elongation_pct"),
        "fatigue_tested": fat.get("tested"),
        "fatigue_test_type": fat.get("test_type"),
        "initiation_tracked_in_3d": fat.get("initiation_tracked_in_3d"),
        "fatigue_initiation_relevance": rec.get("fatigue_initiation_relevance"),
        "data_status": da.get("status"),
        "repository": da.get("repository"),
        "data_url": da.get("url"),
        "primary_doi": next((r.get("doi") for r in refs if r.get("doi")), None),
    }


DOWNLOADS = (
    '<br>Download the catalog: <a href="data/mmd.json">JSON</a> · <a href="data/mmd.csv">CSV</a> · '
    '<a href="https://github.com/danishabbir/MMD">source on GitHub</a>'
)


def write_pages(payload):
    tpl = (ROOT / "site" / "gallery.template.html").read_text()
    head, body = tpl.split('<div class="wrap">', 1)
    (ROOT / "site" / "index.html").write_text(
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + head + "</head>\n<body>\n"
        + '<script src="data/mmd.js"></script>\n<div class="wrap">'
        + body.replace("<!--downloads-->", DOWNLOADS) + "</body>\n</html>\n"
    )
    (ROOT / "site" / "mmd-gallery.html").write_text(
        head + "<script>window.MMD_DATA = " + payload + ";</script>\n" + '<div class="wrap">' + body
    )


def main():
    strict = "--strict" in sys.argv
    merged, order, problems = {}, [], []
    seen_ids = set()
    for path in sorted(RECORDS.glob("*.json")):
        try:
            recs = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            problems.append(f"{path.name}: invalid JSON: {e}")
            continue
        for rec in recs:
            problems += validate(rec, path.name)
            if not rec.get("id"):
                continue
            rec.setdefault("source_file", path.name)
            key = primary_key(rec)
            if key in merged:
                merge_into(merged[key], rec)
                merged[key].setdefault("merged_from", []).append(rec["id"])
                continue
            if rec["id"] in seen_ids:
                rec["id"] = f"{rec['id']}-{path.stem}"
            seen_ids.add(rec["id"])
            merged[key] = rec
            order.append(key)

    catalog = [merged[k] for k in order]
    catalog.sort(key=lambda r: (r.get("material_class") or "", r.get("material") or "", r["id"]))

    (ROOT / "data" / "mmd.json").write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    rows = [flat(r) for r in catalog]
    with open(ROOT / "data" / "mmd.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["id"])
        w.writeheader()
        w.writerows(rows)
    out = ROOT / "site" / "data"
    out.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(catalog, ensure_ascii=False).replace("</", "<\\/")
    (out / "mmd.js").write_text("window.MMD_DATA = " + payload + ";\n")
    write_pages(payload)

    print(f"{len(catalog)} records written ({sum(len(r.get('merged_from', [])) for r in catalog)} duplicates merged)")
    for p in problems:
        print("WARN", p)
    if strict and problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
