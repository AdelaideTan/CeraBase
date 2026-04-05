"""
UI Helpers for Streamlit Pages
Provides language dictionaries, common UI components, and initialization logic.
"""

import streamlit as st  # type: ignore
from datetime import datetime
from supabase import create_client, Client  # type: ignore
import os
from dotenv import load_dotenv  # type: ignore


# ============================================================================
# LANGUAGE CONFIGURATION
# ============================================================================

LANG_DICT = {
    "en": {
        # Main pages
        "page_title_home": "🏛️ Daily Ceramic",
        "page_title_history": "📜 Past Collections",
        
        # Buttons & Labels
        "btn_label": "切換為中文",
        "next_lang": "zh",
        
        # Home page
        "page_title_welcome": "Welcome to CeraBase",
        "cerabase_description": "Welcome to **CeraBase**, your daily guide to exceptional ceramic artworks from The Metropolitan Museum of Art!",
        "line_bot_label": "LINE Bot",
        "line_bot_desc": "Receive daily push notifications with artwork previews and quick links",
        "web_app_label": "Web App",
        "web_app_desc": "Explore artworks in detail with full descriptions in English and Traditional Chinese",
        "features_title": "Features",
        "feature_daily": "Daily Artwork Selection",
        "feature_daily_desc": "AI-curated ceramic pieces from The Met's extensive collection",
        "feature_bilingual": "Bilingual Support",
        "feature_bilingual_desc": "Full English and Traditional Chinese descriptions",
        "feature_history": "History Tracking",
        "feature_history_desc": "Browse and revisit previously shared artworks",
        "feature_links": "Direct Links",
        "feature_links_desc": "Quick access to The Met's official pages for each artwork",
        "feature_ai": "AI Analysis",
        "feature_ai_desc": "Professional descriptions powered by advanced language models",
        "getting_started": "Getting Started",
        "step1": "View Today's Artwork",
        "step1_desc": "Navigate to the home page from the sidebar",
        "step2": "Browse History",
        "step2_desc": "Check out Past Collections to explore previous selections",
        "step3": "Share & Learn",
        "step3_desc": "Share interesting pieces with friends through LINE or the web app",
        "architecture": "Architecture",
        "backend_pipeline": "Backend (Data Pipeline)",
        "backend_desc": "Fetches daily ceramics from The Met API, generates descriptions, and pushes to LINE",
        "database": "Supabase: Cloud database for storing artwork metadata and history",
        "ai_system": "CrewAI + Cerebras LLM: AI-powered bilingual content generation",
        "frontend_ui": "Frontend (User Interface)",
        "frontend_desc": "Streamlit Multi-page App with language switching",
        "line_messages": "LINE Bot Flex Messages for rich mobile notifications",
        "responsive": "Responsive design optimized for web and mobile",
        "tech_stack": "Tech Stack",
        "backend_tech": "Python, CrewAI, Cerebras API",
        "frontend_tech": "Streamlit",
        "database_tech": "Supabase (PostgreSQL)",
        "messaging_tech": "LINE Bot API",
        "data_source": "The Metropolitan Museum of Art Open Access API",
        "support": "Support",
        "support_text": "For questions or issues, please check the project repository or reach out through LINE.",
        "last_updated": "Last Updated",
        "version_info": "Version",
        "language_tip": "Tip: Use the language button in the sidebar to switch between English and Traditional Chinese",
        "current_language": "Current Language",
        "language_en": "🇬🇧 English",
        "language_zh": "🇹🇼 中文",
        "no_data": "No data found in database.",
        
        # Sidebar
        "journey_label": "Aesthetic Journey",
        "history_title": "📜 Quick Access",
        "days_format": "Day {count}",
        
        # Artwork display
        "date": "Date",
        "culture": "Culture",
        "medium": "Medium",
        "official_link": "View on The Met",
        "expert_analysis": "Description",
        "summary": "Summary",
        
        # History page
        "history_grid_title": "Browse Past Collections",
        "detail_page_title": "Artwork Detail",
    },
    "zh": {
        # Main pages
        "page_title_home": "🏛️ 今日作品推薦",
        "page_title_history": "📜 過往收藏",
        
        # Buttons & Labels
        "btn_label": "Switch to English",
        "next_lang": "en",
        
        # Home page
        "page_title_welcome": "歡迎來到 CeraBase",
        "cerabase_description": "歡迎來到 **CeraBase**，您的每日陶瓷藝術推薦指南，來自大都會藝術博物館的精選作品！",
        "line_bot_label": "LINE Bot",
        "line_bot_desc": "每日推播藝術品預覽與快速連結",
        "web_app_label": "網頁應用",
        "web_app_desc": "以英文與繁體中文詳盡描述作品",
        "features_title": "功能",
        "feature_daily": "每日作品精選",
        "feature_daily_desc": "從大都會廣泛收藏中挑選 AI 精選陶瓷作品",
        "feature_bilingual": "雙語支持",
        "feature_bilingual_desc": "提供完整英文與繁體中文描述",
        "feature_history": "歷史追蹤",
        "feature_history_desc": "瀏覽並重溫先前分享的作品",
        "feature_links": "直接連結",
        "feature_links_desc": "快速前往 The Met 官方作品頁面",
        "feature_ai": "AI分析",
        "feature_ai_desc": "由先進語言模型生成專業描述",
        "getting_started": "開始使用",
        "step1": "查看今日作品",
        "step1_desc": "從側邊欄進入首頁",
        "step2": "瀏覽歷史",
        "step2_desc": "查看「過往收藏」以探索先前選品",
        "step3": "分享與學習",
        "step3_desc": "透過 LINE 或網頁與朋友分享有趣作品",
        "architecture": "架構",
        "backend_pipeline": "後端（數據管線）",
        "backend_desc": "從 The Met API 擷取每日陶瓷、生成描述並推播至 LINE",
        "database": "Supabase：雲端資料庫儲存作品元資料與歷史紀錄",
        "ai_system": "CrewAI + Cerebras LLM：AI 雙語內容生成",
        "frontend_ui": "前端（使用者介面）",
        "frontend_desc": "具有語言切換功能的 Streamlit 多頁應用",
        "line_messages": "LINE Bot Flex 訊息提供豐富手機通知",
        "responsive": "響應式設計，優化網頁與行動裝置體驗",
        "tech_stack": "技術棧",
        "backend_tech": "Python、CrewAI、Cerebras API",
        "frontend_tech": "Streamlit",
        "database_tech": "Supabase (PostgreSQL)",
        "messaging_tech": "LINE Bot API",
        "data_source": "大都會藝術博物館開放資源 API",
        "support": "支援",
        "support_text": "如有問題，請查看專案倉庫或透過 LINE 聯絡我們。",
        "last_updated": "最後更新",
        "version_info": "版本",
        "language_tip": "提示：使用側邊欄語言按鈕在英文與繁體中文之間切換",
        "current_language": "目前語言",
        "language_en": "🇬🇧 English",
        "language_zh": "🇹🇼 中文",
        "no_data": "目前資料庫中尚無資料。",
        
        # Sidebar
        "journey_label": "美術鑑賞之旅",
        "history_title": "📜 快速訪問",
        "days_format": "第 {count} 天",
        
        # Artwork display
        "date": "日期",
        "culture": "文化",
        "medium": "媒材",
        "official_link": "在 The Met 上查看",
        "expert_analysis": "關於作品",
        "summary": "摘要",
        
        # History page
        "history_grid_title": "瀏覽過往收藏",
        "detail_page_title": "作品詳情",
    }
}


