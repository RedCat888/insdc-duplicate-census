#!/bin/zsh
# Assemble REPORT.md: generated numbers first, then the hand-written interpretation.
cd ~/Downloads/dig
python3 src/build_dossier.py > /dev/null
python3 src/make_report.py > /dev/null
{
  cat REPORT_NARRATIVE.md
  echo; echo "---"; echo
  cat REPORT_NUMBERS.md
  echo; echo "---"; echo
  cat REPORT_CRITICISM.md
  echo; echo "---"; echo
  cat log/05-hypothesis-verdict.md
  echo; echo "---"; echo
  echo "## Reproducing this"
  echo '```bash'
  echo './run_all.sh'
  echo '```'
  echo
  echo "Environment pinned in \`env.txt\`; fixed seed 20260906 in \`src/params.py\`."
  echo "Preregistration and amendments: \`log/02-preregistration.md\`."
  echo "Everything that failed, including three ways the data was silently wrong:"
  echo "\`log/03-worklog.md\`. Count of everything tried: \`log/99-tally.md\`."
} > REPORT.md
echo "REPORT.md assembled: $(wc -l < REPORT.md) lines"
