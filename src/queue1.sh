#!/bin/zsh
# Sequential GPU queue: ONE low-priority MLX job at a time. Logs in data/logs/.
cd "$(dirname "$0")"
source ../.venv/bin/activate
M=../data/models
L=../data/logs
LIVE="--dataset ../data/swebench_live_post.jsonl --instances ../results/live_ids.txt"
TEST="--instances ../results/test_ids.txt"
C="nice -n 10 python run_conflict.py --max-file-tokens 32000"
G="nice -n 10 python run_generative.py --max-file-tokens 32000"
${=C} --model $M/gemma-4-e4b-it-4bit --tag e4b_test ${=TEST} --frames R,RX > $L/e4b_test.log 2>&1
${=G} --model $M/gemma-4-e4b-it-4bit --tag e4b_test ${=TEST} > $L/gen_e4b_test.log 2>&1
${=C} --model $M/gemma-4-e4b-it-4bit --tag e4b_live ${=LIVE} --limit 200 --frames R,RX > $L/e4b_live.log 2>&1
${=G} --model $M/gemma-4-e4b-it-4bit --tag e4b_live ${=LIVE} --limit 200 > $L/gen_e4b_live.log 2>&1
echo QUEUE1_DONE > $L/queue1.done
