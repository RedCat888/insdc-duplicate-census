#!/usr/bin/env python3
"""Minimal NCBI taxonomy resolver: map a tax_id to its species/genus/family ancestors so
that a benign strain-label difference ("Vibrio cholerae" vs "Vibrio cholerae O1 biovar El
Tor") can be told apart from a genuine cross-species conflict."""
import os, functools

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

@functools.lru_cache(maxsize=1)
def load():
    parent, rank, name = {}, {}, {}
    with open(os.path.join(DATA, "nodes.dmp"), encoding="utf-8", errors="replace") as fh:
        for line in fh:
            p = [x.strip() for x in line.split("|")]
            parent[p[0]] = p[1]; rank[p[0]] = p[2]
    with open(os.path.join(DATA, "names.dmp"), encoding="utf-8", errors="replace") as fh:
        for line in fh:
            p = [x.strip() for x in line.split("|")]
            if len(p) > 3 and p[3] == "scientific name":
                name[p[0]] = p[1]
    return parent, rank, name

def lineage(tid):
    parent, rank, name = load()
    out = []; seen = set()
    while tid and tid in parent and tid not in seen:
        seen.add(tid); out.append((tid, rank.get(tid), name.get(tid)))
        if tid == "1": break
        tid = parent[tid]
    return out

def ancestor_at(tid, want):
    for t, r, n in lineage(tid):
        if r == want: return (t, n)
    return (None, None)

def relation(t1, t2):
    """Coarsest level at which two tax_ids agree."""
    if not t1 or not t2: return "unknown"
    if t1 == t2: return "same_taxid"
    for level in ("species", "genus", "family", "order", "class", "phylum", "superkingdom"):
        a, b = ancestor_at(t1, level)[0], ancestor_at(t2, level)[0]
        if a and b and a == b: return f"same_{level}"
    l1 = {t for t, r, n in lineage(t1)}; l2 = {t for t, r, n in lineage(t2)}
    return "shares_no_rank" if (l1 & l2) - {"1"} else "disjoint"

def sci(tid):
    return load()[2].get(tid)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        a, b = sys.argv[1], sys.argv[2]
        print(a, sci(a), "|", b, sci(b), "->", relation(a, b))
    else:
        for t in sys.argv[1:]:
            print(t, sci(t), [x for x in lineage(t) if x[1] in
                  ("species","genus","family","order","superkingdom")])
