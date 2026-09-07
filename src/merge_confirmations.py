#!/usr/bin/env python3
"""Fold the exhaustive organism-conflict confirmations back into the conflict table, so a
pair that the sampled pass left unconfirmed is not reported as unconfirmed when it was in
fact checked (and confirmed) by the dedicated run."""
import json, os
OUT = os.path.expanduser("~/Downloads/dig/out")
conf = json.load(open(os.path.join(OUT, "confirm_organism_conflicts.json")))
byrun = {}
for r in conf.get("run_level", []):
    byrun[tuple(sorted(r["runs"]))] = r
extra = os.path.join(OUT, "confirm_oxytricha_extra.json")
if os.path.exists(extra):
    for r in json.load(open(extra)):
        byrun[tuple(sorted(r["runs"]))] = dict(r, label="Sterkiella/Oxytricha extra run-pair")
cf = json.load(open(os.path.join(OUT, "conflicts_all.json")))
merged = 0
for c in cf["conflicts"]:
    k = tuple(sorted(c["runs"]))
    if k in byrun and c.get("confirm") in (None, "no_fingerprint"):
        r = byrun[k]
        c["confirm"] = r["verdict"]
        c["confirm_evidence"] = dict(composition_match=r.get("composition_match"),
                                     reads_identical=r.get("reads_identical_in_position"),
                                     reads_compared=r.get("reads_compared"),
                                     read_md5=r.get("read_md5_a"))
        merged += 1
# recount
org = [c for c in cf["conflicts"] if not c["tax_relation"].startswith("metagenome")]
import collections
sp = collections.Counter(tuple(sorted(c["studies"])) for c in org)
status = collections.Counter(c.get("confirm") for c in org)
cf["organism_level_pairs"] = len(org)
cf["organism_level_study_pairs"] = len(sp)
cf["organism_level_confirm_status"] = dict(status)
json.dump(cf, open(os.path.join(OUT, "conflicts_all.json"), "w"), indent=1)
print(f"folded in {merged} confirmations")
print("organism-level conflict pairs:", len(org), "distinct study-pairs:", len(sp))
print("confirmation status:", dict(status))
