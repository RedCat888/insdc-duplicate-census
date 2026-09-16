# Log 06 — Extending the exact channel to NCBI-submitted runs (started 2026-09-15)

## What was planned
REPORT.md "Ranked next steps" #1: NCBI's per-run XML exposes the original uploaded file's MD5
(`<SRAFile supertype="Original">`), so a targeted sweep over the numeric-channel candidates
should turn the SRR/DRR lower bound into a real checksum census.

## What the first probe showed (13 runs, all previously confirmed content-identical by composition)

| pair (confirmed identical by A/C/G/T/N + spots) | Original file A | Original file B |
|---|---|---|
| SRR070588 / SRR071318 (S. lugdunensis / S. epidermidis, JCVI) | `GK7RZZV.VCU148-BP3KB-A7NB-01-609.tar` md5 `6963f045…` | `jtc_sff_1127377707094_BZ1154PEPOOL2-POOL…` md5 `782225d9…` |
| SRR063729 / SRR063733 / SRR063735 (three genera, JCVI) | `GHYYG3201.sff.HMP116-…` `60387f4b…` | `GHYYG3201.sff.HMP120-…` `1d1293a4…` / `GHYYG3201.sff.HMP121-…` `d3e1e15a…` |
| SRR064495 / SRR064997 (JCVI) | `F3N4XA3.SAUREUSCA05-….tar` `7bdf1159…` | `jtc_sff_…SABZ761POOL1-POOL-…` `1454dbd2…` |
| SRR1021212 / SRR1031053 (E. coli / Listeria, NIST) | `CCQMMicroDefault20130121.sff` `629ce99f…` | **no Original file recorded** |
| SRR543504 / SRR578255 (donor 2 / donor 7) | **none** | **none** |

**The submitter-file MD5s differ, or are absent, for every confirmed NCBI-side duplicate.**
The files uploaded were different files (different names, sizes, checksums — in several cases a
per-sample tar on one side and a multi-sample *POOL* SFF on the other); the *loaded run content*
is nonetheless identical.

## What this means
1. The proposed extension (exact submitter checksum over SRR/DRR) would have **missed every
   confirmed NCBI case**. Extending it is still worth doing — it will find the ERR-style
   "same file uploaded twice" events on the NCBI side — but it is not the universal channel.
2. The **base-composition fingerprint** (total_spots + exact A/C/G/T/N) is the only channel that
   is archive-independent, format-independent and header-independent, and it is available in
   *batched* E-utilities efetch (`db=sra`, many ids per call, 10 req/s with an API key). That
   makes a much larger composition census affordable.
3. **New hypothesis (H5, exploratory — not preregistered):** on the NCBI side a distinct
   mechanism exists in which different uploaded files yield identical loaded runs. Consistent
   with demultiplexing / plate-region extraction errors at or before load: SRR070588's original
   file and SRR071318's run alias both name 454 plate `GK7RZZV`; the three-genera group all name
   plate `GHYYG3201`. Whether the error is the submitter's (wrong barcode → wrong sample tar) or
   the archive's (wrong file attached at load) cannot be decided from checksums alone. Testable:
   for each confirmed NCBI pair, do the Original files themselves differ in content
   (download + compare) — if they do, the identity was created at load; if the "different" files
   are actually the same reads in different wrappers, it is a submitter-side re-wrap.

## Disconfirmation
If, over the full candidate sweep, a large majority of composition-confirmed NCBI duplicates DO
share an Original MD5, then (1) is wrong in degree and the exact channel is sufficient; H5 would
then describe a minority mechanism. Recorded before running.

## Practical
- efetch batch: composition + originals for N accessions per request; `total_spots` on `<RUN>`.
- API key stored in `.secrets/ncbi_api_key` (mode 600, gitignored). Never in code or logs.
