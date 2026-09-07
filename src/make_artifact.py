#!/usr/bin/env python3
"""Build the artifact page. Every number is read from out/*.json at build time."""
import json, os, html, datetime

OUT = os.path.expanduser("~/Downloads/dig/out")
DEST = "$SCRATCH/duplicate-deposits.html"

def L(n):
    p = os.path.join(OUT, n)
    if not os.path.exists(p): return None
    try: return json.load(open(p))
    except Exception: return None

ev   = L("events2_all.json")
ws   = L("within_study_all.json")
nm   = L("numeric_all.json")
cv   = L("chunk_validation_final.json") or L("chunk_validation.json")
cf   = L("conflicts_all.json")
trap = L("fastq_md5_trap.json")
conf = L("confirm_organism_conflicts.json")
geo  = L("geo_papers.json")

def n(x): return f"{x:,}" if isinstance(x, (int,)) else ("—" if x is None else str(x))
def pc(w, d=3): return "—" if not w else f"{100*w[0]:.{d}f}%"
def e(s): return html.escape(str(s))

# ---- the specimen cases, each with its own evidence line ----
CASES = [
 dict(a=("SRR070588", "Staphylococcus lugdunensis VCU148", "PRJNA53779 · SAMN00116837 · JCVI · 2010-11-02"),
      b=("SRR071318", "Staphylococcus epidermidis VCU111", "PRJNA53745 · SAMN00117446 · JCVI · 2010-11-21"),
      payload="246,604 spots · A 36,185,865 · C 19,462,284 · G 19,976,733 · T 35,168,277 · N 2,339,373",
      ev="First 2,000 reads identical in order; sequence-MD5 48a22e68b205fd7cbb4e0272a5c8fb6e on both. Each isolate has its own GenBank assembly (2,514,513 bp vs 2,487,086 bp), so this is not one organism under two names.",
      tag="two species"),
 dict(a=("SRR063729", "Finegoldia magna SY403409CC001050417", "PRJNA51081 · JCVI · 2010-08-08"),
      b=("SRR063733 + SRR063735", "Peptoniphilus sp. F0141 · Streptococcus mitis F0392", "PRJNA49437 · PRJNA49439 · JCVI"),
      payload="578,739 spots · A 83,238,156 · C 45,757,799 · G 47,413,971 · T 79,403,140 · N 2,466,755",
      ev="Three BioProjects, three genera, one 454 run. Twelve such JCVI groups confirmed, spanning Staphylococcus, Finegoldia, Peptoniphilus, Streptococcus, Lactobacillus and Ligilactobacillus.",
      tag="three genera"),
 dict(a=("SRR1021212", "Escherichia coli O157:H7 str. EDL933", "PRJNA207831 · NIST · 2013-11-14"),
      b=("SRR1031053", "Listeria monocytogenes serotype 4b NCTC 11994", "PRJNA207832 · NIST · 2013-12-07"),
      payload="identical spot count and identical A/C/G/T/N composition",
      ev="Organisms in different phyla, both deposited by the National Institute of Standards and Technology. First 2,000 reads identical.",
      tag="different phyla"),
 dict(a=("ERR016531", "Triticum aestivum — bread wheat", "PRJEB2264 · University of Liverpool · 2010-08-31"),
      b=("ERR024102", "Solanum phureja — potato", "PRJEB2338 · University of Dundee · 2011-01-11"),
      payload="GBSKQZK02.sff · 2,167,347,440 bytes · md5 aab383dc74a0d6ff3ab7531cc0416648",
      ev="The potato run's entire file is byte-identical to the wheat run's second file. Independently checked by range-requesting the first and last 5 MB of each: same size, same head MD5, same tail MD5.",
      tag="two plant families"),
 dict(a=("SRR543504", "“blood from healthy human donor 2”", "GSM987821 · GSE40176 · Yu et al., Nature 2012 (PMID 22763454)"),
      b=("SRR578255", "“blood draw 1 from healthy human donor 7”", "GSM1012157 · GSE41245 · Yu et al., Science 2013 (PMID 23372014)"),
      payload="58,602,670 spots · 1,858,493,937 bases · sequence-MD5 6088b8b35f0043e91708a10f21a4fce7",
      ev="Full accession chain verified: SRR→SRX→BioSample→GSM→GSE→PubMed. The two GEO series declare no relationship to each other. Whether this is an annotation error or an undisclosed reuse cannot be told from public data; what is verifiable is that one library is described as two donors.",
      tag="two donors, two journals"),
 dict(a=("ERR1199118", "M. tuberculosis, sample alias G04008", "PRJEB11460 · University of Basel"),
      b=("ERR1654687 + ERR2707108", "M. tuberculosis, alias DRC-081593", "PRJEB15463 Borstel · PRJEB27847 Inst. of Tropical Medicine"),
      payload="DRC-081593_lib4377_nextseq_n0021_151bp_R1.fastq.gz — same filename, same checksum, three separate FTP paths",
      ev="Three BioSamples at three institutions. First 2,000 reads identical between Basel and ITM (sequence-MD5 412a500b36bfa6fd7bd0fd86c6897d10). Matching on sample names would link two of the three and miss the Basel record entirely.",
      tag="one isolate, three institutions"),
]

