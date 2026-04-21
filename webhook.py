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
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    # 這裡印出部分 Body 內容協助 Debug
    print(f"📥 收到 Webhook 請求: {body[:100]}...")
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("❌ 無效的數位簽章，請檢查 LINE_CHANNEL_SECRET 是否正確！")
        abort(400)
    except Exception as e:
        print(f"🔥 Webhook Handler 發生錯誤: {e}")
        abort(500)
        
    return 'OK'

@handler.add(PostbackEvent)
def handle_postback(event):
    """
    處理 LINE Flex Message 的按鈕點擊事件 (切換語言)。
    """
    try:
        data = event.postback.data
        print(f"DEBUG: 收到 Postback Data: {data}")
        
        # 解析參數: action=switch_lang&lang=zh&object_id=123
        try:
            params = dict(item.split("=") for item in data.split("&"))
        except ValueError:
            print("❌ Postback Data 格式錯誤")
            return

        if params.get("action") == "switch_lang":
            target_lang = params.get("lang")
            obj_id = params.get("object_id")
            
            if not obj_id:
                print("❌ 缺少 object_id")
                return

            print(f"🔎 正在搜尋作品 ID: {obj_id} (目標語言: {target_lang})")
            
            # 從 Supabase 查詢資料
            res = supabase.table("ceramic_items").select("*").eq("object_id", obj_id).execute()
            
            if not res.data:
                print(f"❌ 找不到作品 ID: {obj_id}")
                return

            report_data = res.data[0]
            print(f"✅ 找到作品: {report_data.get('title_zh') or report_data.get('title_en')}")

            # 重新生成 Flex Message 內容
            flex_contents = build_flex_message_contents(report_data, lang=target_lang)
            
            # 使用 reply_token 回傳訊息 (一個 Token 只能用一次)
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text=f"🏺 CeraBase: {report_data.get('title_' + target_lang)}",
                    contents=flex_contents
                )
            )
            print(f"🚀 已成功切換至 {target_lang.upper()} 版")

    except Exception as e:
        print(f"🔥 Webhook 處理發生錯誤: {e}")

if __name__ == "__main__":
    # Render 環境通常會提供 PORT 環境變數
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
