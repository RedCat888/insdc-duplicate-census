#!/usr/bin/env python3
"""Stream ENA read_run chunk TSVs -> flat key files for external sort.

Emits two streams:
  md5 channel : one line per (submitted-file md5, run)
  num channel : one line per (read_count:base_count, run)
Respects the preregistered exploratory / held-out split.
"""
import gzip, csv, sys, os, glob, argparse
csv.field_size_limit(10_000_000)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import SPLIT_DATE, DEGENERATE_MD5, MIN_SUBMITTED_BYTES, MIN_SHARE_OF_RUN

COLS = ["run_accession","study_accession","secondary_study_accession","sample_accession",
        "submission_accession","tax_id","scientific_name","library_strategy",
        "instrument_platform","center_name","broker_name","first_public",
        "read_count","base_count"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["exploratory","heldout","all"], required=True)
    ap.add_argument("--datadir", default=os.path.expanduser("~/Downloads/dig/data/ena"))
    ap.add_argument("--outdir",  default=os.path.expanduser("~/Downloads/dig/out"))
    a = ap.parse_args()

    os.makedirs(a.outdir, exist_ok=True)
    md5f = open(os.path.join(a.outdir, f"keys_md5_{a.set}.tsv"), "w")
    numf = open(os.path.join(a.outdir, f"keys_num_{a.set}.tsv"), "w")
    stats = dict(rows=0, kept=0, dropped_no_study=0, dropped_low_share=0, md5_parts=0, dropped_degen=0, dropped_small=0,
                 no_md5=0, bad_files=0, num_keys=0)

    for f in sorted(glob.glob(os.path.join(a.datadir, "*.tsv.gz"))):
        try:
            fh = gzip.open(f, "rt", newline="")
            rdr = csv.DictReader(fh, delimiter="\t")
            for r in rdr:
                stats["rows"] += 1
                fp = (r.get("first_public") or "").strip()
                if not fp:
                    continue
                inset = (fp < SPLIT_DATE) if a.set == "exploratory" else \
                        (fp >= SPLIT_DATE) if a.set == "heldout" else True
                if not inset:
                    continue
                if not (r.get("study_accession") or "").strip():
                    stats["dropped_no_study"] = stats.get("dropped_no_study",0)+1
                    continue
                stats["kept"] += 1
                meta = "\t".join((r.get(c) or "").replace("\t"," ") for c in COLS)

                md5s  = [x.strip() for x in (r.get("submitted_md5")   or "").split(";")]
                bytez = [x.strip() for x in (r.get("submitted_bytes") or "").split(";")]
                md5s  = [x for x in md5s if x]
                if not md5s:
                    stats["no_md5"] += 1
                nb = []
                for x in bytez:
                    try: nb.append(int(x))
                    except ValueError: nb.append(0)
                run_total = sum(nb) or 0
                n_files = len(md5s)
                for i, m in enumerate(md5s):
                    if m in DEGENERATE_MD5:
                        stats["dropped_degen"] += 1; continue
                    b = bytez[i] if i < len(bytez) else ""
                    try:
                        if b and int(b) < MIN_SUBMITTED_BYTES:
                            stats["dropped_small"] += 1; continue
                    except ValueError:
                        pass
                    share = (nb[i]/run_total) if (i < len(nb) and run_total) else 1.0
                    if share < MIN_SHARE_OF_RUN:
                        stats["dropped_low_share"] = stats.get("dropped_low_share", 0) + 1
                        continue
                    stats["md5_parts"] += 1
                    md5f.write(f"{m}\t{b}\t{share:.6f}\t{n_files}\t{meta}\n")

                rc, bc = (r.get("read_count") or "").strip(), (r.get("base_count") or "").strip()
                if rc.isdigit() and bc.isdigit() and int(rc) > 0 and int(bc) > 0:
                    stats["num_keys"] += 1
                    numf.write(f"{rc}:{bc}\t{meta}\n")
            fh.close()
        except (EOFError, OSError, csv.Error) as e:
            stats["bad_files"] += 1
            print(f"  !! skipped incomplete {os.path.basename(f)}: {e}", file=sys.stderr)

    md5f.close(); numf.close()
    for k, v in stats.items():
        print(f"{k}\t{v}")

if __name__ == "__main__":
    main()
