#!/bin/zsh
# Full reproduction from a clean clone. No credentials required anywhere.
# Total: ~1-2 h of ENA portal API downloads (~8 GB gz) + ~20 min of local analysis.
set -e
cd "$(dirname "$0")"
mkdir -p data/ena out log

echo "[1/6] pull all ENA read_run metadata (43.8M runs, chunked by first_public month)"
xargs -P 5 -n 3 ./src/pull_one.sh < src/chunks.txt
./src/pull_one.sh pre2014 1990-01-01 2013-12-31 || true

echo "[2/6] build key streams (exploratory = first_public < 2014-09-01, heldout = rest)"
for S in exploratory heldout all; do
  python3 src/build_keys.py --set $S
  LC_ALL=C sort -S 1G -k1,1 out/keys_md5_$S.tsv -o out/keys_md5_$S.sorted.tsv
  LC_ALL=C sort -S 1G -k1,1 out/keys_num_$S.tsv -o out/keys_num_$S.sorted.tsv
done

echo "[3/6] event-level census (primary result)"
for S in exploratory heldout all; do
  python3 src/events2.py --keys out/keys_md5_$S.sorted.tsv --label "$S" \
      --out out/events2_$S.json --dump out/events2_$S.jsonl
done

echo "[4/6] numeric channel calibrated against md5 truth"
python3 src/numeric_channel.py --numkeys out/keys_num_all.sorted.tsv \
    --md5keys out/keys_md5_all.sorted.tsv --out out/numeric_all.json

echo "[5/6] ground-truth verification: download the actual files and hash them"
python3 src/verify_events.py --events out/events2_all.jsonl --n 25 --out out/verify_events.json

echo "[6/6] publication linkage via Europe PMC accession index"
python3 src/pub_links.py --events out/events2_all.jsonl --out out/publinks_all.json
echo "done - see out/ and log/"
