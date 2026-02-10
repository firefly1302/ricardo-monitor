"""One-time script to fetch Telegram Chat ID from bot updates. Run via GitHub Actions."""
import os
import requests

token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if not token:
    print("ERROR: TELEGRAM_BOT_TOKEN not set")
    exit(1)

resp = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=15)
data = resp.json()
print(f"Status: {resp.status_code}")
print(f"Response: {data}")

if data.get("result"):
    for update in data["result"]:
        msg = update.get("message", {})
        chat = msg.get("chat", {})
        if chat.get("id"):
            print(f"\n*** DEINE CHAT-ID: {chat['id']} ***")
            print(f"    Name: {chat.get('first_name', '')} {chat.get('last_name', '')}")
else:
    print("\nKeine Updates gefunden. Hast du /start an den Bot geschickt?")
