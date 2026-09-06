#!/usr/bin/env python3
"""H4 ground truth, sampled across EVENTS (not md5 groups - the pilot's flaw was that all
six sampled pairs came from one event).

For each sampled event: take two runs from different studies that share a checksum, download
BOTH submitted files from ENA's FTP over HTTPS, hash them locally, and check
  (a) the two computed hashes are equal   -> the duplicate claim is true
  (b) each computed hash equals ENA's claimed submitted_md5  -> ENA's field is trustworthy
Nothing here trusts the metadata."""
import sys, os, json, hashlib, urllib.request, argparse, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compare_reads import fastq_urls, first_seqs

def filereport(run, retries=3):
    u = ("https://www.ebi.ac.uk/ena/portal/api/filereport?accession=%s&result=read_run"
         "&fields=run_accession,study_accession,submitted_ftp,submitted_md5,submitted_bytes"
         "&format=tsv" % run)
    for k in range(retries):
        try:
            with urllib.request.urlopen(u, timeout=90) as r:
                lines = r.read().decode().strip().split("\n")
            if len(lines) < 2: return None
            return dict(zip(lines[0].split("\t"), lines[1].split("\t")))
        except Exception:
            time.sleep(2*(k+1))
    return None

def hash_url(url, cap):
    if not url.startswith("http"): url = "https://" + url
    h = hashlib.md5(); n = 0
    req = urllib.request.Request(url, headers={"User-Agent": "dup-census/1.0"})
    with urllib.request.urlopen(req, timeout=1800) as r:
        while True:
            b = r.read(1 << 20)
            if not b: break
            h.update(b); n += len(b)
            if n > cap: return None, n
    return h.hexdigest(), n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", required=True)
    ap.add_argument("--n", type=int, default=25)
    ap.add_argument("--seed", type=int, default=20260906)
    ap.add_argument("--maxbytes", type=int, default=250_000_000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    events = [json.loads(l) for l in open(a.events)]
    rng = random.Random(a.seed); rng.shuffle(events)
    out = []; skipped_big = 0; skipped_meta = 0
    for e in events:
        if len(out) >= a.n: break
        # find two runs in different studies sharing a checksum
        reports = {}
        for run in e["runs"][:24]:
            fr = filereport(run)
            if fr and fr.get("submitted_md5"): reports[run] = fr
            if len(reports) >= 12: break
        bym = {}
        for run, fr in reports.items():
            for i, m in enumerate(fr["submitted_md5"].split(";")):
                if not m: continue
                bym.setdefault(m, []).append((run, i, fr))
        pair = None
        for m, lst in sorted(bym.items(), key=lambda kv: min(
                int(v[2]["submitted_bytes"].split(";")[v[1]] or 0) for v in kv[1])):
            studies = {v[2]["study_accession"] for v in lst}
            if len(lst) >= 2 and len(studies) >= 2:
                seen = {}
                for run, i, fr in lst:
                    seen.setdefault(fr["study_accession"], (run, i, fr))
                if len(seen) >= 2:
                    pair = (m, list(seen.values())[:2]); break
        if not pair: skipped_meta += 1; continue
        m, members = pair
        sizes = [int(fr["submitted_bytes"].split(";")[i] or 0) for _, i, fr in members]
        rec = dict(event_studies=e["studies"], target_md5=m, files=[], max_bytes=max(sizes))
        if max(sizes) > a.maxbytes:
            # NO size-based skipping: fall back to a read-level comparison, which costs the
            # same for a 200 GB run as for a 2 MB one. Sequences only; ENA rewrites headers.
            rec["method"] = "read_level_first2000"
            try:
                seqs = []
                for run, i, fr in members:
                    u = fastq_urls(run)
                    if not u: raise RuntimeError("no fastq for " + run)
                    seqs.append((run, fr["study_accession"], first_seqs(u[0], n=2000)))
                n = min(len(seqs[0][2]), len(seqs[1][2]))
                same = sum(1 for k in range(n) if seqs[0][2][k] == seqs[1][2][k])
                rec["files"] = [dict(run=r, study=st, n_reads=len(sq)) for r, st, sq in seqs]
                rec["reads_compared"] = n; rec["reads_identical_in_position"] = same
                rec["identical_verified"] = (n >= 500 and same == n)
                rec["ena_field_correct"] = None
            except Exception as ex:
                rec["error"] = str(ex)[:200]; rec["identical_verified"] = False
                rec["ena_field_correct"] = None
            out.append(rec)
            print(json.dumps({k: rec.get(k) for k in
                  ("event_studies","method","reads_compared","reads_identical_in_position","identical_verified")}))
            continue
        rec["method"] = "full_file_md5"
        okhash = []
        for run, i, fr in members:
            url = fr["submitted_ftp"].split(";")[i]
            t0 = time.time()
            try:
                got, n = hash_url(url, a.maxbytes*2)
            except Exception as ex:
                rec["files"].append(dict(run=run, study=fr["study_accession"], url=url,
                                         error=str(ex)[:160])); okhash.append(None); continue
            rec["files"].append(dict(run=run, study=fr["study_accession"], url=url,
                claimed_md5=m, computed_md5=got, bytes=n, secs=round(time.time()-t0,1),
                matches_ena=(got == m)))
            okhash.append(got)
        rec["identical_verified"] = (len(okhash) == 2 and okhash[0] and okhash[0] == okhash[1])
        rec["ena_field_correct"] = all(f.get("matches_ena") for f in rec["files"] if "computed_md5" in f)
        out.append(rec)
        print(json.dumps({k: rec[k] for k in ("event_studies","identical_verified","ena_field_correct")}))
    json.dump(dict(results=out, skipped_too_big=skipped_big, skipped_no_pair=skipped_meta,
                   n_verified=sum(1 for r in out if r["identical_verified"]),
                   n_attempted=len(out)), open(a.out, "w"), indent=2)
    print(f"\nVERIFIED IDENTICAL {sum(1 for r in out if r['identical_verified'])}/{len(out)}"
          f"  (skipped: {skipped_big} too big, {skipped_meta} no usable pair)")

if __name__ == "__main__":
    main()
