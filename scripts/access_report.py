#!/usr/bin/env python3
"""Report which MMD records need a data request and which cite paywalled papers.

Paper access comes from OpenAlex open-access status, cached in data/openalex_oa.json.
  closed                        -> paywalled, no legal free copy known to OpenAlex
  green                         -> paywalled at the publisher, free author/repository copy exists
  gold / hybrid / bronze / diamond -> free to read at the publisher

Usage: python3 scripts/access_report.py [--refresh]
Outputs: docs/ACCESS.md, data/access.csv
"""
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "openalex_oa.json"
NON_PAPER = {"dataset", "data-paper"}


def norm(doi):
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", doi.strip(), flags=re.I).lower()


def lookup(doi):
    url = ("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi)
           + "?select=doi,open_access,primary_location,type")
    j = json.load(urllib.request.urlopen(url, timeout=30))
    oa = j.get("open_access") or {}
    src = (j.get("primary_location") or {}).get("source") or {}
    return {"is_oa": oa.get("is_oa"), "oa_status": oa.get("oa_status"), "oa_url": oa.get("oa_url"),
            "venue": src.get("display_name"), "type": j.get("type")}


def load_cache(catalog, refresh):
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    dois = {norm(x["doi"]) for r in catalog for x in r.get("references") or [] if x.get("doi")}
    for d in sorted(dois):
        if refresh or d not in cache or "error" in cache[d]:
            try:
                cache[d] = lookup(d)
            except Exception as e:  # network errors are recorded, not fatal
                cache[d] = {"error": str(e)[:100]}
            time.sleep(0.12)
    CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True) + "\n")
    return cache


def paper_access(rec, cache):
    """Best open-access status across the record's papers (not dataset DOIs)."""
    papers = []
    for ref in rec.get("references") or []:
        if not ref.get("doi"):
            continue
        info = cache.get(norm(ref["doi"]), {})
        if info.get("type") in NON_PAPER:
            continue
        papers.append((norm(ref["doi"]), info))
    if not papers:
        return "no paper DOI", None, None
    rank = {"gold": 0, "diamond": 0, "hybrid": 1, "bronze": 2, "green": 3, "closed": 4}
    doi, info = min(papers, key=lambda p: rank.get(p[1].get("oa_status"), 5))
    status = info.get("oa_status") or "unknown"
    if status == "closed":
        label = "Paywalled"
    elif status == "green":
        label = "Paywalled (free copy elsewhere)"
    elif status in rank:
        label = "Free to read"
    else:
        label = "Unknown"
    return label, doi, info.get("oa_url")


def data_access(rec):
    status = (rec.get("data_availability") or {}).get("status") or ""
    if re.search(r"on request", status, re.I):
        return "On request (stated by authors)"
    if re.search(r"paper only", status, re.I):
        return "Not public: ask authors"
    if re.search(r"partial", status, re.I):
        return "Partially public: rest on request"
    if re.search(r"public", status, re.I):
        return "Public"
    return "Unknown"


