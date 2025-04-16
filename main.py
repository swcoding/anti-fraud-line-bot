import os
from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 你可以把這個 Flask 應用包在雲函式的 handler 裡
app = Flask(__name__)

# 環境變數：可以在 GCP Cloud Functions 的 "環境變數" 頁面設定
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_CHANNEL_SECRET")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 這裡和一般 Flask 專案做法類似，LINE Bot 的 Webhook endpoint 是 /callback
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    # 簡單的關鍵字檢測示範
    suspicious_keywords = ["詐騙", "投資", "ATM", "中獎"]
    user_text = event.message.text

    for keyword in suspicious_keywords:
        if keyword in user_text:
            # 偵測到可疑訊息
            reply_msg = f"「{user_text}」可能是詐騙訊息，請注意！"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_msg)
            )
            break


# ****雲端函式的進入點 (2nd gen)****
def main(request):
    # 在 2nd gen Cloud Functions，可以將 Flask app 作為 WSGI 來處理
    return app(request)

# 如果是 1st gen Cloud Functions，需要在此定義一個和 function 名稱相同的函式
# def linebot_demo(request):
#     return app(request)
