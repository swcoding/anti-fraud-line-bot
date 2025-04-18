from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("princeton-nlp/sup-simcse-bert-base-uncased")

# 詐騙訊息範例
fraud_messages = [
    "👉【限量福利】政府補助每人8000元，點擊申請👉 http://gov-cash-support.tw",
    "📣【投資內線群】昨天漲停！今天再賺一支！加入內部VIP群： http://line.me/R/ti/g/abcdef123",
    "【抽獎通知】你在我們的活動中獲得iPhone 15！點擊確認領取資格 👉 http://apple-lucky.com",
    "🔥 台積電前員工帶隊操作股票，每天穩賺3%！免費入群看操作 👉 http://bit.ly/TSMC-free",
    "【衛福部通知】健保卡補助即將截止，請立即申請：👉 http://nhibonus.gov.tw",
    "🎁【週年活動】全家便利商店感謝回饋，每人可領$500！👉 http://familymart-gift.win",
    "🚨LINE帳號即將被停用！請立即點擊以下連結驗證： http://line-verify-safe.net",
    "📈【加密貨幣內線群】BTC明天有大行情！立即加入掌握先機👉 http://crypto-vip.group",
    "【快訊】您的包裹因地址異常未能投遞，請點此重新填寫：👉 http://ezparcel-check.tw",
    "🎉LINE 週年慶大放送！現在加入就送200點數！👉 http://linepoints-free.com"
]

# 建立詐騙訊息的 embedding 資料庫
fraud_embeddings = model.encode(fraud_messages, convert_to_tensor=True)

# 判斷新訊息是否為詐騙
def is_fraudulent(message: str, threshold: float = 0.9) -> bool:
    new_embedding = model.encode(message, convert_to_tensor=True)
    cosine_scores = util.cos_sim(new_embedding, fraud_embeddings)
    max_score = cosine_scores.max().item()
    print(f"最高相似度分數: {max_score:.4f}")
    return max_score > threshold


if __name__ == "__main__":
    # 範例測試
    new_message = """開會進這個連結：https://tel.meet/tgm-qgua-svj?pin=4239321767044"""

    print(is_fraudulent(new_message))