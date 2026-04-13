import requests
from config import TELEGRAM_TOKEN, CHAT_ID


def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram credentials not set.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        response = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": message
            },
            timeout=10
        )

        if response.status_code != 200:
            print(f"Telegram error: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Telegram request failed: {e}")
