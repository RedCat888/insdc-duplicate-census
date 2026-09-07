# Same bytes, different organism: content-identical sequencing data under conflicting identities in INSDC

## The finding, in one sentence
The world's primary raw-sequencing archives contain many byte-identical copies of the same
sequencing data deposited under separate accessions, and a subset of those copies declare
*different biological identities* — different named bacterial isolates, different plant
species, different human donors — including in reference collections and in the datasets
behind published *Nature* and *Science* papers; the checksum field that would reveal this
(`fastq_md5`) is structurally incapable of doing so, which is why it has gone unexamined.

## Why nobody has looked
ENA regenerates FASTQ from its archived object and writes the run accession into every read
header, so two byte-identical datasets receive *different* `fastq_md5`. Measured directly on a freshly fetched window
(`first_public` in [2013-05-01, 2013-06-01), 15,999 runs): 14,409 runs carry a
`fastq_md5`, yielding 22,044 distinct checksum values and
**0 collisions**. The raw window is kept at
`out/window_2013-05_allfields.tsv` so the count can be recomputed. The one field that does work, `submitted_md5` (the
checksum of the file as the submitter uploaded it), is present for 100% of ENA-submitted (ERR)
runs and ~0% of SRR/DRR, and is not what anyone reaches for.
Demonstrated on a single pair: ERR011033 and ERR208589 share `submitted_md5`
`18811b69387880657958c49b4e37274c` and file size 212,785,687 bytes, and have *different*
`fastq_md5` (`44e45fec…` vs `70822fe5…`).

## Verified cases

Every case below was checked against the actual data, not the metadata: by downloading both
files and hashing them locally, by comparing NCBI's exact A/C/G/T/N base composition, by
comparing the first 2,000 read sequences with headers ignored, or by HTTP range-checking
multi-gigabyte files.

At full scale the census finds 4,328 cross-study pairs whose two deposits declare
different biological identities, collapsing to **278 distinct study-pairs** — of which
**67 are organism-level** (different species or wider) and 211 are environment-label conflicts
between two different metagenome types. A seeded random sample of 150 of the pairs that
needed confirmation was checked against NCBI's exact base composition:
**146 confirmed, 2 refuted, 2 with no fingerprint available** — a confirmation rate of
98.6% [95.2, 99.6]. The two refutations matter: the check discriminates rather
than rubber-stamps. Twelve organism-level conflicts were additionally confirmed exhaustively,
by read-sequence comparison as well as composition, and all twelve held.

Broken down by how far apart the two declared identities are, the 67 organism-level study-pairs
include 33 that name two different species of the same genus and
37 that disagree at genus level or above.

**1. Two named *Staphylococcus* isolates with the same reads (JCVI, public since 2010).**
`SRR070588` is deposited as *Staphylococcus lugdunensis* VCU148 (BioProject PRJNA53779,
BioSample SAMN00116837); `SRR071318` as *Staphylococcus epidermidis* VCU111 (PRJNA53745,
SAMN00117446). Different species, different isolates, different sequencing experiments in the
metadata (`VCU148-BP3KB-A7NB-01-609` vs `VCU111-BP3KB-A8NB-01-604`). Their first 2,000 reads
are identical in the same order (sequence-MD5 `48a22e68b205fd7cbb4e0272a5c8fb6e` for both) and
NCBI reports identical composition (246,604 spots; A 36,185,865 / C 19,462,284 / G 19,976,733
/ T 35,168,277 / N 2,339,373). Both isolates nonetheless have their own distinct GenBank
assemblies (GCF_000649125.1, 2,514,513 bp; GCF_000697805.1, 2,487,086 bp), so this is not one
organism under two names — at least one of the two read deposits is misattached. PRJNA53779
contains exactly one run, and it is this one.

**2. Three genera sharing one 454 run (JCVI).** `SRR063729` (*Finegoldia magna*
SY403409CC001050417), `SRR063733` (*Peptoniphilus* sp. oral taxon 836 str. F0141) and
`SRR063735` (*Streptococcus mitis* bv. 2 str. F0392) — three BioProjects, three genera — share
identical composition (578,739 spots; A 83,238,156 / C 45,757,799 / G 47,413,971 /
T 79,403,140 / N 2,466,755) and identical reads. Twelve such JCVI groups were confirmed,
covering *S. aureus*, *S. epidermidis*, *S. lugdunensis*, *Finegoldia*, *Peptoniphilus*,
*Streptococcus*, *Lactobacillus* and *Ligilactobacillus*.

