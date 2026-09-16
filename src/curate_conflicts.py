#!/usr/bin/env python3
"""Curated classification of the organism-level identity-conflict study pairs.

The automated taxonomy comparison (identity_conflicts.py) flags any cross-study duplicate whose
two declared taxa differ below the level it considers benign. Manual inspection of all 67
flagged study pairs (log/07-organism-conflict-audit.md), with NCBI STAT taxonomy where it can
resolve the question (stat_taxonomy.py), gives the categories below. Every assignment is
recorded here so it can be disputed line by line.

Categories
  REFINEMENT   the two labels name the same organism at different depth or under a synonym
               (M. tuberculosis vs "M. tuberculosis complex sp."; species vs its hybrid;
               Oxytricha trifallax = Sterkiella histriomuscorum). NOT an identity conflict.
  PLACEHOLDER  one or both labels are environmental/provisional placeholders ("uncultured
               archaeon", "Bacteria aborigena", genus-only). Not testable as a species claim.
  HOST_ASSOC   host organism and an organism it physically carries (integrated bracovirus,
               co-isolate). One sequencing run can legitimately appear under both.
  MIXTURE      STAT shows the shared content contains BOTH declared organisms: a pooled or
               multi-organism run deposited once per constituent.
  FILE_MIX     one submitted file (not the whole run) belongs to the other organism.
  MISATTR_ADJ  genuinely incompatible labels, and NCBI STAT identifies which record's content
               contradicts its own label.
  MISATTR_UNADJ genuinely incompatible labels; STAT's 2016-2022 reference set cannot resolve
               the species (plants, fish, fungi, amplicon data), so which side is wrong is
               unknown from public data.
"""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (study A, study B) sorted -> (category, which record STAT contradicts or note)
CURATED = {
  # --- REFINEMENT / SYNONYM ---
  ("PRJEB15463","PRJEB27847"): ("REFINEMENT", "M. tuberculosis vs M. tuberculosis complex sp."),
  ("PRJEB11460","PRJEB9680"):  ("REFINEMENT", "M. tuberculosis vs MTBC sp."),
  ("PRJEB11460","PRJEB15463"): ("REFINEMENT", "M. tuberculosis vs MTBC sp."),
  ("PRJEB11460","PRJEB6273"):  ("REFINEMENT", "M. tuberculosis vs MTBC sp."),
  ("PRJEB11460","PRJEB9545"):  ("REFINEMENT", "M. tuberculosis vs MTBC sp."),
  ("PRJEB11460","PRJEB7727"):  ("REFINEMENT", "M. tuberculosis vs MTBC sp."),
  ("PRJEB22358","PRJNA302362"): ("REFINEMENT", "M. tuberculosis vs MTBC sp."),
  ("PRJNA300644","PRJNA433223"): ("REFINEMENT", "Saccharum officinarum vs Saccharum hybrid cultivar"),
  ("PRJNA545208","PRJNA545783"): ("REFINEMENT", "Bambusa pervariabilis vs its hybrid"),
  ("PRJNA486431","PRJNA510231"): ("REFINEMENT", "'Colon' (tissue placeholder) vs Homo sapiens; STAT: human"),
  ("PRJEB14646","PRJNA326914"): ("REFINEMENT", "Chryseobacterium sp. 113 vs sp. CBo1 — strain-level, both unnamed"),
  ("PRJEB11563","PRJEB12660"):  ("REFINEMENT", "Bos indicus vs Bos taurus — subspecies-level in common usage; microbiome amplicon"),
  ("PRJEB11576","PRJEB12660"):  ("REFINEMENT", "Bos indicus gudali vs Bos taurus — as above"),
  ("PRJNA12857","PRJNA74629"):  ("REFINEMENT", "Oxytricha trifallax = Sterkiella histriomuscorum (synonym)"),
  # --- PLACEHOLDER ---
  ("PRJEB9004","PRJEB9031"):   ("PLACEHOLDER", "uncultured archaeon vs uncultured bacterium (VTT; same amplicon file per primer target)"),
  ("PRJEB18457","PRJEB21687"): ("PLACEHOLDER", "uncultured bacterium vs uncultured archaeon (VTT)"),
  ("PRJEB9004","PRJEB9160"):   ("PLACEHOLDER", "uncultured archaeon vs uncultured bacterium (VTT)"),
  ("PRJEB9004","PRJEB9112"):   ("PLACEHOLDER", "uncultured archaeon vs uncultured fungus (VTT); STAT: Sarocladium 77%"),
  ("PRJEB6874","PRJEB9004"):   ("PLACEHOLDER", "uncultured methanogenic archaeon vs uncultured archaeon (VTT)"),
  ("PRJEB10578","PRJEB10590"): ("PLACEHOLDER", "'Bacteria aborigena' vs 'Bacteria ambigua' — provisional culturomics names, one submitter"),
  ("PRJEB10590","PRJEB7053"):  ("PLACEHOLDER", "as above"),
  ("PRJEB10590","PRJEB9815"):  ("PLACEHOLDER", "as above"),
  ("PRJEB20096","PRJEB7053"):  ("PLACEHOLDER", "'Bacteria aetolus' vs 'Bacteria aborigena' — as above"),
  ("PRJNA381824","PRJNA412964"): ("PLACEHOLDER", "genus-only labels Chryseolinea vs Luedemannella; STAT resolves neither"),
  ("PRJNA342241","PRJNA342756"): ("PLACEHOLDER", "lichen Rinodina archaea vs Steroidobacter (lichen-associated bacterium); STAT: mostly unassigned"),
  # --- HOST + ASSOCIATED ORGANISM ---
  ("PRJNA282814","PRJNA319039"): ("HOST_ASSOC", "Microplitis demolitor wasp vs its integrated bracovirus; STAT: wasp 92%, bracovirus 7%"),
  ("PRJNA290648","PRJNA312233"): ("HOST_ASSOC", "Aphanizomenon UKL13-PB vs co-isolate Hyphomonadaceae UKL13-1 (same culture)"),
  # --- MIXTURE deposited once per constituent ---
  ("PRJNA207831","PRJNA207832"): ("MIXTURE", "NIST CCQM reference run: STAT Listeria 19% + E. coli 10%; filed under each organism"),
  ("PRJNA49437","PRJNA51081"):  ("MIXTURE", "JCVI 454 pool: Finegoldia 30% + S. mitis 16% (+Peptoniphilus); filed under each of 3 organisms"),
  ("PRJNA49439","PRJNA51081"):  ("MIXTURE", "as above"),
  ("PRJNA49437","PRJNA49439"):  ("MIXTURE", "as above"),
  ("PRJNA49443","PRJNA49619"):  ("MIXTURE", "JCVI: L. delbrueckii 57% + L. salivarius 21% (STAT uses pre-2020 genus name)"),
  # --- FILE-LEVEL ---
  ("PRJEB2264","PRJEB2338"):    ("FILE_MIX", "potato SFF GBSKQZK02 sits inside the wheat run; STAT of wheat run: S. tuberosum 46% + Aegilops 35%"),
  # --- MISATTRIBUTION, adjudicated by STAT ---
  ("PRJNA53745","PRJNA53779"):  ("MISATTR_ADJ", "SRR071318 'S. epidermidis VCU111' holds S. lugdunensis 98%; VCU148 record correct"),
  ("PRJNA53793","PRJNA53813"):  ("MISATTR_ADJ", "'S. epidermidis IS-250' record holds S. aureus 77%"),
  ("PRJNA53795","PRJNA53813"):  ("MISATTR_ADJ", "'S. epidermidis IS-250' record holds S. aureus 77%"),
  ("PRJNA317585","PRJNA337915"): ("MISATTR_ADJ", "'Acinetobacter baumannii' record holds S. aureus 95%"),
  ("PRJNA487114","PRJNA487138"): ("MISATTR_ADJ", "'Abies homolepis' (fir) record holds Gallus gallus 45%"),
  ("PRJEB23728","PRJEB23778"):  ("MISATTR_ADJ", "'Salmonella enterica' record holds E. coli 16% / Salmonella 0% (IZSLT)"),
  ("PRJNA324120","PRJNA328794"): ("MISATTR_ADJ", "'Salmonella enterica' record holds E. coli 12% / Salmonella 0%"),
  ("PRJNA324120","PRJNA330858"): ("MISATTR_ADJ", "'Salmonella enterica' record holds E. coli 12% / Salmonella 0%"),
  ("PRJEB13242","PRJEB14753"):  ("MISATTR_ADJ", "'Homo sapiens' record holds Mus musculus 95% (Baylor)"),
  ("PRJNA10769","PRJNA12555"):  ("MISATTR_ADJ", "'Zea mays' record holds Bos taurus 15% / Zea 0%"),
  ("PRJNA308790","PRJNA339509"): ("MISATTR_ADJ", "'Apis cerana' record holds Apis mellifera 66%"),
  ("PRJNA246441","PRJNA302243"): ("MISATTR_ADJ", "'Hippocampus kelloggi' record holds H. erectus 35%"),
  ("PRJNA324615","PRJNA84221"):  ("MISATTR_ADJ", "'Pelosinus fermentans' record holds Acetivibrio (Ruminiclostridium) thermocellus 98%"),
  ("PRJNA321068","PRJNA339810"): ("MISATTR_ADJ", "'Primates' record holds Anopheles 68%"),
  ("PRJNA268581","PRJNA318866"): ("MISATTR_ADJ", "'Enteractinococcus helveticum' record holds Mesorhizobium 70%"),
  # --- MISATTRIBUTION, not resolvable by STAT ---
  ("PRJNA72625","PRJNA80145"):  ("MISATTR_UNADJ", "Gossypium arboreum vs G. barbadense; read-identical (confirmed); no cotton reference in STAT"),
  ("PRJNA72625","PRJNA80143"):  ("MISATTR_UNADJ", "as above"),
  ("PRJNA408223","PRJNA413737"): ("MISATTR_UNADJ", "Actinidia arguta vs A. chinensis (kiwifruit)"),
  ("PRJNA282184","PRJNA282185"): ("MISATTR_UNADJ", "Solanum lycopersicum vs S. habrochaites; STAT ambiguous (S. pennellii 11%, lycopersicum 9%)"),
  ("PRJEB17923","PRJEB19110"):  ("MISATTR_UNADJ", "Picea wilsonii vs P. sitchensis; file-level, different spot counts"),
  ("PRJNA281676","PRJNA315910"): ("MISATTR_UNADJ", "Synodontis nigriventris vs S. eupterus (catfish)"),
  ("PRJEB15412","PRJEB9777"):   ("MISATTR_UNADJ", "Medicago prostrata vs M. radiata"),
  ("PRJNA295128","PRJNA298670"): ("MISATTR_UNADJ", "Dendrobium densiflorum vs Eulophia picta (orchids)"),
  ("PRJNA392566","PRJNA392571"): ("MISATTR_UNADJ", "Lactarius sp. vs Lactifluus echinatus (fungi)"),
  ("PRJEB21445","PRJEB33681"):  ("MISATTR_UNADJ", "Rattus vs Mus as host of microbiome amplicon data"),
  ("PRJEB19502","PRJEB24580"):  ("MISATTR_UNADJ", "Bos taurus vs Mus musculus as host of microbiome amplicon data"),
  ("PRJEB7570","PRJEB7572"):    ("MISATTR_UNADJ", "Bacillus sp. DSM 5850 vs bacterium EM-17"),
  ("PRJNA310178","PRJNA310407"): ("MISATTR_UNADJ", "Acidobacterium capsulatum vs Segatella albensis; STAT resolves neither"),
  ("PRJNA436448","PRJNA470955"): ("MISATTR_UNADJ", "Homo sapiens vs Arabidopsis thaliana — SNU/IBS genome-editing projects, 23 small runs; STAT: Chordata"),
  ("PRJNA436188","PRJNA436448"): ("MISATTR_UNADJ", "Mus vs Homo — same submitter group, 16 runs; STAT partially human"),
  ("PRJNA436188","PRJNA470898"): ("MISATTR_UNADJ", "Mus vs Brassica napus — same group, 8 runs; STAT: Solanaceae"),
  ("PRJNA436448","PRJNA436750"): ("MISATTR_UNADJ", "Homo vs Mus — same group, 4 runs"),
  ("PRJNA451048","PRJNA470899"): ("MISATTR_UNADJ", "Mus vs Arabidopsis — same group, 3 runs"),
  ("PRJNA357678","PRJNA399227"): ("MISATTR_UNADJ", "Mus vs Homo; STAT: Esox lucius 100% (a third organism — likely reference artefact on tiny run)"),
}

