import os
from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from google.cloud import secretmanager


# 你可以把這個 Flask 應用包在雲函式的 handler 裡
app = Flask(__name__)

# 環境變數：可以在 GCP Cloud Functions 的 "環境變數" 頁面設定
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_CHANNEL_SECRET")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/")
def hello_world():
    """Example Hello World route."""
    return f"Hello!"


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


def get_secret(secret_name, project_id=None):
    if not project_id:
        project_id = os.environ["PROJECT_ID"]

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=name)
    my_secret_value = response.payload.data.decode("UTF-8")
    return my_secret_value



# ****雲端函式的進入點 (2nd gen)****
def main(request):
    # 在 2nd gen Cloud Functions，可以將 Flask app 作為 WSGI 來處理
    return app(request)

# ---- Cloud Run 本地開發用 ----
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)