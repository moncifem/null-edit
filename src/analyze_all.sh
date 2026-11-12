#!/bin/zsh
# Regenerate every table and figure of the paper from saved per-token log-probabilities.
# CPU only. Usage: NULLEDIT_RESULTS=../results_dgx zsh analyze_all.sh   (run from src/)
# Steps whose inputs are missing are skipped, so this can be run while experiments are in flight.
set -u
PY=${PY:-../.venv/bin/python}
R=${NULLEDIT_RESULTS:-../results_dgx}
export NULLEDIT_RESULTS=$R
T=../results/test_ids.txt
LIVE=../data/swebench_live_post.jsonl
has() { [ -e "$R/$1" ] }
an() {  # an <tag> <json> [extra args...]
  local tag=$1 out=$2; shift 2
  has conflict_$tag/log.jsonl || { echo "skip $tag"; return 1; }
  $PY analyze_conflict.py --tag $tag --json $R/$out "$@" > $R/${out%.json}.features.txt 2>&1 || { echo "FAILED $tag"; return 1; }
}
gen() { has gen_$1/gen.jsonl && echo "$2 $1" }   # gen <tag> <flag>

# --- E4B, held-out Verified (Table 1, Fig 2) ---
an e4b_test an_e4b_test.json --ids $T $(gen e4b_test --gen) $(gen e4b_test_quote --gen2) \
  && $PY report.py $R/an_e4b_test.json --name "Gemma 4 E4B, SWE-bench Verified held-out (DGX arm)" > $R/report_e4b_test.md
has an_e4b_test.json && $PY extra_stats.py $R/an_e4b_test.json ../results/an_e4b_test.json > $R/extra_e4b_test.md 2>&1

# --- E4B, post-cutoff SWE-bench-Live ---
an e4b_live an_e4b_live.json --dataset $LIVE $(gen e4b_live --gen) $(gen e4b_live_quote --gen2) \
  && $PY report.py $R/an_e4b_live.json --name "Gemma 4 E4B, SWE-bench-Live post-cutoff (DGX arm)" > $R/report_e4b_live.md

# --- instruction / issue controls (RB, R0) merged with R, RX on the same files ---
if has conflict_e4b_ctrl/log.jsonl; then
  $PY merge_frames.py e4b_ctrl_all e4b_ctrl e4b_test
  an e4b_ctrl_all an_e4b_ctrl.json --ids $T && $PY report.py $R/an_e4b_ctrl.json --name "Controls, E4B (DGX arm)" > $R/report_e4b_ctrl.md
fi

# --- 4-bit weights (the MAC arm's MLX checkpoint) run through the DGX code ---
an e4b_q4_test an_e4b_q4_test.json --ids $T \
  && $PY report.py $R/an_e4b_q4_test.json --name "E4B, MLX 4-bit weights in PyTorch (DGX arm)" > $R/report_e4b_q4_test.md

# --- other sizes: merge late RX runs, analyse, scaling table (Table 2, Fig 3) ---
for m in g31b g26b; do
  if has conflict_${m}_test_rx/log.jsonl; then $PY merge_frames.py ${m}_test_h ${m}_test ${m}_test_rx; fi
