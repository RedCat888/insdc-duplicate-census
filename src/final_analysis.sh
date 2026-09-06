#!/bin/zsh
set -e
cd ~/Downloads/dig
echo "=== [A] fill any missing windows, splitting stubborn ones into days ==="
python3 src/pull_fill.py 2>&1 | tail -30

echo "=== [B] validate every file on disk against ENA's own counts ==="
python3 src/validate_chunks.py --chunks src/chunks_final.txt --out out/chunk_validation_final.json 2>&1 | tail -8

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
