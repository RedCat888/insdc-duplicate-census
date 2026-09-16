# Log 09 — The composition channel: extending the exact census to NCBI-submitted runs (2026-09-15)

## The plan that didn't survive contact
REPORT.md ranked next step #1 was: NCBI's per-run XML exposes the *submitted* file's MD5
(`<SRAFile supertype="Original">`), so sweep it over the numeric-channel candidates and turn the
SRR/DRR lower bound into a real checksum census.

First probe (log/06): **the Original MD5s differ, or are absent, for every one of the previously
confirmed NCBI-side duplicates.** SRR070588 uploaded `GK7RZZV.VCU148-…tar`; SRR071318 uploaded
`jtc_sff_…BZ1154PEPOOL2-POOL…` — different files, same loaded reads. The NCBI-side mechanism is
not "the same file uploaded twice"; it is "different uploads that yield the same run", consistent
with demultiplexing or plate-region attachment errors at or before load. A submitted-checksum
sweep would have found none of them.

So the exact channel on the NCBI side is **NCBI's own base composition**: `total_spots` plus the
exact A/C/G/T/N counts, computed from the loaded reads and therefore independent of file format,
compression, read headers, and which archive holds the run. Available for ~96% of runs, and
fetchable in batches of 200 accessions via E-utilities efetch (`db=sra`) — ~175 runs/s with an
API key, so the whole candidate set is a ~25-minute sweep rather than a per-run crawl.

## Sweep
`src/efetch_sweep.py` over the 491,634 runs that sit in any multi-run numeric group
(`out/candidate_runs_multi.txt`), writing one JSON record per run to `out/efetch_multi.jsonl`:
composition, spots, bases, Original files, Primary-ETL md5, study/BioProject/BioSample/taxon,
center, alias, platform, strategy. Resumable; failures land in `.failed` for retry.

## Precision, measured not assumed
The composition key is five numbers summing to `total_bases`, not a cryptographic hash, so its
precision has to be measured. The ERR region is the test bed: `submitted_md5` is present for
100% of ERR runs, so for ERR-only cross-study composition groups we can ask whether the exact
channel agrees.

On the first 255,610 records swept (partial, full numbers pending):

| | |
|---|---|
| composition groups with >1 run (≥1000 spots) | 25,655 |
| … spanning >1 study | 17,865 |
| … spanning >1 BioSample | 20,178 |
| … with no ERR run on either side (**new territory**) | 5,785 |
| … with conflicting declared taxa | 3,494 |
| ERR-only cross-study groups | 11,024 |
| … also sharing a `submitted_md5` | **6,979 (63.3%)** |

**63% precision against the submitted-checksum ground truth, versus 9% for the read-count +
base-count numeric channel.** A seven-fold improvement, and the first channel that works on the
SRR/DRR side at all.

## The 37% is not (all) error — and that is the next measurement
A composition group whose members do *not* share a `submitted_md5` is one of two things:
1. the same reads uploaded as a **different file** (tar vs SFF, re-compressed, renamed) — which
   is exactly the JCVI pattern above, a true duplicate the checksum cannot see; or
2. a genuine **composition collision** — two different datasets that happen to share spot count
   and all five base counts.

Nothing in the metadata separates these. `src/composition_collision_test.py` does it the only
honest way: a seeded random sample of NOT-CONFIRMED groups, first 2,000 reads downloaded for two
runs each, sequences compared with headers ignored. The refutation rate is the composition
channel's measured false-positive rate and **will be reported whatever it is** — if it is high,
the composition channel is a candidate generator like the numeric one, and every claim from it
stays conditional on per-pair confirmation. Pre-registered here before the run.

Note the direction of the bias either way: 63% is a *floor* on precision, because case 1 is a
true duplicate scored as "not confirmed".

## What this changes in the paper
- Ranked next step #1 is answered, but not as predicted: the submitted-checksum extension is the
  wrong tool for the NCBI side, and the reason why (different uploads, identical loaded runs) is
  itself a finding about a second, distinct mechanism.
- The census gains a channel that reaches SRR/DRR at measured 63%+ precision instead of 9%.
- The proposed fix to the archives gets stronger: NCBI **already computes** the content
  fingerprint that would catch this, and serves it per run. It is simply not exposed in bulk and
  not checked at submission.
