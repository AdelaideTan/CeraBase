"""
CeraBase: Daily Ceramic Artwork Recommendation
Cross-platform service (LINE Bot + Streamlit) featuring The Met Museum collection.

Main Entry Point for Streamlit Multi-page App
"""

import streamlit as st
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cerabase.ui_helpers import init_session_state, render_sidebar, LANG_DICT
from dotenv import load_dotenv

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

load_dotenv()

# Initialize session first
init_session_state()

# Get language for dynamic page title
L = LANG_DICT[st.session_state.lang]

st.set_page_config(
    page_title=f"CeraBase - {L['page_title_welcome']}",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/adelaide-tan/cerabase",
        "Report a bug": "https://github.com/adelaide-tan/cerabase/issues",
        "About": "🏺 CeraBase - Daily Ceramic Artwork Recommendation from The Met Museum"
    }
)

# ============================================================================
# RENDER SIDEBAR
# ============================================================================

render_sidebar()

# ============================================================================
# HOME PAGE (If accessed directly)
# ============================================================================

# Refresh language after sidebar
L = LANG_DICT[st.session_state.lang]

st.title("🏺 " + L["page_title_welcome"])
st.markdown(f"""
{L['cerabase_description']}

- **📱 {L['line_bot_label']}**: {L['line_bot_desc']}
- **🌐 {L['web_app_label']}**: {L['web_app_desc']}

### 🎯 {L['features_title']}

- **{L['feature_daily']}**: {L['feature_daily_desc']}
- **{L['feature_bilingual']}**: {L['feature_bilingual_desc']}
- **{L['feature_history']}**: {L['feature_history_desc']}
- **{L['feature_links']}**: {L['feature_links_desc']}
- **{L['feature_ai']}**: {L['feature_ai_desc']}

### 🚀 {L['getting_started']}

1. **{L['step1']}**: {L['step1_desc']}
2. **{L['step2']}**: {L['step2_desc']}
3. **{L['step3']}**: {L['step3_desc']}
""")

