# Tally of everything tried (needed to interpret any reported number)

## Target selection
- Candidate archives probed for reachability: 18 endpoints (JPL CNEOS, IRIS FDSNWS, arXiv
  OAI-PMH, Chronicling America, GBIF, Retraction Watch/Crossref, CourtListener, OpenAlex,
  PMC OA, NASA PDS, Federal Register, COD, NCEI, MAST, USGS, NASA ADS, SIMBAD TAP, VizieR TAP).
- Research targets seriously considered: 10 (table in `01-candidates-and-decision.md`).
- Killed on novelty before investment: 1 (CNEOS fireballs x infrasound).
- Rejected on cost/priority/maintainer-already-does-it: 8.
- Novelty searches: 8 web, 5 Europe PMC structured queries, 4 full-text fetches
  (Chen & Zobel 2017 scope, PMC4747322 full text, NCBI SRA submission standards, GEO series
  relations).

## Analyses run
- Exploratory-set analyses before freezing: 3 (fastq_md5 collision test; submitted_md5
  collision test; concrete-pair inspection).
- Amendments to the frozen pipeline, all recorded: 2 (unit of analysis; empty study accession
  + accessory-file share threshold).
- Preregistration deviations, recorded: 1 (smoke-testing on held-out data).
- Scope decisions forced by measurement: 1 (census period restricted by API throughput).

## Verification performed (each an independent check of the actual data)
- Files downloaded and MD5'd locally: 8 pairs.
- Runs fingerprinted via NCBI exact base composition: 12 JCVI-style groups (12/12 confirmed),
  25 sampled non-ERR cross-study candidates (21 confirmed / 0 refuted / 4 no fingerprint).
- Read-level sequence comparisons (first 2,000 reads, headers ignored): 14.
- HTTP range checks of multi-GB files: 1 pair.
- Organism-level identity conflicts confirmed exhaustively: 12/12, 0 refuted.
- Deliberate negative control that came back REFUTED and is reported as such:
  ERR296666 / ERR326475 (identical read and base counts, completely different composition).

## Data-integrity failures found in my own pipeline (all fixed, all logged)
1. `curl | gzip` swallowed curl's exit status.
2. A truncated response still gzips cleanly, so the gzip-integrity check passed short files
   (2020-08 held 144,991 of 250,426 runs).
3. ENA's `first_public <= E` is exclusive of E, so every window lost its last day and
   single-day windows returned zero while passing their own count check.
4. Legacy annual files 2010-2013 would have been double-counted alongside monthly files.
5. February windows hardcoded to 29 days pulled March-1 runs into non-leap years.
6. Verification silently skipped 8 of 10 events for exceeding a file-size cap.

That is six ways the numbers could have been wrong. Five were found by checking against an
independent source; one (number 3) was found only because the reported counts looked
suspiciously round. Any figure in this report that is not accompanied by a stated check
should be treated with the same suspicion.