**3. *Escherichia coli* and *Listeria monocytogenes* (NIST).** `SRR1021212`
(*E. coli* O157:H7 str. EDL933, PRJNA207831) and `SRR1031053` (*L. monocytogenes* serotype 4b
str. NCTC 11994, PRJNA207832), both deposited by the National Institute of Standards and
Technology, have identical base composition and identical reads. These are organisms in
different phyla.

**4. Wheat and potato share a 2.17 GB file.** `ERR016531` (*Triticum aestivum*, University of
Liverpool, PRJEB2264) submits two SFF files; `ERR024102` (*Solanum phureja*, University of
Dundee, PRJEB2338) submits one. The potato run's entire file `GBSKQZK02.sff` is byte-identical
to the wheat run's `library06_GBSKQZK02.sff`: same 2,167,347,440 bytes, same
`submitted_md5 aab383dc74a0d6ff3ab7531cc0416648`, and independently the same MD5 for the first
and last 5 MB fetched by range request. The same physical 454 region output sits inside a
wheat genome project and a potato genome project.

**5. One library, two healthy donors, two journals.** `SRR543504` and `SRR578255` are both
58,602,670 reads / 1,858,493,937 bases with identical NCBI composition, and their first 2,000
reads are identical (sequence-MD5 `6088b8b35f0043e91708a10f21a4fce7` for both).
`SRR543504` → SRX178476 → SAMN01120345 → GSM987821, in GSE40176, described as
*"blood from healthy human donor 2"*, the dataset for Yu *et al.*, *Nature* 2012 (PMID
22763454), "RNA sequencing of pancreatic circulating tumour cells implicates WNT signalling in
metastasis". `SRR578255` → SRX190448 → SAMN01737260 → GSM1012157, in GSE41245, described as
*"blood draw 1 from healthy human donor 7"*, the dataset for Yu *et al.*, *Science* 2013 (PMID
23372014), "Circulating breast tumor cells exhibit dynamic changes in epithelial and
mesenchymal composition". The same sequencing library is presented as two different healthy
donors in two different papers. We cannot tell from public data whether this is an annotation
error or undisclosed reuse, and we do not assert either; what is verifiable is that the public
record describes one library as two donors.

**6. One tuberculosis isolate as three isolates at three institutions.** `ERR1199118`
(University of Basel, PRJEB11460, sample alias `G04008`), `ERR1654687` (Forschungszentrum
Borstel, PRJEB15463, alias `DRC-081593`) and `ERR2707108` (Institute of Tropical Medicine,
PRJEB27847, alias `DRC-081593`) each store the same file
`DRC-081593_lib4377_nextseq_n0021_151bp_R1.fastq.gz` at three separate FTP paths with the same
checksum, under three BioSample accessions. First 2,000 reads identical between Basel and ITM
(sequence-MD5 `412a500b36bfa6fd7bd0fd86c6897d10`). Name-matching would link two of the three;
the Basel record, under an internal identifier, would be missed.

## Why it matters
- **Pooled analyses count the same data more than once.** ENA's own curation team, in
  "Value, but high costs in post-deposition data curation" (*Database* 2016, PMC4747322),
  tabulates PRJEB1720 and PRJEB4562 side by side as independent studies in its
  ontology-annotation counts. Those two studies share 56 byte-identical files. The words
  "duplicate", "redundant", "identical" and "same data" appear zero times in that paper.
- **In pathogen genomics a duplicate is indistinguishable from a transmission event.**
  Identical genomes give a SNP distance of zero, which is the strongest possible evidence of
  recent transmission. The nine-study *M. tuberculosis* component above spans Borstel, the
  Institute of Tropical Medicine and Basel; at least seven of its nine studies are cited
  together by a single downstream comparative-genomics paper (PMID 35638832), and the
  component also contains the data behind PMID 27194683 — a paper titled "Standard Genotyping
  Overestimates Transmission of *Mycobacterium tuberculosis*".
- **This is against stated policy, not merely untidy.** NCBI's SRA submission standards
  (NCBI Insights, 29 June 2026, "Standards for SRA Data Submission", section 5) state:
  "Duplicate submissions are not permitted; reference the existing accession instead."
- **Reference collections inherit the error permanently.** Once public, INSDC records are not
  withdrawn; ENA's documented remedy (cancelling an object) applies only before release.

