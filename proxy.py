import asyncio
import re
import time
from urllib.parse import urlparse, urljoin, unquote

from fastapi import FastAPI, Response, HTTPException, Request
import httpx
from playwright.async_api import async_playwright
import uvicorn
import sys

app = FastAPI()

# Require target URL from command-line arguments without hardcoded fallbacks
if len(sys.argv) < 2:
  print("[-] Error: Missing target URL argument.")
  print("Usage: python proxy.py <target-url>")
  sys.exit(1)

TARGET_URL = sys.argv[1]

current_akamai_base = None
current_token_query = None
last_fetch_time = 0


async def refresh_stream_metadata():
  """Runs Playwright once to capture a fresh base URL and token."""
  global current_akamai_base, current_token_query, last_fetch_time
  print(f"[*] Fetching fresh stream token via Playwright for: {TARGET_URL}")
  
  async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await (await browser.new_context()).new_page()
    captured_url = None

    def intercept(request):
      nonlocal captured_url
      if not captured_url and "master.m3u8" in request.url:
        captured_url = request.url

    page.on("request", intercept)
    await page.goto(TARGET_URL, wait_until="networkidle")

    for _ in range(15):
      if captured_url:
        break
      await asyncio.sleep(1)

    await browser.close()

    if not captured_url:
      raise Exception("Failed to capture master.m3u8 from page.")

    parsed = urlparse(captured_url)
    current_akamai_base = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rsplit('/', 1)[0]}/"
    current_token_query = parsed.query
    last_fetch_time = time.time()
    print(f"[+] Successfully captured base: {current_akamai_base}")


@app.api_route("/{path:path}", methods=["GET", "HEAD"])
async def transparent_proxy(path: str, request: Request):
  global current_akamai_base, current_token_query

  if not current_akamai_base:
    try:
      await refresh_stream_metadata()
    except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))

  target_url = f"{current_akamai_base}{path}"
  if current_token_query:
    target_url += f"?{current_token_query}"

  if request.url.query:
    separator = "&" if "?" in target_url else "?"
    target_url += f"{separator}{request.url.query}"

  async with httpx.AsyncClient() as client:
    res = await client.get(target_url, headers={"User-Agent": "VLC"})
    
    if res.status_code == 403:
      print("[-] Received 403 Forbidden. Refreshing token...")
      await refresh_stream_metadata()
      target_url = f"{current_akamai_base}{path}?{current_token_query}"
      res = await client.get(target_url, headers={"User-Agent": "VLC"})

    content_type = res.headers.get("content-type", "video/mp2t")
    if path.endswith(".m3u8"):
      content_type = "application/vnd.apple.mpegurl"

    return Response(content=res.content, status_code=res.status_code, media_type=content_type)


if __name__ == "__main__":
  uvicorn.run("proxy:app", host="127.0.0.1", port=8000, reload=False)

