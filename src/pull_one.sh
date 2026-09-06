#!/bin/zsh
OUT=~/Downloads/dig/data/ena
F="run_accession,experiment_accession,sample_accession,study_accession,secondary_study_accession,submission_accession,tax_id,scientific_name,library_strategy,library_source,library_selection,instrument_platform,instrument_model,read_count,base_count,fastq_md5,fastq_bytes,submitted_md5,submitted_bytes,submitted_format,center_name,broker_name,first_public,last_updated"
label=$1; start=$2; end=$3
f="$OUT/$label.tsv.gz"
[[ -s "$f" ]] && { echo "skip $label"; exit 0; }
q="first_public%3E%3D$start%20AND%20first_public%3C%3D$end"
curl -s --max-time 3000 --retry 5 --retry-delay 15 \
  "https://www.ebi.ac.uk/ena/portal/api/search?result=read_run&query=$q&fields=$F&limit=0&format=tsv" \
  | gzip > "$f.part"
if [[ -s "$f.part" ]] && gzcat "$f.part" >/dev/null 2>&1; then
  mv "$f.part" "$f"; echo "$label $(gzcat $f | wc -l)"
else
  rm -f "$f.part"; echo "$label FAILED"
fi
