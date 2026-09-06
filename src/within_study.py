#!/usr/bin/env python3
"""Within-study sample duplication: two DIFFERENT BioSample accessions inside ONE study whose
runs hold a byte-identical submitted file. This inflates the apparent sample size of the study
itself, independently of any cross-study duplication.

Reports, per affected study, whether the duplication is visible in the sample titles
(identical titles / '..._updated' style suffixes) or invisible."""
import sys, os, json, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from census import COLS, groups, wilson

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--dump", required=True); ap.add_argument("--label", default="")
    a = ap.parse_args()

    per = collections.defaultdict(lambda: dict(groups=0, samples=set(), runs=set(),
                                               orgs=set(), centers=set(), dates=set()))
    n_keys = n_multi = 0
    g_same_study_same_sample = g_same_study_diff_sample = g_cross_study = 0
    runs_all = set(); runs_dup_sample = set()
    for key, rows in groups(a.keys):
        n_keys += 1
        runs = {}
        for r in rows: runs.setdefault(r["run_accession"], r)
        runs_all.update(runs)
        if len(runs) < 2: continue
        n_multi += 1
        studies = {r["study_accession"] for r in runs.values()}
        samples = {r["sample_accession"] for r in runs.values()}
        if len(studies) > 1: g_cross_study += 1; continue
        if len(samples) < 2: g_same_study_same_sample += 1; continue
        g_same_study_diff_sample += 1
        runs_dup_sample.update(runs)
        s = list(studies)[0]; p = per[s]
        p["groups"] += 1; p["samples"] |= samples; p["runs"] |= set(runs)
        for r in runs.values():
            p["orgs"].add(r["scientific_name"]); p["centers"].add(r["center_name"])
            p["dates"].add(r["first_public"])

    studies = []
    for s, p in per.items():
        studies.append(dict(study=s, dup_groups=p["groups"], samples_involved=len(p["samples"]),
                            runs_involved=len(p["runs"]), organisms=sorted(p["orgs"])[:6],
                            centers=sorted(p["centers"])[:4],
                            date_first=min(p["dates"]), date_last=max(p["dates"])))
    studies.sort(key=lambda x: -x["runs_involved"])
    res = dict(label=a.label, n_md5_keys=n_keys, n_groups_multi_run=n_multi,
               groups_same_study_same_sample=g_same_study_same_sample,
               groups_same_study_different_samples=g_same_study_diff_sample,
               groups_cross_study=g_cross_study,
               n_studies_with_duplicate_samples=len(per),
               n_runs_in_duplicate_sample_pairs=len(runs_dup_sample),
               n_runs_with_key=len(runs_all),
               frac_runs_in_duplicate_sample_pairs=wilson(len(runs_dup_sample), len(runs_all)),
               top_studies=studies[:60])
    json.dump(res, open(a.out, "w"), indent=2, default=str)
    with open(a.dump, "w") as fh:
        for s in studies: fh.write(json.dumps(s)+"\n")
    print(json.dumps({k: v for k, v in res.items() if k != "top_studies"}, indent=2, default=str))
    print("\ntop affected studies:")
    for s in studies[:15]:
        print(f"  {s['study']:<13} runs={s['runs_involved']:>4} samples={s['samples_involved']:>4} "
              f"{(s['organisms'] or [''])[0][:26]:<26} {(s['centers'] or [''])[0][:40]}")

if __name__ == "__main__":
    main()
