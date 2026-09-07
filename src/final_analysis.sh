#!/bin/zsh
set -e
cd ~/Downloads/dig
echo "=== [A] validate every file on disk against ENA's own counts, and measure coverage ==="
python3 src/validate_chunks.py --only-present --out out/chunk_validation_final.json 2>&1 | tail -8
python3 - <<'PY2'
import json, os
d=json.load(open(os.path.expanduser("~/Downloads/dig/out/chunk_validation_final.json")))
bad=d.get("bad") or []
if bad:
    # a window that does not match its own count is removed from the analysis entirely,
    # rather than being analysed as if complete
    for lab in bad:
        p=os.path.expanduser(f"~/Downloads/dig/data/ena/{lab}.tsv.gz")
        if os.path.exists(p): os.rename(p, p+".REJECTED")
    print(f"quarantined {len(bad)} windows that failed their count check")
print("coverage:", d.get("coverage"), "rows:", d.get("rows_total"), "of", d.get("archive_total"))
PY2

echo "=== [C] build key streams ==="
for S in exploratory heldout all; do
  python3 src/build_keys.py --set $S 2>/dev/null | sed "s/^/  $S /"
  LC_ALL=C sort -S 2G -k1,1 out/keys_md5_$S.tsv -o out/keys_md5_$S.sorted.tsv
  LC_ALL=C sort -S 2G -k1,1 out/keys_num_$S.tsv -o out/keys_num_$S.sorted.tsv
done

echo "=== [D] event census: exploratory (seen) then HELD OUT then all ==="
for S in exploratory heldout all; do
  python3 src/events2.py --keys out/keys_md5_$S.sorted.tsv --label "$S" \
      --out out/events2_$S.json --dump out/events2_$S.jsonl > out/events2_$S.txt
  echo "  $S -> out/events2_$S.json"
done

echo "=== [E] within-study sample duplication ==="
python3 src/within_study.py --keys out/keys_md5_all.sorted.tsv \
    --out out/within_study_all.json --dump out/within_study_all.jsonl --label all > out/within_study_all.txt

echo "=== [F] numeric channel calibration against md5 truth ==="
python3 src/numeric_channel.py --numkeys out/keys_num_all.sorted.tsv \
    --md5keys out/keys_md5_all.sorted.tsv --out out/numeric_all.json > out/numeric_all.txt 2>&1

echo "DONE_FINAL_ANALYSIS"