def main():
    catalog = json.loads((ROOT / "data" / "mmd.json").read_text())
    cache = load_cache(catalog, "--refresh" in sys.argv)
    rows = []
    for r in catalog:
        pa, doi, free = paper_access(r, cache)
        da = r.get("data_availability") or {}
        first = next((x for x in r.get("references") or [] if x.get("doi") and norm(x["doi"]) == doi), None)
        rows.append({
            "id": r["id"], "material": r.get("material"), "material_class": r.get("material_class"),
            "title": r.get("title"), "fatigue_initiation_relevance": r.get("fatigue_initiation_relevance"),
            "data_access": data_access(r), "data_status_raw": da.get("status"),
            "data_url": da.get("url") or (("https://doi.org/" + da["doi"]) if da.get("doi") else ""),
            "paper_access": pa, "paper_doi": doi or "", "free_copy_url": free or "",
            "citation": (first or {}).get("citation", ""),
        })
    with open(ROOT / "data" / "access.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    write_markdown(rows)
    print(f"{len(rows)} records; report written to docs/ACCESS.md and data/access.csv")


REL = {"High": 0, "Medium": 1, "Low": 2}


def md_table(rows, cols):
    head = "| " + " | ".join(c[0] for c in cols) + " |\n|" + "---|" * len(cols) + "\n"
    body = "".join("| " + " | ".join(str(c[1](r)).replace("|", "/").replace("\n", " ") for c in cols) + " |\n"
                   for r in rows)
    return head + body


def doi_link(r):
    return f"[{r['paper_doi']}](https://doi.org/{r['paper_doi']})" if r["paper_doi"] else "—"


def write_markdown(rows):
    srt = lambda rs: sorted(rs, key=lambda r: (REL.get(r["fatigue_initiation_relevance"], 9), r["material_class"] or "", r["material"] or ""))
    request = srt([r for r in rows if r["data_access"] != "Public"])
    paywalled = srt([r for r in rows if r["paper_access"].startswith("Paywalled")])
    both = [r for r in request if r["paper_access"] == "Paywalled"]
    count = lambda rs, k, v: sum(1 for r in rs if r[k] == v)

    out = ["# Data and paper access\n",
           "Generated by `scripts/access_report.py` from `data/mmd.json`. Paper access is the OpenAlex "
           "open-access status of each record's cited papers (the most open one counts). Full table: "
           "`data/access.csv`.\n",
           "## Summary\n",
           f"- Records: {len(rows)}",
           f"- 3D data must be requested from authors: **{len(request)}** "
           f"({count(rows, 'data_access', 'On request (stated by authors)')} where the paper says *available on request*, "
           f"{count(rows, 'data_access', 'Not public: ask authors')} with no public data, "
           f"{count(rows, 'data_access', 'Partially public: rest on request')} partially public)",
           f"- Paper paywalled: **{len(paywalled)}** "
           f"({count(rows, 'paper_access', 'Paywalled')} with no free copy, "
           f"{count(rows, 'paper_access', 'Paywalled (free copy elsewhere)')} with a free author/repository copy)",
           f"- Both paywalled paper and no public data: **{len(both)}**\n"]

    cols_req = [("Relevance", lambda r: r["fatigue_initiation_relevance"] or "—"),
                ("Material", lambda r: r["material"]),
                ("Study", lambda r: r["title"]),
                ("Paper", doi_link),
                ("Paper access", lambda r: r["paper_access"])]
    for label, intro in [
        ("On request (stated by authors)", "The paper or dataset page says the data are available on request."),
        ("Not public: ask authors", "No public 3D data was found. Results exist only as figures in the paper; contact the corresponding author."),
        ("Partially public: rest on request", "Some files are public; the 3D volumes or other parts are not."),
    ]:
        sub = [r for r in request if r["data_access"] == label]
        out += [f"## Data to request: {label} ({len(sub)})\n", intro + "\n", md_table(sub, cols_req)]

    cols_pw = [("Relevance", lambda r: r["fatigue_initiation_relevance"] or "—"),
               ("Material", lambda r: r["material"]),
               ("Paper", doi_link),
               ("Data", lambda r: r["data_access"]),
               ("Free copy", lambda r: f"[link]({r['free_copy_url']})" if r["free_copy_url"] else "—")]
    for label, intro in [
        ("Paywalled", "No legal free copy known to OpenAlex. Needs a subscription, interlibrary loan, or a copy from the authors."),
        ("Paywalled (free copy elsewhere)", "Paywalled at the publisher, but an accepted manuscript or preprint is free in a repository."),
    ]:
        sub = [r for r in paywalled if r["paper_access"] == label]
        out += [f"## Papers: {label} ({len(sub)})\n", intro + "\n", md_table(sub, cols_pw)]

    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "ACCESS.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
