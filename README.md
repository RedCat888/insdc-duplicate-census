# A checksum census of duplicate raw-read deposits in the INSDC sequence archives

Public data only, no credentials anywhere. Everything is reproducible from a clean clone
with `./run_all.sh`.

## What this is
The European Nucleotide Archive publishes, for every sequencing run, the MD5 checksum of the
file the submitter actually uploaded (`submitted_md5`), plus read and base counts. Nobody has
used that to ask a simple question: **how often is the same raw sequencing data present in the
archive more than once, under separate accessions and separate study identities?**

## Why it has not been asked
The obvious field is a trap. `fastq_md5` — the checksum most people would reach for — is
useless for this, because ENA regenerates FASTQ per accession and the read headers embed the
run accession. Two byte-identical datasets therefore get *different* `fastq_md5`. Measured:
138,552 distinct `fastq_md5` across 138,552 checksum-bearing runs released in 2012, i.e. not a
single collision. The signal lives only in `submitted_md5`, which is present for 100% of ERR
(ENA-submitted) runs and 0% of SRR/DRR.

## Data and licence
- ENA Portal API (`https://www.ebi.ac.uk/ena/portal/api/`), `result=read_run`, all
  43,824,523 runs, chunked by `first_public` month. EMBL-EBI Terms of Use: the data are
  freely available and redistributable, INSDC records carry no restriction on reuse.
- NCBI SRA per-run XML (`trace.ncbi.nlm.nih.gov/Traces/sra-db-be/run_new`) for exact base
  composition — US Government work, public domain.
- ENA taxonomy REST API for tax_id lineages.
- Europe PMC REST for the accession→publication index (CC-BY).

## Layout
    src/       pipeline (see run_all.sh for order)
    log/       preregistration, amendments, and an honest worklog including dead ends
    out/       results
    data/      downloaded metadata (not committed)

## Reading order for someone checking this work
1. `log/02-preregistration.md` — hypotheses, disconfirmation thresholds, and the
   exploratory/held-out split, frozen before the held-out data was touched, plus two
   amendments made on exploratory data and recorded rather than hidden.
2. `log/01-candidates-and-decision.md` — the candidate spread and what was killed.
3. `log/03-worklog.md` — what failed, including a false refutation that took an hour to
   understand.
4. `REPORT.md` — the finding.
