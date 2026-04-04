import os
import json
import re
from dotenv import load_dotenv
from crewai import Crew, LLM
from supabase import create_client, Client

# Add src directory to module search path for the new package layout
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cerabase.line_utils import send_line_daily_report

# 匯入自定義模組
from cerabase.fetch_art import get_random_pottery
from cerabase.agents import create_pottery_agent
from cerabase.tasks import get_pottery_tasks

# 載入 .env 檔案
load_dotenv()

# --- 1. 品質保證：確保抽到有圖的作品 ---
def get_high_quality_pottery():
    """迴圈抽取直到獲得有圖片的作品"""
    attempts = 0
    while attempts < 15:
        attempts += 1
        data = get_random_pottery()
        if not data:
            continue
            
        img = data.get('image_url')
        # 檢查條件：有網址且不是預設的 No Image
        if img and img != "No Image" and "http" in img:
            print(f"✨ 成功抽到高品質作品 (嘗試次數: {attempts})")
            return data
        
        print(f"⏭️  第 {attempts} 次抽取圖資不足，重新抽取中...")
    return None

# --- 2. 資料清洗函式 ---
def clean_data_string(text):
    if not isinstance(text, str):
        return str(text)
    # 處理特殊字元與換行
    text = text.replace('\u001f', '–') 
    text = "".join(char for char in text if char.isprintable() or char == '–')
    text = text.replace('"', "'")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# --- 3. 字數驗證與截斷函式 ---
def validate_and_trim_descriptions(data):
    """
    驗證並調整描述的字數至合規範圍。
    - description_en: 150-250 個單詞
    - description_zh: 300-500 個字
    
    如果超過上限，自動截斷；如果不足下限，保留原文並標記警告。
    """
    
    # 驗證英文描述
    if "description_en" in data:
        desc_en = data["description_en"]
        word_count = len(desc_en.split())
        
        if word_count > 250:
            # 超過上限，截斷到 250 字
            words = desc_en.split()
            data["description_en"] = " ".join(words[:250]) + "..."
            print(f"⚠️  英文描述超過上限 ({word_count} → 250 字)，已自動截斷")
        elif word_count < 150:
            print(f"⚠️  英文描述不足下限 ({word_count} < 150 字)，保留原文但請注意品質")
    
    # 驗證中文描述
    if "description_zh" in data:
        desc_zh = data["description_zh"]
        char_count = len(desc_zh)
        
        if char_count > 500:
            # 超過上限，截斷到 500 字
            data["description_zh"] = desc_zh[:500] + "..."
            print(f"⚠️  中文描述超過上限 ({char_count} → 500 字)，已自動截斷")
        elif char_count < 300:
            print(f"⚠️  中文描述不足下限 ({char_count} < 300 字)，保留原文但請注意品質")
    
    return data