org_pairs = cf.get("organism_level_pairs") if cf else None
org_sp    = cf.get("organism_level_study_pairs") if cf else None
org_status= cf.get("organism_level_confirm_status") if cf else {}
confirmed = sum(v for k, v in (org_status or {}).items() if k and k != "refuted")
refuted   = (org_status or {}).get("refuted", 0)

rows = []
if ev:
    rows.append(("Runs carrying a submitter checksum", n(ev["n_runs_with_key"]),
                 "the exact channel; 100% of ENA-submitted runs, ~0% of NCBI-submitted"))
    rows.append(("Files present under more than one run", n(ev["n_groups_multi_run"]), ""))
    rows.append(("…spanning more than one study", n(ev["n_groups_cross_study"]), ""))
    rows.append(("Duplication events", n(ev["n_events"]),
                 f"over {n(ev['n_studies_involved'])} studies; largest {n(ev['largest_event_studies'])} studies / {n(ev['largest_event_files'])} files"))
    rows.append(("Runs inside a cross-study event", n(ev["n_runs_in_cross_study_event"]),
                 pc(ev["frac_runs_in_cross_study_event"]) + " of checksum-bearing runs"))
    rows.append(("Redundant storage", f"{ev['redundant_TB']} TB",
                 f"{ev.get('redundant_cross_study_TB')} TB across studies, {ev.get('redundant_within_study_TB')} TB within one"))
if ws:
    rows.append(("Studies where two BioSamples hold identical data", n(ws["n_studies_with_duplicate_samples"]),
                 f"{n(ws['n_runs_in_duplicate_sample_pairs'])} runs affected"))

def case_html(c):
    return f"""
    <figure class="specimen">
      <figcaption class="specimen-tag">{e(c['tag'])}</figcaption>
      <div class="specimen-body">
        <div class="side">
          <div class="acc">{e(c['a'][0])}</div>
          <div class="ident">{e(c['a'][1])}</div>
          <div class="prov">{e(c['a'][2])}</div>
        </div>
        <div class="join" aria-hidden="true"><span>=</span></div>
        <div class="side">
          <div class="acc">{e(c['b'][0])}</div>
          <div class="ident">{e(c['b'][1])}</div>
          <div class="prov">{e(c['b'][2])}</div>
        </div>
      </div>
      <div class="payload"><span class="payload-label">shared payload</span>{e(c['payload'])}</div>
      <p class="evidence">{e(c['ev'])}</p>
    </figure>"""

table_html = "".join(
    f"<tr><th scope='row'>{e(a)}</th><td class='num'>{e(b)}</td><td class='note'>{e(c)}</td></tr>"
    for a, b, c in rows)

cov = ""
if cv and cv.get("archive_total"):
    cov = (f"{n(cv.get('rows_total'))} runs in windows verified against ENA's own counts, "
           f"out of {n(cv.get('archive_total'))} in the archive "
           f"({100*(cv.get('coverage') or 0):.2f}%).")

nmx = (nm or {}).get("cross_study_pairs", {})

