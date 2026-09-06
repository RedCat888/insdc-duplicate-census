# PREREGISTRATION — frozen 2026-09-06, before touching held-out data
Project: checksum census of duplicate raw-read deposits in INSDC (via ENA portal API).

## Data split (declared now, enforced in code)
- **EXPLORATORY (already seen):** ENA read_run records with `first_public <= 2014-08-31`
  (n = 849,092 rows across 14 monthly/annual chunks). All pipeline design, filter
  thresholds and artifact rules are fixed on this set only.
- **HELD OUT (untouched until the pipeline is frozen):** `first_public >= 2014-09-01`
  (~43.0M runs). Not to be read by any analysis script until `FROZEN` is written into
  `src/params.py` and committed.

## What I already know from the exploratory set (declared, so it can't be smuggled in later)
- 34.3% of exploratory runs carry a non-empty `submitted_md5`.
- 832 md5 values appear in >1 run; 224 span >1 study; 67 span >1 submitting center.
- One verified case: ERR011033 (MPI-EVA, PRJEB2072, 2010-05-07) and ERR208589
  (Uppsala, PRJEB1198, 2012-12-23) share filename ESJK8KC01.sff, md5
  18811b69387880657958c49b4e37274c and 212,785,687 bytes; different sample accessions;
  `fastq_md5` differs between them.
- One suspicious case: ERR016531 (Liverpool, wheat 454 study) and ERR024102 (IBB PAS,
  potato genome study) share submitted md5 aab383dc74a0d6ff3ab7531cc0416648 but ENA
  reports different base_counts (595,849,249 vs 332,280,492).

## Hypotheses and disconfirmation thresholds (set now)

**H1 — the phenomenon is real at scale.**
Among held-out runs carrying a `submitted_md5`, the fraction belonging to a
cross-study byte-identical duplicate group is >= 0.05%.
*Disconfirmed if < 0.02%.* Report as null and stop.

**H2 — it is not just one trivial artifact.**
After removing (a) degenerate files (submitted_bytes < 1000, or md5 equal to the md5 of an
empty or empty-gzip file), and (b) groups where every member shares the same
`submission_accession`, at least 40% of cross-study duplicate groups survive.
*Disconfirmed if < 15%.*

**H3 — a nonzero subset crosses institutional or biological boundaries.**
At least 10% of surviving cross-study groups span >1 distinct `center_name`, and a
nonzero number span >1 `tax_id`. Cross-taxon groups are near-certain metadata errors and
are reported separately.
*Disconfirmed if cross-center < 3%.*

**H4 — the checksums mean what I think they mean.**
For a random sample of 20 surviving cross-study duplicate pairs (seeded, small files
preferred for bandwidth), downloading both submitted files and hashing locally reproduces
identical content in >= 90% of pairs.
*Disconfirmed if < 80%.* This is the decisive artifact check; failing it kills the project
regardless of H1-H3.

## Null / artifact tests committed to in advance
1. **Study-label shuffle.** Permute `study_accession` across runs within first_public year
   and recompute the cross-study fraction of duplicate groups. Duplicates are exact md5
   matches so they cannot be manufactured by chance; the test asks whether duplicates are
   *structured* with respect to studies. Prediction: observed cross-study fraction is
   markedly LOWER than shuffled (duplicates cluster within study/submission).
2. **Numeric-fingerprint chance model.** For the secondary channel (matching on
   `read_count` + `base_count` where `submitted_md5` is absent), shuffle `base_count`
   across runs to measure the chance-collision rate, and report the numeric channel only
   as an upper bound with that baseline subtracted.
3. **Broker concentration.** If >70% of surviving groups come from one `broker_name` or one
   `center_name`, treat as a submission-pipeline artifact, not a general phenomenon.
4. **Empty/sentinel md5 scan** before anything else.
5. **Temporal replication.** Rate computed independently per year; the claim requires it to
   be present across multiple years, not a single-year spike.

## Reported numbers must include
- The count of distinct analyses run (tally kept in `log/99-tally.md`).
- Confidence intervals on all proportions (Wilson).
- The verification sample results, including failures.