# ============================================================================
# STREAMLIT INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize Streamlit session state variables."""
    # 1. 檢查網址是否有帶語言參數 ?lang=zh
    query_lang = st.query_params.get("lang")
    if query_lang in ["en", "zh"]:
        st.session_state.lang = query_lang
    
    # 2. 檢查網址是否有帶作品 ID 參數 ?id=123
    query_id = st.query_params.get("id")
    if query_id:
        st.session_state.selected_id = query_id
    # 預設值設定
    if 'lang' not in st.session_state:
        st.session_state.lang = 'en'
    if 'selected_id' not in st.session_state:
        st.session_state.selected_id = None


def toggle_language():
    """Toggle between English and Chinese."""
    st.session_state.lang = LANG_DICT[st.session_state.lang]["next_lang"]


@st.cache_resource
def get_supabase_client():
    """Initialize and return Supabase client."""
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        st.error("❌ Supabase configuration missing. Check .env file.")
        st.stop()
    
    return create_client(url, key)


# ============================================================================
# SIDEBAR COMPONENTS
# ============================================================================

def render_sidebar():
    """Render the main sidebar with language toggle and navigation."""
    supabase = get_supabase_client()
    L = LANG_DICT[st.session_state.lang]
    
    with st.sidebar:
        # 1. Art appreciation counter (Top)
        try:
            first_res = supabase.table("ceramic_items").select("created_at").order("created_at", desc=False).limit(1).execute()
            if first_res.data:
                start_date = datetime.fromisoformat(
                    first_res.data[0]['created_at'].replace('Z', '+00:00')
                )
                days_diff = (datetime.now(start_date.tzinfo) - start_date).days + 1
                day_display = L["days_format"].format(count=days_diff)
                st.metric(label=L["journey_label"], value=day_display)
        except Exception as e:
            err_msg = str(e)
            st.warning(f"Could not fetch counter: {err_msg[:30]}")  # type: ignore
        
        # Spacer to push language button to bottom
        st.write("") # small gap
        
        # 2. Language Toggle (Moved to bottom and made to look smaller)
        # Using a container or columns to shrink the button if needed, 
        # or just small text + button.
        st.divider()
        st.caption(f"🌐 {L['current_language']}: {L['language_' + st.session_state.lang]}")
        st.button(
            L["btn_label"], 
            on_click=toggle_language, 
            use_container_width=True,
            type="secondary",
            help="Switch Language"
        )


