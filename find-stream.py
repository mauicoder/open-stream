import sys
import asyncio
import subprocess
import argparse
from playwright.async_api import async_playwright

parser = argparse.ArgumentParser(description="Automated RSI Stream Grabber for VLC")
parser.add_argument("url", help="The RSI live event URL")
args = parser.parse_args()

RSI_URL = args.url

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        captured_url = None

        def intercept_request(request):
            nonlocal captured_url
            if not captured_url and "master.m3u8" in request.url:
                captured_url = request.url
                print(f"\n[+] Successfully caught authenticated master stream URL!")

        page.on("request", intercept_request)

        print(f"Opening browser for: {RSI_URL}")
        await page.goto(RSI_URL)

        print("Waiting for the video player to initialize...")
        for _ in range(25):
            if captured_url:
                break
            await asyncio.sleep(1)

        await browser.close()

        if captured_url:
            print("Launching VLC with master stream (full resolution)...")
            subprocess.Popen([
                'open', '-na', 'VLC', '--args',
                '--http-user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                captured_url
            ])
        else:
            print("[-] Error: Stream URL not captured. Make sure the event is currently live.")

if __name__ == "__main__":
    asyncio.run(main())