def main():
    d = json.load(open(os.path.join(ROOT, "out", "conflicts_all.json")))["conflicts"]
    benign = {"metagenome_type_conflict", "metagenome_vs_organism", "same_taxid", "refinement", "same_species", "unknown"}
    org = [x for x in d if x["tax_relation"] not in benign]
    by = collections.defaultdict(list)
    for x in org: by[tuple(sorted(x["studies"]))].append(x)
    stat = {}
    try:
        for r in json.load(open(os.path.join(ROOT, "out", "stat_adjudication.json")))["rows"]:
            stat.setdefault(tuple(sorted(r["studies"])), []).append(r)
    except FileNotFoundError: pass
    rows = []; missing = []
    for sp, xs in by.items():
        cat, note = CURATED.get(sp, (None, None))
        if cat is None: missing.append(sp)
        names = collections.Counter(tuple(x["names"]) for x in xs).most_common(1)[0][0]
        sr = stat.get(sp, [])
        vc = collections.Counter(r["verdict"] for r in sr).most_common(1)
        rows.append(dict(studies=list(sp), n_run_pairs=len(xs), names=list(names), tax_relation=xs[0]["tax_relation"],
                         centers=[xs[0]["centers"][0], xs[0]["centers"][1]], category=cat, note=note,
                         stat_verdict=vc[0][0] if vc else None, stat_verdict_n=f"{vc[0][1]}/{len(sr)}" if vc else None))
    if missing: print("UNCURATED:", missing, file=sys.stderr)
    cats = collections.Counter(r["category"] for r in rows)
    runpairs = collections.Counter()
    for r in rows: runpairs[r["category"]] += r["n_run_pairs"]
    summary = {"study_pairs_total": len(rows), "by_category_study_pairs": dict(cats), "by_category_run_pairs": dict(runpairs),
               "genuine_conflict_study_pairs": sum(v for k, v in cats.items() if k and k.startswith("MISATTR")) + cats.get("MIXTURE", 0) + cats.get("FILE_MIX", 0),
               "not_conflicts": cats.get("REFINEMENT", 0) + cats.get("PLACEHOLDER", 0) + cats.get("HOST_ASSOC", 0)}
    json.dump({"summary": summary, "rows": sorted(rows, key=lambda r: (r["category"] or "", -r["n_run_pairs"]))},
              open(os.path.join(ROOT, "out", "organism_conflicts_curated.json"), "w"), indent=1)
    with open(os.path.join(ROOT, "out", "organism_conflicts_curated.tsv"), "w") as fh:
        fh.write("category\tstudyA\tstudyB\trun_pairs\tnameA\tnameB\tcenterA\tcenterB\tstat_verdict\tnote\n")
        for r in sorted(rows, key=lambda r: (r["category"] or "", -r["n_run_pairs"])):
            fh.write("\t".join(str(x) for x in [r["category"], r["studies"][0], r["studies"][1], r["n_run_pairs"], r["names"][0], r["names"][1],
                     r["centers"][0], r["centers"][1], r["stat_verdict"], r["note"]]) + "\n")
    print(json.dumps(summary, indent=1))

if __name__ == "__main__":
    main()