done
SC=()
for pair in E2B:e2b_test E4B:e4b_test 12B:g12b_test "26B-A4B:g26b_test" 31B:g31b_test; do
  name=${pair%%:*}; tag=${pair##*:}
  [ -e $R/conflict_${tag}_h/log.jsonl ] && tag=${tag}_h
  short=${tag%_test*}
  if [ $name = E4B ]; then has an_e4b_test.json && SC+=("$name=an_e4b_test.json"); continue; fi
  an $tag an_$tag.json --ids $T $(gen ${short}_test --gen) $(gen ${short}_test_quote --gen2) && {
    nm=$name; [ $name = 31B ] && nm="31B*"   # 31B covers files up to 11,000 tokens only: reported where it has files
    $PY report.py $R/an_$tag.json --name "Gemma 4 $name, held-out (DGX arm)" > $R/report_$tag.md; SC+=("$nm=an_$tag.json"); }
done
[ ${#SC} -ge 2 ] && $PY scaling.py $SC > $R/scaling.md

# --- code-lines-only map (section 4.6): exploratory on issues 1-100, pre-registered confirmation on issues 101-200 ---
has conflict_g26b_test/log.jsonl && $PY analyze_codeonly.py --ids $T --limit 100 --common --out codeonly_sizes.json \
  --runs E2B=e2b_test 12B=g12b_test 26B-A4B=g26b_test --ref E4B=e4b_test > $R/report_codeonly_sizes.md
has conflict_g31b_test/log.jsonl && $PY analyze_codeonly.py --ids $T --limit 100 --out codeonly_31b.json \
  --runs 31B=g31b_test --ref E4B=e4b_test > $R/report_codeonly_31b.md
CF=(); for pair in 12B:g12b_conf "26B-A4B:g26b_conf" 31B:g31b_conf; do has conflict_${pair##*:}/log.jsonl && CF+=("${pair%%:*}=${pair##*:}"); done
[ ${#CF} -ge 1 ] && $PY analyze_codeonly.py --ids ../results/conf_ids.txt --out codeonly_conf.json --runs $CF --ref E4B=e4b_test > $R/report_codeonly_conf.md

# --- live, other sizes ---
for pair in E2B:e2b_live 12B:g12b_live "26B-A4B:g26b_live" 31B:g31b_live; do
  name=${pair%%:*}; tag=${pair##*:}
  an $tag an_$tag.json --dataset $LIVE && $PY report.py $R/an_$tag.json --name "Gemma 4 $name, SWE-bench-Live (DGX arm)" > $R/report_$tag.md
done

# --- file level, fixed point ---
has file_cands.json && has conflict_e4b_test/log.jsonl && $PY analyze_filelevel.py --tag e4b_test > $R/report_filelevel.md 2>&1; grep -q Traceback $R/report_filelevel.md 2>/dev/null && rm $R/report_filelevel.md
has fixedpoint_e4b/scores.jsonl && $PY analyze_fixedpoint.py --tag e4b > $R/report_fixedpoint.md 2>&1

$PY figures.py pydata__xarray-4075 xarray/core/weighted.py
ls $R/*.md

# --- context budget (post hoc, agent-facing) ---
has conflict_e4b_test/log.jsonl && $PY context_budget.py --tag e4b_test --ids $T $(gen e4b_test_quote --gen2) $(gen e4b_test --gen) --json $R/context_budget_e4b_test.json > $R/report_context_budget.md

# --- let-it-write baseline and map-guided edit ---
has edit_e4b_test/gen.jsonl && $PY analyze_edit.py --tag e4b_test --conflict-tag e4b_test --hints $R/hints_e4b_test.json > $R/report_edit.md 2>&1

# --- no-prefill check on the greedy-no-op files ---
has noprefill_e4b_test/gen.jsonl && $PY -c "
import json,sys
r=[json.loads(l) for l in open('$R/noprefill_e4b_test/gen.jsonl')]
print(len(r),'files; reply opens with a python fence:',sum(x['starts_with_fence'] for x in r),'; and copies the file opening:',sum(x['copies_file_opening'] for x in r))
for x in r:
    if not x['copies_file_opening']: print('---',x['iid'],x['path'],repr(x['response'][:160]))
" > $R/report_noprefill.md

# --- numbers quoted in the paper that no other report prints ---
$PY paper_numbers.py > $R/report_paper_numbers.md 2>/dev/null

# --- MAC arm (MLX, 4-bit) reports quoted in the paper; they always read ../results ---
M=../results
if [ -e $M/edit_e4b_test_mac/gen.jsonl ]; then
  NULLEDIT_RESULTS=$M $PY analyze_edit.py --tag e4b_test_mac --conflict-tag e4b_test --hints $M/hints_e4b_test_mac.json > $M/report_edit_mac.md 2>/dev/null
  NULLEDIT_RESULTS=$M $PY analyze_edit.py --tag e4b_test_mac --conflict-tag e4b_test --hints $M/hints_e4b_test_mac.json --lenient-truncation > $M/report_edit_mac_lenient.md 2>/dev/null
fi
[ -e $M/conflict_g12b_conf_mac/log.jsonl ] && NULLEDIT_RESULTS=$M $PY analyze_codeonly.py --ids $M/conf_ids.txt --runs 12B-4bit=g12b_conf_mac > $M/report_codeonly_conf_mac.md 2>/dev/null
