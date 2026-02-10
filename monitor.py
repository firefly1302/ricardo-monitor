#!/usr/bin/env python3
"""
Ricardo.ch Seller Monitor
Monitors a seller's shop page for new listings and sends Telegram notifications.
Designed to run as a GitHub Actions cron job.
"""

import json
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests

# --- Configuration ---
SELLER_NAME = os.environ.get("RICARDO_SELLER", "Danash")
SHOP_URL = f"https://www.ricardo.ch/de/shop/{SELLER_NAME}/offers/"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
STATE_FILE = Path(__file__).parent / "known_listings.json"


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"listings": {}}


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def send_telegram(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[TELEGRAM DISABLED] {message}")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            print("[TELEGRAM] Sent notification successfully")
        else:
            print(f"[TELEGRAM ERROR] Status {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")


def parse_listing_texts(texts: list[str]) -> dict:
    """Parse the text elements from a Ricardo listing link.

    Typical pattern:
      ['Beliebt', 'Title Here', 'Grösse M | Brand', '8.00', '(2 Gebote)', '15.00', 'Sofort kaufen']
    or without badges:
      ['Title Here', 'Grösse M | Brand', '8.00', '(0 Gebote)', '15.00', 'Sofort kaufen']
    """
    skip_words = {"Beliebt", "Neu", "Popular", "New", "Gesponsert", "Sponsored"}
    filtered = [t for t in texts if t not in skip_words]

    title = filtered[0] if filtered else "Neues Inserat"

    # Find prices: look for numbers like "8.00", "15.00"
    prices = []
    for t in filtered:
        if re.match(r"^\d+\.\d{2}$", t):
            prices.append(t)

    bid_price = prices[0] if len(prices) >= 1 else ""
    buy_now_price = prices[1] if len(prices) >= 2 else ""

    return {
        "title": title,
        "price": bid_price,
        "buy_now": buy_now_price,
    }


def fetch_listings() -> dict:
    """Fetch the seller's shop page and extract all listings."""
    print(f"[FETCH] Fetching {SHOP_URL}")
    resp = cffi_requests.get(SHOP_URL, impersonate="chrome", timeout=30)
    print(f"[FETCH] Status: {resp.status_code}, Length: {len(resp.text)} bytes")

    if resp.status_code != 200:
        print(f"[ERROR] Got status {resp.status_code}")
        sys.exit(1)

    soup = BeautifulSoup(resp.text, "html.parser")
    listings = {}

    # Find all article links: /de/a/article-title-XXXXXXXXXX/
    article_links = soup.find_all("a", href=re.compile(r"/de/a/[^/]+-\d{8,}/"))
    seen_ids = set()

    for link in article_links:
        href = link.get("href", "")
        match = re.search(r"-(\d{8,})/?$", href)
        if not match:
            continue
        article_id = match.group(1)
        if article_id in seen_ids:
            continue
        seen_ids.add(article_id)

        texts = [t.strip() for t in link.stripped_strings]
        info = parse_listing_texts(texts)
        info["url"] = f"https://www.ricardo.ch{href}"
        listings[article_id] = info

    print(f"[PARSE] Found {len(listings)} listings")
    return listings


def main():
    print(f"=== Ricardo Monitor for seller '{SELLER_NAME}' ===")

    state = load_state()
    known = state.get("listings", {})
    print(f"[STATE] {len(known)} previously known listings")

    current = fetch_listings()

    if not current:
        print("[WARN] No listings found - page structure may have changed.")
        return

    # Find new listings
    new_listings = {lid: info for lid, info in current.items() if lid not in known}

    if new_listings:
        print(f"[NEW] {len(new_listings)} new listing(s)!")
        for lid, info in new_listings.items():
            title = info["title"]
            url = info["url"]

            price_str = ""
            if info.get("price"):
                price_str += f"\nAktuell: CHF {info['price']}"
            if info.get("buy_now"):
                price_str += f"\nSofortkauf: CHF {info['buy_now']}"

            message = (
                f"<b>Neues Inserat von {SELLER_NAME}!</b>\n\n"
                f"{title}{price_str}\n\n"
                f'<a href="{url}">Auf Ricardo ansehen</a>'
            )
            send_telegram(message)
    else:
        print("[OK] No new listings.")

    removed = {lid for lid in known if lid not in current}
    if removed:
        print(f"[REMOVED] {len(removed)} listing(s) no longer available")

    state["listings"] = current
    save_state(state)
    print(f"[STATE] Saved {len(current)} listings")


if __name__ == "__main__":
    main()
