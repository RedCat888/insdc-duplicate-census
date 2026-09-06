#!/bin/zsh
# Pull all ENA read_run metadata, chunked by first_public month/year.
OUT=~/Downloads/dig/data/ena
F="run_accession,experiment_accession,sample_accession,study_accession,secondary_study_accession,submission_accession,tax_id,scientific_name,library_strategy,library_source,library_selection,instrument_platform,instrument_model,read_count,base_count,fastq_md5,fastq_bytes,submitted_md5,submitted_bytes,submitted_format,center_name,broker_name,first_public,last_updated"
pull(){ # $1=label $2=start $3=end
  local f="$OUT/$1.tsv.gz"
  [[ -s "$f" ]] && { echo "skip $1"; return; }
  local q="first_public%3E%3D$2%20AND%20first_public%3C%3D$3"
  curl -s --max-time 1800 --retry 4 --retry-delay 10 \
    "https://www.ebi.ac.uk/ena/portal/api/search?result=read_run&query=$q&fields=$F&limit=0&format=tsv" \
    | gzip > "$f"
  echo "$1 $(gzcat $f | wc -l)"
}
pull pre2010 1990-01-01 2009-12-31
for y in {2010..2013}; do pull $y $y-01-01 $y-12-31; done
for y in {2014..2026}; do
  for m in 01 02 03 04 05 06 07 08 09 10 11 12; do
    case $m in 01|03|05|07|08|10|12) d=31;; 04|06|09|11) d=30;; 02) d=29;; esac
    pull ${y}-${m} ${y}-${m}-01 ${y}-${m}-${d}
  done
done
echo DONE_PULL_ENA
