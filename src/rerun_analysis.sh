#!/bin/zsh
set -e
cd ~/Downloads/dig
echo "=== rebuilding key streams with the csv-quoting fix ==="
for S in exploratory heldout all; do
  python3 src/build_keys.py --set $S 2>/dev/null | sed "s/^/  $S /"
  LC_ALL=C sort -S 2G -k1,1 out/keys_md5_$S.tsv -o out/keys_md5_$S.sorted.tsv
  LC_ALL=C sort -S 2G -k1,1 out/keys_num_$S.tsv -o out/keys_num_$S.sorted.tsv
done
echo "=== event census ==="
for S in exploratory heldout all; do
  python3 src/events2.py --keys out/keys_md5_$S.sorted.tsv --label "$S" \
     --out out/events2_$S.json --dump out/events2_$S.jsonl > out/events2_$S.txt
done
echo "=== within-study ==="
python3 src/within_study.py --keys out/keys_md5_all.sorted.tsv \
   --out out/within_study_all.json --dump out/within_study_all.jsonl --label all > out/within_study_all.txt
echo "=== numeric channel ==="
python3 src/numeric_channel.py --numkeys out/keys_num_all.sorted.tsv \
   --md5keys out/keys_md5_all.sorted.tsv --out out/numeric_all.json > out/numeric_all.txt 2>&1
echo "=== identity conflicts ==="
python3 src/identity_conflicts.py --md5keys out/keys_md5_all.sorted.tsv \
   --numkeys out/keys_num_all.sorted.tsv --out out/conflicts_all.json --confirm-max 150
python3 src/merge_confirmations.py
./src/assemble_report.sh
echo RERUN_DONE
