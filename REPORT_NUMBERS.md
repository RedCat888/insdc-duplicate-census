# Duplicate raw-read deposits in the INSDC sequence archives: a checksum census

Generated 2026-09-06 from the result files in `out/`. Every figure below is read from those files by `src/make_report.py`.

## Data completeness
- Windows checked against ENA's own counts: **77**, passing exactly: **77**, failing: **0**.
- Runs carrying a usable submitter checksum (the exact channel): **412,439**; distinct checksums **522,738**.
- Coverage: **1,393,511** runs in verified windows out of **43,824,523** in the whole archive (**3.18%**).

## Result 1 — the census (exact channel, complete for ENA-submitted runs)
- **exploratory (first_public < 2014-09-01)**: 251,040 checksum-bearing runs -> 649 files present under more than one run; 177 of those span more than one study; **12 duplication events** over 26 studies; 227 runs (0.0904% [0.0794, 0.1030] of checksum-bearing runs).
  - redundant storage: **0.662 TB** total (0.2134 TB across studies, 0.4484 TB within a study).
  - events spanning more than one institution (normalised names): 2; more than one taxon: 2; largest event: 4 studies / 64 shared files.
  - null test (study labels permuted, sizes preserved): observed 178 of 649 duplicate groups span studies; under permutation 645.2. Duplicates are far more concentrated inside single studies than chance, so the cross-study set is a genuine tail rather than an artefact of study sizes.
- **HELD OUT (first_public >= 2014-09-01)**: 161,399 checksum-bearing runs -> 3,281 files present under more than one run; 31 of those span more than one study; **3 duplication events** over 7 studies; 32 runs (0.0198% [0.0140, 0.0280] of checksum-bearing runs).
  - redundant storage: **4.461 TB** total (0.0013 TB across studies, 4.4602 TB within a study).
  - events spanning more than one institution (normalised names): 0; more than one taxon: 0; largest event: 3 studies / 28 shared files.
  - null test (study labels permuted, sizes preserved): observed 31 of 3,281 duplicate groups span studies; under permutation 3249.0. Duplicates are far more concentrated inside single studies than chance, so the cross-study set is a genuine tail rather than an artefact of study sizes.
- **whole archive**: 412,439 checksum-bearing runs -> 4,122 files present under more than one run; 400 of those span more than one study; **17 duplication events** over 37 studies; 451 runs (0.1093% [0.0997, 0.1199] of checksum-bearing runs).
  - redundant storage: **5.126 TB** total (0.2176 TB across studies, 4.9086 TB within a study).
  - events spanning more than one institution (normalised names): 2; more than one taxon: 2; largest event: 4 studies / 190 shared files.
  - null test (study labels permuted, sizes preserved): observed 401 of 4,122 duplicate groups span studies; under permutation 4106.6. Duplicates are far more concentrated inside single studies than chance, so the cross-study set is a genuine tail rather than an artefact of study sizes.

## Result 2 — within-study sample duplication
- 424 checksum groups join runs that sit in the SAME study under DIFFERENT BioSample accessions, across **23 studies** and 450 runs (0.1091% [0.0995, 0.1197] of checksum-bearing runs).
  - `PRJEB6072`: 122 runs / 122 BioSamples involved — Homo sapiens, HUBRECHT INSTITUTE, UTRECHT, THE NETHERLANDS
  - `PRJEB3197`: 112 runs / 112 BioSamples involved — Canis lupus, European Bioinformatics Institute;Princeton Universi
  - `PRJEB107617`: 68 runs / 68 BioSamples involved — synthetic metagenome, WAGENINGEN UNIVERSITY, LABORATORY OF MICROBIOLOGY
  - `PRJEB6521`: 42 runs / 42 BioSamples involved — Homo sapiens, ExpKirUU
  - `PRJEB51827`: 24 runs / 12 BioSamples involved — Triticum aestivum, Earlham Institute
  - `PRJEB8503`: 24 runs / 24 BioSamples involved — Homo sapiens, AstraZeneca;AZ
  - `PRJEB104715`: 14 runs / 6 BioSamples involved — bovine metagenome, Scotland's Rural College;SRUC-DRIC
  - `PRJEB7116`: 8 runs / 8 BioSamples involved — Campylobacter, CENTRE FOR GENOMIC RESEARCH (CGR)

