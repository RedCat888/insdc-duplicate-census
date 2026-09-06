#!/usr/bin/env python3
"""Ground truth of last resort: pull the first N reads of two runs from ENA's FASTQ and
compare the SEQUENCES (headers are ignored - ENA rewrites them per accession)."""
import sys, gzip, io, json, urllib.request, hashlib

def fastq_urls(acc):
    u = (f"https://www.ebi.ac.uk/ena/portal/api/filereport?accession={acc}"
         "&result=read_run&fields=fastq_ftp,fastq_md5,fastq_bytes&format=tsv")
    with urllib.request.urlopen(u, timeout=90) as r:
        lines = r.read().decode().strip().split("\n")
    if len(lines) < 2: return []
    d = dict(zip(lines[0].split("\t"), lines[1].split("\t")))
    return [x for x in d.get("fastq_ftp", "").split(";") if x]

def first_seqs(url, n=2000, maxbytes=12_000_000):
    if not url.startswith("http"): url = "https://" + url
    req = urllib.request.Request(url, headers={"User-Agent": "dup-census/1.0"})
    buf = io.BytesIO(); got = 0
    with urllib.request.urlopen(req, timeout=300) as r:
        while got < maxbytes:
            b = r.read(1 << 18)
            if not b: break
            buf.write(b); got += len(b)
    buf.seek(0)
    seqs = []
    try:
        with gzip.GzipFile(fileobj=buf) as gz:
            for i, line in enumerate(io.TextIOWrapper(gz, errors="replace")):
                if i % 4 == 1:
                    seqs.append(line.strip())
                    if len(seqs) >= n: break
    except EOFError:
        pass
    return seqs

if __name__ == "__main__":
    a, b = sys.argv[1], sys.argv[2]
    ua, ub = fastq_urls(a), fastq_urls(b)
    print(f"{a}: {len(ua)} fastq file(s)\n{b}: {len(ub)} fastq file(s)")
    sa, sb = first_seqs(ua[0]), first_seqs(ub[0])
    print(f"reads read: {a}={len(sa)}  {b}={len(sb)}")
    n = min(len(sa), len(sb))
    same_order = sum(1 for i in range(n) if sa[i] == sb[i])
    setb = set(sb)
    overlap = sum(1 for s in sa[:n] if s in setb)
    print(f"identical in the same position : {same_order}/{n}")
    print(f"present anywhere in the other  : {overlap}/{n}")
    print(f"md5 of first {n} sequences: {a}={hashlib.md5(''.join(sa[:n]).encode()).hexdigest()}")
    print(f"                            {b}={hashlib.md5(''.join(sb[:n]).encode()).hexdigest()}")
    print(f"first read {a}: {sa[0][:90] if sa else None}")
    print(f"first read {b}: {sb[0][:90] if sb else None}")
