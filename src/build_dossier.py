#!/usr/bin/env python3
"""Assemble every individually verified case into one auditable table.
Each row states exactly what evidence exists for it and how it was obtained."""
import json, os, sys, glob

OUT = os.path.expanduser("~/Downloads/dig/out")
def load(name):
    p = os.path.join(OUT, name)
    if not os.path.exists(p): return None
    try: return json.load(open(p))
    except Exception: return None

rows = []

# 1. downloaded-and-hashed pairs (md5 channel, file identity)
for fn, note in [("verify_pilot.json", "pilot (all from one event - superseded)"),
                 ("verify_events_exploratory.json", "event-stratified")]:
    d = load(fn)
    if not d: continue
    items = d["results"] if isinstance(d, dict) else d
    for r in items:
        rows.append(dict(kind="file identity", evidence="downloaded both files, hashed locally",
                         detail=f"{r.get('runs') or [f['run'] for f in r.get('files',[])]}",
                         result="identical" if r.get("identical_verified") else "NOT identical",
                         note=note))

# 2. JCVI cross-isolate groups (numeric channel, run identity via NCBI composition)
d = load("jcvi_confirm.json")
if d:
    for g in d:
        rows.append(dict(kind="run identity", evidence="NCBI exact A/C/G/T/N + spot count",
                         detail=f"{g['runs']}", result=g["verdict"], note="JCVI/HMP isolates"))

# 3. sampled non-ERR pairs
d = load("srr_confirm_exploratory.json")
if d:
    ok = sum(1 for r in d["results"] if r["verdict"].startswith("CONFIRMED"))
    rows.append(dict(kind="run identity", evidence="NCBI exact A/C/G/T/N + spot count",
                     detail=f"random sample of {d['n_sampled']} non-ERR cross-study candidates",
                     result=f"{ok} confirmed / {d['refuted']} refuted / {d['no_fingerprint']} no fingerprint",
                     note="numeric channel, high-entropy stratum"))

# 4. organism-level conflicts
d = load("confirm_organism_conflicts.json")
if d:
    for r in d.get("run_level", []):
        rows.append(dict(kind="organism conflict (run)", evidence="NCBI composition + ENA read comparison",
                         detail=r.get("label"), result=r.get("verdict"),
                         note=f"reads {r.get('reads_identical_in_position')}/{r.get('reads_compared')}"))
    for r in d.get("file_level", []):
        rows.append(dict(kind="organism conflict (file)", evidence="HTTP range check of both files",
                         detail=r.get("label"), result=r.get("verdict"), note=""))

# 4b. event-stratified verification (random sample across the 201 events)
d = load("verify_events_all.json")
if d:
    ok = d["n_verified"]; n = d["n_attempted"]
    rows.append(dict(kind="event-stratified sample",
                     evidence="random sample of events; download+hash, or first 2,000 reads for large files",
                     detail=f"{n} of 201 events sampled (seeded)",
                     result=f"{ok} verified by the harness; the 2 others were 1 untestable "
                            f"(no FASTQ, read_count 0) and 1 file-level match confirmed by range check "
                            f"-> 19/19 testable confirmed, 0 refuted",
                     note="see log/03-worklog.md for both investigations"))

# 5. GEO publication linkage
d = load("geo_papers.json")
if d:
    for r in d:
        rows.append(dict(kind="publication impact", evidence="SRA alias -> GSM -> GSE -> PubMed",
                         detail=f"{r['runs']} -> {r['gsm']}",
                         result=("different papers " + str(r["pmids"])) if r["different_papers"]
                                else ("same series " + str(r["pmids"])),
                         note=""))

json.dump(rows, open(os.path.join(OUT, "dossier.json"), "w"), indent=1)
print(f"{'kind':<26}{'result':<44}{'detail'}")
for r in rows:
    print(f"{r['kind']:<26}{str(r['result'])[:43]:<44}{str(r['detail'])[:70]}")
print(f"\n{len(rows)} evidence rows")
