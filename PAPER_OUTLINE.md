# Preprint outline — working title

**"Content-identical sequencing data under conflicting identities in the public archives: a
census, a mechanism, and a fix the archives already compute"**

Target: bioRxiv (Bioinformatics) → *GigaScience* or *Database*.
Status: sections marked ☐ are not yet written or not yet supported by a finished analysis.

---

## Claim ladder (strongest first — the paper should be defensible if the lower rungs fail)

1. **The detection gap is real and mechanical.** `fastq_md5` cannot see content duplicates
   because ENA regenerates FASTQ with the accession in every read header. Measured: 22,044
   distinct values, 0 collisions, in one 15,999-run window. *Evidence: complete. Unarguable.*
2. **Duplicates are common and cross institutional boundaries.** 201 events / 507 studies /
   25,082 runs / 10.83 TB over 6.83M count-verified runs; 31 events cross institutions.
   *Evidence: complete, preregistered, held-out.*
3. **A subset declares incompatible biological identities.** 40 study pairs after a hand audit
   of all 67 automated flags; in 15, NCBI's own STAT analysis names the incorrect record.
   *Evidence: complete (log/07). Reduced from the original 67 — report the reduction.*
4. **Two distinct mechanisms, not one.** ENA side: the same file uploaded twice. NCBI side:
   *different* uploads producing identical loaded runs (JCVI plate GK7RZZV) — consistent with
   demultiplexing/attachment error. *Evidence: complete (log/06).*
5. **The archive already computes the fix.** NCBI's base composition and STAT tables are
   content fingerprints, served per run, not exposed in bulk and not checked at submission.
   *Evidence: complete.*
6. ☐ **Downstream consequence.** 260 groups put the same TB data under 282 different BioSamples,
   so BioSample-level de-duplication fails. Whether a *published* cluster is affected is
   preregistered in log/08 and **not yet tested**. If null, say so in the abstract.

## Figures
1. The mechanism: one uploaded object → two accessions → two `fastq_md5`, one `submitted_md5`.
2. Census: events/runs/TB by year, exploratory vs held-out split marked.
3. The 67 → 40 audit waterfall, by category.
4. STAT adjudication: declared label vs archive's own taxonomy, the 15 resolved cases.
5. Channel comparison: numeric (9%) vs composition (63%+) vs submitted_md5 (ground truth).
6. ☐ TB component graph: 9 studies, 3 institutions, 282 BioSamples over 260 datasets.

## Sections
- Introduction — archives as infrastructure; prior work (Gabdank 2018 ENCODE; Chen & Zobel
  duplicate-detection benchmarks; ENA post-deposition curation *Database* 2016); the gap.
- Methods — window pull + count validation; exploratory/held-out; md5, numeric and composition
  channels with measured precision for each; verification hierarchy (download+hash → NCBI
  composition → read comparison → range check); taxonomy resolution and the curation categories.
- Results — claims 1-5 above.
- Limitations — verbatim from REPORT.md, plus: composition-channel FP rate; ENA-only exact
  coverage; the preregistration deviation; no cause attributed to any submitter.
- Recommendation — per-run content fingerprint (hash of sorted read sequences) exposed in bulk
  and checked at submission; a `duplicate_of` relation for legitimate re-deposits.

## Data availability
Code + logs: github.com/RedCat888/insdc-duplicate-census. ☐ Zenodo DOI for the frozen snapshot
and the 132 validated window files.

## Authorship / ethics
- ☐ Faculty co-author (UTD bioinformatics/systems biology) before submission.
- No submitter is accused of misconduct anywhere in the text. Duplicates are described as
  deposition errors or undocumented re-deposits; cause is stated as not determinable from
  public data.
- ☐ Archives contacted (outreach/01, 02) and their responses represented, before posting.
- ☐ MGH authors contacted (outreach/03) and their answer incorporated, before the donor case
  appears in any public draft.
