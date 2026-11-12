#!/bin/bash
# Sequential job runner for the DGX: pops the first line of todo.txt and runs it, until the file is empty.
# Lines can be appended / reordered while it runs.  Usage: nohup src/runner.sh &
cd "$(dirname "$0")"
source ../.venv/bin/activate
export SCORER_BACKEND=torch PYTHONUNBUFFERED=1
L=../data/logs
mkdir -p $L
TODO=../${TODO:-todo.txt}
PROG=$L/${PROG:-runner.progress}
while true; do
  [ -f ../STOP ] && { echo "$(date -u +%F\ %T) STOP file found" >> $PROG; break; }
  line=$(head -n 1 $TODO 2>/dev/null)
  if [ -z "$line" ]; then sleep 30; continue; fi
  sed -i '1d' $TODO
  name=$(echo "$line" | cut -d'|' -f1 | xargs)
  cmd=$(echo "$line" | cut -d'|' -f2-)
  echo "$(date -u +%F\ %T) START $name" >> $PROG
  bash -c "$cmd" > $L/$name.log 2>&1
  rc=$?
  echo "$(date -u +%F\ %T) END $name (exit $rc)" >> $PROG
  if [ $rc -ne 0 ]; then echo "$line" >> ../failed.txt; fi
done
