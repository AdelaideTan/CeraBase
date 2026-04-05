# webhook.py
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import PostbackEvent, FlexSendMessage
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

app = Flask(__name__)

# LINE 設定 (請確保 .env 裡有這些)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET')) # <--- 需要補這組 Secret

# Supabase 設定
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# 引入你寫好的 Flex Message 生成工具
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from cerabase.line_utils import build_flex_message_contents

@app.route("/", methods=['GET'])
def health():
    return "CeraBase Webhook is Running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    # 解析按鈕中的數據：action=switch_lang&lang=zh&object_id=123
    params = dict(item.split("=") for item in data.split("&"))
    
    if params.get("action") == "switch_lang":
        target_lang = params.get("lang")
        obj_id = params.get("object_id")
        
        # 1. 向資料庫查詢該作品
        res = supabase.table("ceramic_items").select("*").eq("object_id", obj_id).execute()
        
        if res.data:
            report_data = res.data[0]
            # 2. 生成新語言的卡片
            flex_contents = build_flex_message_contents(report_data, lang=target_lang)
            # 3. 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text=f"🏺 CeraBase: {report_data.get('title_' + target_lang)}",
                    contents=flex_contents
                )
            )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
