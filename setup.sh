#!/bin/bash

# 1. Create a local virtual environment named 'venv'
python3 -m venv venv

# 2. Install all required dependencies inside this private environment
./venv/bin/pip install fastapi uvicorn httpx playwright

# 3. Download the embedded Chromium browser binary
./venv/bin/playwright install chromium

