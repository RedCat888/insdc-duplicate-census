#!/usr/bin/env python3
"""For each duplication event, find papers that cite each of its studies (Europe PMC
ACCESSION_ID index), and flag events whose studies are cited by DIFFERENT papers -
i.e. the same bytes underpin more than one publication."""
import sys, os, json, time, argparse, urllib.request, urllib.parse, collections

CACHE = {}
def epmc_acc(acc, retries=3):
    if acc in CACHE: return CACHE[acc]
    q = urllib.parse.urlencode({"query": f'ACCESSION_ID:"{acc}"', "format": "json",
                                "pageSize": "25", "resultType": "lite"})
    u = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + q
    for k in range(retries):
        try:
            with urllib.request.urlopen(u, timeout=60) as r:
                d = json.load(r)
            out = [dict(pmid=x.get("pmid"), doi=x.get("doi"), year=x.get("pubYear"),
                        title=(x.get("title") or "")[:180],
                        journal=x.get("journalTitle"))
                   for x in d.get("resultList", {}).get("result", [])]
            CACHE[acc] = out
            return out
        except Exception:
            time.sleep(1.5*(k+1))
    CACHE[acc] = []
    return []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-events", type=int, default=100000)
    ap.add_argument("--sleep", type=float, default=0.15)
    a = ap.parse_args()
    events = [json.loads(l) for l in open(a.events)][:a.max_events]
    res = []
    for i, e in enumerate(events):
        per = {}
        for s in e["studies"]:
            per[s] = epmc_acc(s); time.sleep(a.sleep)
        allp = {p["pmid"] for v in per.values() for p in v if p.get("pmid")}
        cited = {s: {p["pmid"] for p in v if p.get("pmid")} for s, v in per.items()}
        with_pub = [s for s in cited if cited[s]]
        distinct = len(allp)
        # do two studies in this event have disjoint, non-empty paper sets?
        disjoint = False
        ws = [s for s in with_pub]
        for x in range(len(ws)):
            for y in range(x+1, len(ws)):
                if cited[ws[x]] and cited[ws[y]] and not (cited[ws[x]] & cited[ws[y]]):
                    disjoint = True
        res.append(dict(studies=e["studies"], n_studies=e["n_studies"],
                        n_shared_files=e["n_shared_files"], n_runs=e["n_runs"],
                        n_centers_norm=e["n_centers_norm"], taxa=e.get("taxa"),
                        date_first=e.get("date_first"), date_last=e.get("date_last"),
                        studies_with_indexed_paper=len(with_pub),
                        distinct_pmids=distinct,
                        different_papers=disjoint,
                        papers=per))
        if (i+1) % 25 == 0:
            print(f"  {i+1}/{len(events)} events linked", file=sys.stderr)
    json.dump(res, open(a.out, "w"), indent=1)
    n_any = sum(1 for r in res if r["studies_with_indexed_paper"] > 0)
    n_ge2 = sum(1 for r in res if r["studies_with_indexed_paper"] >= 2)
    n_diff = sum(1 for r in res if r["different_papers"])
    print(json.dumps(dict(events=len(res), events_with_any_indexed_paper=n_any,
                          events_with_2plus_studies_having_papers=n_ge2,
                          events_where_studies_cited_by_different_papers=n_diff), indent=2))

if __name__ == "__main__":
    main()
