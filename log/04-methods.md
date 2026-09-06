# Methods (settled; numbers live in REPORT.md)

## Data acquisition
All 43,824,523 `read_run` records in the ENA Portal API, requested as TSV in windows of
`first_public` (monthly to 2018, 10-day slices from 2019 where monthly responses exceed
~200k rows), 24 fields per run. No credentials. Two acceptance conditions per window:
`curl --fail` must exit 0 (the response is written to a file, never piped, so curl's status
is not swallowed by a downstream `gzip`), and the row count must equal ENA's own
`/count` for the identical window. Windows that fail are re-fetched, and if a window will
not come back intact it is split into single days. `src/validate_chunks.py` re-checks every
file on disk against the API afterwards and also reports files present on disk that are not
in the canonical window list (which would otherwise be double-counted).

## The two detection channels

**Exact channel (`submitted_md5`).** ENA publishes the MD5 of each file as the submitter
uploaded it. Coverage is 100% of ERR (ENA-submitted) runs and ~0% of SRR/DRR, so this channel
is a *complete census of the ENA-submitted subset*, not a sample of INSDC. A match means two
runs list a byte-identical submitted FILE; because a run may submit several files it does not
by itself mean the two RUNS hold the same data. Filters: the matched file must be >= 10,000
bytes and >= 10% of its run's total submitted bytes (this removes accessory files inside
multi-file submissions such as Complete Genomics ASM directories); runs with an empty
`study_accession` are dropped; groups all sharing one `submission_accession` are dropped.

`fastq_md5` is useless here and this is the reason the phenomenon is unexamined: ENA
regenerates FASTQ per accession with the run accession embedded in read headers, so identical
data receives different `fastq_md5`. Verified on ERR011033/ERR208589 — same
`submitted_md5` (18811b69...), different `fastq_md5` (44e45fec... vs 70822fe5...).

**Numeric channel (`read_count` + `base_count`).** Covers every run including SRR/DRR, using
ENA's own accounting (NCBI's `total_bases` differs for the same run because of clipping, so
counts are never compared across archives). This channel is high recall / low precision and
is used ONLY to generate candidates: measured against the ERR labelled set, cross-study
recall 0.983 [0.942, 0.995] and precision 0.055 [0.046, 0.065]. Restricting to pairs where
`base_count` is not an exact multiple of `read_count` (variable-length reads, so base_count
carries real entropy) raised precision to 1.000 [0.806, 1.000]. Round subsample counts such
as `4000000:200000000`, shared by 1,145 runs across 10 studies and four different species,
are exactly the low-entropy noise this excludes.

## Confirmation — nothing is reported on metadata alone
1. **NCBI run composition**: `total_spots` plus exact A/C/G/T/N counts from the per-run XML.
   Archive-independent, invariant to file format and compression.
2. **Read-level comparison**: the first 2,000 sequences of each run from ENA's FASTQ, headers
   ignored. Costs the same for a 200 GB run as for a 2 MB one, so verification is not biased
   toward small files.
3. **Download and hash**: both submitted files fetched and MD5'd locally.
4. **HTTP range check** for multi-GB files: size plus MD5 of the first and last 5 MB.

## Unit of analysis
A **duplication event** is a connected component of the graph whose nodes are studies and
whose edges are "these two studies share >= 1 byte-identical submitted file". One re-deposit
of a whole study is one event, not one per file. Run-level fractions count each run once.
Group-level percentages are not reported: they inflate a single re-deposit of 56 files into
56 "findings".

## Preregistration
`log/02-preregistration.md`, frozen before any held-out data was read, with an
exploratory window (`first_public < 2014-09-01`) and a held-out remainder, and two amendments
made on exploratory data and recorded rather than hidden.
