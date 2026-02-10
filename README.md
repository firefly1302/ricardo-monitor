# Ricardo Seller Monitor

Monitors the Ricardo.ch seller **Danash** for new listings and sends push notifications via Telegram.

Runs automatically every 10 minutes via GitHub Actions - no server or laptop needed.

## Setup (10 Minuten)

### 1. Telegram Bot erstellen

1. Oeffne Telegram und suche nach **@BotFather**
2. Sende `/newbot`
3. Waehle einen Namen (z.B. "Ricardo Monitor")
4. Waehle einen Username (z.B. "danash_monitor_bot")
5. Du bekommst einen **Bot Token** - kopiere ihn (sieht so aus: `7123456789:AAF...`)
6. Oeffne deinen neuen Bot in Telegram und sende `/start`
7. Um deine **Chat ID** zu finden:
   - Oeffne `https://api.telegram.org/bot<DEIN_TOKEN>/getUpdates` im Browser
   - Suche nach `"chat":{"id":123456789}` - die Zahl ist deine Chat ID

### 2. GitHub Repository erstellen

1. Gehe zu https://github.com/new
2. Erstelle ein **Public** Repository (z.B. "ricardo-monitor")
   - Public = unlimitierte GitHub Actions Minuten (gratis!)
3. Pushe den Code:

```bash
cd ~/ricardo-monitor
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/DEIN_USERNAME/ricardo-monitor.git
git push -u origin main
```

### 3. Secrets konfigurieren

1. Gehe zu deinem Repository auf GitHub
2. Settings > Secrets and variables > Actions
3. Fuege diese Secrets hinzu:
   - `TELEGRAM_BOT_TOKEN` = Dein Bot Token von Schritt 1
   - `TELEGRAM_CHAT_ID` = Deine Chat ID von Schritt 1

### 4. Testen

1. Gehe zu Actions > "Ricardo Seller Monitor"
2. Klicke "Run workflow" > "Run workflow"
3. Warte ~30 Sekunden und pruefe das Log

Beim ersten Lauf wird das Skript alle aktuellen Inserate speichern (ohne Benachrichtigung).
Ab dem zweiten Lauf bekommst du Telegram-Nachrichten fuer neue Inserate!

## Anpassen

### Anderen Seller ueberwachen

Aendere in `.github/workflows/monitor.yml`:
```yaml
RICARDO_SELLER: AndereSeller
```

### Intervall aendern

In `.github/workflows/monitor.yml` den Cron-Ausdruck aendern:
- `*/5 * * * *` = alle 5 Minuten
- `*/10 * * * *` = alle 10 Minuten (Standard)
- `*/30 * * * *` = alle 30 Minuten

### Nur zu bestimmten Zeiten

```yaml
# Nur 7-23 Uhr (Schweizer Zeit = UTC+1)
- cron: '*/10 6-22 * * *'
```

## Troubleshooting

- **Keine Listings gefunden**: Die Datei `debug_page.html` wird gespeichert. Pruefe ob Ricardo die Seitenstruktur geaendert hat.
- **403 Fehler**: Ricardo blockiert evtl. GitHub Actions IPs. Versuche den User-Agent in `monitor.py` zu aendern.
- **Telegram kommt nicht**: Pruefe ob du `/start` an deinen Bot geschickt hast und ob die Secrets richtig sind.
