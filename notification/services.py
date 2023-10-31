import os

import requests
from dotenv import load_dotenv

load_dotenv()


def send_notification(message):
    url = (
        f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}"
        f"/sendMessage?chat_id={os.getenv('TELEGRAM_CHAT_ID')}&text={message}"
    )

    requests.get(url)