## Result 3 — the numeric channel, calibrated not assumed
- Against the ERR labelled region (where submitter checksums give ground truth), cross-study pairs: precision 3.6831% [3.2391, 4.1853], recall 100.0000% [98.3213, 100.0000] (TP 225, FP 5,884, FN 0).
- It is therefore used only to generate candidates; every claim from it is confirmed against NCBI's exact base composition or by comparing reads.

## Result 4 — individually verified cases
- 35 verification rows in `out/dossier.json`.
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
  - organism conflict (run): Gossypium barbadense vs G. arboreum (cotton) -> **CONFIRMED** (NCBI composition + ENA read comparison)
  - organism conflict (run): Gossypium arboreum vs G. barbadense (cotton) -> **CONFIRMED** (NCBI composition + ENA read comparison)
  - organism conflict (run): S. epidermidis IS-250 vs S. aureus IS-91 (JCVI) -> **CONFIRMED** (NCBI composition + ENA read comparison)
  - organism conflict (run): S. epidermidis IS-250 vs S. aureus IS-99 (JCVI) -> **CONFIRMED** (NCBI composition + ENA read comparison)
  - organism conflict (run): S. lugdunensis VCU148 vs S. epidermidis VCU111 (JCVI) -> **CONFIRMED** (NCBI composition + ENA read comparison)
  - organism conflict (run): Sterkiella histriomuscorum vs Oxytricha trifallax (WUGSC) -> **CONFIRMED** (NCBI composition + ENA read comparison)
  - organism conflict (run): E. coli O157:H7 EDL933 vs Listeria monocytogenes NCTC 11994 (NIST) -> **CONFIRMED** (NCBI composition + ENA read comparison)
  - organism conflict (run): Finegoldia magna vs Peptoniphilus sp. (JCVI) -> **CONFIRMED** (NCBI composition + ENA read comparison)
  - organism conflict (run): Finegoldia magna vs Streptococcus mitis (JCVI) -> **CONFIRMED** (NCBI composition + ENA read comparison)
  - organism conflict (run): Peptoniphilus sp. vs Streptococcus mitis (JCVI) -> **CONFIRMED** (NCBI composition + ENA read comparison)
  - organism conflict (run): Ligilactobacillus salivarius vs Lactobacillus delbrueckii (JCVI) -> **CONFIRMED** (NCBI composition + ENA read comparison)
  - organism conflict (file): Triticum aestivum (Liverpool) vs Solanum phureja (Dundee) - shared 454 region GBSKQZK02 -> **CONFIRMED** (HTTP range check of both files)
  - publication impact: ['SRR543504', 'SRR578255'] -> ['GSM987821', 'GSM1012157'] -> **different papers [['22763454'], ['23372014']]** (SRA alias -> GSM -> GSE -> PubMed)
  - publication impact: ['SRR492421', 'SRR507824'] -> ['GSM923567', 'GSM946520'] -> **same series [['25319994'], ['25319994']]** (SRA alias -> GSM -> GSE -> PubMed)
- organism-level conflicts confirmed at run level: 11/11
- GEO linkage ['SRR543504', 'SRR578255'] -> ['GSM987821', 'GSM1012157']: DIFFERENT papers [['22763454'], ['23372014']]
- GEO linkage ['SRR492421', 'SRR507824'] -> ['GSM923567', 'GSM946520']: same series [['25319994'], ['25319994']]

_Numbers above are generated; narrative interpretation is in the sections written by hand below._
