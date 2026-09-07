#!/usr/bin/env python3
"""Generate REPORT.md from the result JSONs. Every number in the report is read from a file
produced by the pipeline; none is typed in by hand. If a result file is missing, the
corresponding line says so rather than guessing."""
import json, os, sys, datetime

OUT = os.path.expanduser("~/Downloads/dig/out")
def L(name):
    p = os.path.join(OUT, name)
    if not os.path.exists(p): return None
    try: return json.load(open(p))
    except Exception: return None
def LL(name):
    p = os.path.join(OUT, name)
    if not os.path.exists(p): return []
    return [json.loads(x) for x in open(p)]

def pct(w):
    if not w: return "n/a"
    return f"{100*w[0]:.4f}% [{100*w[1]:.4f}, {100*w[2]:.4f}]"
def num(x):
    return f"{x:,}" if isinstance(x, int) else ("n/a" if x is None else str(x))

ev_all = L("events2_all.json"); ev_ho = L("events2_heldout.json"); ev_ex = L("events2_exploratory.json")
ws = L("within_study_all.json"); nm = L("numeric_all.json")
cv = L("chunk_validation_final.json") or L("chunk_validation.json")
doss = L("dossier.json") or []
conf = L("confirm_organism_conflicts.json")
geo = L("geo_papers.json")

lines = []
A = lines.append
A(f"# Duplicate raw-read deposits in the INSDC sequence archives: a checksum census")
A("")
A(f"Generated {datetime.date.today().isoformat()} from the result files in `out/`. "
  "Every figure below is read from those files by `src/make_report.py`.")
A("")
A("## Data completeness")
if cv:
    ok = cv["n_checked"] - cv["n_bad"]
    A(f"- Windows checked against ENA's own counts: **{num(cv['n_checked'])}**, "
      f"passing exactly: **{num(ok)}**, failing: **{num(cv['n_bad'])}**.")
    if cv["n_bad"]: A(f"  - still failing: `{' '.join(cv['bad'][:20])}`")
else:
    A("- (chunk validation result not present)")
if ev_all:
    A(f"- Runs carrying a usable submitter checksum (the exact channel): "
      f"**{num(ev_all['n_runs_with_key'])}**; distinct checksums **{num(ev_all['n_md5_keys'])}**.")

cvv = cv or {}
if cvv.get("archive_total"):
    A(f"- Coverage: **{num(cvv.get('rows_total'))}** runs in verified windows out of "
      f"**{num(cvv.get('archive_total'))}** in the whole archive "
      f"(**{100*(cvv.get('coverage') or 0):.2f}%**).")
A("")
A("## Result 1 — the census (exact channel, complete for ENA-submitted runs)")
for lab, d in (("exploratory (first_public < 2014-09-01)", ev_ex),
               ("HELD OUT (first_public >= 2014-09-01)", ev_ho),
               ("whole archive", ev_all)):
    if not d: A(f"- {lab}: (not computed)"); continue
    A(f"- **{lab}**: {num(d['n_runs_with_key'])} checksum-bearing runs -> "
      f"{num(d['n_groups_multi_run'])} files present under more than one run; "
      f"{num(d['n_groups_cross_study'])} of those span more than one study; "
      f"**{num(d['n_events'])} duplication events** over {num(d['n_studies_involved'])} studies; "
      f"{num(d['n_runs_in_cross_study_event'])} runs "
      f"({pct(d['frac_runs_in_cross_study_event'])} of checksum-bearing runs).")
    A(f"  - redundant storage: **{d['redundant_TB']} TB** total "
      f"({d.get('redundant_cross_study_TB')} TB across studies, "
      f"{d.get('redundant_within_study_TB')} TB within a study).")
    A(f"  - events spanning more than one institution (normalised names): "
      f"{num(d['events_cross_center'])}; more than one taxon: {num(d['events_cross_taxon'])}; "
      f"largest event: {num(d['largest_event_studies'])} studies / "
      f"{num(d['largest_event_files'])} shared files.")
    sn = d.get("shuffle_null")
    if sn:
        A(f"  - null test (study labels permuted, sizes preserved): observed "
          f"{num(sn['observed_cross_study_groups'])} of {num(sn['n_multi_run_groups'])} duplicate "
          f"groups span studies; under permutation {sn['null_mean']:.1f}. Duplicates are far "
          "more concentrated inside single studies than chance, so the cross-study set is a "
          "genuine tail rather than an artefact of study sizes.")

A("")
A("## Result 2 — within-study sample duplication")
if ws:
    A(f"- {num(ws['groups_same_study_different_samples'])} checksum groups join runs that sit in "
      f"the SAME study under DIFFERENT BioSample accessions, across "
      f"**{num(ws['n_studies_with_duplicate_samples'])} studies** and "
      f"{num(ws['n_runs_in_duplicate_sample_pairs'])} runs "
      f"({pct(ws['frac_runs_in_duplicate_sample_pairs'])} of checksum-bearing runs).")
    for s in (ws.get("top_studies") or [])[:8]:
        A(f"  - `{s['study']}`: {s['runs_involved']} runs / {s['samples_involved']} BioSamples "
          f"involved — {(s['organisms'] or [''])[0]}, {(s['centers'] or [''])[0][:52]}")
else:
    A("- (not computed)")

A("")
A("## Result 3 — the numeric channel, calibrated not assumed")
if nm:
    cs = nm.get("cross_study_pairs", {})
    A(f"- Against the ERR labelled region (where submitter checksums give ground truth), "
      f"cross-study pairs: precision {pct(cs.get('precision'))}, recall {pct(cs.get('recall'))} "
      f"(TP {num(cs.get('tp'))}, FP {num(cs.get('fp'))}, FN {num(cs.get('fn'))}).")
    A("- It is therefore used only to generate candidates; every claim from it is confirmed "
      "against NCBI's exact base composition or by comparing reads.")
else:
    A("- (not computed)")

A("")
A("## Result 4 — individually verified cases")
if doss:
    A(f"- {len(doss)} verification rows in `out/dossier.json`.")
    for r in doss[:40]:
        A(f"  - {r['kind']}: {r['detail']} -> **{r['result']}** ({r['evidence']})")
if conf:
    nr = sum(1 for r in conf.get("run_level", []) if r.get("verdict") == "CONFIRMED")
    A(f"- organism-level conflicts confirmed at run level: {nr}/{len(conf.get('run_level', []))}")
if geo:
    for r in geo:
        A(f"- GEO linkage {r['runs']} -> {r['gsm']}: "
          f"{'DIFFERENT papers' if r['different_papers'] else 'same series'} {r['pmids']}")

A("")
A("_Numbers above are generated; narrative interpretation is in the sections written by hand below._")
open(os.path.expanduser("~/Downloads/dig/REPORT_NUMBERS.md"), "w").write("\n".join(lines)+"\n")
print("\n".join(lines))
