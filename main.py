import os
import json
import re
from dotenv import load_dotenv
from crewai import Crew, LLM
from supabase import Client

# Add src directory to module search path for the new package layout
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cerabase.line_utils import send_line_daily_report
from cerabase.utils import get_supabase_client, clean_data_string, validate_and_trim_descriptions

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

def main():
    # --- A. 初始化 Supabase 與 LLM ---
    try:
        supabase = get_supabase_client()
    except Exception as e:
        print(e)
        return

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