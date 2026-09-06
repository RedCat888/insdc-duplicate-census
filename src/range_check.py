#!/usr/bin/env python3
"""Cheap independent check that two large remote files are the same object: hash the first
and last N bytes of each via HTTP range requests, and compare sizes. Avoids downloading
multi-GB files while still testing bytes we fetched ourselves."""
import sys, hashlib, urllib.request

def probe(url, n=5_000_000):
    if not url.startswith("http"): url = "https://" + url
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent":"dup-census/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        size = int(r.headers.get("Content-Length", 0))
    def rng(a, b):
        rq = urllib.request.Request(url, headers={"User-Agent":"dup-census/1.0",
                                                  "Range": f"bytes={a}-{b}"})
        with urllib.request.urlopen(rq, timeout=300) as r:
            return r.read()
    head = rng(0, n-1)
    tail = rng(max(0, size-n), size-1) if size > n else b""
    return dict(size=size, head_md5=hashlib.md5(head).hexdigest(),
                tail_md5=hashlib.md5(tail).hexdigest(), head_bytes=len(head), tail_bytes=len(tail))

if __name__ == "__main__":
    a, b = sys.argv[1], sys.argv[2]
    pa, pb = probe(a), probe(b)
    print("A", pa); print("B", pb)
    print("size match:", pa["size"] == pb["size"])
    print("head match:", pa["head_md5"] == pb["head_md5"])
    print("tail match:", pa["tail_md5"] == pb["tail_md5"])
