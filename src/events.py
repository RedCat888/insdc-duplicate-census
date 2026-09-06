#!/usr/bin/env python3
"""Event-level duplication census (Amendment 1).

An EVENT is a connected component of the graph  nodes=studies, edges="share >=1
byte-identical submitted file".  One re-deposit of a whole study is one event, however many
files it contains.
"""
import sys, os, json, math, argparse, collections, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from census import COLS, groups, wilson

STOP = set("""university universite universidad institute institution research national center centre
for of the laboratory laboratories lab college hospital school dept department genomics genome
genomic sequencing sequence facility ltd gmbh inc llc bv sa spa co corp company group unit
academy academia faculty medical medicine science sciences technology technologies and
center. cnrs""".split())
def norm_center(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    toks = {t for t in s.split() if len(t) >= 3 and t not in STOP}
    return frozenset(toks)

def distinct_centers(center_strings):
    """Conservative: cluster center strings; two are the same institution if their
    normalised token sets intersect. Returns number of clusters."""
    sets = [norm_center(c) for c in center_strings if c.strip()]
    sets = [s for s in sets if s]
    clusters = []
    for s in sets:
        hit = None
        for i, c in enumerate(clusters):
            if s & c: hit = i; break
        if hit is None: clusters.append(set(s))
        else: clusters[hit] |= s
    return max(len(clusters), 1)

class UF:
    def __init__(self): self.p = {}
    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb: self.p[ra] = rb

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", required=True); ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--dump", required=True)
    a = ap.parse_args()

    uf = UF()
    studyinfo = collections.defaultdict(lambda: dict(centers=set(), taxa=set(), strat=set(),
                                                     broker=set(), plat=set(), dates=set(),
                                                     runs=set(), subs=set()))
    edges = collections.Counter()          # frozenset(studyA,studyB) -> n shared files
    runs_seen = set(); runs_dupgrp = set(); runs_xstudy = set()
    n_keys = n_multi = n_xstudy_groups = n_samesub = 0

    for key, rows in groups(a.keys):
        n_keys += 1
        runs = {r["run_accession"] for r in rows}
        runs_seen |= runs
        if len(runs) < 2: continue
        n_multi += 1; runs_dupgrp |= runs
        studies = {r["study_accession"] for r in rows}
        if len(studies) < 2: continue
        subs = {r["submission_accession"] for r in rows if r["submission_accession"]}
        if subs and len(subs) <= 1:
            n_samesub += 1; continue
        n_xstudy_groups += 1
        runs_xstudy |= runs
        for r in rows:
            s = r["study_accession"]; si = studyinfo[s]
            si["centers"].add(r["center_name"]); si["taxa"].add(r["tax_id"])
            si["strat"].add(r["library_strategy"]); si["broker"].add(r["broker_name"])
            si["plat"].add(r["instrument_platform"]); si["dates"].add(r["first_public"])
            si["runs"].add(r["run_accession"]); si["subs"].add(r["submission_accession"])
        sl = sorted(studies)
        for i in range(len(sl)):
            for j in range(i+1, len(sl)):
                uf.union(sl[i], sl[j]); edges[frozenset((sl[i], sl[j]))] += 1

    comps = collections.defaultdict(set)
    for s in studyinfo: comps[uf.find(s)].add(s)

    events = []
    for root, studies in comps.items():
        cent, taxa, strat, brok, plat, dates, runs = set(), set(), set(), set(), set(), set(), set()
        for s in studies:
            si = studyinfo[s]
            cent |= si["centers"]; taxa |= si["taxa"]; strat |= si["strat"]
            brok |= si["broker"]; plat |= si["plat"]; dates |= si["dates"]; runs |= si["runs"]
        nfiles = sum(v for k, v in edges.items() if k & studies)
        d = sorted(dates)
        events.append(dict(studies=sorted(studies), n_studies=len(studies), n_runs=len(runs),
                           n_shared_files=nfiles, centers=sorted(cent),
                           n_centers_norm=distinct_centers(cent), taxa=sorted(taxa),
                           strategies=sorted(strat), brokers=sorted(brok),
                           platforms=sorted(plat), date_first=d[0], date_last=d[-1],
                           runs=sorted(runs)[:40]))
    events.sort(key=lambda e: -e["n_shared_files"])

    n_ev = len(events)
    xc = sum(1 for e in events if e["n_centers_norm"] > 1)
    xt = sum(1 for e in events if len(e["taxa"]) > 1)
    xs = sum(1 for e in events if len(e["strategies"]) > 1)
    xp = sum(1 for e in events if len(e["platforms"]) > 1)
    from datetime import date
    def dd(e):
        try:
            a_ = date(*map(int, e["date_first"].split("-"))); b_ = date(*map(int, e["date_last"].split("-")))
            return (b_-a_).days
        except Exception: return None
    gaps = sorted(g for g in (dd(e) for e in events) if g is not None)

    res = dict(label=a.label, n_runs_with_key=len(runs_seen), n_md5_keys=n_keys,
               n_groups_multi_run=n_multi, n_groups_same_submission_dropped=n_samesub,
               n_groups_cross_study_surviving=n_xstudy_groups,
               n_runs_in_dup_group=len(runs_dupgrp), n_runs_in_cross_study_event=len(runs_xstudy),
               frac_runs_in_dup_group=wilson(len(runs_dupgrp), len(runs_seen)),
               frac_runs_in_cross_study_event=wilson(len(runs_xstudy), len(runs_seen)),
               n_events=n_ev, n_studies_involved=len(studyinfo),
               events_cross_center=xc, frac_events_cross_center=wilson(xc, n_ev) if n_ev else None,
               events_cross_taxon=xt, frac_events_cross_taxon=wilson(xt, n_ev) if n_ev else None,
               events_cross_strategy=xs, events_cross_platform=xp,
               gap_days_median=(gaps[len(gaps)//2] if gaps else None),
               gap_days_max=(gaps[-1] if gaps else None),
               events_size_hist=dict(collections.Counter(min(e["n_studies"], 6) for e in events)),
               files_per_event_median=(sorted(e["n_shared_files"] for e in events)[n_ev//2] if n_ev else None),
               files_per_event_max=(max((e["n_shared_files"] for e in events), default=0)))
    json.dump(res, open(a.out, "w"), indent=2, default=str)
    with open(a.dump, "w") as fh:
        for e in events: fh.write(json.dumps(e)+"\n")
    print(json.dumps(res, indent=2, default=str))

if __name__ == "__main__":
    main()
