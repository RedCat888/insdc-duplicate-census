#!/usr/bin/env python3
"""Resolve a duplicate run-pair to publications through GEO.

Most SRA runs that came from GEO carry the GEO sample id in their SRA `alias`
(e.g. "GSM987821_r1"). GEO's `gds` records carry the series (GSE) and its PubMed id, which
is a far denser link than Europe PMC's accession index (3/21 pairs) - so where a pair is
GEO-derived we can say whether the same data underlies two different papers."""
import sys, os, re, json, time, urllib.request, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ncbi_fingerprint import fetch, parse

def eutils(url, retries=3):
    for k in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r: return json.load(r)
        except Exception: time.sleep(1.5*(k+1))
    return None

def gsm_info(gsm):
    d = eutils("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
               f"?db=gds&term={gsm}%5BAccession%5D&retmode=json")
    ids = (d or {}).get("esearchresult", {}).get("idlist") or []
    if not ids: return None
    s = eutils("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
               f"?db=gds&id={ids[0]}&retmode=json")
    if not s: return None
    r = s["result"][s["result"]["uids"][0]]
    return dict(gsm=gsm, gse="GSE"+str(r.get("gse")), title=(r.get("title") or "")[:140],
                pubmedids=r.get("pubmedids"), taxon=r.get("taxon"), n_samples=r.get("n_samples"))

def gsm_of(run):
    d = parse(fetch(run), run)
    al = (d or {}).get("alias") or ""
    m = re.match(r"(GSM\d+)", al)
    return m.group(1) if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="+", required=True, help="RUNA:RUNB ...")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = []
    for p in a.pairs:
        x, y = p.split(":")
        gx, gy = gsm_of(x), gsm_of(y)
        ix = gsm_info(gx) if gx else None
        iy = gsm_info(gy) if gy else None
        same_series = bool(ix and iy and ix["gse"] == iy["gse"])
        px = set(map(str, (ix or {}).get("pubmedids") or []))
        py = set(map(str, (iy or {}).get("pubmedids") or []))
        rec = dict(runs=[x, y], gsm=[gx, gy], geo=[ix, iy], same_series=same_series,
                   different_papers=bool(px and py and not (px & py)),
                   pmids=[sorted(px), sorted(py)])
        out.append(rec)
        print(f"{x}/{gx} [{(ix or {}).get('gse')}] vs {y}/{gy} [{(iy or {}).get('gse')}]  "
              f"same_series={same_series} different_papers={rec['different_papers']} pmids={rec['pmids']}")
        time.sleep(0.4)
    json.dump(out, open(a.out, "w"), indent=1)

if __name__ == "__main__":
    main()
