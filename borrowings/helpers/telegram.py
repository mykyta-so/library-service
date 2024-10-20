import os

import requests
from dotenv import load_dotenv

load_dotenv()


def send_message(message):
    url = f"https://api.telegram.org/bot{os.getenv("TELEGRAM_BOT_TOKEN")}/sendMessage"
    payload = {"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": message}

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        raise Exception(f"Error sending message: {response.text}")