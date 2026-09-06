#!/usr/bin/env python3
"""Numeric-fingerprint channel, calibrated against the md5 ground truth.

key = read_count:base_count  (ENA's own accounting, so archive-internal and comparable)
Because submitted_md5 exists for 100% of ERR runs and ~0% of SRR/DRR, ERR-only pairs give a
labelled set on which the numeric channel's precision and recall can be MEASURED rather than
assumed. That measurement is what licenses using it on SRR/DRR runs.
"""
import sys, os, json, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from census import COLS, groups, wilson

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--numkeys", required=True)     # sorted keys_num_*.tsv
    ap.add_argument("--md5keys", required=True)     # sorted keys_md5_*.tsv
    ap.add_argument("--out", required=True)
    ap.add_argument("--dump", default=None)
    a = ap.parse_args()

    # --- md5 truth: set of unordered run pairs known byte-identical ---
    md5pairs = set(); md5runs = set()
    for key, rows in groups(a.md5keys):
        runs = sorted({r["run_accession"] for r in rows})
        md5runs |= set(runs)
        if len(runs) < 2: continue
        for i in range(len(runs)):
            for j in range(i+1, len(runs)):
                md5pairs.add((runs[i], runs[j]))

    numpairs = set(); numgroups = 0; numgroups_x = 0
    meta = {}
    dump = []
    for key, rows in groups(a.numkeys):
        runs = sorted({r["run_accession"] for r in rows})
        if len(runs) < 2: continue
        # memory guard for archive scale: only keep metadata for runs we will actually pair,
        # and never expand a runaway key (round subsample counts are shared by 100k+ runs)
        if len(runs) <= 60:
            for r in rows: meta.setdefault(r["run_accession"], r)
        numgroups += 1
        if len({r["study_accession"] for r in rows}) > 1:
            numgroups_x += 1
        if len(runs) > 60:      # runaway key (e.g. tiny/subsampled files) - record, don't expand
            dump.append(dict(key=key, n_runs=len(runs), note="oversized, pairs not expanded",
                             studies=sorted({r['study_accession'] for r in rows})[:8]))
            continue
        for i in range(len(runs)):
            for j in range(i+1, len(runs)):
                numpairs.add((runs[i], runs[j]))

    def is_err(p): return p[0].startswith("ERR") and p[1].startswith("ERR")
    # restrict to the labelled region: both runs ERR (md5 truth available for both)
    num_err  = {p for p in numpairs if is_err(p)}
    md5_err  = {p for p in md5pairs if is_err(p)}
    tp = len(num_err & md5_err)
    fp = len(num_err - md5_err)
    fn = len(md5_err - num_err)

    def xstudy(p):
        a_, b_ = meta.get(p[0]), meta.get(p[1])
        if not a_ or not b_: return None
        return a_["study_accession"] != b_["study_accession"]
    num_err_x = {p for p in num_err if xstudy(p)}
    md5_err_x = {p for p in md5_err if xstudy(p)}
    tpx = len(num_err_x & md5_err_x); fpx = len(num_err_x - md5_err_x); fnx = len(md5_err_x - num_err_x)

    res = dict(
        n_numeric_groups_multi_run=numgroups, n_numeric_groups_cross_study=numgroups_x,
        n_numeric_pairs=len(numpairs), n_md5_pairs=len(md5pairs),
        labelled_region="both runs ERR (submitted_md5 present for 100% of ERR)",
        all_pairs=dict(tp=tp, fp=fp, fn=fn,
                       precision=wilson(tp, tp+fp) if tp+fp else None,
                       recall=wilson(tp, tp+fn) if tp+fn else None),
        cross_study_pairs=dict(tp=tpx, fp=fpx, fn=fnx,
                       precision=wilson(tpx, tpx+fpx) if tpx+fpx else None,
                       recall=wilson(tpx, tpx+fnx) if tpx+fnx else None),
    )
    # a few false positives and false negatives, for inspection
    res["example_fp_cross_study"] = [
        dict(pair=p, a={k: meta[p[0]][k] for k in ("study_accession","read_count","base_count","center_name","library_strategy")},
                 b={k: meta[p[1]][k] for k in ("study_accession","read_count","base_count","center_name","library_strategy")})
        for p in list(num_err_x - md5_err_x)[:8]]
    res["example_fn_cross_study"] = [
        dict(pair=p, a={k: meta[p[0]][k] for k in ("study_accession","read_count","base_count","center_name")} if p[0] in meta else None,
                 b={k: meta[p[1]][k] for k in ("study_accession","read_count","base_count","center_name")} if p[1] in meta else None)
        for p in list(md5_err_x - num_err_x)[:8]]
    res["oversized_numeric_keys"] = dump[:20]
    res["n_oversized_numeric_keys"] = len(dump)
    json.dump(res, open(a.out, "w"), indent=2, default=str)
    print(json.dumps(res, indent=2, default=str)[:5000])

if __name__ == "__main__":
    main()
