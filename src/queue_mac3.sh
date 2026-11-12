#!/bin/zsh
# Laptop (MAC arm), one throttled low-priority job: confirmation set of Revision 3b, 12B 4-bit, files <= 12k tokens.
cd "$(dirname "$0")"
while pgrep -f "diag_alt_mac|run_conflict|run_edit" > /dev/null; do sleep 20; done
export THROTTLE=${THROTTLE:-1.5} SCORER_BACKEND=mlx NULLEDIT_RESULTS=../results PYTHONUNBUFFERED=1
L=../data/logs
echo "$(date -u +%H:%M:%S) START g12b_conf_mac" >> $L/queue_mac3.progress
nice -n 10 ../.venv/bin/python run_conflict.py --max-file-tokens 12000 --model ../data/models/gemma-4-12B-it-4bit --tag g12b_conf_mac --instances ../results/conf_ids.txt --frames R > $L/g12b_conf_mac.log 2>&1
echo "$(date -u +%H:%M:%S) END g12b_conf_mac ($?)" >> $L/queue_mac3.progress
