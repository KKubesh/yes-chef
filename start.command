#!/bin/bash
# Double-click this file to start Yes, Chef, then keep this window open while you use it.
cd "$(dirname "$0")"
if ! command -v node >/dev/null 2>&1; then
  echo "Yes, Chef needs Node.js. Install it from https://nodejs.org (the LTS version), then double-click this file again."
  read -r -p "Press Return to close."
  exit 1
fi
(sleep 1; open "http://localhost:4747") &
node server.js