# ============================================================================
# COMMON UI PATTERNS
# ============================================================================

def display_artwork_card(item, lang_suffix, lang_dict):
    """Display a single artwork in card format with two-column layout."""
    title = item.get(f'title_{lang_suffix}', 'N/A')
    date = item.get(f'date_{lang_suffix}', 'N/A')
    culture = item.get(f'culture_{lang_suffix}', 'N/A')
    medium = item.get(f'medium_{lang_suffix}', 'N/A')
    description = item.get(f'description_{lang_suffix}', 'No content available.')
    summary = item.get(f'summary_{lang_suffix}', None)

    # CSS hack to make columns equal height
    st.markdown("""
        <style>
        [data-testid="stHorizontalBlock"] {
            align-items: stretch !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Top Row: Image (Left) and Details (Right) ---
    with st.container(border=True):
        col_img, col_details = st.columns([1, 0.8], gap="small")
        
        with col_img:
            # Image - Using use_container_width for modern Streamlit compatibility
            if item.get("image_url"):
                st.image(item["image_url"], use_container_width=True)
        
        with col_details:
            with st.container(border=True):
                # Title
                st.markdown(f"### {title}")
                
                # Artwork Details
                st.markdown(f"📅 **{lang_dict['date']}**  \n{date}")
                st.markdown(f"🌍 **{lang_dict['culture']}**  \n{culture}")
                st.markdown(f"🎨 **{lang_dict['medium']}**  \n{medium}")
            
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
            
            # Official link button
            if item.get("met_url"):
                st.link_button(
                    f"🔗 {lang_dict['official_link']}",
                    item["met_url"],
                    use_container_width=True
                )

    # --- Bottom Row: Full Width Description ---
    st.divider()
    st.subheader(lang_dict["expert_analysis"])
    st.write(description)


def display_artwork_grid_item(item, lang_suffix):
    """Display a single artwork in grid/card format for history page with fixed height."""
    # Build the card content
    card_html = '<div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; display: flex; flex-direction: column; min-height: 480px; height: 100%; overflow: hidden;">'
    
    # Image with fixed aspect ratio (20:13 like LINE messages)
    if item.get("image_url"):
        card_html += f"""
        <div style="width: 100%; height: 250px; overflow: hidden; border-radius: 4px; margin-bottom: 8px;">
            <img src="{item['image_url']}" style="width: 100%; height: 100%; object-fit: cover; object-position: center;">
        </div>
        """
    
    # Title with dynamic font size based on text length
    title = item.get(f'title_{lang_suffix}', 'Unknown')
    title_length = len(title)
    
    # 動態調整字體大小，更激進地縮小如果需要
    if title_length <= 10:
        title_font_size = "24px"
    elif title_length <= 20:
        title_font_size = "20px"
    elif title_length <= 30:
        title_font_size = "16px"
    else:
        title_font_size = "14px"
    
    card_html += f"<h3 style='font-size: {title_font_size}; margin: 8px 0; line-height: 1.2;'>{title}</h3>"
    
    # Quick info
    date = item.get(f'date_{lang_suffix}', 'N/A')
    culture = item.get(f'culture_{lang_suffix}', 'N/A')
    card_html += f"<p style='font-size: 12px; color: #666; margin: 4px 0;'>📅 {date} | 🌍 {culture}</p>"
    
    # Brief summary (根據語言顯示)，截斷如果太長
    summary_key = f'summary_{lang_suffix}'
    summary = item.get(summary_key)
    
    # 如果有 summary，優先顯示，截斷到適當長度
    if summary:
        # 估計字符數，中文約300-500字，英文150-250詞，但這裡截斷到200字符以適應
        truncated_summary = summary[:200] + "..." if len(summary) > 200 else summary
        card_html += f"<p style='font-size: 14px; margin: 8px 0; line-height: 1.4;'>✨ <em>{truncated_summary}</em></p>"
    else:
        # 如果沒有 summary，回落使用簡短描述
        description = item.get(f'description_{lang_suffix}', '')
        if description:
            truncated_desc = description[:150] + "..." if len(description) > 150 else description
            card_html += f"<p style='font-size: 14px; margin: 8px 0; line-height: 1.4;'>{truncated_desc}</p>"
    
    card_html += '<div style="flex-grow: 1;"></div>'
    card_html += '</div>'
    
    st.markdown(card_html, unsafe_allow_html=True)
    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    
    # Button displayed directly under the card block, with unique key per item
    button_clicked = st.button(
        "👁️ View Details",
        key=f"history_card_btn_{item.get('id', title)}",
        width="stretch"
    )
    
    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)
    return item['id'] if button_clicked else None
