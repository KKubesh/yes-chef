#!/bin/bash
# Double-click to open a throwaway TEST copy of Yes, Chef at http://localhost:4748
# It starts from a brand-new board every time (so the walkthrough runs), and never touches your real data.json.
# It can run at the same time as your normal Yes, Chef. Close this window to stop it.
cd "$(dirname "$0")"
if ! command -v node >/dev/null 2>&1; then
  echo "Yes, Chef needs Node.js. Install it from https://nodejs.org (the LTS version), then double-click this file again."
  read -r -p "Press Return to close."
  exit 1
fi
rm -rf test-run && mkdir test-run   # wipe the last test so it starts fresh
echo "TEST copy: scratch data in the test-run folder, wiped each time you start it."
(sleep 1; open "http://localhost:4748") &
PORT=4748 FOCUS_DATA="$PWD/test-run/data.json" node server.js
