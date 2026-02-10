# Ricardo Seller Monitor

## Projektübersicht
Überwacht den Ricardo.ch-Verkäufer **Danash** (Lausanne) auf neue Inserate und sendet Push-Benachrichtigungen via Telegram. Läuft automatisch alle 10 Minuten via GitHub Actions - kein Server nötig.

## Tech Stack
- **Sprache:** Python 3.12
- **Scraping:** cloudscraper (Cloudflare-Bypass), BeautifulSoup4
- **Benachrichtigung:** Telegram Bot API
- **Hosting:** GitHub Actions (Cron-Job, gratis bei Public Repo)
- **State:** JSON-Datei (`known_listings.json`), wird per Git-Commit persistiert

## Dateien
```
monitor.py                      # Haupt-Skript: Scraping + Vergleich + Telegram
known_listings.json             # State: bekannte Inserate (wird automatisch aktualisiert)
requirements.txt                # Python Dependencies
.github/workflows/monitor.yml   # GitHub Actions Cron-Job (alle 10 Min)
```

## Wie es funktioniert
1. `cloudscraper` fetcht `https://www.ricardo.ch/de/shop/Danash/offers/` (umgeht Cloudflare)
2. BeautifulSoup extrahiert Artikel-Links (`/de/a/titel-XXXXXXXXXX/`)
3. Artikel-IDs werden mit `known_listings.json` verglichen
4. Neue Inserate werden via Telegram Bot API gemeldet (Titel, Preis, Sofortkauf, Link)
5. State wird aktualisiert und per Git-Commit gespeichert

## Parsing-Logik
Ricardo Artikel-Links enthalten Text-Elemente in dieser Reihenfolge:
- Optional: Badge ("Beliebt", "Neu")
- Titel
- Beschreibung (Grösse/Marke)
- Aktueller Preis (z.B. "8.00")
- Gebote (z.B. "(2 Gebote)")
- Sofortkauf-Preis (z.B. "15.00")
- "Sofort kaufen"

Artikel-ID wird aus der URL extrahiert: `-(\d{8,})` am Ende.

## GitHub Secrets
- `TELEGRAM_BOT_TOKEN` - Telegram Bot Token von @BotFather
- `TELEGRAM_CHAT_ID` - Empfänger Chat-ID

## Environment Variables
- `RICARDO_SELLER` - Verkäufername (Default: "Danash")
- `TELEGRAM_BOT_TOKEN` - Bot Token
- `TELEGRAM_CHAT_ID` - Chat ID

## Deployment
- GitHub Repo: firefly1302/ricardo-monitor (Public)
- GitHub Actions: Cron alle 10 Min (`*/10 * * * *`)
- Manueller Trigger via "Run workflow" möglich

## Wichtige Hinweise
- Ricardo blockiert normale HTTP-Requests (Cloudflare 403) → `cloudscraper` ist Pflicht
- `requests` wird nur für Telegram API verwendet (kein Cloudflare)
- Beim ersten Lauf werden alle aktuellen Inserate gespeichert (keine Benachrichtigung)
- Ab dem zweiten Lauf kommen nur neue Inserate als Notification
