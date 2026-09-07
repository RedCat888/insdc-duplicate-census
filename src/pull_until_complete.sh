#!/bin/zsh
# Keep retrying any census window that is still missing, until all are present or we give up.
# Truncation is transient, so a straight retry is the right remedy; each attempt is still
# accepted only if its row count equals ENA's own count for the same window.
cd ~/Downloads/dig
for attempt in 1 2 3 4 5 6 7 8; do
  python3 - <<'PY'
import glob, os
have={os.path.basename(f)[:-7] for f in glob.glob('data/ena/*.tsv.gz')}
miss=[l.strip() for l in open('src/chunks.txt')
      if l.split()[0] not in have and l.split()[1] < '2019-01-01']
open('src/chunks_left.txt','w').write("\n".join(miss)+("\n" if miss else ""))
print(f"attempt: {len(miss)} census windows still missing")
PY
  n=$(grep -c . src/chunks_left.txt 2>/dev/null || echo 0)
  [[ "$n" -eq 0 ]] && { echo CENSUS_ALL_PRESENT; break; }
  xargs -P 4 -n 3 ./src/pull_one.sh < src/chunks_left.txt
done
