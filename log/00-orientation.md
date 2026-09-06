# Dig log — started 2026-09-06

Env: macOS darwin 25.1.0, Python 3.14.3 (homebrew), numpy 2.4.3 / pandas 3.0.1 / scipy 1.17.1.
Disk free: 83 GiB. Network: OK (oeis.org 200, data.gov 200).
Prior work in this dir tree: ~/Downloads/oeis-lab (OEIS unrecorded-identity sweep, done 2026-09-06).
=> deliberately avoiding math-sequence databases this time.

## Phase 0: candidate generation + reachability probes

### Kills (cheap, before investment)
- **CNEOS fireballs x seismic/infrasound archives** — KILLED 2026-09-06. arXiv 2606.04278
  ("The Role of Source Geometry and Atmospheric Propagation in Global Bolide Infrasound
  Detectability", 2026) already did the systematic sweep of the global IMS infrasound network
  against all 623 CNEOS bolides 2007-2025. Also GLM/GOES bolide pipeline exists
  (neo-bolide). Nothing left that a laptop can add; public infrasound coverage is worse
  than IMS anyway. n=883 CNEOS events total — underpowered regardless.

### Live leads
- **ENA/SRA duplicate raw-run deposits.** 43,824,523 read_runs; metadata pullable free
  (~12 s and 29 MB per 157k runs). fastq_md5 present for 88% but ZERO collisions in the
  2012 slice (138,552 md5 / 138,552 runs) => ENA-regenerated FASTQ almost certainly embeds
  the accession in read headers, so fastq_md5 cannot see content duplicates.
  submitted_md5 (original uploaded file, immune to that) present for 37% of 2012 runs.
  Full pull started.
