#!/usr/bin/env python3
"""Adjudicate organism-level identity conflicts with NCBI's own STAT taxonomy analysis.

NCBI runs STAT (k-mer MinHash taxonomy, Katz et al. 2021) on every SRA run, including
ENA-submitted ones it mirrors, and serves the result at
  https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/run_taxonomy?acc=<run>&cluster_name=public

For a pair of runs declared as different organisms this gives two independent facts:
  1. whether the two STAT tables are byte-identical (a third content-identity channel,
     independent of our checksums and of our composition/read comparisons), and
  2. which declared label the read content supports: for each side, the fraction of
     identified reads assigned to a taxon on the declared taxon's lineage (ancestor-or-self)
     or below it in the STAT tree.

Outputs out/stat_adjudication.json and out/stat_adjudication.tsv. STAT tables are cached
under data/stat/.
"""
import os, sys, json, time, argparse, hashlib, collections, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from taxonomy_ena import rec as tax_rec

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "data", "stat")
os.makedirs(CACHE, exist_ok=True)

def fetch_stat(acc, retries=3):
    p = os.path.join(CACHE, acc + ".json")
    if os.path.exists(p):
        try: return json.load(open(p))
        except Exception: pass
    u = f"https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/run_taxonomy?&acc={acc}&cluster_name=public"
    for k in range(retries):
        try:
            with urllib.request.urlopen(u, timeout=60) as r:
                raw = r.read()
            if not raw.strip():
                json.dump(None, open(p, "w")); return None
            d = json.loads(raw)
            d = d[0] if isinstance(d, list) and d else d
            json.dump(d, open(p, "w")); return d
        except Exception as e:
            time.sleep(2 * (k + 1))
    return None

def table_md5(d):
    return hashlib.md5(json.dumps(d["tax_table"], sort_keys=True).encode()).hexdigest()

def declared_names(tax_id):
    """Names that identify the declared taxon or its ancestors: scientific name, species
    binomial (for strain/subspecies ranks), genus, and ENA lineage names."""
    d = tax_rec(str(tax_id))
    if not d: return set(), None
    n = (d.get("scientificName") or "").strip()
    names = {n}
    toks = n.split()
    if d.get("rank") not in ("species", "genus") and len(toks) >= 2 and d.get("binomial") == "true":
        names.add(" ".join(toks[:2]))
    if d.get("binomial") == "true" and toks: names.add(toks[0])
    for x in (d.get("lineage") or "").split(";"):
        if x.strip(): names.add(x.strip())
    return names, d

def declared_names_strict(tax_id):
    """Only names at or below species: scientific name and species binomial. Excludes genus and
    lineage, so reads assigned at genus level or above count for neither side."""
    d = tax_rec(str(tax_id))
    if not d: return set()
    n = (d.get("scientificName") or "").strip(); toks = n.split()
    names = {n}
    if d.get("rank") not in ("species", "genus") and len(toks) >= 2 and d.get("binomial") == "true":
        names.add(" ".join(toks[:2]))
    if d.get("rank") in ("genus",) or (d.get("binomial") != "true"):
        return set()   # genus-level or placeholder declared taxon: no species-level claim to test
    return names

