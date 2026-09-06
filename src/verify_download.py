#!/usr/bin/env python3
"""H4: download the actual submitted files for claimed-duplicate runs and hash them locally.
This is the decisive artifact check - it does not trust ENA's md5 field at all."""
import sys, os, json, hashlib, urllib.request, argparse, random, time

def filereport(run):
    u = ("https://www.ebi.ac.uk/ena/portal/api/filereport?accession=%s&result=read_run"
         "&fields=run_accession,study_accession,submitted_ftp,submitted_md5,submitted_bytes"
         "&format=tsv" % run)
    with urllib.request.urlopen(u, timeout=60) as r:
        lines = r.read().decode().strip().split("\n")
    if len(lines) < 2: return None
    h = lines[0].split("\t"); v = lines[1].split("\t")
    return dict(zip(h, v))

def fetch_md5(url, limit_bytes=None):
    if not url.startswith("http"): url = "https://" + url
    h = hashlib.md5(); n = 0
    req = urllib.request.Request(url, headers={"User-Agent": "dup-census/1.0"})
    with urllib.request.urlopen(req, timeout=600) as r:
        while True:
            b = r.read(1 << 20)
            if not b: break
            h.update(b); n += len(b)
            if limit_bytes and n > limit_bytes: return None, n
    return h.hexdigest(), n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", required=True, help="json list of {md5, members:[{run,study}]}")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--seed", type=int, default=20260906)
    ap.add_argument("--maxbytes", type=int, default=400_000_000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    cands = json.load(open(a.pairs))
    random.seed(a.seed); random.shuffle(cands)
    results = []; done = 0
    for c in cands:
        if done >= a.n: break
        members = c["members"]
        runs = sorted({m["run"] for m in members})
        studies = {m["study"] for m in members}
        if len(studies) < 2 or len(runs) < 2: continue
        pick = runs[:2]
        info = {}
        ok = True
        for run in pick:
            fr = filereport(run)
            if not fr or not fr.get("submitted_ftp"): ok = False; break
            urls = fr["submitted_ftp"].split(";")
            md5s = fr["submitted_md5"].split(";")
            byts = fr["submitted_bytes"].split(";")
            idx = md5s.index(c["md5"]) if c["md5"] in md5s else 0
            info[run] = dict(url=urls[idx], claimed_md5=md5s[idx],
                             claimed_bytes=int(byts[idx]) if idx < len(byts) and byts[idx].isdigit() else None)
        if not ok: continue
        if any((info[r]["claimed_bytes"] or 0) > a.maxbytes for r in pick):
            continue
        rec = dict(target_md5=c["md5"], runs=pick, studies=sorted(studies), files={})
        good = True
        for run in pick:
            t0 = time.time()
            try:
                got, n = fetch_md5(info[run]["url"], limit_bytes=a.maxbytes)
            except Exception as e:
                rec["files"][run] = dict(error=str(e)[:200], **info[run]); good = False; continue
            rec["files"][run] = dict(computed_md5=got, computed_bytes=n,
                                     secs=round(time.time()-t0, 1), **info[run])
        cm = [rec["files"][r].get("computed_md5") for r in pick]
        rec["identical_verified"] = (good and cm[0] is not None and cm[0] == cm[1])
        rec["matches_ena_claim"] = all(rec["files"][r].get("computed_md5") == rec["files"][r]["claimed_md5"]
                                       for r in pick if "computed_md5" in rec["files"][r])
        results.append(rec); done += 1
        print(json.dumps({k: rec[k] for k in ("runs","studies","identical_verified","matches_ena_claim")}))
    json.dump(results, open(a.out, "w"), indent=2)
    ok = sum(1 for r in results if r["identical_verified"])
    print(f"\nVERIFIED IDENTICAL: {ok}/{len(results)}")

if __name__ == "__main__":
    main()
