# Candidate spread, kills, and the commit
Written 2026-09-06, BEFORE any analysis of held-out data.

## Candidates generated and what happened to each

| # | Candidate | Probed? | Verdict |
|---|-----------|---------|---------|
| 1 | CNEOS fireball catalog x public seismic/infrasound archives | yes: CNEOS API (n=883 events, 0.1 deg coords) | **KILLED.** arXiv 2606.04278 (2026) already swept the global IMS infrasound network against all CNEOS bolides 2007-2025; GOES-GLM bolide pipeline also exists. Public infrasound coverage is worse than IMS. n=883 is underpowered anyway. |
| 2 | Retracted papers propagating into curated bio-databases (ClinVar / GO / ChEMBL / GWAS Catalog) | yes: Retraction Watch CSV 66 MB / 72,390 rows free via Crossref; goa_human.gaf 15 MB | **HELD IN RESERVE.** Space looks open (Europe PMC finds nothing for ChEMBL/GO x retraction; the closest is a 2025 BRCA1/2-only ClinVar meta-research). But expected effect is tiny (retractions ~0.1% of literature) and the finding is predictable in direction. Good fallback. |
| 3 | Duplicate raw-read deposits in INSDC (ENA/SRA) via submitter checksums | yes, extensively — see below | **COMMITTED.** |
| 4 | arXiv withdrawn-paper corpus (negative space) | metadata reachable (OAI-PMH 200) | Rejected: cheap but thin; withdrawal comments are sparse and the population is small. |
| 5 | FDA facility inspections -> drug shortages | not deep-probed | Rejected: facility->product join is the whole project and prior literature exists (Woodcock & Wosinska and successors). |
| 6 | Crystallography Open Database duplicate structures | probed (endpoint alive) | Rejected: COD maintainers already run duplicate detection; `cod-tools` ships it and COD publishes a duplicates table. Would be re-deriving a maintained artifact. |
| 7 | Historical climate/phenology signal from digitized newspapers (Chronicling America) | probed: old LOC endpoint 404s (collection moved) | Rejected: OCR + geolocation + validation cost is very high and the aurora/tornado/phenology niches each have an established compiler (Silverman, Grazulis, Hayakawa). |
| 8 | Biodiversity Heritage Library OCR -> occurrence records missing from GBIF | surfaced during search | Rejected for now: extraction-heavy, validation nearly impossible without specialists. |
| 9 | Sentinel-value ("Null Island", 1970-01-01) contamination census across public datasets | — | Rejected: already tooled (CoordinateCleaner) and largely folklore-confirmed. |
| 10 | GBIF specimen coordinate errors | endpoint alive | Rejected: same reason as 9. |

## Why #3 wins
- **Joinable across communities.** Research-integrity/meta-science has never looked at raw-sequence archives; genomics has never looked at its own archive this way. Chen & Zobel (Database 2017) is the closest existing work and it explicitly **excluded SRA raw reads**, examined *assembled* nucleotide entries, and used *curator-merged* records rather than checksums.
- **Something changed.** ENA now exposes `submitted_md5` for every run through a free unauthenticated portal API. 43,824,523 runs, ~12 s per 157k rows.
- **Something is annoying — and it is the exact reason this is unexamined.** The obvious field, `fastq_md5`, is USELESS for this: ENA regenerates FASTQ from the archived object and the read headers embed the run accession, so two byte-identical datasets get different `fastq_md5`. Verified: 138,552 distinct fastq_md5 across 138,552 md5-bearing runs in 2012 — zero collisions. The signal lives only in `submitted_md5` (the submitter's original upload), which is present for ~34% of runs and is not what anyone reaches for.
- **Exact and falsifiable.** A 128-bit checksum collision is not a statistical claim. And it is verifiable to the ground: the files are downloadable, so I can hash them myself.

## Existing-work statement (what I must be able to say plainly)
Closest prior work: (a) Chen, Zhou & Zobel, "Duplicates, redundancies and inconsistencies in the primary nucleotide databases: a descriptive study", *Database* 2017 — 67,888 curator-merged groups / 111,823 duplicate pairs across 21 organisms in GenBank/ENA/DDBJ **assembled sequence** records; SRA excluded. (b) Wang et al., "DupChecker", *BMC Bioinformatics* 2014 — an R package that MD5-fingerprints raw files **you have already downloaded**, aimed at microarray (CEL) meta-analysis; never run as a census. (c) SRA policy states duplicate submissions are not permitted and submitters should cite the existing accession.
Mine differs by being an **archive-wide census of raw sequencing runs using the submitters' own checksums**, which nobody has published.
