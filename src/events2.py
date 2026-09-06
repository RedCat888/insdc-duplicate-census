#!/usr/bin/env python3
"""Enriched event-level census: adds redundant bytes, per-taxon/per-year breakdowns,
hub diagnostics, and the study-label shuffle null."""
import sys, os, json, argparse, collections, random, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from census import COLS, groups, wilson
from events import UF, distinct_centers, norm_center

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", required=True); ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--dump", required=True)
    ap.add_argument("--shuffle", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20260906)
    a = ap.parse_args()

    uf = UF()
    edges = collections.Counter()
    studymeta = collections.defaultdict(lambda: dict(centers=set(), taxa=set(), sci=set(),
                        strat=set(), broker=set(), plat=set(), dates=set(), runs=set()))
    dupbytes = 0          # bytes stored redundantly (all copies beyond the first)
    totbytes = 0
    n_keys = n_multi = n_x = n_samesub = 0
    runs_seen = set(); runs_dup = set(); runs_x = set()
    grp_sizes = []
    # for the shuffle null
    all_groups_studies = []      # list of list-of-run for multi-run groups
    run2study = {}

    for key, rows in groups(a.keys):
        n_keys += 1
        runs = sorted({r["run_accession"] for r in rows})
        runs_seen.update(runs)
        for r in rows:
            run2study[r["run_accession"]] = r["study_accession"]
            try: 
                b = int(r["_extra"][0]) if r["_extra"] and r["_extra"][0].isdigit() else 0
            except Exception: b = 0
            r["_b"] = b
        if len(runs) < 2:
            continue
        n_multi += 1; runs_dup.update(runs); grp_sizes.append(len(runs))
        all_groups_studies.append(runs)
        # redundant bytes: (#copies - 1) * size
        sz = max((r["_b"] for r in rows), default=0)
        dupbytes += sz * (len(runs) - 1); totbytes += sz * len(runs)
        studies = {r["study_accession"] for r in rows}
        if len(studies) < 2: continue
        subs = {r["submission_accession"] for r in rows if r["submission_accession"]}
        if subs and len(subs) <= 1:
            n_samesub += 1; continue
        n_x += 1; runs_x.update(runs)
        for r in rows:
            s = r["study_accession"]; si = studymeta[s]
            si["centers"].add(r["center_name"]); si["taxa"].add(r["tax_id"])
            si["sci"].add(r["scientific_name"]); si["strat"].add(r["library_strategy"])
            si["broker"].add(r["broker_name"]); si["plat"].add(r["instrument_platform"])
            si["dates"].add(r["first_public"]); si["runs"].add(r["run_accession"])
        sl = sorted(studies)
        for i in range(len(sl)):
            for j in range(i+1, len(sl)):
                uf.union(sl[i], sl[j]); edges[frozenset((sl[i], sl[j]))] += 1

    comps = collections.defaultdict(set)
    for s in studymeta: comps[uf.find(s)].add(s)
    events = []
    for root, studies in comps.items():
        agg = collections.defaultdict(set)
        for s in studies:
            for k, v in studymeta[s].items(): agg[k] |= v
        nfiles = sum(v for k, v in edges.items() if k & studies)
        d = sorted(agg["dates"])
        events.append(dict(studies=sorted(studies), n_studies=len(studies),
            n_runs=len(agg["runs"]), n_shared_files=nfiles,
            centers=sorted(agg["centers"]), n_centers_norm=distinct_centers(agg["centers"]),
            taxa=sorted(agg["taxa"]), scientific_names=sorted(agg["sci"]),
            strategies=sorted(agg["strat"]), brokers=sorted(agg["broker"]),
            platforms=sorted(agg["plat"]), date_first=d[0] if d else None,
            date_last=d[-1] if d else None, runs=sorted(agg["runs"])[:60]))
    events.sort(key=lambda e: -e["n_shared_files"])

    # ---- shuffle null: reassign runs to studies at random, study sizes preserved ----
    rng = random.Random(a.seed)
    study_of = list(run2study.values()); runs_list = list(run2study.keys())
    obs_x = sum(1 for runs in all_groups_studies if len({run2study[r] for r in runs}) > 1)
    null_x = []
    for _ in range(a.shuffle):
        perm = study_of[:]; rng.shuffle(perm)
        m = dict(zip(runs_list, perm))
        null_x.append(sum(1 for runs in all_groups_studies if len({m[r] for r in runs}) > 1))

    yr = collections.Counter(e["date_last"][:4] for e in events if e["date_last"])
    tx = collections.Counter()
    for e in events:
        for n in e["scientific_names"]: tx[n] += 1

    n_ev = len(events)
    res = dict(label=a.label, n_runs_with_key=len(runs_seen), n_md5_keys=n_keys,
        n_groups_multi_run=n_multi, n_groups_cross_study=n_x,
        n_groups_same_submission_dropped=n_samesub,
        n_runs_in_dup_group=len(runs_dup), n_runs_in_cross_study_event=len(runs_x),
        frac_runs_in_dup_group=wilson(len(runs_dup), len(runs_seen)),
        frac_runs_in_cross_study_event=wilson(len(runs_x), len(runs_seen)),
        redundant_bytes=dupbytes, redundant_TB=round(dupbytes/1e12, 3),
        bytes_in_dup_groups_TB=round(totbytes/1e12, 3),
        n_events=n_ev, n_studies_involved=len(studymeta),
        events_cross_center=sum(1 for e in events if e["n_centers_norm"] > 1),
        events_cross_taxon=sum(1 for e in events if len(e["taxa"]) > 1),
        events_cross_strategy=sum(1 for e in events if len(e["strategies"]) > 1),
        events_cross_platform=sum(1 for e in events if len(e["platforms"]) > 1),
        largest_event_studies=max((e["n_studies"] for e in events), default=0),
        largest_event_files=max((e["n_shared_files"] for e in events), default=0),
        event_size_hist=dict(collections.Counter(min(e["n_studies"], 10) for e in events)),
        group_size_hist=dict(collections.Counter(min(g, 10) for g in grp_sizes)),
        shuffle_null=dict(observed_cross_study_groups=obs_x, null_draws=null_x,
                          null_mean=sum(null_x)/len(null_x) if null_x else None,
                          n_multi_run_groups=n_multi),
        events_by_year_of_last_deposit=dict(sorted(yr.items())),
        top_organisms=tx.most_common(25))
    if n_ev:
        res["frac_events_cross_center"] = wilson(res["events_cross_center"], n_ev)
        res["frac_events_cross_taxon"] = wilson(res["events_cross_taxon"], n_ev)
    json.dump(res, open(a.out, "w"), indent=2, default=str)
    with open(a.dump, "w") as fh:
        for e in events: fh.write(json.dumps(e)+"\n")
    print(json.dumps({k: v for k, v in res.items() if k not in ("top_organisms",)}, indent=2, default=str))

if __name__ == "__main__":
    main()
