# Duplicate raw-read deposits in the INSDC sequence archives: a checksum census

Generated 2026-09-06 from the result files in `out/`. Every figure below is read from those files by `src/make_report.py`.

## Data completeness
- Windows checked against ENA's own counts: **132**, passing exactly: **132**, failing: **0**.
- Runs carrying a usable submitter checksum (the exact channel): **1,873,023**; distinct checksums **2,628,784**.
- Coverage: **6,827,778** runs in verified windows out of **43,824,523** in the whole archive (**15.58%**).

## Result 1 — the census (exact channel, complete for ENA-submitted runs)
- **exploratory (first_public < 2014-09-01)**: 281,702 checksum-bearing runs -> 653 files present under more than one run; 177 of those span more than one study; **12 duplication events** over 27 studies; 229 runs (0.0813% [0.0714, 0.0925] of checksum-bearing runs).
  - redundant storage: **0.701 TB** total (0.2148 TB across studies, 0.4861 TB within a study).
  - events spanning more than one institution (normalised names): 2; more than one taxon: 2; largest event: 5 studies / 64 shared files.
  - null test (study labels permuted, sizes preserved): observed 178 of 653 duplicate groups span studies; under permutation 650.0. Duplicates are far more concentrated inside single studies than chance, so the cross-study set is a genuine tail rather than an artefact of study sizes.
- **HELD OUT (first_public >= 2014-09-01)**: 1,591,321 checksum-bearing runs -> 17,067 files present under more than one run; 12,322 of those span more than one study; **179 duplication events** over 441 studies; 15,888 runs (0.9984% [0.9831, 1.0140] of checksum-bearing runs).
  - redundant storage: **9.769 TB** total (3.5417 TB across studies, 6.2277 TB within a study).
  - events spanning more than one institution (normalised names): 28; more than one taxon: 53; largest event: 10 studies / 2,058 shared files.
  - null test (study labels permuted, sizes preserved): observed 12,322 of 17,067 duplicate groups span studies; under permutation 16966.6. Duplicates are far more concentrated inside single studies than chance, so the cross-study set is a genuine tail rather than an artefact of study sizes.
- **whole archive**: 1,873,023 checksum-bearing runs -> 22,315 files present under more than one run; 17,200 of those span more than one study; **201 duplication events** over 507 studies; 25,082 runs (1.3391% [1.3228, 1.3557] of checksum-bearing runs).
  - redundant storage: **10.826 TB** total (4.1151 TB across studies, 6.7105 TB within a study).
  - events spanning more than one institution (normalised names): 31; more than one taxon: 59; largest event: 20 studies / 5,628 shared files.
  - null test (study labels permuted, sizes preserved): observed 17,201 of 22,315 duplicate groups span studies; under permutation 22215.8. Duplicates are far more concentrated inside single studies than chance, so the cross-study set is a genuine tail rather than an artefact of study sizes.

## Result 2 — within-study sample duplication
- 1,165 checksum groups join runs that sit in the SAME study under DIFFERENT BioSample accessions, across **129 studies** and 1,474 runs (0.0787% [0.0748, 0.0828] of checksum-bearing runs).
  - `PRJEB27984`: 192 runs / 192 BioSamples involved — Mus musculus, European Bioinformatics Institute;Karolinska Institu
  - `PRJEB19206`: 156 runs / 156 BioSamples involved — Campylobacter coli, UNIVERSITY OF ABERDEEN
  - `PRJEB6072`: 122 runs / 122 BioSamples involved — Homo sapiens, HUBRECHT INSTITUTE, UTRECHT, THE NETHERLANDS
  - `PRJEB3197`: 112 runs / 112 BioSamples involved — Canis lupus, European Bioinformatics Institute;Princeton Universi
  - `PRJEB13000`: 78 runs / 78 BioSamples involved — Homo sapiens, European Bioinformatics Institute;WIS
  - `PRJEB107617`: 68 runs / 68 BioSamples involved — synthetic metagenome, WAGENINGEN UNIVERSITY, LABORATORY OF MICROBIOLOGY
  - `PRJEB9654`: 54 runs / 54 BioSamples involved — soil metagenome, NEIKER TECNALIA
  - `PRJEB6521`: 42 runs / 42 BioSamples involved — Homo sapiens, ExpKirUU

## Result 3 — the numeric channel, calibrated not assumed
- Against the ERR labelled region (where submitter checksums give ground truth), cross-study pairs: precision 9.1655% [8.9907, 9.3434], recall 100.0000% [99.9593, 100.0000] (TP 9,428, FP 93,436, FN 0).
- It is therefore used only to generate candidates; every claim from it is confirmed against NCBI's exact base composition or by comparing reads.

## Result 4 — individually verified cases
- 36 verification rows in `out/dossier.json`.
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
  - event-stratified sample: 20 of 201 events sampled (seeded) -> **18 verified by the harness; the 2 others were 1 untestable (no FASTQ, read_count 0) and 1 file-level match confirmed by range check -> 19/19 testable confirmed, 0 refuted** (random sample of events; download+hash, or first 2,000 reads for large files)
  - publication impact: ['SRR543504', 'SRR578255'] -> ['GSM987821', 'GSM1012157'] -> **different papers [['22763454'], ['23372014']]** (SRA alias -> GSM -> GSE -> PubMed)
  - publication impact: ['SRR492421', 'SRR507824'] -> ['GSM923567', 'GSM946520'] -> **same series [['25319994'], ['25319994']]** (SRA alias -> GSM -> GSE -> PubMed)
- organism-level conflicts confirmed at run level: 11/11
- GEO linkage ['SRR543504', 'SRR578255'] -> ['GSM987821', 'GSM1012157']: DIFFERENT papers [['22763454'], ['23372014']]
- GEO linkage ['SRR492421', 'SRR507824'] -> ['GSM923567', 'GSM946520']: same series [['25319994'], ['25319994']]

_Numbers above are generated; narrative interpretation is in the sections written by hand below._
