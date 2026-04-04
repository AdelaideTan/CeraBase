# tasks.py
from crewai import Task

def get_pottery_tasks(agent, art_data):
    # 提取基礎繼承數據
    oid = str(art_data.get('objectID', '0'))
    murl = art_data.get('met_url', 'No URL')
    iurl = art_data.get('image_url', 'No Image')
    dt = art_data.get('date', 'Unknown')
    dept = art_data.get('curatorial_department', 'Ceramics')
    
    # 這裡是關鍵：包含 API 硬數據與你剛剛新增的「官網爬蟲長文案」
    raw_info = str(art_data.get('description_raw', 'No detailed data available')).replace("{", "[").replace("}", "]")
    
    # --- 任務 1：深度專業分析與無損統整 ---
    report_task = Task(
        description=f"""
        你現在是一位【大都會博物館官方網站文案主編】兼【嚴謹的檔案研究員】。
        
        你的目標是將【原始數據區塊】精簡統整為「精煉、層次分明、零幻覺」的官方介紹（General Description）。
        --------------------------------------------------
        【原始數據區塊 (包含官網描述與技術碎片)】: 
        {raw_info}
        --------------------------------------------------
        
        執行指南（必須遵守）：
        1. **嚴格遵守字數限制**（禁止超出）：
           - 英文描述 (description_en)：100-150 個單詞。
           - 中文描述 (description_zh)：250-300 個字。
           若原始數據過長，請精選最重要的資訊進行統整。
        
        2. **零幻覺原則**：
           - 只統整原始數據中明確存在的資訊。
           - 禁止猜測或自行延伸編造任何細節。
           - 如果數據缺失，在文中用「[資訊缺失]」明確標記。
        
        3. **結構化敘述**：選擇最核心的信息，按「背景 → 物理特徵 → 文化/藝術意義 → 出處」順序組織。
        
        4. **專業語氣與雙語對齊**：
           - 中文：優雅易讀，適合博物館介紹文案。
           - 英文：專業學術風格，適合藝術評論。
           - 事實表述需保持一致。
        
        5. **數據繼承**：objectID: {oid}, met_url: {murl}, image_url: {iurl}, curatorial_department: {dept}
        
        6. **日期處理**：產出 `date_zh` (中文格式) 與 `date_en` (原始英文格式)。
        """,
        expected_output="A concise, word-count-compliant description (EN: 150-250 words, ZH: 300-500 characters) based 100% on raw facts with zero hallucination.",
        agent=agent
    )

    # --- 任務 2：生成精華大綱 (Summary EN & ZH) ---
    summary_task = Task(
        description=f"""
        基於前一個任務生成的詳細報告，請為作品「{art_data.get('title', 'Unknown Title')}」編寫兩句精華總結。
        
        要求：
        1. **英文版 (summary_en)**：
           - 精煉且吸睛：僅限「一句」英文，字數控制在 20 個單詞以內。
           - 突顯該作品最重要的歷史意義、藝術風格或文化亮點。
        
        2. **中文版 (summary_zh)**：
           - 精煉且吸睛：僅限「一句」繁體中文，字數控制在 30-40 個字以內。
           - 與英文版傳達相同的核心價值，但用台灣人易懂的語氣。
        
        3. **格式要求**：這兩句總結將分別放入 JSON 的 "summary_en" 和 "summary_zh" 欄位中。
        """,
        expected_output="Two single sentences (EN: max 20 words, ZH: max 40 characters) summarizing the essence of the artwork.",
        agent=agent,
        context=[report_task] # 確保根據 Task 1 的結果來精煉
    )

    # --- 任務 3：最終格式彙整 (JSON 封裝) ---
    # 我們將輸出規範移到最後一個 Task，確保 JSON 包含 summary_en
    final_output_task = Task(
        description=f"""
        將上述所有分析與總結封裝為最終的 JSON 格式。
        
        輸出規範（嚴格執行）：
        - 輸出必須為「純 JSON 物件」，嚴禁包含 ```json 等 Markdown 外殼。
        - **必須包含且僅包含以下欄位**：
          "title_zh", "title_en",
          "date_zh", "date_en",
          "culture_zh", "culture_en",
          "medium_zh", "medium_en",
          "description_zh", "description_en",
          "materials_zh", "materials_en",
          "summary_en", "summary_zh",  <-- 這兩個是剛生成的精華大綱（英文和中文）
          "objectID", "met_url", "image_url", "curatorial_department"
        """,
        expected_output="A polished JSON object containing all required fields including the new 'summary_en'.",
        agent=agent,
        context=[report_task, summary_task]
    )
    
    # 回傳所有任務，CrewAI 會按順序執行
    return [report_task, summary_task, final_output_task]