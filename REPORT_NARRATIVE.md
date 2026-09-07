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
header, so two byte-identical datasets receive *different* `fastq_md5`. Measured directly:
across all 138,552 checksum-bearing runs released in 2012, there were 138,552 distinct
`fastq_md5` values — not one collision. The one field that does work, `submitted_md5` (the
checksum of the file as the submitter uploaded it), is present for 100% of ENA-submitted (ERR)
runs and ~0% of SRR/DRR, and is not what anyone reaches for.
Demonstrated on a single pair: ERR011033 and ERR208589 share `submitted_md5`
`18811b69387880657958c49b4e37274c` and file size 212,785,687 bytes, and have *different*
`fastq_md5` (`44e45fec…` vs `70822fe5…`).

## Verified cases

Every case below was checked against the actual data, not the metadata: by downloading both
files and hashing them locally, by comparing NCBI's exact A/C/G/T/N base composition, by
comparing the first 2,000 read sequences with headers ignored, or by HTTP range-checking
multi-gigabyte files. 12 of 12 organism-level conflicts confirmed, 0 refuted.

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
