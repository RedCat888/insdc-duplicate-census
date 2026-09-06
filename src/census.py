#!/usr/bin/env python3
"""Group sorted key files into duplicate groups and compute the preregistered statistics."""
import sys, os, math, json, argparse, itertools, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import SEED

COLS = ["run_accession","study_accession","secondary_study_accession","sample_accession",
        "submission_accession","tax_id","scientific_name","library_strategy",
        "instrument_platform","center_name","broker_name","first_public",
        "read_count","base_count"]

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0, 0.0)
    p = k / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (p, max(0.0, c-h), min(1.0, c+h))

def groups(path, keycol=0, metastart=1):
    """Yield (key, [rowdicts]) from a key-sorted TSV."""
    cur, buf = None, []
    with open(path) as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            k = p[keycol]
            meta = p[metastart:]
            d = dict(zip(COLS, meta[-len(COLS):]))
            d["_extra"] = meta[:len(meta)-len(COLS)]
            if k != cur:
                if cur is not None and buf: yield cur, buf
                cur, buf = k, [d]
            else:
                buf.append(d)
    if cur is not None and buf: yield cur, buf

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dump", default=None, help="write surviving groups here")
    a = ap.parse_args()

    S = collections.Counter()
    runs_in_dupgroup = set(); runs_in_xstudy = set(); runs_seen = set()
    surviving = []
    gapdist = []
    for key, rows in groups(a.keys):
        runs = {r["run_accession"] for r in rows}
        for r in runs: runs_seen.add(r)
        S["keys"] += 1
        if len(runs) < 2:
            continue
        S["groups_multi_run"] += 1
        for r in runs: runs_in_dupgroup.add(r)
        studies = {r["study_accession"] for r in rows}
        if len(studies) < 2:
            S["groups_within_study"] += 1
            continue
        S["groups_cross_study"] += 1
        for r in runs: runs_in_xstudy.add(r)
        subs = {r["submission_accession"] for r in rows if r["submission_accession"]}
        if len(subs) <= 1 and subs:
            S["groups_same_submission"] += 1
            continue
        S["groups_surviving"] += 1
        centers = {r["center_name"] for r in rows}
        taxa    = {r["tax_id"] for r in rows}
        strats  = {r["library_strategy"] for r in rows}
        plats   = {r["instrument_platform"] for r in rows}
        brokers = {r["broker_name"] for r in rows}
        if len(centers) > 1: S["surv_cross_center"] += 1
        if len(taxa)    > 1: S["surv_cross_tax"] += 1
        if len(strats)  > 1: S["surv_cross_strategy"] += 1
        if len(plats)   > 1: S["surv_cross_platform"] += 1
        dates = sorted(r["first_public"] for r in rows)
        try:
            from datetime import date
            d0 = date(*map(int, dates[0].split("-")))
            d1 = date(*map(int, dates[-1].split("-")))
            gapdist.append((d1-d0).days)
        except Exception:
            pass
        S[f"size_{min(len(runs),6)}"] += 1
        surviving.append(dict(key=key, n_runs=len(runs), n_studies=len(studies),
                              n_centers=len(centers), n_taxa=len(taxa),
                              centers=sorted(centers)[:6], taxa=sorted(taxa)[:6],
                              strategies=sorted(strats)[:6], brokers=sorted(brokers)[:4],
                              runs=sorted(runs)[:12], studies=sorted(studies)[:12],
                              dates=[dates[0], dates[-1]]))

    n_runs = len(runs_seen)
    res = dict(label=a.label, keys_file=a.keys, n_runs_with_key=n_runs, **dict(S))
    res["frac_runs_in_dup_group"] = wilson(len(runs_in_dupgroup), n_runs)
    res["frac_runs_in_cross_study_group"] = wilson(len(runs_in_xstudy), n_runs)
    res["n_runs_in_dup_group"] = len(runs_in_dupgroup)
    res["n_runs_in_cross_study_group"] = len(runs_in_xstudy)
    if S["groups_cross_study"]:
        res["frac_cross_study_surviving"] = wilson(S["groups_surviving"], S["groups_cross_study"])
    if S["groups_surviving"]:
        res["frac_surv_cross_center"] = wilson(S["surv_cross_center"], S["groups_surviving"])
        res["frac_surv_cross_tax"]    = wilson(S["surv_cross_tax"], S["groups_surviving"])
    if gapdist:
        gapdist.sort()
        res["gap_days_median"] = gapdist[len(gapdist)//2]
        res["gap_days_p90"] = gapdist[int(len(gapdist)*0.9)]
        res["gap_days_max"] = gapdist[-1]
        res["gap_days_zero_frac"] = sum(1 for g in gapdist if g == 0)/len(gapdist)
    with open(a.out, "w") as fh: json.dump(res, fh, indent=2, default=str)
    if a.dump:
        with open(a.dump, "w") as fh:
            for g in surviving: fh.write(json.dumps(g)+"\n")
    print(json.dumps(res, indent=2, default=str))

if __name__ == "__main__":
    main()