## What would show this is wrong
- If the read data behind a claimed duplicate differed — different composition, different
  reads. Tested on every case reported; 12 of 12 confirmed, 0 refuted, and the numeric channel
  was refuted where it deserved to be (ERR296666/ERR326475 share read and base counts exactly
  but have completely different base composition, and are correctly reported as a chance
  collision, not a duplicate).
- If `submitted_md5` were a stored assertion rather than a property of the bytes. Tested by
  downloading both files for sampled pairs and hashing them locally; ENA's value matched the
  bytes we fetched in every case tested.
- If the "duplicates" were one stored object referenced twice rather than two stored copies.
  Tested: the copies live at different FTP paths.
- If the conflicting labels were benign synonyms. Tested with taxonomy resolution: strain-level
  relabelling such as *Vibrio cholerae* vs *Vibrio cholerae* O1 biovar El Tor is classified as
  benign and excluded; only same-genus-different-species or wider disagreements are counted as
  organism-level conflicts.

---

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

---

## The harshest fair criticism, and my answer

**"Labs are allowed to reuse their own data. You have found normal practice."**
Partly true and reported as such: most duplication events are one group depositing its own
data twice, and the census separates same-institution from cross-institution events. Three
things survive the objection. INSDC policy is explicit that a duplicate submission should not
be made and the existing accession should be cited instead. The consequence — a pooled
analysis counting one dataset twice — does not depend on intent. And the sharp subset, where
the two copies declare *different organisms or different donors*, cannot be legitimate reuse
under any reading: 12 of 12 such cases tested were confirmed content-identical.

**"Your exact channel covers only ENA-submitted runs, so this is not an INSDC census."**
Conceded, and stated wherever a number is given. `submitted_md5` is present for 100% of ERR
runs and ~0% of SRR/DRR, because NCBI's public metadata dumps have the `<FILE checksum=…>`
block stripped (verified by extracting run.xml files from
`NCBI_SRA_Metadata_20260906.tar.gz`). For the ENA-submitted subset the census is complete
rather than sampled. The SRR/DRR side is reached only through the numeric channel plus
per-run confirmation, and every number derived that way is labelled a lower bound.

**"The numeric channel has 5% precision. You cannot conclude anything from it."**
Agreed, and nothing is concluded from it. Measured cross-study precision 0.055 [0.046, 0.065]
with recall 0.983 [0.942, 0.995]; it is used purely as a candidate generator. Every pair
reported from it was confirmed against NCBI's exact base composition and, where available, by
comparing read sequences. The channel's own false positives are demonstrated rather than
hidden: ERR296666 and ERR326475 share `read_count` 2,532,937 and `base_count` 506,587,400
exactly and are *not* duplicates — their base compositions differ completely.

**"Connected components can chain unrelated studies together through a hub."**
Checked. In the partial-data run the event-size distribution was 113 components of 2 studies,
15 of 3, 6 of 4, 5 of 5, and single components of 9, 10 and 18; the large components are
internally coherent (one barley programme at IPK; one *M. tuberculosis* collection across
three collaborating institutions; one DTU *E. coli* surveillance series). Size distributions
are reported rather than only totals.

**"A shared checksum means a shared file, not a duplicate dataset."**
Correct, and this cost an hour to understand properly. A run may submit several files, so an
md5 match is a file-level claim. ERR016531 (wheat, two SFFs) and ERR024102 (potato, one SFF)
share one file but are not run-level duplicates, and a run-level composition check correctly
refutes run identity while the file identity stands. The pipeline now keeps the two claims
separate, requires the shared file to be at least 10% of its run's submitted bytes and at
least 10 kB, and never describes an md5 event as a duplicate run.

**"You verified a handful of pairs out of thousands."**
The verified count is reported exactly, with the sampling procedure, and the sample is not
size-biased: files above the download cap are verified by comparing the first 2,000 read
sequences instead of being skipped, which costs the same for a 200 GB run as for a 2 MB one.
An earlier verification pass that silently skipped 8 of 10 events for exceeding a size cap is
recorded in the worklog as the reason this matters.

**"Your metadata could simply be incomplete."**
This was the single largest risk and it bit three times: `curl | gzip` swallowing curl's exit
status, a truncated response still gzipping cleanly, and — worst — ENA treating
`first_public <= E` as exclusive of E, so every window silently lost its final day and
single-day windows returned zero while passing a per-window count check. All three are
documented in `log/03-worklog.md`. The acceptance test is now global and independent of the
query semantics: the row counts of all windows must sum to ENA's count for the entire archive.

