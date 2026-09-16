#!/usr/bin/env python3
"""Batched NCBI E-utilities sweep: per-run content fingerprint for a list of accessions.

For every run returned (efetch db=sra returns whole experiment packages, so sibling runs come
back too) records:
  total_spots, total_bases, exact A/C/G/T/N composition   -> archive/format/header-independent key
  Original uploaded file(s): filename, size, md5           -> submitter-checksum channel (NCBI side)
  study / bioproject / biosample / sample / tax_id / organism / center / alias / published

Resumable: accessions already present in --out are skipped. Rate: --workers concurrent POSTs of
--batch ids each; with an API key NCBI allows 10 req/s, and each request takes ~6-20 s, so this
sits far under the limit. The API key is read from .secrets/ncbi_api_key and never logged.
"""
import argparse, json, os, sys, time, threading, queue, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def load_key():
    p = os.path.join(ROOT, ".secrets", "ncbi_api_key")
    return open(p).read().strip() if os.path.exists(p) else None

def fetch_batch(ids, key, retries=5):
    data = {"db": "sra", "id": ",".join(ids)}
    if key: data["api_key"] = key
    body = urllib.parse.urlencode(data).encode()
    for k in range(retries):
        try:
            req = urllib.request.Request(EUTILS, data=body, headers={"User-Agent": "insdc-duplicate-census/1.0"})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except Exception as e:
            wait = 3 * (2 ** k)
            print(f"  retry {k+1}/{retries} after {type(e).__name__}: {e} (sleep {wait}s)", file=sys.stderr)
            time.sleep(wait)
    return None

def text(el, path):
    x = el.find(path)
    return x.text if x is not None and x.text is not None else None

def parse_package_set(xml_bytes):
    """Yield one dict per RUN in the EXPERIMENT_PACKAGE_SET."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        print(f"  XML parse error: {e}", file=sys.stderr)
        return
    for pkg in root.iter("EXPERIMENT_PACKAGE"):
        exp = pkg.find("EXPERIMENT")
        study = pkg.find("STUDY")
        sample = pkg.find("SAMPLE")
        exp_acc = exp.get("accession") if exp is not None else None
        study_acc = study.get("accession") if study is not None else None
        bioproject = None
        if study is not None:
            for x in study.iter("EXTERNAL_ID"):
                if x.get("namespace") == "BioProject": bioproject = x.text
        sample_acc = sample.get("accession") if sample is not None else None
        biosample = None; tax_id = None; organism = None
        if sample is not None:
            for x in sample.iter("EXTERNAL_ID"):
                if x.get("namespace") == "BioSample": biosample = x.text
            tax_id = text(sample, ".//SAMPLE_NAME/TAXON_ID")
            organism = text(sample, ".//SAMPLE_NAME/SCIENTIFIC_NAME")
        strategy = text(exp, ".//LIBRARY_STRATEGY") if exp is not None else None
        platform = None
        if exp is not None:
            pl = exp.find("PLATFORM")
            if pl is not None and len(pl):
                platform = list(pl)[0].tag
        rs = pkg.find("RUN_SET")
        if rs is None: continue
        for run in rs.findall("RUN"):
            d = {
                "acc": run.get("accession"),
                "alias": run.get("alias"),
                "center": run.get("center_name"),
                "published": run.get("published"),
                "total_spots": int(run.get("total_spots")) if run.get("total_spots") else None,
                "total_bases": int(run.get("total_bases")) if run.get("total_bases") else None,
                "size": int(run.get("size")) if run.get("size") else None,
                "experiment": exp_acc, "study": study_acc, "bioproject": bioproject,
                "sample": sample_acc, "biosample": biosample, "tax_id": tax_id, "organism": organism,
                "strategy": strategy, "platform": platform,
            }
            bases = run.find("Bases")
            if bases is not None:
                d["bases"] = {b.get("value"): int(b.get("count")) for b in bases.findall("Base")}
            orig = []; primary = None
            for f in run.iter("SRAFile"):
                st = f.get("supertype")
                if st == "Original":
                    orig.append({"filename": f.get("filename"), "size": int(f.get("size") or 0), "md5": f.get("md5")})
                elif st == "Primary ETL" and primary is None:
                    primary = {"md5": f.get("md5"), "size": int(f.get("size") or 0)}
            d["original_files"] = orig
            d["primary_etl"] = primary
            # sample members inside the run's Pool (per-run organism as loaded)
            pool = run.find("Pool")
            if pool is not None:
                mem = pool.find("Member")
                if mem is not None:
                    d["pool_tax_id"] = mem.get("tax_id"); d["pool_organism"] = mem.get("organism")
            yield d

def composition_key(d):
    b = d.get("bases")
    if not b or d.get("total_spots") is None: return None
    return f"{d['total_spots']}:{b.get('A',0)}:{b.get('C',0)}:{b.get('G',0)}:{b.get('T',0)}:{b.get('N',0)}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", required=True, help="file with one accession per line")
    ap.add_argument("--out", required=True, help="JSONL output (appended; resumable)")
    ap.add_argument("--batch", type=int, default=200)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    key = load_key()
    if not key: print("no API key at .secrets/ncbi_api_key — running at 3 req/s", file=sys.stderr)

    wanted = [l.strip() for l in open(a.ids) if l.strip()]
    if a.limit: wanted = wanted[:a.limit]
    done = set()
    if os.path.exists(a.out):
        for line in open(a.out):
            try: done.add(json.loads(line)["acc"])
            except Exception: pass
    todo = [x for x in wanted if x not in done]
    print(f"wanted={len(wanted)} already={len(done)} todo={len(todo)}", file=sys.stderr)
    batches = [todo[i:i+a.batch] for i in range(0, len(todo), a.batch)]

    q = queue.Queue()
    for b in batches: q.put(b)
    lock = threading.Lock()
    out = open(a.out, "a")
    stats = {"runs": 0, "batches": 0, "failed": 0, "t0": time.time()}

    def worker():
        while True:
            try: ids = q.get_nowait()
            except queue.Empty: return
            xml = fetch_batch(ids, key)
            if xml is None:
                with lock:
                    stats["failed"] += 1
                    open(a.out + ".failed", "a").write("\n".join(ids) + "\n")
                q.task_done(); continue
            recs = list(parse_package_set(xml))
            with lock:
                for d in recs:
                    if d["acc"] in done: continue
                    done.add(d["acc"])
                    d["ckey"] = composition_key(d)
                    out.write(json.dumps(d, separators=(",", ":")) + "\n")
                    stats["runs"] += 1
                out.flush()
                stats["batches"] += 1
                if stats["batches"] % 10 == 0:
                    el = time.time() - stats["t0"]
                    print(f"[{time.strftime('%H:%M:%S')}] batches={stats['batches']}/{len(batches)} "
                          f"runs={stats['runs']} failed={stats['failed']} rate={stats['runs']/el:.0f}/s", file=sys.stderr)
            q.task_done()

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(a.workers)]
    for t in threads: t.start()
    for t in threads: t.join()
    out.close()
    el = time.time() - stats["t0"]
    print(f"done: runs={stats['runs']} batches={stats['batches']} failed={stats['failed']} in {el/60:.1f} min", file=sys.stderr)

if __name__ == "__main__":
    main()
