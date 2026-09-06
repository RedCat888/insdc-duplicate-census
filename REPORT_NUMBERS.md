# Duplicate raw-read deposits in the INSDC sequence archives: a checksum census

Generated 2026-09-06 from the result files in `out/`. Every figure below is read from those files by `src/make_report.py`.

## Data completeness
- Windows checked against ENA's own counts: **101**, passing exactly: **64**, failing: **37**.
  - still failing: `2015-02 2017-02 2018-02 2018-11 2018-12 2019-01 2019-08 2019-09 2019-10 2019-11 2019-12 2020-01 2020-02 2020-03 2020-04 2020-05 2020-06 2020-07 2020-08 2020-09`

## Result 1 — the census (exact channel, complete for ENA-submitted runs)
- **exploratory (first_public < 2014-09-01)**: 278,484 checksum-bearing runs -> 622 files present under more than one run; 177 of those span more than one study; **12 duplication events** over 27 studies; 229 runs (0.0822% [0.0723, 0.0936] of checksum-bearing runs).
  - redundant storage: **0.701 TB** total (0.2148 TB across studies, 0.4859 TB within a study).
  - events spanning more than one institution (normalised names): 2; more than one taxon: 2; largest event: 5 studies / 64 shared files.
  - null test (study labels permuted, sizes preserved): observed 178 of 622 duplicate groups span studies; under permutation 618.8. Duplicates are far more concentrated inside single studies than chance, so the cross-study set is a genuine tail rather than an artefact of study sizes.
- HELD OUT (first_public >= 2014-09-01): (not computed)
- whole archive: (not computed)

## Result 2 — within-study sample duplication
- (not computed)

## Result 3 — the numeric channel, calibrated not assumed
- (not computed)

## Result 4 — individually verified cases
- 23 verification rows in `out/dossier.json`.
  - file identity: ['ERR248843', 'ERR338688'] -> **identical** (downloaded both files, hashed locally)
  - file identity: ['ERR248826', 'ERR338671'] -> **identical** (downloaded both files, hashed locally)
  - file identity: ['ERR248859', 'ERR338648'] -> **identical** (downloaded both files, hashed locally)
  - file identity: ['ERR248866', 'ERR338655'] -> **identical** (downloaded both files, hashed locally)
  - file identity: ['ERR248833', 'ERR338678'] -> **identical** (downloaded both files, hashed locally)
  - file identity: ['ERR248871', 'ERR338660'] -> **identical** (downloaded both files, hashed locally)
  - file identity: ['ERR037074', 'ERR186225'] -> **identical** (downloaded both files, hashed locally)
  - file identity: ['ERR022895', 'ERR037360'] -> **identical** (downloaded both files, hashed locally)
  - run identity: ['SRR064495', 'SRR064997'] -> **CONFIRMED identical** (NCBI exact A/C/G/T/N + spot count)
  - run identity: ['SRR090137', 'SRR090151', 'SRR090234'] -> **CONFIRMED identical** (NCBI exact A/C/G/T/N + spot count)
  - run identity: ['SRR064494', 'SRR065000'] -> **CONFIRMED identical** (NCBI exact A/C/G/T/N + spot count)
  - run identity: ['SRR090139', 'SRR090222', 'SRR090228'] -> **CONFIRMED identical** (NCBI exact A/C/G/T/N + spot count)
  - run identity: ['SRR070588', 'SRR071318'] -> **CONFIRMED identical** (NCBI exact A/C/G/T/N + spot count)
  - run identity: ['SRR064493', 'SRR064999'] -> **CONFIRMED identical** (NCBI exact A/C/G/T/N + spot count)
  - run identity: ['SRR063729', 'SRR063733', 'SRR063735'] -> **CONFIRMED identical** (NCBI exact A/C/G/T/N + spot count)
  - run identity: ['SRR060132', 'SRR060133'] -> **CONFIRMED identical** (NCBI exact A/C/G/T/N + spot count)
  - run identity: ['SRR089838', 'SRR089848', 'SRR090117'] -> **CONFIRMED identical** (NCBI exact A/C/G/T/N + spot count)
  - run identity: ['SRR090138', 'SRR090152', 'SRR090235'] -> **CONFIRMED identical** (NCBI exact A/C/G/T/N + spot count)
  - run identity: ['SRR407427', 'SRR547765'] -> **CONFIRMED identical** (NCBI exact A/C/G/T/N + spot count)
  - run identity: ['SRR064498', 'SRR065001'] -> **CONFIRMED identical** (NCBI exact A/C/G/T/N + spot count)
  - run identity: random sample of 25 non-ERR cross-study candidates -> **21 confirmed / 0 refuted / 4 no fingerprint** (NCBI exact A/C/G/T/N + spot count)
  - publication impact: ['SRR543504', 'SRR578255'] -> ['GSM987821', 'GSM1012157'] -> **different papers [['22763454'], ['23372014']]** (SRA alias -> GSM -> GSE -> PubMed)
  - publication impact: ['SRR492421', 'SRR507824'] -> ['GSM923567', 'GSM946520'] -> **same series [['25319994'], ['25319994']]** (SRA alias -> GSM -> GSE -> PubMed)
- GEO linkage ['SRR543504', 'SRR578255'] -> ['GSM987821', 'GSM1012157']: DIFFERENT papers [['22763454'], ['23372014']]
- GEO linkage ['SRR492421', 'SRR507824'] -> ['GSM923567', 'GSM946520']: same series [['25319994'], ['25319994']]

_Numbers above are generated; narrative interpretation is in the sections written by hand below._
