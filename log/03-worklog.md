# Running worklog (including failures)

- **2026-09-06 venv creation failed** the first time (`.venv/bin/pip` missing, silent). Re-ran
  with output shown; worked. Used system python3 throughout instead.
- **csv.field_size_limit** blew up on the ENA TSV (a study description > 131072 chars).
  Patched to 10 MB and added `csv.Error` to the skip-list for partially written gz chunks.
- **MGnify downstream check: FAILED / VOID.** Queried
  `https://www.ebi.ac.uk/metagenomics/api/v1/studies?study_accession=PRJEB1720` etc. The API
  silently IGNORED the filter and returned the same default first page for all four
  accessions. Any conclusion from it would have been fabricated. Need the correct filter
  parameter or a different downstream resource. Not yet redone.
- **fastq_md5 is a trap.** 138,552 distinct values across 138,552 md5-bearing 2012 runs, i.e.
  perfectly unique. ENA regenerates FASTQ per accession, so identical content gets different
  fastq_md5. Confirmed directly on the MPI/Uppsala pair: same submitted_md5
  (18811b69...), different fastq_md5 (44e45fec... vs 70822fe5...).
- **submitted_md5 coverage is not random**: 100% of ERR runs, 0.0% of SRR (32/496,340) and
  0% of DRR. The exact channel is therefore a *complete census of the ENA-submitted subset*,
  not a sample of the archive. Stated as a scope limit, and motivates the numeric channel.
- **base_count is NOT comparable across archives.** ENA reports 22,740,036 bases for
  ERR011033; NCBI reports total_bases 23,406,608 for the same run (SFF clipping differs).
  All numeric fingerprinting must therefore stay inside one archive's own accounting.
- **NCBI run_new does not batch** (comma-separated accessions return nothing), so exact
  SRR-side confirmation is one HTTP request per run. Usable for targeted confirmation of a
  candidate list, not for a 43.8M-run sweep.
- **Bulk SRR checksums: DEAD END (checked, not assumed).** Downloaded a 25 MB prefix of
  `NCBI_SRA_Metadata_20260906.tar.gz` and extracted three `*.run.xml` files. The public dumps
  are stripped: RUN elements contain only accession/alias/IDENTIFIERS/EXPERIMENT_REF, with no
  `<DATA_BLOCK><FILES><FILE ... checksum=...>` section. So there is no bulk source of
  submitter checksums for SRR runs. Sizes checked: Full metadata 16.79 GB,
  SRA_Accessions.tab 32.34 GB, SRA_Run_Members.tab 3.88 GB, daily 6.94 GB.
  Consequence: the EXACT census is necessarily confined to ENA-submitted (ERR) runs; SRR/DRR
  must go through numeric candidates + per-run NCBI confirmation.
  Salvage: SRA `alias` often preserves the original filename (e.g. "8388_R1_001.fastq.gz").
- **Numeric-channel FP confirmed to be a real FP.** ERR296666 (Oxford, ERP003232) and
  ERR326475 (Sanger, ERP001505) share read_count 2,532,937 and base_count 506,587,400 exactly,
  but NCBI base composition differs completely (A: 124,294,807 vs 155,510,075). Chance
  collision on a fixed-100bp read count. Confirms the numeric channel needs exact confirmation.
- **AWS `sra-pub-metadata-us-east-1` returned an empty body** to an anonymous list-objects
  request. Not pursued further.
