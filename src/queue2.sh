#!/bin/zsh
# Second sequential queue (starts when queue1 has finished). One low-priority MLX job at a time.
cd "$(dirname "$0")"
source ../.venv/bin/activate
M=../data/models
L=../data/logs
while [ ! -f $L/queue1.done ]; do sleep 20; done
TEST="--instances ../results/test_ids.txt"
C="nice -n 10 python run_conflict.py --max-file-tokens 32000"
G="nice -n 10 python run_generative.py --max-file-tokens 32000"
# controls: right issue + copy instruction (RB), no issue + copy (R0)
${=C} --model $M/gemma-4-e4b-it-4bit --tag e4b_ctrl ${=TEST} --limit 100 --frames RB,R0 > $L/e4b_ctrl.log 2>&1
# first-deviation identity vs real sampling
nice -n 10 python calibrate_sampling.py --model $M/gemma-4-e4b-it-4bit --tag e4b --instances ../results/test_ids.txt > $L/calib.log 2>&1
# file level: gold + 3 BM25 hard negatives
${=C} --model $M/gemma-4-e4b-it-4bit --tag e4b_test --instances ../results/file_ids.txt --files cands --cands ../results/file_cands_paths.json --frames R,RX > $L/e4b_file.log 2>&1
# fixed-point patch verification
nice -n 10 python run_fixedpoint.py --model $M/gemma-4-e4b-it-4bit --tag e4b --instances ../results/test_ids.txt --limit 110 --k 3 --max-file-tokens 6000 > $L/fixedpoint_e4b.log 2>&1
# model-size scaling
${=C} --model $M/gemma-4-e2b-it-4bit --tag e2b_test ${=TEST} --limit 150 --frames R,RX > $L/e2b_test.log 2>&1
${=G} --model $M/gemma-4-e2b-it-4bit --tag e2b_test ${=TEST} --limit 150 > $L/gen_e2b_test.log 2>&1
${=C} --model $M/gemma-4-12B-it-4bit --tag g12b_test ${=TEST} --limit 150 --frames R,RX > $L/g12b_test.log 2>&1
${=G} --model $M/gemma-4-12B-it-4bit --tag g12b_test ${=TEST} --limit 150 > $L/gen_g12b_test.log 2>&1
echo QUEUE2_DONE > $L/queue2.done