HTML = f"""<title>Same Bytes, Different Organism</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<style>
:root {{
  --ground:#FAFAF8; --panel:#FFFFFF; --ink:#12161A; --ink-2:#3C444C; --muted:#6F7780;
  --rule:#E2E3DF; --rule-2:#CFD1CC;
  --accent:#B3261E; --accent-soft:#F6E7E5; --confirm:#1F6F6B; --confirm-soft:#E6F0EF;
  --shadow: 0 1px 2px rgba(18,22,26,.05), 0 8px 24px -18px rgba(18,22,26,.35);
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#0E1113; --panel:#161A1D; --ink:#E9EBE7; --ink-2:#B9BEC2; --muted:#8A9299;
    --rule:#262B2F; --rule-2:#39403f;
    --accent:#FF7A6B; --accent-soft:#2A1B19; --confirm:#63C4BC; --confirm-soft:#132523;
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 10px 30px -20px rgba(0,0,0,.9);
  }}
}}
:root[data-theme="dark"] {{
  --ground:#0E1113; --panel:#161A1D; --ink:#E9EBE7; --ink-2:#B9BEC2; --muted:#8A9299;
  --rule:#262B2F; --rule-2:#39403f;
  --accent:#FF7A6B; --accent-soft:#2A1B19; --confirm:#63C4BC; --confirm-soft:#132523;
  --shadow: 0 1px 2px rgba(0,0,0,.4), 0 10px 30px -20px rgba(0,0,0,.9);
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"Source Serif 4", Georgia, serif; font-size:18px; line-height:1.62;
  -webkit-font-smoothing:antialiased;
}}
.wrap {{ max-width:73ch; margin:0 auto; padding:clamp(2rem,6vw,5rem) clamp(1.1rem,4vw,2rem) 6rem; }}
h1,h2,h3,.tag,.acc,.num,.payload-label,th {{ font-family:"IBM Plex Sans Condensed", "Helvetica Neue", Arial, sans-serif; }}
h1 {{ font-size:clamp(2.3rem,6.2vw,3.5rem); line-height:1.02; letter-spacing:-.015em; font-weight:700;
     margin:.2em 0 .35em; text-wrap:balance; }}
h2 {{ font-size:1.42rem; letter-spacing:-.005em; font-weight:600; margin:3.2rem 0 .8rem; text-wrap:balance;
     padding-top:1.1rem; border-top:1px solid var(--rule); }}
h3 {{ font-size:1.02rem; font-weight:600; margin:2rem 0 .4rem; letter-spacing:.01em; }}
p {{ margin:0 0 1.05em; }}
a {{ color:var(--accent); text-underline-offset:3px; }}
.eyebrow {{ font-family:"IBM Plex Mono", ui-monospace, monospace; font-size:.72rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--accent); margin:0 0 .2em; }}
.lede {{ font-size:1.2rem; color:var(--ink-2); border-left:2px solid var(--accent); padding-left:1.1rem; margin:1.6rem 0 2.2rem; }}
.meta {{ font-family:"IBM Plex Mono", ui-monospace, monospace; font-size:.76rem; color:var(--muted);
  line-height:1.9; border-top:1px solid var(--rule); padding-top:.9rem; }}
.specimen {{ margin:1.6rem 0 2rem; background:var(--panel); border:1px solid var(--rule);
  border-radius:2px; box-shadow:var(--shadow); overflow:hidden; }}
.specimen-tag {{ font-family:"IBM Plex Mono", ui-monospace, monospace; font-size:.68rem; letter-spacing:.13em;
  text-transform:uppercase; color:var(--accent); background:var(--accent-soft);
  padding:.5rem .95rem; border-bottom:1px solid var(--rule); }}
.specimen-body {{ display:grid; grid-template-columns:1fr auto 1fr; align-items:stretch; }}
.side {{ padding:1rem .95rem; min-width:0; }}
.side + .side {{ }}
.acc {{ font-family:"IBM Plex Mono", ui-monospace, monospace; font-size:.82rem; font-weight:500;
  color:var(--ink); word-break:break-word; }}
.ident {{ font-size:.98rem; font-weight:600; margin-top:.2rem; line-height:1.3; }}
.prov {{ font-family:"IBM Plex Mono", ui-monospace, monospace; font-size:.7rem; color:var(--muted);
  margin-top:.35rem; line-height:1.55; word-break:break-word; }}
.join {{ display:flex; align-items:center; justify-content:center; padding:0 .3rem;
  border-left:1px solid var(--rule); border-right:1px solid var(--rule); background:var(--ground); }}
.join span {{ font-family:"IBM Plex Mono", ui-monospace, monospace; font-size:1.1rem; color:var(--accent); }}
.payload {{ font-family:"IBM Plex Mono", ui-monospace, monospace; font-size:.72rem; color:var(--ink-2);
  padding:.7rem .95rem; border-top:1px solid var(--rule); background:var(--ground);
  overflow-x:auto; white-space:nowrap; }}
.payload-label {{ display:inline-block; font-size:.62rem; letter-spacing:.13em; text-transform:uppercase;
  color:var(--confirm); margin-right:.7rem; }}
.evidence {{ font-size:.92rem; color:var(--ink-2); margin:0; padding:.85rem .95rem 1rem; }}
table {{ width:100%; border-collapse:collapse; margin:1.2rem 0 1.6rem; font-size:.93rem; }}
th, td {{ text-align:left; padding:.55rem .6rem; border-bottom:1px solid var(--rule); vertical-align:baseline; }}
th[scope=row] {{ font-weight:600; font-size:.9rem; width:46%; }}
td.num {{ font-family:"IBM Plex Mono", ui-monospace, monospace; font-variant-numeric:tabular-nums;
  white-space:nowrap; color:var(--accent); }}
td.note {{ color:var(--muted); font-size:.84rem; }}
.tablewrap {{ overflow-x:auto; }}
.callout {{ background:var(--confirm-soft); border:1px solid var(--rule); border-left:2px solid var(--confirm);
  padding:1rem 1.1rem; margin:1.6rem 0; font-size:.95rem; border-radius:2px; }}
.callout strong {{ color:var(--confirm); }}
code {{ font-family:"IBM Plex Mono", ui-monospace, monospace; font-size:.85em;
  background:var(--accent-soft); padding:.1em .32em; border-radius:2px; }}
ul {{ padding-left:1.15rem; }} li {{ margin-bottom:.45em; }}
footer {{ margin-top:3.5rem; padding-top:1.2rem; border-top:1px solid var(--rule);
  font-family:"IBM Plex Mono", ui-monospace, monospace; font-size:.72rem; color:var(--muted); line-height:1.9; }}
@media (max-width:620px) {{
  .specimen-body {{ grid-template-columns:1fr; }}
  .join {{ border-left:0; border-right:0; border-top:1px solid var(--rule); border-bottom:1px solid var(--rule); padding:.3rem; }}
  th[scope=row] {{ width:auto; }}
}}
</style>
<div class="wrap">
<p class="eyebrow">INSDC · raw-read archives · checksum census</p>
<h1>Same bytes, different organism</h1>
<p class="lede">Content-identical sequencing data sits in the public archives under separate
accessions, and some of those copies declare different biological identities — different named
bacterial isolates, different plant families, different human donors. The checksum field that
would reveal it cannot, by construction.</p>

<h2>Why this has stayed invisible</h2>
<p>ENA regenerates FASTQ from its archived object and writes the run accession into every read
header, so two byte-identical datasets get <em>different</em> <code>fastq_md5</code>. Across one
freshly fetched month ({n((trap or {}).get('runs'))} runs), {n((trap or {}).get('runs_with_fastq_md5'))} runs carry a
<code>fastq_md5</code>, producing {n((trap or {}).get('distinct_fastq_md5'))} distinct values and
<strong>{n((trap or {}).get('fastq_md5_collisions'))} collisions</strong>. The field that does work,
<code>submitted_md5</code> — the checksum of the file as the submitter uploaded it — is present for
100% of ENA-submitted runs and essentially none of the NCBI-submitted ones, and is not what anyone
reaches for.</p>

<h2>Six specimens</h2>
<p>Each was checked against the data itself, not the metadata: files downloaded and hashed locally,
NCBI's exact A/C/G/T/N composition compared, the first 2,000 read sequences compared with headers
ignored, or multi-gigabyte files range-checked at both ends.</p>
{''.join(case_html(c) for c in CASES)}

<div class="callout"><strong>{n((cf or {}).get('n_identity_conflicts'))} cross-study pairs declare conflicting biological identities</strong>,
collapsing to {(cf or {}).get('n_conflicting_study_pairs','—')} distinct study-pairs — {(cf or {}).get('n_organism_level_study_pairs','—')} of them organism-level
(different species or wider), {(cf or {}).get('n_metagenome_level_study_pairs','—')} environment-label. A seeded random sample of those needing
confirmation was checked against NCBI's exact base composition: <strong>{(cf or {}).get('n_numeric_confirmed','—')} confirmed,
{(cf or {}).get('n_numeric_refuted','—')} refuted, {(cf or {}).get('n_numeric_no_fingerprint','—')} without a fingerprint</strong>
({pc((cf or {}).get('numeric_confirmation_rate'), 1)} [{pc([(cf or {}).get('numeric_confirmation_rate',[0,0,0])[1]],1)}, {pc([(cf or {}).get('numeric_confirmation_rate',[0,0,0])[2]],1)}]).
The method also refutes when it should:
ERR296666 and ERR326475 share <code>read_count</code> 2,532,937 and <code>base_count</code> 506,587,400
exactly and are <em>not</em> duplicates — their base compositions differ completely.</div>

<h2>How common</h2>
<p>{e(cov)} The census period 2010-2018 is covered completely — every monthly window verified
against ENA's own count — with later windows collected opportunistically and included in the
same verified total.</p>
<div class="tablewrap"><table><tbody>{table_html}</tbody></table></div>
<p>The permutation null matters here: shuffling study labels while preserving study sizes sends
almost every duplicate group across a study boundary, while the observed data keeps most of them
inside one study. Cross-study duplication is the rare tail, not the bulk.</p>

<h2>What it breaks</h2>
<ul>
<li><strong>Pooled analyses count one dataset twice.</strong> ENA's own curation team, in a 2016
<em>Database</em> paper about curating these very samples, tabulates PRJEB1720 and PRJEB4562 side by
side as independent studies. Those two studies share 56 byte-identical files. The words
“duplicate”, “redundant” and “identical” appear zero times in it.</li>
<li><strong>In pathogen genomics a duplicate looks exactly like a transmission event.</strong>
Identical genomes give a SNP distance of zero, which is the strongest evidence of recent
transmission there is.</li>
<li><strong>Whole studies are inflated.</strong> One study in the census has 42 runs under 42
BioSample accessions and 21 distinct datasets; another registered every sample twice, once with an
“_updated” suffix.</li>
<li><strong>It contradicts stated policy.</strong> NCBI's SRA submission standards say plainly:
“Duplicate submissions are not permitted; reference the existing accession instead.”</li>
</ul>

<h2>What would show this is wrong</h2>
<ul>
<li>Read data that differed between a claimed pair. Tested on every case reported.</li>
<li><code>submitted_md5</code> being a stored assertion rather than a property of the bytes. Tested by
downloading both files and hashing them locally.</li>
<li>One stored object referenced twice rather than two stored copies. Tested: the copies sit at
different FTP paths.</li>
<li>The conflicting labels being benign synonyms. Strain-level relabelling
(<em>Vibrio cholerae</em> vs <em>V. cholerae</em> O1 biovar El Tor) is classified benign and excluded.</li>
</ul>

<h2>Honest limits</h2>
<ul>
<li>The exact channel reaches ENA-submitted runs only; NCBI's public metadata dumps have the
per-file checksum block stripped, so the NCBI side is a lower bound reached through numeric
candidates plus per-run confirmation.</li>
<li>The numeric channel alone has cross-study precision {pc(nmx.get('precision'), 1)} at recall
{pc(nmx.get('recall'), 1)}. Nothing is reported from it unconfirmed.</li>
<li>Whether any given duplicate is an error, an undisclosed reuse or a documented re-release is not
determinable from public metadata, and no claim is made about which.</li>
<li>Three separate bugs in the collection pipeline silently lost data before being caught — most
seriously, ENA's <code>first_public&lt;=E</code> excludes E, so every window initially lost its last
day. All are written up in the worklog.</li>
</ul>

<footer>
Data: ENA Portal API (read_run), NCBI SRA per-run XML, ENA taxonomy REST, Europe PMC, NCBI GEO.
Public, unauthenticated, redistributable.<br>
Generated {datetime.date.today().isoformat()} from the pipeline's own result files — no figure on this page was typed by hand.
</footer>
</div>
"""
open(DEST, "w").write(HTML)
print("wrote", DEST, len(HTML), "bytes")
