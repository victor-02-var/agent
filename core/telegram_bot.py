import os
import requests
from dotenv import load_dotenv

load_dotenv()

class SentinelTelegram:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CEO_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_executive_alert(self, repo_name, health_score, affliction):
        """Sends a high-level strategic summary to the CEO"""
        emoji = "🔴" if health_score < 40 else "🟡" if health_score < 75 else "🟢"
        
        message = (
            f"<b>🛡️ Sentinel Executive Brief: {repo_name}</b>\n\n"
            f"<b>Current Health:</b> {emoji} {health_score}/100\n"
            f"<b>Primary Affliction:</b> {affliction.get('issue', 'N/A')}\n"
            f"<b>Annual ROI Risk:</b> {affliction.get('revenue_impact', 'N/A')}\n\n"
            f"<i>👉 View full encrypted audit on the dashboard.</i>"
        )
        
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            requests.post(self.base_url, json=payload)
        except Exception as e:
            print(f"Telegram failed: {e}")