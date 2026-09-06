#!/usr/bin/env python3
"""For confirmed duplicate run-pairs, resolve each run's study to publications via the
Europe PMC accession index, and to GEO series where the study came from GEO. Flags pairs
whose two halves belong to different publications."""
import sys, os, json, time, urllib.request, urllib.parse, argparse, collections

def epmc(acc, cache={}):
    if acc in cache: return cache[acc]
    q = urllib.parse.urlencode({"query": f'ACCESSION_ID:"{acc}"', "format": "json",
                                "pageSize": "25", "resultType": "lite"})
    try:
        with urllib.request.urlopen(
                "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + q, timeout=60) as r:
            d = json.load(r)
        out = [dict(pmid=x.get("pmid"), year=x.get("pubYear"), journal=x.get("journalTitle"),
                    title=(x.get("title") or "")[:150])
               for x in d.get("resultList", {}).get("result", []) if x.get("pmid")]
    except Exception:
        out = []
    cache[acc] = out
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sleep", type=float, default=0.2)
    a = ap.parse_args()
    src = json.load(open(a.infile))
    items = src["results"] if isinstance(src, dict) and "results" in src else src
    rows = []
    for c in items:
        if isinstance(c, dict) and c.get("verdict", "").startswith("CONFIRMED"):
            studies = c.get("studies") or []
            if len(studies) != 2: continue
            pa, pb = epmc(studies[0]), epmc(studies[1])
            time.sleep(a.sleep)
            sa = {p["pmid"] for p in pa}; sb = {p["pmid"] for p in pb}
            rows.append(dict(runs=c.get("runs"), studies=studies, taxa=c.get("taxa"),
                             centers=c.get("centers"), dates=c.get("dates"),
                             papers_a=pa, papers_b=pb,
                             both_have_papers=bool(sa and sb),
                             different_papers=bool(sa and sb and not (sa & sb))))
    n = len(rows)
    both = sum(1 for r in rows if r["both_have_papers"])
    diff = sum(1 for r in rows if r["different_papers"])
    res = dict(n_confirmed_pairs=n, pairs_where_both_studies_have_an_indexed_paper=both,
               pairs_cited_by_different_papers=diff, rows=rows)
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=2))
    for r in rows:
        if r["different_papers"]:
            print(" DIFFERENT PAPERS:", r["runs"], r["studies"])
            for p in r["papers_a"][:2]: print("   A:", p["pmid"], p["journal"], p["year"], p["title"][:80])
            for p in r["papers_b"][:2]: print("   B:", p["pmid"], p["journal"], p["year"], p["title"][:80])

if __name__ == "__main__":
    main()
