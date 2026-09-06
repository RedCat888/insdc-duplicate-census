#!/bin/zsh
# Pull one ENA read_run metadata window. Robust against the two failure modes that bit us:
#   1. `curl | gzip` hides curl's exit status  -> write to a temp file, check curl's status
#   2. a truncated response still gzips cleanly -> compare row count with ENA's own count
setopt pipefail
OUT=~/Downloads/dig/data/ena
F="run_accession,experiment_accession,sample_accession,study_accession,secondary_study_accession,submission_accession,tax_id,scientific_name,library_strategy,library_source,library_selection,instrument_platform,instrument_model,read_count,base_count,fastq_md5,fastq_bytes,submitted_md5,submitted_bytes,submitted_format,center_name,broker_name,first_public,last_updated"
label=$1; start=$2; end=$3
f="$OUT/$label.tsv.gz"
[[ -s "$f" ]] && { echo "skip $label"; exit 0; }
q="first_public%3E%3D$start%20AND%20first_public%3C%3D$end"
tmp="$OUT/.$label.$$.tsv"

want=$(curl -sS --fail --max-time 600 --retry 4 --retry-delay 5 \
  "https://www.ebi.ac.uk/ena/portal/api/count?result=read_run&query=$q" | tail -1)
[[ -z "$want" ]] && { echo "$label FAILED (no count)"; exit 1; }

curl -sS --fail --max-time 2400 --retry 4 --retry-delay 10 --speed-time 120 --speed-limit 1000 \
  "https://www.ebi.ac.uk/ena/portal/api/search?result=read_run&query=$q&fields=$F&limit=0&format=tsv" \
  -o "$tmp"
rc=$?
if [[ $rc -ne 0 ]]; then rm -f "$tmp"; echo "$label FAILED (curl rc=$rc)"; exit 1; fi
got=$(( $(wc -l < "$tmp") - 1 ))
if [[ "$got" != "$want" ]]; then
  rm -f "$tmp"; echo "$label FAILED got=$got want=$want"; exit 1
fi
gzip -c "$tmp" > "$f.$$.part" && mv "$f.$$.part" "$f" && rm -f "$tmp"
echo "$label OK $got"
