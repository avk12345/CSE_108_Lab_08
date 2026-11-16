#!/usr/bin/env bash
set -eu

cd "$(dirname "$0")/.."
log_dir=/tmp/cse108
mkdir -p "$log_dir"

# Locks prevent duplicate servers if this script runs again in the same container.
nohup flock -n "$log_dir/flask.lock" \
    python -m flask --app app run --debug --host=0.0.0.0 --port=5000 \
    >> "$log_dir/flask.log" 2>&1 < /dev/null &

nohup flock -n "$log_dir/vite.lock" \
    npm --prefix frontend run dev -- --host 0.0.0.0 --port 5173 --strictPort \
    >> "$log_dir/vite.log" 2>&1 < /dev/null &

printf 'Starting Flask and Vite. Logs: %s/flask.log and %s/vite.log\n' "$log_dir" "$log_dir"
