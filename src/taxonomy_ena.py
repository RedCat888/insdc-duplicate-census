#!/usr/bin/env python3
"""Taxonomy resolution via ENA's REST API, with a JSON disk cache.
(The NCBI taxdump download kept truncating under bandwidth contention; this needs only the
few thousand tax_ids that actually appear in duplicate pairs.)

Classifies a pair of tax_ids as:
  same_taxid | same_species | same_genus | same_family | same_higher | disjoint | unknown
so that a benign strain-label difference ("Vibrio cholerae" vs "Vibrio cholerae O1 biovar El
Tor" -> same_species) is not counted as a cross-species conflict.
"""
import os, json, time, urllib.request, urllib.error, threading

CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "taxcache.json")
_lock = threading.Lock()
try:
    _cache = json.load(open(CACHE_PATH))
except Exception:
    _cache = {}

def _save():
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "w") as fh: json.dump(_cache, fh)
    os.replace(tmp, CACHE_PATH)

def rec(tid, retries=3):
    tid = str(tid).strip()
    if not tid: return None
    if tid in _cache: return _cache[tid]
    u = f"https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/{tid}"
    d = None
    for k in range(retries):
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                d = json.load(r)
            break
        except urllib.error.HTTPError as e:
            # A 404 is a definitive answer: this tax_id has no ENA record. Retrying it three
            # times with backoff cost ~6 s per unknown id and stalled the whole conflict pass.
            if e.code in (400, 404):
                break
            time.sleep(0.5*(k+1))
        except Exception:
            time.sleep(0.5*(k+1))
    with _lock:
        _cache[tid] = d
        if len(_cache) % 500 == 0: _save()
    return d

def lineage_ranks(d):
    if not d: return []
    return [x.strip() for x in (d.get("lineage") or "").split(";") if x.strip()]

def species_name(d):
    """Best-effort species binomial. ENA's lineage stops at genus, so for strain-rank taxa the
    binomial is taken as the first two tokens of the scientific name."""
    if not d: return None
    if d.get("metagenome") == "true": return None
    n = (d.get("scientificName") or "").strip()
    if d.get("rank") == "species": return n
    t = n.split()
    if len(t) >= 2 and d.get("binomial") == "true": return " ".join(t[:2])
    return None

def relation(t1, t2):
    t1, t2 = str(t1).strip(), str(t2).strip()
    if not t1 or not t2: return "unknown"
    if t1 == t2: return "same_taxid"
    d1, d2 = rec(t1), rec(t2)
    if not d1 or not d2: return "unknown"
    s1, s2 = species_name(d1), species_name(d2)
    if s1 and s2 and s1 == s2: return "same_species"
    l1, l2 = lineage_ranks(d1), lineage_ranks(d2)
    if not l1 or not l2: return "unknown"
    n1 = (d1.get("scientificName") or "").strip()
    n2 = (d2.get("scientificName") or "").strip()
    if (n1 and n1 in l2) or (n2 and n2 in l1):
        # one is a strict ancestor of the other ("metagenome" -> "human gut metagenome"):
        # a refinement of the label, not a contradiction
        return "refinement"
    m1, m2 = d1.get("metagenome") == "true", d2.get("metagenome") == "true"
    if m1 and m2:
        # two DIFFERENT metagenome tax_ids = two different declared environments
        return "metagenome_type_conflict"
    if m1 != m2:
        return "metagenome_vs_organism"
    if l1 and l2 and l1[-1] == l2[-1]:
        return "same_genus"
    common = 0
    for a, b in zip(l1, l2):
        if a == b: common += 1
        else: break
    if common == 0: return "disjoint"
    return f"same_higher_depth{common}"

def flush(): _save()

if __name__ == "__main__":
    import sys
    for i in range(1, len(sys.argv), 2):
        a, b = sys.argv[i], sys.argv[i+1]
        da, db = rec(a), rec(b)
        print(f"{a} ({da and da.get('scientificName')})  vs  {b} ({db and db.get('scientificName')})"
              f"  ->  {relation(a,b)}")
    flush()
