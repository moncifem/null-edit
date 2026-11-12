#!/bin/zsh
# Third sequential queue (starts when queue2 has finished). One low-priority MLX job at a time.
cd "$(dirname "$0")"
source ../.venv/bin/activate
M=../data/models
L=../data/logs
while [ ! -f $L/queue2.done ]; do sleep 20; done
TEST="--instances ../results/test_ids.txt"
LIVE="--dataset ../data/swebench_live_post.jsonl --instances ../results/live_ids.txt"
C="nice -n 10 python run_conflict.py --max-file-tokens 32000"
G="nice -n 10 python run_generative.py --max-file-tokens 32000"
${=G} --mode quote --model $M/gemma-4-e4b-it-4bit --tag e4b_test_quote ${=TEST} > $L/genq_e4b_test.log 2>&1
${=G} --mode quote --model $M/gemma-4-e4b-it-4bit --tag e4b_live_quote ${=LIVE} --limit 200 > $L/genq_e4b_live.log 2>&1
${=C} --model $M/gemma-4-12B-it-4bit --tag g12b_live ${=LIVE} --limit 120 --frames R,RX > $L/g12b_live.log 2>&1
${=G} --model $M/gemma-4-12B-it-4bit --tag g12b_live ${=LIVE} --limit 120 > $L/gen_g12b_live.log 2>&1
${=G} --mode quote --model $M/gemma-4-12B-it-4bit --tag g12b_test_quote ${=TEST} --limit 150 > $L/genq_g12b_test.log 2>&1
${=G} --mode quote --model $M/gemma-4-12B-it-4bit --tag g12b_live_quote ${=LIVE} --limit 120 > $L/genq_g12b_live.log 2>&1
${=G} --mode quote --model $M/gemma-4-e2b-it-4bit --tag e2b_test_quote ${=TEST} --limit 150 > $L/genq_e2b_test.log 2>&1
echo QUEUE3_DONE > $L/queue3.done
