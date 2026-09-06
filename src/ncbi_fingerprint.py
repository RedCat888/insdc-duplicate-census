#!/usr/bin/env python3
"""Fetch NCBI's per-run fingerprint: original-file md5(s), exact A/C/G/T/N base composition,
spot count, and read-length statistics. Archive-independent - works for ERR and SRR alike."""
import urllib.request, re, json, sys, time, hashlib

def fetch(acc, retries=3):
    u = f"https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/run_new?acc={acc}"
    for k in range(retries):
        try:
            with urllib.request.urlopen(u, timeout=90) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if k == retries-1: return None
            time.sleep(2*(k+1))

def parse(xml, acc):
    if not xml or "<RUN " not in xml: return None
    d = {"acc": acc}
    m = re.search(r'<RUN[^>]*\stotal_spots="(\d+)"[^>]*\stotal_bases="(\d+)"', xml)
    if m: d["total_spots"], d["total_bases"] = int(m.group(1)), int(m.group(2))
    m = re.search(r'<RUN[^>]*\salias="([^"]*)"', xml)
    if m: d["alias"] = m.group(1)
    bases = dict(re.findall(r'<Base value="([ACGTN])" count="(\d+)"/>', xml))
    if bases: d["bases"] = {k: int(v) for k, v in bases.items()}
    orig = re.findall(r'<SRAFile[^>]*filename="([^"]*)"[^>]*size="(\d+)"[^>]*md5="([0-9a-f]+)"[^>]*supertype="Original"', xml)
    d["original_files"] = [{"filename": f, "size": int(s), "md5": m5} for f, s, m5 in orig]
    stats = re.findall(r'<Read index="(\d+)" count="(\d+)" average="([\d.]+)" stdev="([\d.]+)"/>', xml)
    d["read_stats"] = [{"index": int(i), "count": int(c), "avg": float(av), "stdev": float(sd)}
                       for i, c, av, sd in stats]
    m = re.search(r'<STUDY[^>]*accession="([^"]+)"', xml)
    if m: d["study"] = m.group(1)
    m = re.search(r'<EXTERNAL_ID namespace="BioProject"[^>]*>([^<]+)<', xml)
    if m: d["bioproject"] = m.group(1)
    qc = re.findall(r'<Quality value="(\d+)" count="(\d+)"/>', xml)
    if qc:
        d["qual_hash"] = hashlib.md5((";".join(f"{a}:{b}" for a, b in qc)).encode()).hexdigest()[:16]
        d["qual_n"] = len(qc)
    m = re.search(r'<INSTRUMENT_MODEL>([^<]*)<', xml)
    if m: d["instrument"] = m.group(1)
    return d

def composition_key(d):
    """Archive-independent content fingerprint: exact base composition + spot count."""
    if not d or "bases" not in d or "total_spots" not in d: return None
    b = d["bases"]
    return (d["total_spots"], b.get("A"), b.get("C"), b.get("G"), b.get("T"), b.get("N"))

if __name__ == "__main__":
    for acc in sys.argv[1:]:
        d = parse(fetch(acc), acc)
        print(json.dumps({"acc": acc, "key": composition_key(d),
                          "orig": d.get("original_files") if d else None,
                          "alias": d.get("alias") if d else None,
                          "study": d.get("study") if d else None,
                          "qual_hash": d.get("qual_hash") if d else None,
                          "read_stats": d.get("read_stats") if d else None}))
