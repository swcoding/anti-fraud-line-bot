import hmac
import hashlib
import base64
import requests
import json
import os

# 1️⃣ 替換成你的 channel secret
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_CHANNEL_SECRET")

if __name__ == "__main__":

    # 2️⃣ 這是模擬 webhook 的 JSON body
    body = {
        "events": [
            {
                "type": "message",
                "replyToken": "00000000000000000000000000000000",
                "source": {
                    "userId": "U0123456789abcdef",
                    "type": "user"
                },
                "timestamp": 1600000000000,
                "message": {
                    "type": "text",
                    "id": "100001",
                    "text": "中獎了快匯款"
                }
            }
        ]
    }
    body_str = json.dumps(body)

    # 3️⃣ 用 HMAC-SHA256 + base64 產生 X-Line-Signature
    hash = hmac.new(CHANNEL_SECRET.encode('utf-8'), body_str.encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(hash).decode('utf-8')

    # 4️⃣ 傳送 POST 請求到你的 Cloud Function
    url = "https://anti-fraud-line-bot-618206330066.asia-east1.run.app/callback"
    headers = {
        "Content-Type": "application/json",
        "X-Line-Signature": signature
    }
    res = requests.post(url, data=body_str, headers=headers)

    print("Status Code:", res.status_code)
    print("Response:", res.text)
