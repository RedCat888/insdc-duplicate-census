#!/usr/bin/env python3
"""Confirm (or refute) that two runs hold the same data, using two independent routes:
  1. NCBI exact base composition (total_spots + A/C/G/T/N) - archive-independent
  2. ENA read-level comparison of the first 2000 sequences - works when NCBI has no stats
Refusing to rely on either alone."""
import sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ncbi_fingerprint import fetch, parse, composition_key
from compare_reads import fastq_urls, first_seqs

def confirm(a, b, want_reads=True):
    out = {"runs": [a, b]}
    ka = composition_key(parse(fetch(a), a))
    kb = composition_key(parse(fetch(b), b))
    out["ncbi_key_a"] = list(ka) if ka else None
    out["ncbi_key_b"] = list(kb) if kb else None
    if ka and kb:
        out["composition_match"] = (ka == kb)
    else:
        out["composition_match"] = None
    if want_reads and (out["composition_match"] is not False):
        try:
            ua, ub = fastq_urls(a), fastq_urls(b)
            if ua and ub:
                sa, sb = first_seqs(ua[0], n=2000), first_seqs(ub[0], n=2000)
                n = min(len(sa), len(sb))
                same = sum(1 for i in range(n) if sa[i] == sb[i])
                out["reads_compared"] = n
                out["reads_identical_in_position"] = same
                out["read_md5_a"] = hashlib.md5("".join(sa[:n]).encode()).hexdigest()
                out["read_md5_b"] = hashlib.md5("".join(sb[:n]).encode()).hexdigest()
                out["read_match"] = (n >= 200 and same == n)
            else:
                out["read_match"] = None
        except Exception as e:
            out["read_error"] = str(e)[:180]; out["read_match"] = None
    verdict = "unknown"
    if out.get("composition_match") is True or out.get("read_match") is True: verdict = "CONFIRMED"
    if out.get("composition_match") is False or out.get("read_match") is False: verdict = "REFUTED"
    out["verdict"] = verdict
    return out

if __name__ == "__main__":
    pairs = [sys.argv[i:i+2] for i in range(1, len(sys.argv), 2)]
    res = []
    for a, b in pairs:
        r = confirm(a, b); res.append(r)
        print(f"{a} vs {b}: {r['verdict']}  comp={r.get('composition_match')} "
              f"reads={r.get('reads_identical_in_position')}/{r.get('reads_compared')}")
    print(json.dumps(res, indent=1)[:200])
