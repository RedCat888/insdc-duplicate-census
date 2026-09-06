#!/usr/bin/env python3
"""The sharp claim: content-identical sequencing data deposited under DIFFERENT declared
biological identities.

Pairs come from two channels:
  md5     - exact, complete for ENA-submitted (ERR) runs
  numeric - read_count+base_count with base_count NOT an exact multiple of read_count
            (the high-entropy stratum; measured precision 1.00 [0.81,1.00] on the ERR
            labelled set, and 21/21 confirmed on non-ERR runs), then confirmed one by one
            against NCBI's exact A/C/G/T/N base composition.
Every reported conflict is confirmed; nothing rests on the numeric key alone.
"""
import sys, os, json, argparse, collections, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from census import COLS, groups, wilson
import taxonomy_ena as tx
from ncbi_fingerprint import fetch, parse, composition_key

BENIGN = {"same_taxid", "same_species", "refinement"}

def pairs_from_md5(path):
    for key, rows in groups(path):
        runs = {}
        for r in rows: runs.setdefault(r["run_accession"], r)
        if len(runs) < 2: continue
        bystudy = {}
        for v in runs.values(): bystudy.setdefault(v["study_accession"], v)
        if len(bystudy) < 2: continue
        vs = list(bystudy.values())
        for i in range(len(vs)):
            for j in range(i+1, len(vs)):
                yield ("md5", key, vs[i], vs[j])

def pairs_from_numeric(path, min_reads, max_group):
    for key, rows in groups(path):
        runs = {}
        for r in rows: runs.setdefault(r["run_accession"], r)
        if len(runs) < 2 or len(runs) > max_group: continue
        rc, bc = key.split(":"); rc, bc = int(rc), int(bc)
        if rc < min_reads or bc % rc == 0: continue
        bystudy = {}
        for v in runs.values(): bystudy.setdefault(v["study_accession"], v)
        if len(bystudy) < 2: continue
        vs = list(bystudy.values())
        for i in range(len(vs)):
            for j in range(i+1, len(vs)):
                yield ("numeric", key, vs[i], vs[j])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md5keys"); ap.add_argument("--numkeys")
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-reads", type=int, default=1000)
    ap.add_argument("--max-group", type=int, default=40)
    ap.add_argument("--confirm-max", type=int, default=400)
    ap.add_argument("--seed", type=int, default=20260906)
    ap.add_argument("--sleep", type=float, default=0.34)
    a = ap.parse_args()

    seen = set(); cands = []
    srcs = []
    if a.md5keys: srcs.append(pairs_from_md5(a.md5keys))
    if a.numkeys: srcs.append(pairs_from_numeric(a.numkeys, a.min_reads, a.max_group))
    for src in srcs:
        for chan, key, x, y in src:
            k = tuple(sorted((x["run_accession"], y["run_accession"])))
            if k in seen: continue
            seen.add(k)
            cands.append(dict(channel=chan, key=key,
                runs=[x["run_accession"], y["run_accession"]],
                studies=[x["study_accession"], y["study_accession"]],
                taxa=[x["tax_id"], y["tax_id"]],
                names=[x["scientific_name"], y["scientific_name"]],
                centers=[x["center_name"], y["center_name"]],
                strategies=[x["library_strategy"], y["library_strategy"]],
                dates=[x["first_public"], y["first_public"]]))
    print(f"cross-study candidate pairs: {len(cands)} "
          f"(md5 {sum(1 for c in cands if c['channel']=='md5')}, "
          f"numeric {sum(1 for c in cands if c['channel']=='numeric')})", file=sys.stderr)

    rel = collections.Counter()
    for c in cands:
        c["tax_relation"] = tx.relation(c["taxa"][0], c["taxa"][1])
        rel[c["tax_relation"]] += 1
    tx.flush()
    conflicts = [c for c in cands if c["tax_relation"] not in BENIGN and c["tax_relation"] != "unknown"]
    print(f"pairs whose two deposits declare different biological identities: {len(conflicts)}",
          file=sys.stderr)

    # IMPORTANT distinction, learned the hard way (see log/03-worklog.md):
    #   md5 channel     -> identity of a FILE. Exact by construction (128-bit + byte size).
    #                      A run may submit several files, so two runs sharing one file need
    #                      NOT be run-level duplicates. Claim = "this file sits in both studies".
    #   numeric channel -> identity of a RUN. Confirmed by NCBI run-level base composition.
    # Applying run-level composition confirmation to an md5 pair produces a spurious
    # "REFUTED" (this happened for ERR016531/ERR024102: wheat run has 2 SFFs, potato run has
    # 1, and the shared file is the potato run's whole content and the wheat run's second half).
    need = [c for c in conflicts if c["channel"] == "numeric"]
    rng = random.Random(a.seed); rng.shuffle(need)
    todo = need[:a.confirm_max]
    conf = ref = unk = 0
    for i, c in enumerate(todo):
        ks = {}
        for r in c["runs"]:
            d = parse(fetch(r), r); time.sleep(a.sleep)
            ks[r] = composition_key(d)
        v = list(ks.values())
        if any(x is None for x in v): c["confirm"] = "no_fingerprint"; unk += 1
        elif v[0] == v[1]:           c["confirm"] = "CONFIRMED"; conf += 1
        else:                        c["confirm"] = "refuted"; ref += 1
        c["ncbi_keys"] = {k: (list(x) if x else None) for k, x in ks.items()}
        if (i+1) % 25 == 0:
            print(f"  confirmed {conf} / refuted {ref} / no-fp {unk}  ({i+1}/{len(todo)})", file=sys.stderr)
    for c in conflicts:
        if c["channel"] == "md5": c["confirm"] = "EXACT_md5"

    res = dict(n_candidate_pairs=len(cands), tax_relation_counts=dict(rel),
               n_identity_conflicts=len(conflicts),
               n_numeric_conflicts=len(need), n_numeric_confirmed=conf,
               n_numeric_refuted=ref, n_numeric_no_fingerprint=unk,
               numeric_confirmation_rate=wilson(conf, conf+ref) if conf+ref else None,
               conflicts=conflicts)
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "conflicts"}, indent=2, default=str))

if __name__ == "__main__":
    main()
