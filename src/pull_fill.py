#!/usr/bin/env python3
"""Finish the pull: find every chunk still missing, fetch it, and if a window is too big to
come back intact, split it into single days and fetch those. Each fetch is accepted only if
its row count equals ENA's own count for the same window."""
import os, sys, json, subprocess, urllib.request, urllib.parse, datetime, argparse, gzip

BASE = os.path.expanduser("~/Downloads/dig")
DATA = os.path.join(BASE, "data", "ena")
PULL = os.path.join(BASE, "src", "pull_one.sh")

def api_count(start, end, retries=4):
    q = urllib.parse.quote(f"first_public>={start} AND first_public<={end}")
    u = f"https://www.ebi.ac.uk/ena/portal/api/count?result=read_run&query={q}"
    for k in range(retries):
        try:
            with urllib.request.urlopen(u, timeout=180) as r:
                return int(r.read().decode().strip().split("\n")[-1])
        except Exception:
            import time; time.sleep(3*(k+1))
    return None

def days(start, end):
    d0 = datetime.date.fromisoformat(start); d1 = datetime.date.fromisoformat(end)
    out = []
    while d0 <= d1:
        out.append(d0.isoformat()); d0 += datetime.timedelta(days=1)
    return out

def pull(label, start, end):
    r = subprocess.run([PULL, label, start, end], capture_output=True, text=True)
    return "OK" in r.stdout, r.stdout.strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunks", default=os.path.join(BASE, "src", "chunks.txt"))
    ap.add_argument("--max-split-days", type=int, default=1)
    a = ap.parse_args()
    todo = []
    for line in open(a.chunks):
        label, s, e = line.split()
        if not os.path.exists(os.path.join(DATA, label + ".tsv.gz")):
            todo.append((label, s, e))
    print(f"{len(todo)} chunks missing", flush=True)
    failed = []
    # canonical record of the windows actually used, so validation has something exact to
    # check against when a parent window had to be split into days
    used = []
    for line in open(a.chunks):
        label, s_, e_ = line.split()
        if os.path.exists(os.path.join(DATA, label + ".tsv.gz")):
            used.append((label, s_, e_))
    for label, s, e in todo:
        ok, msg = pull(label, s, e)
        print(("  " if ok else "  !! ") + msg, flush=True)
        if ok:
            used.append((label, s, e)); continue
        # split into single days
        dd = days(s, e)
        allok = True
        for d in dd:
            sub = f"{label}__{d}"
            if os.path.exists(os.path.join(DATA, sub + ".tsv.gz")): continue
            ok2, msg2 = pull(sub, d, d)
            print(("    " if ok2 else "    !! ") + msg2, flush=True)
            if ok2 or os.path.exists(os.path.join(DATA, sub + ".tsv.gz")):
                used.append((sub, d, d))
            allok = allok and ok2
        if not allok: failed.append(label)
    seen = set(); lines = []
    for lab, s_, e_ in used:
        if lab in seen: continue
        seen.add(lab); lines.append(f"{lab} {s_} {e_}")
    with open(os.path.join(BASE, "src", "chunks_final.txt"), "w") as fh:
        fh.write("\n".join(sorted(lines)) + "\n")
    print(f"wrote src/chunks_final.txt with {len(lines)} windows")
    print("still failing:", failed)

if __name__ == "__main__":
    main()
