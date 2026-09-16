# Log 08 — The *M. tuberculosis* component, quantified (2026-09-15)

Preparation for ranked-next-step #2 ("quantify the pathogen-genomics consequence directly").
Source: `out/tb_component_groups.json`, `out/tb_diff_biosample_groups.json`, generated from
`out/keys_md5_all.sorted.tsv`.

## Structure of the component
Nine studies, three institutions (University of Basel; Forschungszentrum Borstel; Institute of
Tropical Medicine, Antwerp), 2015-06-22 to 2018-09-29, all Illumina WGS.

| | |
|---|---|
| shared-file groups | 364 (308 of size 2, 56 of size 3) |
| runs involved | 394 |
| **groups whose runs sit under DIFFERENT BioSamples** | **260** |
| runs in those groups | 290, under 282 distinct BioSamples |
| groups under the same BioSample (benign; the sample ties them together) | 104 |

That split is the number that matters and it was not in the report. A duplicate under one
BioSample is discoverable by anyone reading the metadata. **260 groups — 290 runs under 282
separate BioSample accessions — present the same sequencing data as separate biological
samples.** To a pipeline that de-duplicates by BioSample (the standard practice), those are
independent isolates.

### By study pair (different-BioSample groups only)
| studies | groups |
|---|---|
| PRJEB15463 + PRJEB27847 (Borstel + ITM) | 66 |
| PRJEB11460 + PRJEB9680 (Basel + Borstel) | 64 |
| PRJEB11460 + PRJEB15463 + PRJEB27847 (all three) | 56 |
| PRJEB10533 + PRJEB11460 | 42 |
| PRJEB11460 + PRJEB6273 | 18 |
| PRJEB11460 + PRJEB7727 | 8 |
| PRJEB11460 + PRJEB15463 | 4 |
| PRJEB11460 + PRJEB9545 | 2 |

PRJEB12179's 34 groups are all **same-BioSample** (e.g. ERR1367658 / ERR1465774, both
SAMEA3715435) and are therefore excluded from the 260.

## Correction to the report
REPORT.md line 112 states the component's studies "are cited together by a single downstream
comparative-genomics paper (PMID 35638832)". Checked against the Europe PMC accession index:
that PMID does cite **8 of the 9** studies (all but PRJEB15463, which has no Europe PMC
accession link) — so the count is right, but **the characterisation is wrong**. PMID 35638832
is Tomasi et al., *Microbiol Spectr* 2022, "A tRNA-Acetylating Toxin and Detoxifying Enzyme in
*Mycobacterium tuberculosis*" — a molecular-microbiology paper that surveyed clinical isolates
for stop mutations, not a comparative-genomics or transmission study. It must be described that
way or dropped.

Also: the report says the component "contains the data behind PMID 27194683" (Stucki et al.,
*J Clin Microbiol* 2016, "Standard Genotyping Overestimates Transmission of *M. tuberculosis*").
That is PRJEB12179 — whose duplicates are all same-BioSample. The rhetorical pairing of that
title with this finding is therefore **not supported** and is withdrawn. It reads as if that
paper's conclusions were affected; nothing here shows that.

## Candidate papers for the actual experiment
Papers citing studies in the component that are genuinely about transmission clustering:
- **PMID 30341041** — "The relationship between transmission time and clustering methods in
  *Mycobacterium tuberculosis*" (cites PRJEB27847)
- **PMID 38696531** — "HIV co-infection is associated with reduced *M. tuberculosis*
  transmissibility" (cites PRJEB11460)
- **PMID 33239092** — "MDR *M. tuberculosis* outbreak clone in Eswatini…" (cites PRJEB6273)
- **PMID 30479891, 28425484** — cite PRJEB7727

## The experiment, specified before it is run
**Question:** does any published transmission cluster contain two runs that are the same data?

1. For each candidate paper, obtain the accession or isolate list (supplementary tables).
2. Intersect with the 290 runs / 282 BioSamples in `out/tb_diff_biosample_groups.json`.
3. **Pre-specified outcomes:**
   - *Positive:* ≥1 reported cluster contains ≥2 BioSamples from the same duplicate group →
     the paper reports a zero-SNP link between one dataset and itself. Report the cluster.
   - *Null:* no overlap, or overlapping samples never co-occur in a reported cluster → report
     that the mechanism exists but no published conclusion is shown to be affected, and say so
     in the abstract.
4. Only if a positive: obtain the SNP pipeline and re-run with duplicates collapsed.

**This is written down before step 1 so the null result gets reported.** The honest framing if
it comes back null: "duplicates are present in datasets used by transmission studies; we could
not demonstrate an affected published conclusion from public data, and the risk remains
hypothetical." That is still publishable and it is what the evidence would support.

## Note on the mechanism (not an accusation)
Borstel and ITM share the file name `DRC-081593_lib4377_nextseq_n0021_151bp_R1.fastq.gz`; Basel
deposits the same bytes under an internal alias (`G04008`). These are three collaborating
institutions in the same DRC-based research programme. Re-deposit of a collaborator's sequencing
output under a local sample identifier is the obvious explanation and is not misconduct. The
consequence — 282 BioSamples for 260 distinct datasets — is the same regardless of cause.