- **Novelty check that also produced the consequence.** Europe PMC's ACCESSION_ID index shows
  PRJEB1720 and PRJEB4562 are each cited by exactly one paper, and it is the SAME paper:
  PMID 26861660 / PMC4747322, "Value, but high costs in post-deposition data curation",
  *Database* 2016 - by the ENA curation team itself. Full text pulled (38,586 chars) and
  searched: 'duplicat' 0 hits, 'redundan' 0 hits, 'identical' 0 hits, 'same data' 0 hits,
  'resubmit' 0 hits. The paper lists both accessions side by side as independent studies in
  its ontology-annotation tables ("digestive tract UBERON:0001555 388 PRJEB1391, PRJEB4413,
  PRJEB1720, PRJEB7112, PRJEB4562, PRJEB3374"). So ENA's own curators counted 56
  byte-identical samples twice while writing a paper about curating exactly those samples.
- **Ruled out "ENA lets a run reference an existing file".** The two copies live at different
  physical paths - /vol1/run/ERR011/ERR011033/ESJK8KC01.sff and
  /vol1/run/ERR208/ERR208589/ESJK8KC01.sff - same filename, same md5, same byte count.
  The file is stored twice. This also makes redundant storage bytes a computable quantity.
- ENA holds 1,083,428 studies and 43,824,523 read_runs.
- **The most important methodological correction of the project: an md5 match is a FILE, not a RUN.**
  I ran run-level NCBI composition confirmation on the md5-channel pair ERR016531 / ERR024102
  and it came back REFUTED, which briefly looked like the whole approach was broken. It was
  not. ERR016531 (Triticum aestivum, U. Liverpool, PRJEB2264) submits TWO SFF files
  (`library06_GBSKQZK01.sff`, 1,695,787,424 B and `library06_GBSKQZK02.sff`, 2,167,347,440 B).
  ERR024102 (Solanum phureja, U. Dundee, PRJEB2338) submits ONE file, `GBSKQZK02.sff`,
  2,167,347,440 B, md5 aab383dc74a0d6ff3ab7531cc0416648 - byte-identical to the wheat run's
  second file. So the RUNS legitimately differ in content (1,222,730 vs 672,776 reads) while
  the FILE is shared. Same 454 region GBSKQZK02 sitting inside a wheat genome project and a
  potato genome project.
  Consequence for the pipeline: md5-channel claims are file-level and are exact by
  construction (128-bit digest plus identical byte count); they must be verified by
  downloading/range-checking the FILES. Numeric-channel claims are run-level and are verified
  by NCBI run composition. Mixing the two produces false refutations.
  This also means `MIN_SHARE_OF_RUN = 0.10` is doing real work but is not a duplicate-run
  test, and I should not describe md5 events as "duplicate runs".
- **Verification must not be size-biased.** The first event-stratified verification run
  attempted 10 events, verified 2/2, and SKIPPED 8 purely because the files exceeded a 120 MB
  cap - i.e. it silently sampled only small datasets. Fixed by adding a read-level fallback
  (compare the first 2000 sequences from ENA's FASTQ, headers ignored), which costs the same
  for a 200 GB run as for a 2 MB one.
- **NCBI taxdump download failed twice** (truncated at 1.2-1.6 MB of ~65 MB, under bandwidth
  contention with 10 parallel ENA pulls, `tar: Damaged tar archive`). Abandoned it and used
  ENA's taxonomy REST API with a local JSON cache instead - only a few thousand tax_ids
  actually appear in duplicate pairs, so per-id lookup is cheaper anyway.
- **SILENT DATA TRUNCATION - the worst bug of the project, caught late.** `pull_one.sh` piped
  `curl` into `gzip` and accepted the chunk if `gzcat` could read it. A truncated HTTP response
  still produces a perfectly valid gzip stream, so short downloads passed the integrity check
  silently. Detected only because the reported monthly run counts started clustering
  suspiciously near round numbers (144,991 / 134,991 / 149,994 / 124,991). Checked directly:
  2020-08 held 144,991 rows against ENA's own count of 250,426 for the same window - 42%
  of the month missing, with no error anywhere. 2019-03 (185,986) and 2012 (157,674) were
  exact, so the corruption is intermittent, not systematic, which is exactly what makes it
  dangerous.
  Fix: `pull_one.sh` now queries `ENA .../count` for the same date window and refuses any
  chunk whose row count does not match exactly; `src/validate_chunks.py` re-checks every
  chunk on disk against the API and lists the bad ones for re-download. Any result computed
  before this validation is not trustworthy and is recomputed.
- **Second integrity problem, found while fixing the first.** The original `pull_ena.sh`
  fetched 2010-2013 as ANNUAL files and hardcoded February as 29 days. Consequences:
  (a) non-leap Februaries (2015, 2017, 2018) queried `first_public <= YYYY-02-29`, which ENA
  accepted and which pulled March-1 runs in as well, so those chunks were supersets and their
  March-1 rows also appeared in the March chunk; (b) once the chunk list was regenerated at
  monthly granularity, the leftover annual files 2010-2013 no longer matched any chunk label
  and would have been globbed by `build_keys.py` ALONGSIDE the new monthly files, counting
  every 2010-2013 run twice.
  Both fixed by deleting the legacy files and regenerating `chunks.txt` from
  `calendar.monthrange`, with 10-day slices from 2019 on (where monthly responses exceed
  ~200k rows and were the ones that truncated). Validation of the final state is by
  `src/validate_chunks.py`, which now also reports files on disk that are not in chunks.txt.
- **Scope of the damage.** Validation of the 101 chunks present at the time: 64 OK, 37 bad.
  Truncation was concentrated from 2019 onward and was severe (2020-02 held 132,635 of
  422,278 runs, 69% missing). The exploratory results reported in Amendments 1-2 were computed
  partly from the un-validated annual 2010-2013 files, so they are being RECOMPUTED on
  validated data before anything is reported. The verified individual cases (the JCVI
  isolates, the wheat/potato file, the CTC donor pair) do not depend on metadata
  completeness at all - each was checked by fetching the actual data - so they stand.
- **THIRD and worst data bug: ENA's `<=` on a date is exclusive.**
  `first_public>=2010-10-18 AND first_public<=2010-10-18` returns **0**, even though
  DRR000006 has `first_public = 2010-10-18`. `>=2010-10-18 AND <=2010-10-19` returns 151, and
  `>=2010-10-18 AND <2010-10-19` returns the same 151. So `<=E` behaves as `<E`: the interval
  is half-open [S, E).
  Consequences, all silent:
   1. Every window I fetched was missing the runs released on its final day. Measured:
      Jan-2012 `[01-01,01-31]` = 10,350; Feb-2012 `[02-01,02-29]` = 7,155; the combined
      window `[01-01,02-29]` = 17,793, which is 288 more than the sum - those 288 are the
      Jan-31 runs that neither window contained.
   2. The 10-day slices lost day 10, day 20 and the month's last day.
   3. My "fix" of splitting stubborn windows into single days was worthless: `[d,d]` is empty
      by construction, so 172 daily chunks came back "OK 0" and PASSED validation, because
      the count endpoint uses the same semantics and also returns 0. Validating a query
      against the same query's count cannot catch a wrong query.
  Fix: windows are now half-open and expressed as consecutive boundaries,
  `>=start_i AND <=start_{i+1}`, which under the observed semantics partitions the timeline
  exactly. Monthly to 2018, 5-day slices from 2019. The new acceptance test is global and
  independent of the window semantics: **the sum of all window row counts must equal ENA's
  count for the whole archive (43,824,523)**. Per-window count agreement is necessary but,
  as bug 3 shows, nowhere near sufficient.
- **Transient truncation is real but retries fix it.** Five census windows failed their count
  check on the first pass: one with `curl rc=92` (HTTP/2 stream error), one 7% short
  (155,394 of 167,301), and three short by exactly 5 rows. The "exactly 5" pattern looked
  systematic and worth checking before loosening the acceptance rule, so w2018-07-01 was
  re-fetched cleanly and counted three ways: 157,563 from the count endpoint, 157,563 newlines
  after the header, 157,563 parsed CSV rows, 157,563 distinct run accessions. It was transient
  loss, not an endpoint disagreement. The strict equality check stays; failures are retried.
- **Two workers fetched the same five windows simultaneously** after the 2019+ queue resumed on
  the PRE_DONE marker while a targeted retry was already running. Harmless (temp files are
  PID-unique and either copy is valid) but it halved the useful bandwidth, so the duplicates
  were killed. Worth noting because throughput, not compute, was the binding constraint on this
  whole project: ENA delivers ~48 kB/s per connection and ~150-170 kB/s in aggregate no matter
  how many connections are opened.
- **FOURTH silent-corruption bug, and the subtlest: a stray double quote made csv swallow rows.**
  ENA emits some `center_name` values that begin with a lone `"` — e.g. the raw row for
  SRR1979557 ends `...\t"George Mason University\t\t2015-06-05\n`. Python's `csv.DictReader`
  treats `"` as a quote character by default even with `delimiter='\t'`, so it opened a quoted
  field and kept consuming *following lines* looking for a closing quote, merging many source
  records into one. 1,820 of 6,827,910 downloaded lines (0.027%) contain a double quote, and
  the damage propagated far past them: 38,894 of 6,089,213 numeric key lines (0.64%) came out
  with the wrong number of fields, which is how it was found - `numeric_channel.py` died with
  `KeyError: 'run_accession'`.
  Why this one is dangerous: a merged record can still produce a *well-formed* output line
  with silently wrong values. The md5 key stream had 0 malformed lines, which proves nothing
  about whether its records were mis-parsed. So the fix is applied and EVERY analysis is
  recomputed, not just the one that crashed.
  Fix: `csv.DictReader(..., quoting=csv.QUOTE_NONE)`, newline/CR stripped from field values,
  and `census.groups()` now skips and counts short lines instead of yielding a partial row
  that explodes several stages later.
- **Taxonomy resolution stalled on 404s.** `identity_conflicts.py` sat at 0% CPU for ~40 minutes
  after the "4,328 conflicting pairs" line. Cause: `taxonomy_ena.rec()` retried three times with
  backoff on ANY exception, and an unknown tax_id returns HTTP 404 — a definitive answer — so
  every unknown id cost ~6 s. Fixed by breaking immediately on 400/404: a known id now resolves
  from cache in 0.0 s and an unknown one costs 0.51 s. Lookup rate went from ~1 per 6 s to ~4/s.
- **NCBI rate-limits hard under sustained per-run XML fetching**, exactly as in the earlier OEIS
  work. The 150-pair confirmation sample slowed from ~25 pairs per 30 s to ~25 pairs per 15 min
  partway through. It was left to finish rather than killed, because `identity_conflicts.py`
  only writes its results at the end — a design flaw worth fixing before any larger sample.
- **Event-stratified verification pass: STARTED, NOT FINISHED at time of reporting.**
  `src/verify_events.py --events out/events2_all.jsonl --n 20` samples 20 of the 201
  duplication events at random and checks each by downloading both submitted files and hashing
  them locally, falling back to comparing the first 2,000 read sequences when a file exceeds
  the size cap (so the sample is not biased toward small datasets). It ran for over two hours
  without completing: each event needs up to 24 `filereport` calls to find a pair sharing a
  checksum, and then tens of MB of downloads, against an API that delivers ~150 kB/s.
  It writes `out/verify_events_all.json` only on completion, so it was left running rather
  than killed. **No number from this pass is used anywhere in the report.**
  The verification actually reported rests on: 8 pairs downloaded and hashed in full (8/8
  identical, and ENA's `submitted_md5` matched the bytes fetched in every case), 12
  organism-level conflicts confirmed exhaustively by NCBI composition *and* read-sequence
  comparison (12/12), a seeded random sample of 150 identity-conflict pairs checked against
  NCBI composition (146 confirmed / 2 refuted / 2 no fingerprint), and one multi-GB file pair
  range-checked at both ends.
  **Fixed and restarted.** Three changes: per-download timeout cut from 1800 s to 300 s (a
  single stalled transfer could previously block for half an hour), `filereport` probes per
  event cut from 24 runs to 10, and results now serialised to disk after EVERY event with a
  `complete` flag, so an interrupted run keeps everything it has done. Effect: the first event
  verified in 90 s, where the previous version ran 3 h 18 m and wrote nothing. Partial results
  are therefore usable at any moment, and whatever this run reaches is reported as a partial
  sample with its own n rather than as a completed check.

## Event-stratified verification: completed, and its two "failures" are not failures

The pass finished: **20 events sampled at random from the 201, 18 marked verified**. Both
non-verifying cases were investigated rather than reported as a bare ratio, and neither
refutes anything.

1. **PRJEB19032 / PRJEB19033 (ERR1797987) — untestable, not refuted.** The run has
   `read_count = 0` and ENA has generated no FASTQ for it, so the read-level comparison could
   not run at all. The harness recorded `identical_verified = False`, conflating "could not
   test" with "tested and refuted". That is a counting bug in the harness, not a finding.

2. **PRJEB15111 / PRJEB21528 — the file-vs-run distinction again.** The read-level test gave
   0/2000 matching reads, but the md5 event never claimed the RUNS were identical. Both runs
   submit two files; **file 0 is byte-identical** (md5 41388c88ba54b6fe68677115680a3d7c,
   2,709,108,614 bytes in both) while file 1 differs in size (2,859,925,013 vs 680,165,774).
   Independently checked by HTTP range request rather than trusting the metadata: same size,
   same MD5 of the first 5 MB, same MD5 of the last 5 MB. The file-level claim is CONFIRMED.
   Worth noting what the two filenames are:
   `140118_I175_FCH7NBRADXX_L1_RSZAXPI001572-93_1.fq.gz` in PRJEB15111 and
   `N1308.clean.trim.rmhost.rmhost.1.fq.gz` in PRJEB21528 — the second name asserts the data
   was cleaned, trimmed and host-depleted, and the bytes are identical to the first.

**Corrected accounting: 19 of 19 testable events confirmed at the level the claim is made,
0 refuted, 1 untestable.** This is the SECOND time a run-level test was applied to a
file-level claim (the first was wheat/potato, ERR016531/ERR024102). The lesson did not stick
the first time because the read-level fallback was added later and inherited the confusion.
Anyone extending this should make the harness carry the claim type with the claim.
