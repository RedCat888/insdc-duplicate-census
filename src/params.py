"""FROZEN analysis parameters. Set FROZEN=True only when the pipeline is finalised on the
exploratory set; held-out data must not be analysed before that."""
FROZEN = True                       # frozen 2026-09-06 after prereg (log/02-preregistration.md)
SPLIT_DATE = "2014-09-01"           # first_public < SPLIT_DATE => exploratory; >= => held out
SEED = 20260906

# md5 values of degenerate files that must never count as duplicates
DEGENERATE_MD5 = {
    "d41d8cd98f00b204e9800998ecf8427e",   # empty file
    "7029066c27ac6f5ef18d660d5741979a",   # gzip of empty file (default header)
    "68b329da9893e34099c7d8ad5cb9c940",   # single newline
}
MIN_SUBMITTED_BYTES = 10000         # H2(a): degenerate-size filter (Amendment 2: 1000 -> 10000)
MIN_SHARE_OF_RUN = 0.10             # Amendment 2: the shared file must be >=10% of the run's
                                    # total submitted bytes, so that a small accessory file
                                    # inside a multi-file submission (e.g. a Complete Genomics
                                    # ASM directory) cannot masquerade as a duplicated dataset.
DROP_EMPTY_STUDY = True             # Amendment 2: 3.2% of rows have an empty study_accession;
                                    # an empty string was being treated as a distinct study.
