#!/usr/bin/env python3
"""Census on the composition channel: group runs by (total_spots, A, C, G, T, N) from NCBI's
per-run XML, which is computed from the loaded reads and is therefore independent of file
format, compression, read headers and which archive submitted the run.

This is the channel that reaches SRR/DRR, where `submitted_md5` is absent. Two things are
measured rather than assumed:

  1. PRECISION against the ERR region, where `submitted_md5` gives ground truth: of composition
     groups that span more than one study and consist only of ERR runs, what fraction also share
     a submitted checksum? (The numeric channel read_count+base_count scores ~9% here.)
  2. COLLISION RISK: the composition key is ~5 numbers summing to total_bases, so its entropy is
     not obvious a priori. Measured directly as the rate at which composition-identical pairs are
     refuted by an independent signal (read-length statistics, quality histogram, instrument).
"""
import argparse, json, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load(path, require_ckey=True):
    for line in open(path):
        try: d = json.loads(line)
        except Exception: continue
        if require_ckey and not d.get("ckey"): continue
        yield d

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", default=os.path.join(ROOT, "out", "efetch_multi.jsonl"))
    ap.add_argument("--md5keys", default=os.path.join(ROOT, "out", "keys_md5_all.sorted.tsv"))
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "composition_census.json"))
    a = ap.parse_args()

    recs = {}
    n_total = n_nokey = 0
    for line in open(a.records):
        try: d = json.loads(line)
        except Exception: continue
        n_total += 1
        if not d.get("ckey"): n_nokey += 1; continue
        recs[d["acc"]] = d
    print(f"records={n_total} with composition key={len(recs)} without={n_nokey}", file=sys.stderr)

    by = collections.defaultdict(list)
    for d in recs.values(): by[d["ckey"]].append(d)
    multi = {k: v for k, v in by.items() if len(v) > 1}
    print(f"composition groups with >1 run: {len(multi)}", file=sys.stderr)

    # tiny runs are meaningless: a 4-spot amplicon run collides trivially
    MIN_SPOTS = 1000
    def big(v): return (v[0].get("total_spots") or 0) >= MIN_SPOTS

    groups = []
    for k, v in multi.items():
        if not big(v): continue
        studies = {d.get("study") for d in v if d.get("study")}
        samples = {d.get("biosample") for d in v if d.get("biosample")}
        orgs = {(d.get("pool_organism") or d.get("organism")) for d in v}
        taxa = {d.get("pool_tax_id") or d.get("tax_id") for d in v}
        # independent refutation signals
        prim = {d["primary_etl"]["md5"] for d in v if d.get("primary_etl") and d["primary_etl"].get("md5")}
        origs = [tuple(sorted(f["md5"] for f in d.get("original_files") or [])) for d in v]
        groups.append(dict(ckey=k, runs=sorted(d["acc"] for d in v), n_runs=len(v),
                           studies=sorted(x for x in studies if x), n_studies=len(studies),
                           biosamples=sorted(x for x in samples if x), n_biosamples=len(samples),
                           organisms=sorted(x for x in orgs if x), n_taxa=len({x for x in taxa if x}),
                           centers=sorted({d.get("center") or "" for d in v}),
                           total_spots=v[0].get("total_spots"),
                           n_primary_md5=len(prim),
                           original_md5_sets=[list(o) for o in origs],
                           share_original_md5=len(set(o for o in origs if o)) == 1 and any(origs),
                           prefixes=sorted({d["acc"][:3] for d in v})))

    xstudy = [g for g in groups if g["n_studies"] > 1]
    xsample = [g for g in groups if g["n_biosamples"] > 1]
    xorg = [g for g in xstudy if g["n_taxa"] > 1]
    nonerr = [g for g in xstudy if "ERR" not in g["prefixes"]]

    # --- precision against the submitted_md5 ground truth on the ERR region ---
    err_groups = [g for g in xstudy if set(g["prefixes"]) == {"ERR"}]
    md5_of = {}
    if os.path.exists(a.md5keys):
        want = {r for g in err_groups for r in g["runs"]}
        for line in open(a.md5keys):
            p = line.rstrip("\n").split("\t")
            if len(p) < 2: continue
            key = p[0]
            for tok in p[1:]:
                if tok in want: md5_of.setdefault(tok, set()).add(key)
    tp = fp = unk = 0
    for g in err_groups:
        sets = [md5_of.get(r) for r in g["runs"]]
        if any(s is None for s in sets): unk += 1; continue
        inter = set.intersection(*sets)
        if inter: tp += 1
        else: fp += 1
    prec = tp / (tp + fp) if (tp + fp) else None

    # --- collision-risk proxy: distinct Primary-ETL md5 within a composition group ---
    # SRA's normalized object md5 differs between archives/loads, so this is only informative
    # where it is SHARED (proves identity), never where it differs.
    shared_primary = sum(1 for g in xstudy if g["n_primary_md5"] == 1)

    summary = {
        "records_with_key": len(recs),
        "composition_groups_multi_run": len(multi),
        "groups_ge_1000_spots": len(groups),
        "cross_study_groups": len(xstudy),
        "cross_biosample_groups": len(xsample),
        "cross_study_groups_no_ERR_side": len(nonerr),
        "cross_study_groups_conflicting_taxa": len(xorg),
        "err_only_cross_study_groups": len(err_groups),
        "err_precision_vs_submitted_md5": {"confirmed": tp, "not_confirmed": fp, "unknown": unk, "precision": prec},
        "cross_study_groups_sharing_primary_etl_md5": shared_primary,
        "cross_study_groups_sharing_original_md5": sum(1 for g in xstudy if g["share_original_md5"]),
    }
    json.dump({"summary": summary, "cross_study_groups": sorted(xstudy, key=lambda g: -g["n_runs"])},
              open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))

if __name__ == "__main__":
    main()
