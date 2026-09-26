#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <event-url>"
    echo "Example: $0 https://my-server.com/event/8"
    exit 1
fi

./venv/bin/python find-stream.py "$1"