## Limitations
- Coverage of the exact channel is ENA-submitted runs only; the SRR/DRR figures are lower bounds.
- Study→publication linkage is sparse. Europe PMC's accession index resolved both studies for
  only 3 of 21 confirmed pairs; the GEO route (SRA alias → GSM → GSE → PubMed) is far denser
  but applies only to GEO-derived runs.
- "Different institution" rests on normalised `center_name` token sets and is deliberately
  conservative, so it under-counts.
- Whether a given duplicate is an annotation error, an undisclosed reuse, or a documented
  re-release is not determinable from public metadata, and no claim is made about which.
- The preregistered exploratory/held-out split was compromised by my own smoke testing; see
  the deviation notice in `log/02-preregistration.md`. The case studies are exploratory
  discoveries, not confirmations of a prior prediction.

## Ranked next steps
1. **Extend the exact channel to NCBI-submitted runs.** NCBI's per-run XML *does* expose the
   original file's MD5 (`<SRAFile … supertype="Original">`) — it is simply not in the bulk
   dumps. One request per run makes a full sweep impractical, but a targeted sweep over the
   numeric-channel candidate set is affordable and would turn today's lower bound on the
   SRR/DRR side into a real census. This is the single highest-value follow-up.
2. **Quantify the pathogen-genomics consequence directly.** Take a published *M. tuberculosis*
   or *E. coli* phylogenetic or transmission analysis whose accession list overlaps a
   duplication event, re-run it with duplicates collapsed, and report how many zero-SNP
   "transmission links" disappear. This converts a mechanism into a measured effect.
3. **Ask ENA and NCBI to publish content fingerprints.** A per-run hash of the sorted read
   sequences — format-, compression- and header-independent — would make this class of error
   detectable by anyone in a single pass, and would have caught every case in this report at
   submission time.

---

# Verdict on the preregistered hypotheses

Evaluated on the HELD-OUT split (`first_public >= 2014-09-01`), whose thresholds were
fixed in `log/02-preregistration.md` before it was analysed. See the deviation notice in
that file: the pipeline and thresholds were frozen first, but held-out output was seen
during smoke-testing, so the qualitative case studies are exploratory rather than
confirmatory. The quantitative thresholds below were never altered.

**H1 — the phenomenon is real at scale.** Threshold: >= 0.05% of checksum-bearing runs
in a cross-study duplication event; disconfirmed below 0.02%.
Observed on held-out data: **0.9984%** [0.9831, 1.0140] (15,888 of 1,591,321 runs). **PASSES**, by a factor of ~20.

**H2 — not one trivial artefact.** Threshold: >= 40% of cross-study groups survive the
degenerate-file and same-submission filters; disconfirmed below 15%.
Observed: 12,322 of 12,322 survive = **100.00%**. **PASSES.**
(The share/size filters removed accessory files earlier in the pipeline;
same-submission groups dropped: 0.)

**H3 — crosses institutional and biological boundaries.** Threshold: >= 10% of events
span more than one normalised institution, and a nonzero number span more than one taxon;
disconfirmed below 3% cross-institution.
Observed: **28 of 179 events = 15.6%** cross-institution; **53** events span more than one taxon. **PASSES.**

**H4 — the checksums mean what I think they mean.** Threshold: >= 90% of a sampled set
reproduces identical content on direct checking; disconfirmed below 80%.
Observed: download-and-hash of submitted files reproduced identical content in 8 of 8
pairs attempted; NCBI exact-composition checking of a seeded random sample of identity
conflicts gave **146 confirmed / 2 refuted / 2 without a fingerprint**, a confirmation rate of
**98.65%** [95.21, 99.63]. Twelve organism-level conflicts were confirmed
exhaustively by read-sequence comparison as well, all twelve holding. **PASSES.**

**All four preregistered hypotheses pass on held-out data.** The one preregistered
prediction that did NOT hold is the direction of the permutation null's interpretation at
scale: in the exploratory window only 27% of duplicate groups crossed a study boundary,
but in the held-out window 72% do. Duplication is still concentrated within
studies relative to chance (permuted: 16967 of 17,067), but far less so in later years than
the early-window figure suggested. That shift is reported rather than smoothed over.

---

## Reproducing this
```bash
./run_all.sh
```

Environment pinned in `env.txt`; fixed seed 20260906 in `src/params.py`.
Preregistration and amendments: `log/02-preregistration.md`.
Everything that failed, including three ways the data was silently wrong:
`log/03-worklog.md`. Count of everything tried: `log/99-tally.md`.
