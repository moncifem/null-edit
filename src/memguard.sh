#!/bin/bash
# Kill our own job (never anything else) when available memory drops under 8 GB, so the machine never stalls.
while true; do
  a=$(awk "/MemAvailable/ {print int(\$2/1048576)}" /proc/meminfo)
  if [ "$a" -lt 8 ]; then
    echo "$(date -u "+%F %T") available ${a} GB -> killing job" >> $(dirname "$0")/../data/logs/memguard.log
    pkill -9 -u "$USER" -f "python (run_conflict|run_generative|run_edit|run_noprefill|diag_long)"
    sleep 20
  fi
  sleep 1
done
