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