def support(d, declared_tid, strict=False):
    """Fraction of identified reads assigned to a STAT node whose ancestor-or-self chain carries
    a name identifying the declared taxon (species binomial / genus / lineage)."""
    t = d["tax_table"]; tot = d["tax_totals"]
    ident = tot.get("identified") or 0
    if not ident: return None, None
    names = declared_names_strict(declared_tid) if strict else declared_names(declared_tid)[0]
    if not names: return None, None
    by = {r["tax_id"]: r for r in t}
    chain_ok = {}
    def ok(tid):
        if tid in chain_ok: return chain_ok[tid]
        seen = set(); cur = tid; res = False
        while cur is not None and cur in by and cur not in seen:
            if by[cur]["org"] in names: res = True; break
            seen.add(cur); cur = by[cur].get("parent")
        chain_ok[tid] = res; return res
    compatible = sum(r["self_count"] for r in t if ok(r["tax_id"]))
    top = sorted([r for r in t if r.get("rank") == "species"], key=lambda r: -r["total_count"])[:3]
    return compatible / ident, [(r["org"], round(100 * r["total_count"] / ident, 1)) for r in top]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conflicts", default=os.path.join(ROOT, "out", "conflicts_all.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "stat_adjudication"))
    ap.add_argument("--extra", nargs="*", default=[], help="extra run pairs as A:B:nameA:nameB:tidA:tidB")
    a = ap.parse_args()
    c = json.load(open(a.conflicts))["conflicts"]
    benign = {"metagenome_type_conflict", "metagenome_vs_organism", "same_taxid", "refinement", "same_species", "unknown"}
    pairs = [x for x in c if x["tax_relation"] not in benign]
    for e in a.extra:
        A, B, nA, nB, tA, tB = e.split(":")
        pairs.append({"runs": [A, B], "studies": ["?", "?"], "taxa": [tA, tB], "names": [nA, nB],
                      "tax_relation": "extra", "channel": "extra", "confirm": None})
    print(f"{len(pairs)} run pairs", file=sys.stderr)
    runs = sorted({r for p in pairs for r in p["runs"]})
    stat = {}
    for i, acc in enumerate(runs):
        stat[acc] = fetch_stat(acc)
        if (i + 1) % 50 == 0: print(f"  fetched {i+1}/{len(runs)}", file=sys.stderr)
        time.sleep(0.25)
    have = sum(1 for v in stat.values() if v)
    print(f"STAT available for {have}/{len(runs)} runs", file=sys.stderr)

    rows = []
    for p in pairs:
        A, B = p["runs"]; sa, sb = stat.get(A), stat.get(B)
        row = {"runs": p["runs"], "studies": p["studies"], "names": p["names"], "taxa": p["taxa"],
               "tax_relation": p["tax_relation"], "prior_confirm": p.get("confirm"),
               "stat_available": [bool(sa), bool(sb)], "stat_identical": None,
               "support_A_by_A": None, "support_B_by_A": None, "support_A_by_B": None, "support_B_by_B": None,
               "top_species_A": None, "top_species_B": None, "verdict": None}
        if sa and sb:
            ta, tb = sa["tax_totals"], sb["tax_totals"]
            row["stat_identical"] = table_md5(sa) == table_md5(sb)
            row["stat_analysed"] = [ta.get("analysed"), tb.get("analysed")]
            row["stat_same_ref_date"] = (ta.get("last_update") or "")[:10] == (tb.get("last_update") or "")[:10]
            row["stat_same_spots"] = ta.get("analysed") == tb.get("analysed")
        # which label does each run's content support?
        try:
            if sa:
                row["support_A_by_A"], row["top_species_A"] = support(sa, p["taxa"][0])
                row["support_B_by_A"], _ = support(sa, p["taxa"][1])
                row["strict_A"], _ = support(sa, p["taxa"][0], strict=True)
                row["strict_B"], _ = support(sa, p["taxa"][1], strict=True)
            if sb:
                row["support_A_by_B"], row["top_species_B"] = support(sb, p["taxa"][0])
                row["support_B_by_B"], _ = support(sb, p["taxa"][1])
        except Exception as e:
            row["error"] = repr(e)
        # verdict on the shared content (use A's table; identical when stat_identical)
        sA, sB = row.get("strict_A"), row.get("strict_B")
        if sA is None and sB is None:
            row["verdict"] = "untestable (no species-level claim on either side)"
        else:
            sA = sA or 0.0; sB = sB or 0.0
            if sA >= 0.02 and sB < sA / 10: row["verdict"] = "species-level reads support A only"
            elif sB >= 0.02 and sA < sB / 10: row["verdict"] = "species-level reads support B only"
            elif sA >= 0.02 and sB >= 0.02: row["verdict"] = "species-level reads support both (mixture)"
            elif sA < 0.005 and sB < 0.005: row["verdict"] = "species-level reads support neither"
            else: row["verdict"] = "ambiguous"
        rows.append(row)

    # study-pair roll-up
    by = collections.defaultdict(list)
    for r in rows: by[tuple(sorted(r["studies"]))].append(r)
    summary = {"n_run_pairs": len(rows), "n_study_pairs": len(by),
               "stat_both_available": sum(1 for r in rows if all(r["stat_available"])),
               "stat_identical": sum(1 for r in rows if r["stat_identical"] is True),
               "stat_differs": sum(1 for r in rows if r["stat_identical"] is False),
               "same_ref_date": sum(1 for r in rows if r.get("stat_same_ref_date")),
               "same_ref_date_and_identical": sum(1 for r in rows if r.get("stat_same_ref_date") and r["stat_identical"]),
               "same_ref_date_and_differs": sum(1 for r in rows if r.get("stat_same_ref_date") and r["stat_identical"] is False),
               "diff_ref_date_same_spots": sum(1 for r in rows if r.get("stat_same_ref_date") is False and r.get("stat_same_spots")),
               "diff_ref_date_diff_spots": sum(1 for r in rows if r.get("stat_same_ref_date") is False and r.get("stat_same_spots") is False),
               "verdicts": collections.Counter(r["verdict"] for r in rows)}
    json.dump({"summary": summary, "rows": rows}, open(a.out + ".json", "w"), indent=1)
    with open(a.out + ".tsv", "w") as fh:
        fh.write("runA\trunB\tstudyA\tstudyB\tnameA\tnameB\trelation\tprior\tstat_identical\tsuppA\tsuppB\ttopA\tverdict\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in [r["runs"][0], r["runs"][1], r["studies"][0], r["studies"][1],
                r["names"][0], r["names"][1], r["tax_relation"], r["prior_confirm"], r["stat_identical"],
                None if r.get("strict_A") is None else round(r["strict_A"], 4),
                None if r.get("strict_B") is None else round(r["strict_B"], 4),
                r["top_species_A"], r["verdict"]]) + "\n")
    print(json.dumps(summary, indent=1, default=str), file=sys.stderr)

if __name__ == "__main__":
    main()
