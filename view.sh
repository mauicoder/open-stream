#!/bin/bash

# Handle missing parameter
if [ -z "$1" ]; then
    echo "[-] Error: Missing event URL."
    echo "Usage: $0 <event-url>"
    echo "Example: $0 https://www.rsi.ch/sport/risultati/#/live/f1/1828020"
    exit 1
fi

EVENT_URL="$1"

# Check if the proxy is already running on port 8000; if not, start it with the event URL argument
if ! nc -z 127.0.0.1 8000 2>/dev/null; then
    echo "[*] Starting proxy server with event URL..."
    ./venv/bin/python proxy.py "$EVENT_URL" &
    # Wait a couple of seconds for uvicorn/playwright dependencies to initialize
    sleep 2
else
    echo "[*] Proxy is already running. (Note: If switching events, restart the proxy script)."
fi

# VLC points to a clean, dumb endpoint
PROXY_STREAM_URL="http://127.0.0.1:8000/master.m3u8"

echo "[*] Launching VLC with transparent proxy stream..."
open -na VLC --args \
    --http-user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
    "$PROXY_STREAM_URL"

