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
