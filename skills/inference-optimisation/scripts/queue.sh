#!/usr/bin/env bash
# Serialized GPU queue: runs bench.py on each config in order, one GPU job at a time across all callers.
#   queue.sh ctl-a cand ctl-b            # interleave controls around each candidate
#   BENCH_FLAGS="--long 131072" queue.sh cand
# Detach long queues so they survive agent/terminal restarts:
#   setsid nohup bash queue.sh ctl-a cand ctl-b > queue.log 2>&1 < /dev/null & disown
# Run from your experiment directory (the one holding configs/ and ledger.jsonl).
LOCK=${QUEUE_LOCK:-/tmp/inference-hillclimb.lock}
exec 9>"$LOCK"; flock 9
for n in "$@"; do
  python3 "${BENCH:-$(dirname "$0")/bench.py}" run "configs/$n.json" ${BENCH_FLAGS:-} > "runs-$n.log" 2>&1
  echo "done $n: $(tail -c 300 "runs-$n.log" | tr '\n' ' ' | cut -c1-200)"
done
echo QUEUE_DONE "$@"
