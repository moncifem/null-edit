#!/bin/zsh
# Laptop (MAC arm) follow-up, ONE throttled low-priority job at a time, after the edit run has finished:
# cross-backend check of the long-file copy cost of 12B and E2B (MLX 4-bit; the DGX arm uses PyTorch bf16).
# Files: first 10 single-file issues of the held-out order with a 5k-12k-token file and first 10 under 5k
# (results/lencheck_ids.txt, chosen by length only).
cd "$(dirname "$0")"
while pgrep -f "run_edit.py" > /dev/null; do sleep 30; done
export THROTTLE=${THROTTLE:-1.5} SCORER_BACKEND=mlx NULLEDIT_RESULTS=../results PYTHONUNBUFFERED=1
L=../data/logs
# no-prefill check (HYPOTHESES.md Revision 2d): the 4-bit model answers freely on the 84 files that are greedy no-ops for bf16
echo "$(date -u +%H:%M:%S) START noprefill_e4b_test_mac" >> $L/queue_mac2.progress
nice -n 10 ../.venv/bin/python run_noprefill.py --model ../data/models/gemma-4-e4b-it-4bit --tag e4b_test_mac --files ../results/noprefill_files_dgx84.json > $L/noprefill_e4b_test_mac.log 2>&1
echo "$(date -u +%H:%M:%S) END noprefill_e4b_test_mac ($?)" >> $L/queue_mac2.progress
for pair in g12b:gemma-4-12B-it-4bit e2b:gemma-4-e2b-it-4bit; do
  tag=${pair%%:*}_lencheck; m=${pair##*:}
  echo "$(date -u +%H:%M:%S) START $tag" >> $L/queue_mac2.progress
  nice -n 10 ../.venv/bin/python run_conflict.py --max-file-tokens 32000 --model ../data/models/$m --tag $tag --instances ../results/lencheck_ids.txt --frames R,RX > $L/$tag.log 2>&1
  echo "$(date -u +%H:%M:%S) END $tag ($?)" >> $L/queue_mac2.progress
done
