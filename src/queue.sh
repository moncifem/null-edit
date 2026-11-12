#!/bin/zsh
# Single sequential GPU queue: ONE low-priority, duty-cycled MLX job at a time.
# THROTTLE=1.5 -> the GPU works ~40% of the time (sleeps 1.5x the compute time after each chunk).
cd "$(dirname "$0")"
source ../.venv/bin/activate
export THROTTLE=${THROTTLE:-1.5}
M=../data/models
L=../data/logs
TEST="--instances ../results/test_ids.txt"
LIVE="--dataset ../data/swebench_live_post.jsonl --instances ../results/live_ids.txt"
C="nice -n 10 python run_conflict.py --max-file-tokens 32000"
G="nice -n 10 python run_generative.py --max-file-tokens 32000"
E4B=$M/gemma-4-e4b-it-4bit; E2B=$M/gemma-4-e2b-it-4bit; G12=$M/gemma-4-12B-it-4bit
step() { echo "$(date -u +%H:%M:%S) START $1" >> $L/queue.progress; shift; "$@"; echo "$(date -u +%H:%M:%S) END" >> $L/queue.progress; }
# --- core: held-out localization, E4B ---
step e4b_test      ${=C} --model $E4B --tag e4b_test ${=TEST} --limit 250 --frames R,RX            > $L/e4b_test.log 2>&1
step gen_e4b_test  ${=G} --model $E4B --tag e4b_test ${=TEST} --limit 250                          > $L/gen_e4b_test.log 2>&1
step genq_e4b_test ${=G} --mode quote --model $E4B --tag e4b_test_quote ${=TEST} --limit 250       > $L/genq_e4b_test.log 2>&1
# --- memorization control: post-cutoff issues ---
step e4b_live      ${=C} --model $E4B --tag e4b_live ${=LIVE} --limit 150 --frames R,RX            > $L/e4b_live.log 2>&1
step gen_e4b_live  ${=G} --model $E4B --tag e4b_live ${=LIVE} --limit 150                          > $L/gen_e4b_live.log 2>&1
step genq_e4b_live ${=G} --mode quote --model $E4B --tag e4b_live_quote ${=LIVE} --limit 150       > $L/genq_e4b_live.log 2>&1
# --- controls: right issue + copy instruction (RB), no issue + copy (R0) ---
step e4b_ctrl      ${=C} --model $E4B --tag e4b_ctrl ${=TEST} --limit 60 --frames RB,R0            > $L/e4b_ctrl.log 2>&1
# --- fixed-point patch verification ---
step fixedpoint    nice -n 10 python run_fixedpoint.py --model $E4B --tag e4b ${=TEST} --limit 80 --k 3 --max-file-tokens 6000 > $L/fixedpoint_e4b.log 2>&1
# --- file level: gold + 3 BM25 hard negatives ---
step e4b_file      ${=C} --model $E4B --tag e4b_test --instances ../results/file_ids.txt --limit 80 --files cands --cands ../results/file_cands_paths.json --frames R,RX > $L/e4b_file.log 2>&1
# --- model-size scaling ---
step g12b_test     ${=C} --model $G12 --tag g12b_test ${=TEST} --limit 100 --frames R,RX           > $L/g12b_test.log 2>&1
step gen_g12b_test ${=G} --model $G12 --tag g12b_test ${=TEST} --limit 100                         > $L/gen_g12b_test.log 2>&1
step e2b_test      ${=C} --model $E2B --tag e2b_test ${=TEST} --limit 100 --frames R,RX            > $L/e2b_test.log 2>&1
step gen_e2b_test  ${=G} --model $E2B --tag e2b_test ${=TEST} --limit 100                          > $L/gen_e2b_test.log 2>&1
# --- first-deviation identity vs real sampling ---
step calib         nice -n 10 python calibrate_sampling.py --model $E4B --tag e4b --instances ../results/test_ids.txt > $L/calib.log 2>&1
# --- 12B on post-cutoff issues ---
step g12b_live     ${=C} --model $G12 --tag g12b_live ${=LIVE} --limit 80 --frames R,RX            > $L/g12b_live.log 2>&1
step gen_g12b_live ${=G} --model $G12 --tag g12b_live ${=LIVE} --limit 80                          > $L/gen_g12b_live.log 2>&1
echo QUEUE_DONE > $L/queue.done