## Pre-committed stopping rule
If H1 or H4 is disconfirmed, I write it up as a documented null and move to candidate #2
(retraction propagation into curated bio-databases). I do not narrow the scope to rescue it.

---
# AMENDMENT 1 — 2026-09-06, made on EXPLORATORY data only, before any held-out analysis

Running the frozen pipeline on the exploratory set exposed two defects in the
preregistered metrics. Both are recorded here rather than silently fixed.

**Defect A — wrong unit of analysis.** 58 of 181 surviving groups were "cross-taxon", but
56 of those 58 are the *same* event: Southern Medical University deposited PRJEB1720
(tax 256318, "metagenome") and then PRJEB4562 (tax 408170, "gut metagenome") containing 56
byte-identical files. Counting md5 groups counts one re-deposit 56 times. Group-level
percentages are therefore meaningless as independence measures.
**Fix:** the unit of analysis becomes a **duplication event** = a connected component of the
graph whose nodes are studies and whose edges are "these two studies share >=1
byte-identical submitted file". Event-level counts are primary; run-level fractions
(each run counted once) remain valid and are also reported. Group-level counts are dropped.

**Defect B — center_name aliasing.** "CRUK-CRI", "Cancer Research UK Cambridge Institute"
and "CR-UK Cambridge Institute" are one institution; "Max Planck Institute for Evolutionary
Anthropology;MPI-EVA" repeats itself. Raw `center_name` inequality overstates
cross-institution duplication.
**Fix:** normalise center names (lowercase, strip punctuation, drop the stopword tokens
university/institute/institution/research/national/center/centre/for/of/the/laboratory/
lab/college/hospital/school/dept/department/genomics/genome/sequencing/facility/ltd/gmbh/
inc/the) and treat two centers as distinct only if their remaining token sets are disjoint.
This is conservative: it under-counts genuine cross-institution cases rather than over-counting.

**Revised H3:** at least 10% of duplication *events* span >1 normalised center.
*Disconfirmed if < 3%.*
**H1 and H2 thresholds are unchanged** (run-level and event-level respectively; H2 now reads
"at least 40% of cross-study *events* survive the degenerate + same-submission filters").
**H4 (download-and-hash verification) unchanged and still decisive.**

No held-out data has been read at this point. Exploratory numbers to date, for the record:
279,612 md5-bearing runs; 0.290% [0.271, 0.311] of runs in any duplicate group; 0.088%
[0.077, 0.099] in a cross-study group; 182 cross-study groups; median gap between the two
deposits 97 days, max 1533 days, zero same-day.

---
# AMENDMENT 2 — 2026-09-06, still EXPLORATORY only, still no held-out data read

Two further defects found by eyeballing all 15 exploratory events one at a time.

**Defect C — empty study_accession treated as a study.** 26,821 of 831,164 exploratory rows
(3.227%) carry an empty `study_accession`; only 8 of those are ERR runs, but one of them
produced a spurious "cross-study" event (`studies=['', 'PRJEB4210']`). It matters much more
for the numeric channel, which includes SRR runs.
**Fix:** rows with an empty study_accession are dropped from both key streams.

**Defect D — accessory files inside multi-file submissions.** ERR163011 (Complete Genomics)
submits an entire ASM directory: hundreds of files (`cnvDetailsBeta-*`, `evidenceDnbs-chr1*`,
...). A 2,707-byte CNV summary TSV was byte-identical to one in another study and generated a
"duplicate dataset" event between VIB-UGent and Leeds. This is a shared accessory file, not a
shared dataset.
**Fix:** the matched file must be >= 10% of its run's total submitted bytes, and >= 10,000
bytes. Measured on the exploratory set, this drops exactly 2 of 180 cross-study groups - the
two Complete Genomics artifacts - and keeps all 178 others (share distribution: 98 groups at
share >= 0.5, 80 at 0.1-0.5, 2 below 0.1).

Thresholds were chosen from the exploratory share distribution and are now frozen.
