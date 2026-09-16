#!/usr/bin/env python3
"""Measure the false-positive rate of the composition channel directly.

The composition key (total_spots + exact A/C/G/T/N) is not a cryptographic hash, so its
precision is an empirical question. Against the ERR region, where `submitted_md5` gives ground
truth, composition-identical cross-study groups split into:

  CONFIRMED      also share a submitted_md5  -> certainly the same bytes
  NOT CONFIRMED  do not                      -> EITHER the same reads uploaded as a different
                                                file (different wrapper, different name, tar vs
                                                SFF, re-compressed) OR a genuine collision.

Only reads can tell those apart. This script takes a seeded random sample of NOT CONFIRMED
groups, downloads the first N reads of two runs from each, and compares the sequences with
headers ignored. The resulting refutation rate is the composition channel's measured
false-positive rate, and is reported whatever it turns out to be.
"""
import argparse, json, os, sys, random, hashlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compare_reads import fastq_urls, first_seqs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def seqs_md5(acc, n):
    urls = fastq_urls(acc)
    if not urls: return None, "no fastq"
    s = first_seqs(urls[0], n=n)
    if not s: return None, "no reads"
    return hashlib.md5("\n".join(s[:n]).encode()).hexdigest(), f"{len(s[:n])} reads"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", default=os.path.join(ROOT, "out", "composition_census.json"))
    ap.add_argument("--md5keys", default=os.path.join(ROOT, "out", "keys_md5_all.sorted.tsv"))
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "composition_collision_test.json"))
    ap.add_argument("--n", type=int, default=40, help="groups to test")
    ap.add_argument("--reads", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260915)
    a = ap.parse_args()

    groups = json.load(open(a.census))["cross_study_groups"]
    err = [g for g in groups if set(g["prefixes"]) == {"ERR"}]
    want = {r for g in err for r in g["runs"]}
    md5_of = collections.defaultdict(set)
    for line in open(a.md5keys):
        p = line.rstrip("\n").split("\t")
        if len(p) < 2: continue
        for tok in p[1:]:
            if tok in want: md5_of[tok].add(p[0])
    notconf = []
    for g in err:
        sets = [md5_of.get(r) for r in g["runs"]]
        if any(not s for s in sets): continue
        if not set.intersection(*sets): notconf.append(g)
    print(f"ERR-only cross-study composition groups: {len(err)}; not confirmed by submitted_md5: {len(notconf)}",
          file=sys.stderr)

    rnd = random.Random(a.seed)
    sample = rnd.sample(notconf, min(a.n, len(notconf)))
    rows = []
    for i, g in enumerate(sample):
        A, B = g["runs"][0], g["runs"][1]
        ha, na = seqs_md5(A, a.reads)
        hb, nb = seqs_md5(B, a.reads)
        verdict = ("IDENTICAL" if (ha and hb and ha == hb) else
                   "DIFFERENT" if (ha and hb) else "UNTESTABLE")
        rows.append(dict(runs=[A, B], studies=g["studies"], spots=g["total_spots"],
                         organisms=g["organisms"], md5_a=ha, md5_b=hb, note_a=na, note_b=nb,
                         verdict=verdict))
        print(f"[{i+1}/{len(sample)}] {A} {B} {verdict} ({na} / {nb})", file=sys.stderr)
        json.dump({"rows": rows}, open(a.out, "w"), indent=1)

    c = collections.Counter(r["verdict"] for r in rows)
    testable = c["IDENTICAL"] + c["DIFFERENT"]
    fp_rate = c["DIFFERENT"] / testable if testable else None
    summary = dict(n_err_cross_study=len(err), n_not_confirmed=len(notconf), sampled=len(rows),
                   identical=c["IDENTICAL"], different=c["DIFFERENT"], untestable=c["UNTESTABLE"],
                   measured_false_positive_rate_among_not_confirmed=fp_rate, seed=a.seed, reads=a.reads)
    json.dump({"summary": summary, "rows": rows}, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))

if __name__ == "__main__":
    main()
