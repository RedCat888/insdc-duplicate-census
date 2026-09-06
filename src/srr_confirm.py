#!/usr/bin/env python3
"""Extend the census beyond the ENA-submitted (ERR) subset.

SRR/DRR runs carry no submitted_md5, so exact duplicates cannot be found by checksum in bulk.
Instead: use the numeric channel (read_count + base_count, ENA's own accounting) as a
HIGH-RECALL / LOW-PRECISION candidate generator, then confirm each candidate EXACTLY against
NCBI's per-run content fingerprint - total_spots plus the exact A/C/G/T/N base composition,
which is derived from the reads themselves and is invariant to file format, compression and
read-header rewriting.

Measured on the ERR subset (where submitted_md5 gives ground truth), the numeric channel has
recall 0.983 [0.942,0.995] and precision 0.055 [0.046,0.065]; restricted to pairs where
base_count is NOT an exact multiple of read_count, precision was 1.000 [0.806,1.000] on 16/16.
"""
import sys, os, json, argparse, random, collections, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from census import COLS, groups, wilson
from ncbi_fingerprint import fetch, parse, composition_key

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--numkeys", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sample", type=int, default=300)
    ap.add_argument("--seed", type=int, default=20260906)
    ap.add_argument("--require-nonmultiple", action="store_true")
    ap.add_argument("--min-reads", type=int, default=1000)
    ap.add_argument("--sleep", type=float, default=0.34)
    ap.add_argument("--max-group", type=int, default=40)
    a = ap.parse_args()

    cands = []
    n_groups = n_groups_x = 0
    for key, rows in groups(a.numkeys):
        runs = {}
        for r in rows: runs.setdefault(r["run_accession"], r)
        if len(runs) < 2: continue
        n_groups += 1
        if len({r["study_accession"] for r in rows}) < 2: continue
        n_groups_x += 1
        if len(runs) > a.max_group: continue
        rc, bc = key.split(":"); rc, bc = int(rc), int(bc)
        if rc < a.min_reads: continue
        if a.require_nonmultiple and bc % rc == 0: continue
        # only pairs with NO md5 available on either side (i.e. not ERR) - the new territory
        rl = [v for v in runs.values() if not v["run_accession"].startswith("ERR")]
        bystudy = {}
        for v in rl: bystudy.setdefault(v["study_accession"], v)
        if len(bystudy) < 2: continue
        m = list(bystudy.values())[:2]
        cands.append(dict(key=key, read_count=rc, base_count=bc,
                          runs=[m[0]["run_accession"], m[1]["run_accession"]],
                          studies=[m[0]["study_accession"], m[1]["study_accession"]],
                          centers=[m[0]["center_name"], m[1]["center_name"]],
                          taxa=[m[0]["tax_id"], m[1]["tax_id"]],
                          strategies=[m[0]["library_strategy"], m[1]["library_strategy"]],
                          dates=[m[0]["first_public"], m[1]["first_public"]]))
    print(f"numeric groups multi-run={n_groups} cross-study={n_groups_x} "
          f"non-ERR cross-study candidate pairs={len(cands)}", file=sys.stderr)

    rng = random.Random(a.seed); rng.shuffle(cands)
    sel = cands[:a.sample]
    confirmed = refuted = failed = 0; out = []
    for i, c in enumerate(sel):
        keys = {}
        for run in c["runs"]:
            d = parse(fetch(run), run); time.sleep(a.sleep)
            keys[run] = dict(comp=composition_key(d),
                             orig=[f["md5"] for f in (d or {}).get("original_files", [])],
                             spots=(d or {}).get("total_spots"),
                             alias=(d or {}).get("alias"))
        k1, k2 = (keys[c["runs"][0]]["comp"], keys[c["runs"][1]]["comp"])
        if k1 is None or k2 is None:
            verdict = "no_fingerprint"; failed += 1
        elif k1 == k2:
            verdict = "CONFIRMED_identical_composition"; confirmed += 1
        else:
            verdict = "refuted"; refuted += 1
        o = dict(c); o["ncbi"] = keys; o["verdict"] = verdict
        out.append(o)
        if (i+1) % 20 == 0:
            print(f"  {i+1}/{len(sel)}  confirmed={confirmed} refuted={refuted} failed={failed}",
                  file=sys.stderr)
    res = dict(n_candidates_total=len(cands), n_sampled=len(sel),
               confirmed=confirmed, refuted=refuted, no_fingerprint=failed,
               precision_of_numeric_channel_on_non_ERR=wilson(confirmed, confirmed+refuted)
                   if confirmed+refuted else None,
               estimated_true_pairs=(round(len(cands) * confirmed/(confirmed+refuted))
                   if confirmed+refuted else None),
               filters=dict(require_nonmultiple=a.require_nonmultiple, min_reads=a.min_reads,
                            max_group=a.max_group),
               results=out)
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "results"}, indent=2, default=str))

if __name__ == "__main__":
    main()
