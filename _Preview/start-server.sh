#!/bin/bash
# Start the preview server from project root to allow proper path resolution

cd "$(dirname "$0")/.."
echo "Starting server from: $(pwd)"
echo "Preview site available at: http://localhost:8080/_Preview/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m http.server 8080

