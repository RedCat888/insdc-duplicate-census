#!/usr/bin/env python3
"""Confirm every organism-level identity conflict found in the exploratory window.
Numeric-channel pairs are run-level claims -> NCBI composition + ENA read comparison.
md5-channel pairs are file-level claims -> HTTP range check of the two files."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from confirm_pair import confirm
from range_check import probe

RUN_PAIRS = [
 ("SRR340034","SRR346135","Gossypium barbadense vs G. arboreum (cotton)"),
 ("SRR340033","SRR346324","Gossypium arboreum vs G. barbadense (cotton)"),
 ("SRR090139","SRR090222","S. epidermidis IS-250 vs S. aureus IS-91 (JCVI)"),
 ("SRR090139","SRR090228","S. epidermidis IS-250 vs S. aureus IS-99 (JCVI)"),
 ("SRR070588","SRR071318","S. lugdunensis VCU148 vs S. epidermidis VCU111 (JCVI)"),
 ("SRR000202","SRR627587","Sterkiella histriomuscorum vs Oxytricha trifallax (WUGSC)"),
 ("SRR1021212","SRR1031053","E. coli O157:H7 EDL933 vs Listeria monocytogenes NCTC 11994 (NIST)"),
 ("SRR063729","SRR063733","Finegoldia magna vs Peptoniphilus sp. (JCVI)"),
 ("SRR063729","SRR063735","Finegoldia magna vs Streptococcus mitis (JCVI)"),
 ("SRR063733","SRR063735","Peptoniphilus sp. vs Streptococcus mitis (JCVI)"),
 ("SRR060132","SRR060133","Ligilactobacillus salivarius vs Lactobacillus delbrueckii (JCVI)"),
]
FILE_PAIRS = [
 ("ftp.sra.ebi.ac.uk/vol1/run/ERR016/ERR016531/library06_GBSKQZK02.sff",
  "ftp.sra.ebi.ac.uk/vol1/run/ERR024/ERR024102/GBSKQZK02.sff",
  "Triticum aestivum (Liverpool) vs Solanum phureja (Dundee) - shared 454 region GBSKQZK02"),
]
out = {"run_level": [], "file_level": []}
for a, b, lab in RUN_PAIRS:
    r = confirm(a, b); r["label"] = lab; out["run_level"].append(r)
    print(f"{r['verdict']:<10} {lab}", flush=True)
    print(f"           comp={r.get('composition_match')} "
          f"reads={r.get('reads_identical_in_position')}/{r.get('reads_compared')}", flush=True)
for a, b, lab in FILE_PAIRS:
    try:
        pa, pb = probe(a), probe(b)
        v = (pa["size"] == pb["size"] and pa["head_md5"] == pb["head_md5"]
             and pa["tail_md5"] == pb["tail_md5"])
        rec = dict(label=lab, a=pa, b=pb, verdict="CONFIRMED" if v else "REFUTED")
    except Exception as e:
        rec = dict(label=lab, error=str(e)[:200], verdict="unknown")
    out["file_level"].append(rec)
    print(f"{rec['verdict']:<10} {lab}", flush=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "out",
          "confirm_organism_conflicts.json"), "w"), indent=1)
nr = sum(1 for r in out["run_level"] if r["verdict"] == "CONFIRMED")
nf = sum(1 for r in out["file_level"] if r["verdict"] == "CONFIRMED")
print(f"\nrun-level CONFIRMED {nr}/{len(out['run_level'])}; file-level CONFIRMED {nf}/{len(out['file_level'])}")