def main():
    # --- A. 初始化 Supabase 與 LLM ---
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ 錯誤：找不到 SUPABASE_URL 或 SUPABASE_KEY，請檢查 .env 檔案。")
        return

    supabase: Client = create_client(url, key)

    cerebras_llm = LLM(
        model="cerebras/qwen-3-235b-a22b-instruct-2507", 
        api_key=os.getenv("CEREBRAS_API_KEY"),
        base_url="https://api.cerebras.ai/v1",
        temperature=0.2,
        max_tokens=3000
    )

    # --- B. 智慧抓取邏輯：品質檢查 + 重複檢查 ---
    print("\n🎨 正在搜尋尚未收藏的高品質陶瓷作品...")
    
    final_art_data = None
    while True:
        # 1. 先找有圖的作品
        raw_art = get_high_quality_pottery()
        if not raw_art:
            print("❌ 嘗試多次仍無法獲取高品質數據，程式停止。")
            return

        # 2. 立即查重 (Pre-check)
        obj_id = str(raw_art.get('objectID'))
        print(f"🔎 正在檢查資料庫是否已收藏 ID: {obj_id} ...")
        
        try:
            # 這裡使用的是你在 Supabase 建立的欄位名稱 "object_id"
            existing = supabase.table("ceramic_items").select("object_id").eq("object_id", obj_id).execute()
            
            if not existing.data:
                print(f"🆕 發現全新作品！準備開始 AI 分析任務...")
                final_art_data = raw_art
                break
            else:
                print(f"♻️  作品 (ID: {obj_id}) 已在收藏中，自動跳過並重新抽取...")
        except Exception as db_err:
            print(f"❌ 資料庫查詢出錯: {db_err}")
            print("💡 請確認 Supabase 中的 Table 名稱為 'ceramic_items' 且欄位名稱為 'object_id'")
            return

    # --- C. 執行 CrewAI 任務 (確認是新作品才執行) ---
    cleaned_art_data = {k: (clean_data_string(v) if isinstance(v, str) else v) for k, v in final_art_data.items()}

    docent_agent = create_pottery_agent(cerebras_llm)
    pottery_tasks = get_pottery_tasks(docent_agent, cleaned_art_data)

    pottery_crew = Crew(
        agents=[docent_agent],
        tasks=pottery_tasks,
        verbose=True
    )

    print(f"\n🚀 正在產出雙語報告：{cleaned_art_data.get('title')}...")
    result = pottery_crew.kickoff()

    # --- D. 報告顯示邏輯 ---
    def print_daily_ceramic_report(data):
        img_url = data.get('image_url')
        img_markdown = f"![作品]({img_url})" if img_url and img_url != "No Image" else "*(無預覽圖)*"
        
        for lang_name, suffix in [("中文版", "zh"), ("English", "en")]:
            display_date = data.get(f'date_{suffix}', data.get('date', 'N/A'))
            print("\n" + "━"*50)
            print(f"## 🏺 Daily Ceramic ({lang_name}) ##\n")
            print(f"{img_markdown}\n")
            print(f"- **Title**: {data.get(f'title_{suffix}', 'N/A')}")
            print(f"- **Date**: {display_date}")
            print(f"- **Culture**: {data.get(f'culture_{suffix}', 'N/A')}")
            print(f"- **Medium**: {data.get(f'medium_{suffix}', 'N/A')}")

            if suffix == "en" and data.get("summary_en"):
                print(f"\n### ✨ AI One-liner Summary ###\n{data.get('summary_en')}")

            print(f"\n### 📖 Description ###\n{data.get(f'description_{suffix}', 'N/A')}")
            print(f"\n### Key Materials ###\n{data.get(f'materials_{suffix}', 'N/A')}")
            print(f"\n🔗 [點此查看大都會博物館原始頁面]({data.get('met_url', '#')})")
            print("━"*50)

    # --- E. 解析 JSON 並正式入庫 ---
    try:
        raw_output = result.raw
        # 清理 AI 輸出的 Markdown 語法
        clean_json_str = raw_output.strip().replace("```json", "").replace("```", "").strip()
        report_data = json.loads(clean_json_str)
        
        if report_data:
            # 0.5. 驗證與調整描述字數
            report_data = validate_and_trim_descriptions(report_data)
            
            # 1. 顯示報告
            print_daily_ceramic_report(report_data)
            
            # 2. 準備入庫
            print("\n☁️  正在將資料同步至 Supabase...")
            db_data = {
                "object_id": str(report_data.get("objectID")),
                "title_zh": report_data.get("title_zh"),
                "title_en": report_data.get("title_en"),
                "date_zh": report_data.get("date_zh"),
                "date_en": report_data.get("date_en"),
                "culture_zh": report_data.get("culture_zh"),
                "culture_en": report_data.get("culture_en"),
                "medium_zh": report_data.get("medium_zh"),
                "medium_en": report_data.get("medium_en"),
                "materials_zh": report_data.get("materials_zh"),
                "materials_en": report_data.get("materials_en"),
                "description_zh": report_data.get("description_zh"),
                "description_en": report_data.get("description_en"),
                "summary_zh": report_data.get("summary_zh"),
                "summary_en": report_data.get("summary_en"),
                "image_url": report_data.get("image_url"),
                "met_url": report_data.get("met_url"),
            }

            # 3. 執行 Insert
            supabase.table("ceramic_items").insert(db_data).execute()
            print(f"\n✅ 成功收藏新作品：{db_data['title_zh']}！")

            send_line_daily_report(report_data)
                
        else:
            print("❌ AI 輸出內容解析後為空。")
            
    except Exception as e:
        print(f"❌ 解析或存檔失敗: {e}")
        print(f"原始輸出內容：\n{result.raw}")

if __name__ == "__main__":
    main()

# Linebot
from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage

def send_line_flex_message(report_data):
    # 初始化 Line API
    line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
    user_id = os.getenv("LINE_USER_ID")
    
    # 這裡我們用最簡單的 Text 版測試，成功後我們再換成超漂亮的 Flex 版
    message_text = f"🏺 【今日陶瓷推薦】\n\n" \
                   f"名稱：{report_data.get('title_zh')}\n" \
                   f"年代：{report_data.get('date_zh')}\n" \
                   f"產地：{report_data.get('culture_zh')}\n\n" \
                   f"✨ AI 簡評：\n{report_data.get('description_zh')[:100]}..."

    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=message_text))
        print("📲 Line 訊息發送成功！")
    except Exception as e:
        print(f"❌ Line 發送失敗: {e}")