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
