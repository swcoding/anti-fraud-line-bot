from flask import Flask, request, abort
import os
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN_LONGLIVED", "YOUR_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_CHANNEL_SECRET")

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/")
def hello():
    return "Hello!"


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text
    
    # 簡單的詐騙判斷邏輯
    scam_keywords = ["匯款", "中獎", "點此連結", "投資"]
    is_scam = any(keyword in user_text for keyword in scam_keywords)

    if is_scam:
        reply = f"{user_text} ⚠️ 這則訊息可能是詐騙，請提高警覺！"

        message = TextMessage(text=reply)
        body = ReplyMessageRequest(reply_token=event.reply_token, messages=[message])
        messaging_api.reply_message(body)


# ****雲端函式的進入點 (2nd gen)****
def main(request):
    # 在 2nd gen Cloud Functions，可以將 Flask app 作為 WSGI 來處理
    return app(request)

# ---- Cloud Run 本地開發用 ----
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)