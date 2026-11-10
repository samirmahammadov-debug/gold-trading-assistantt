
import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            secret = os.environ.get("WEBHOOK_SECRET")
            supplied = self.headers.get("X-Webhook-Secret")

            if not secret or supplied != secret:
                self.send_error(401, "Unauthorized")
                return

            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))

            token = os.environ["TELEGRAM_BOT_TOKEN"]
            chat_id = os.environ["TELEGRAM_CHAT_ID"]

            symbol = data.get("symbol", "XAUUSD")
            direction = data.get("direction", "WAIT")
            entry = data.get("entry", "-")
            sl = data.get("sl", "-")
            tp1 = data.get("tp1", "-")
            tp2 = data.get("tp2", "-")
            timeframe = data.get("timeframe", "M15")

            if direction not in ("BUY", "SELL"):
                self.send_error(400, "Invalid signal")
                return

            message = (
                f"🥇 GOLD TRADING SIGNAL\n\n"
                f"Pair: {symbol}\n"
                f"Direction: {direction}\n"
                f"Timeframe: {timeframe}\n"
                f"Entry: {entry}\n"
                f"Stop Loss: {sl}\n"
                f"Take Profit 1: {tp1}\n"
                f"Take Profit 2: {tp2}\n\n"
                f"Risk: Moderate\n"
                f"Confirm the setup before trading."
            )

            payload = json.dumps({
                "chat_id": chat_id,
                "text": message
            }).encode()

            req = urllib.request.Request(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data=payload,
                headers={"Content-Type": "application/json"}
            )

            urllib.request.urlopen(req, timeout=10).read()

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Signal sent")

        except Exception:
            self.send_error(500, "Internal server error")
