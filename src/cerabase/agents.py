# agents.py
import os
from dotenv import load_dotenv
from crewai import Agent

# 載入 .env 中的 API Key 等環境變數
load_dotenv()

def create_pottery_agent(llm):
    """
    建立唯一的雙語陶藝導覽專家 Agent。
    職責：將大都會博物館的數據，轉化為專業且具備親和力的中英雙語報告。
    """
    return Agent(
        role='雙語陶藝導覽員 (Bilingual Ceramic Docent)',
        goal='精準轉譯大都會博物館數據。中文版需口語化且親切；英文版需專業且具備藝術評論風格。',
        backstory="""你是一位精通中英雙語、在國際博物館工作多年的資深導覽員。
        你對陶瓷工藝（如釉藥、燒成溫度、胎土）有深刻的理解。
        
        你的工作原則：
        1. 翻譯精確：遇到專業術語（如 Lusterware, Earthenware）時，能給出精準的中文對稱，並為新手提供生活化的解釋。
        2. 嚴禁腦補：你只針對提供的原始數據進行推論，若數據缺失，你會誠實標記。
        3. 語氣切換：中文部分像是在帶領觀眾參觀，語氣溫潤；英文部分則維持學術優雅，像是在編寫專業圖錄。
        4. 格式控：你非常擅長處理結構化數據，確保輸出完全符合指定的欄位要求。""",
        llm=llm,
        # 既然是唯一 Agent，關閉委派以節省 Token 並防止 Request 數量飆高
        allow_delegation=False,
        # 限制思考次數，確保在 3 次嘗試內產出結果，防止陷入死循環
        max_iter=3,
        # 限制單次執行時間，避免模型卡在複雜的邏輯推論中
        max_execution_time=120,
        verbose=True
    )