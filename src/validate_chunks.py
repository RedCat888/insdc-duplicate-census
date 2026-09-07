#!/usr/bin/env python3
"""Verify every downloaded chunk against ENA's own count for the same date range.

Why this exists: pull_one.sh piped curl into gzip and then checked that the gzip was
well-formed. A TRUNCATED HTTP response still gzips cleanly, so short files passed silently.
2020-08 held 144,991 of 250,426 runs and looked fine. Never again."""
import os, sys, gzip, json, urllib.request, urllib.parse, argparse, calendar

DATA = os.path.expanduser("~/Downloads/dig/data/ena")

def api_count(start, end, retries=4):
    q = urllib.parse.quote(f"first_public>={start} AND first_public<={end}")
    u = f"https://www.ebi.ac.uk/ena/portal/api/count?result=read_run&query={q}"
    for k in range(retries):
        try:
            with urllib.request.urlopen(u, timeout=180) as r:
                t = r.read().decode().strip().split("\n")
            return int(t[-1])
        except Exception:
            import time; time.sleep(3*(k+1))
    return None

def rows(path):
    n = 0
    try:
        with gzip.open(path, "rt", errors="replace") as fh:
            for _ in fh: n += 1
    except Exception:
        return None
    return max(0, n-1)          # minus header

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunks", default=os.path.expanduser("~/Downloads/dig/src/chunks.txt"))
    ap.add_argument("--out", default=os.path.expanduser("~/Downloads/dig/out/chunk_validation.json"))
    ap.add_argument("--only-present", action="store_true")
    a = ap.parse_args()
    report = []
    bad = []
    for line in open(a.chunks):
        label, start, end = line.split()
        p = os.path.join(DATA, label + ".tsv.gz")
        if not os.path.exists(p):
            if not a.only_present: report.append(dict(label=label, status="MISSING"))
            continue
        got = rows(p); want = api_count(start, end)
        ok = (got is not None and want is not None and got == want)
        report.append(dict(label=label, rows=got, api_count=want, ok=ok))
        if not ok:
            bad.append(label)
            print(f"  BAD {label}: rows={got} api={want}", flush=True)
    json.dump(dict(report=report, bad=bad, n_checked=len(report),
                   n_bad=len(bad)), open(a.out, "w"), indent=1)
    tot = sum(r.get("rows") or 0 for r in report if r.get("ok"))
    print(f"\nchecked {len(report)}  ok {len(report)-len(bad)}  BAD {len(bad)}")
    print("rows in verified chunks:", f"{tot:,}")
    if bad: print("bad labels:", " ".join(bad))
    # GLOBAL acceptance test. Per-window agreement is not sufficient: a wrong query is
    # validated against its own wrong count. The union must equal the whole archive.
    whole = api_count("1990-01-01", "2030-01-01")
    print(f"archive total per ENA: {whole:,}" if whole else "archive total: UNAVAILABLE")
    if whole:
        print(f"coverage: {tot:,} / {whole:,} = {100.0*tot/whole:.4f}%  (shortfall {whole-tot:,})")
    js = json.load(open(a.out)) if os.path.exists(a.out) else {}
    js.update(dict(rows_total=tot, archive_total=whole,
                   coverage=(tot/whole if whole else None)))
    json.dump(js, open(a.out, "w"), indent=1)

if __name__ == "__main__":
    main()
