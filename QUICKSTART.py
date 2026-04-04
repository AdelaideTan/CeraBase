#!/usr/bin/env python3
"""
🏺 CeraBase - Quick Reference Guide
Last Updated: April 2026
"""

# ============================================================================
# PROJECT OVERVIEW
# ============================================================================
"""
CeraBase is a cross-platform ceramic artwork recommendation system featuring:

✅ Daily Automation (main.py)
   - Fetches ceramics from The Met API
   - AI analysis with Cerebras LLM
   - Bilingual (English & Chinese) descriptions
   - Saves to Supabase cloud database
   - Sends LINE Bot notifications

✅ Web Dashboard (Streamlit)
   - Multi-page app (Home + History)
   - Language toggle (EN/ZH)
   - Art appreciation counter
   - Grid browsing with search & sorting
   - Responsive design

✅ LINE Bot Integration
   - Rich Flex Messages with images
   - Metadata display
   - Quick action buttons
   - Bilingual support

Technology Stack:
- Backend: Python, CrewAI, Cerebras LLM
- Frontend: Streamlit
- Database: Supabase (PostgreSQL)
- Messaging: LINE Bot API
- Data Source: The Metropolitan Museum Open Access API
"""

# ============================================================================
# FILE STRUCTURE
# ============================================================================
"""
CeraBase/
├── app.py                    ← Streamlit entry point (welcome page)
├── main.py                   ← Daily automation pipeline
├── .env                      ← Configuration (API keys, credentials)
├── pyproject.toml            ← Python package config
├── README.md                 ← Full documentation
├── IMPLEMENTATION.md         ← Implementation summary (this file)
│
├── pages/                    ← Streamlit multi-page app
│   ├── 00_home.py           ← Daily artwork display
│   └── 01_history.py        ← Past collections grid browser
│
└── src/cerabase/            ← Main package
    ├── __init__.py
    ├── ui_helpers.py        ← Shared Streamlit components & language config
    ├── fetch_art.py         ← The Met API integration
    ├── agents.py            ← CrewAI agent configuration
    ├── tasks.py             ← AI task definitions
    └── line_utils.py        ← LINE Bot Flex Message templates
"""

# ============================================================================
# QUICK START
# ============================================================================
"""
1. Activate Environment:
   source cerabase_venv/bin/activate

2. Configure .env:
   SUPABASE_URL=...
   SUPABASE_KEY=...
   CEREBRAS_API_KEY=...
   LINE_CHANNEL_ACCESS_TOKEN=...
   LINE_USER_ID=...

3a. Run Daily Automation:
    python main.py
    → Fetches, analyzes, stores, sends LINE notification

3b. Launch Web App:
    streamlit run app.py
    → Opens at http://localhost:8501

4. Browse the App:
   - Home: View today's featured artwork
   - History: Browse past collections
   - Sidebar: Toggle language, see counter, quick access history
"""

# ============================================================================
# KEY MODULES EXPLAINED
# ============================================================================
"""
┌─ src/cerabase/ui_helpers.py ────────────────────────────────────────┐
│                                                                      │
│ Shared utilities for Streamlit pages:                              │
│                                                                      │
│ • LANG_DICT: Language configuration (EN/ZH)                        │
│ • init_session_state(): Initialize Streamlit session               │
│ • get_supabase_client(): Cache Supabase connection                │
│ • render_sidebar(): Display sidebar with language toggle           │
│ • display_artwork_card(): Full detail layout                       │
│ • display_artwork_grid_item(): Compact grid card                   │
│                                                                      │
│ Usage in pages:                                                     │
│   from cerabase.ui_helpers import (                                 │
│       init_session_state, render_sidebar, LANG_DICT               │
│   )                                                                  │
└──────────────────────────────────────────────────────────────────────┘

┌─ pages/00_home.py ──────────────────────────────────────────────────┐
│                                                                      │
│ Daily Artwork Showcase                                              │
│                                                                      │
│ Features:                                                            │
│ • Display latest or selected artwork from Supabase                 │
│ • Bilingual title, description, metadata                           │
│ • Image + detail panel layout                                      │
│ • Link to The Met official page                                    │
│ • AI summary display                                                │
│                                                                      │
│ Data Flow:                                                           │
│   Supabase → Display (latest OR selected by user)                  │
└──────────────────────────────────────────────────────────────────────┘

┌─ pages/01_history.py ───────────────────────────────────────────────┐
│                                                                      │
│ Past Collections Browser                                            │
│                                                                      │
│ Features:                                                            │
│ • Grid layout with responsive columns (3 items)                    │
│ • Sorting: Latest, Oldest, Alphabetical                            │
│ • Search: Filter by title                                          │
│ • Pagination: 6, 12, or 20 items per page                          │
│ • Click card → View Details (navigates to Home)                    │
│                                                                      │
│ Data Flow:                                                           │
│   Supabase → Query → Filter & Sort → Display Grid                  │
└──────────────────────────────────────────────────────────────────────┘

┌─ src/cerabase/line_utils.py ────────────────────────────────────────┐
│                                                                      │
│ LINE Bot Messaging                                                   │
│                                                                      │
│ Functions:                                                           │
│ • build_flex_message_contents(data, lang): Build Flex JSON         │
│ • send_line_daily_report(data, lang): Send push notification       │
│ • send_line_text_notification(...): Send text (fallback)           │
│                                                                      │
│ Flex Message Structure:                                             │
│   ┌─ Hero Image ────────────────────────────────────────┐          │
│   ├─ Title (bold, large)                               │          │
│   ├─ Metadata Grid (Date, Culture, Medium)            │          │
│   ├─ AI Summary (italics)                             │          │
│   └─ Buttons                                            │          │
│      ├─ "View on The Met" (secondary)                  │          │
│      └─ "View Full Details" → Streamlit App (primary)  │          │
└──────────────────────────────────────────────────────────────────────┘

┌─ main.py ───────────────────────────────────────────────────────────┐
│                                                                      │
│ Daily Automation Pipeline                                           │
│                                                                      │
│ Process:                                                             │
│ 1. get_high_quality_pottery()                                       │
│    → Fetch from The Met API until image found                      │
│                                                                      │
│ 2. Duplicate check                                                  │
│    → Query Supabase for existing object_id                         │
│    → If duplicate, retry fetch                                      │
│                                                                      │
│ 3. AI Analysis (CrewAI)                                             │
│    → docent_agent (Bilingual guide)                                │
│    → pottery_tasks (3 sequential tasks):                           │
│       ├─ Task 1: Deep analysis & lossless integration             │
│       ├─ Task 2: Generate English summary (one-liner)             │
│       └─ Task 3: Format as JSON with all fields                   │
│                                                                      │
│ 4. Save to Supabase                                                 │
│    → Insert complete record with all metadata                      │
│                                                                      │
│ 5. Notify via LINE                                                  │
│    → send_line_daily_report(report_data)                           │
│    → Flex Message in English (configurable)                        │
└──────────────────────────────────────────────────────────────────────┘
"""

# ============================================================================
# CONFIGURATION REFERENCE
# ============================================================================
"""
Environment Variables (.env):

SUPABASE_URL              The URL of your Supabase project
SUPABASE_KEY              Supabase API key (anon public key)
CEREBRAS_API_KEY          API key for Cerebras LLM service
LINE_CHANNEL_ACCESS_TOKEN LINE Bot channel access token
LINE_USER_ID              LINE user ID to send messages to
STREAMLIT_APP_URL         (Optional) Your Streamlit Cloud app URL

Supabase Table Schema (ceramic_items):
├─ id (BIGINT, PRIMARY KEY, GENERATED)
├─ object_id (TEXT, UNIQUE) ← The Met Museum object ID
├─ title_zh, title_en
├─ date_zh, date_en
├─ culture_zh, culture_en
├─ medium_zh, medium_en
├─ description_zh, description_en
├─ materials_zh, materials_en
├─ summary_en, summary_zh
├─ image_url
├─ met_url
├─ created_at (TIMESTAMP DEFAULT NOW())
└─ updated_at (TIMESTAMP DEFAULT NOW())
"""

# ============================================================================
# LANGUAGE SUPPORT
# ============================================================================
"""
The system supports TWO languages:

LANG_DICT = {
    "en": {
        # English labels for all UI elements
        "page_title_home": "🏛️ Daily Ceramic",
        "page_title_history": "📜 Past Collections",
        "btn_label": "切換為中文",  # Button to switch to Chinese
        ... (20+ labels)
    },
    "zh": {
        # Traditional Chinese (Taiwan) labels
        "page_title_home": "🏛️ 今日作品推薦",
        "page_title_history": "📜 過往收藏",
        "btn_label": "Switch to English",  # Button to switch to English
        ... (20+ labels)
    }
}

How it works:
1. User clicks language button in sidebar
2. toggle_language() switches st.session_state.lang
3. st.rerun() refreshes page
4. UI re-renders with new language from LANG_DICT
5. Database queries use lang_suffix = st.session_state.lang
"""

# ============================================================================
# DATA FLOW DIAGRAMS
# ============================================================================
"""
DAILY AUTOMATION FLOW:
═════════════════════════════════════════════════════════════════════

The Met API
    ↓
get_random_pottery() [with quality checks]
    ↓ (has image? not fragment?)
Supabase [duplicate check]
    ↓ (new artwork?)
CrewAI Multi-task Analysis
    ├─ Task 1: Deep professional analysis (EN/ZH)
    ├─ Task 2: Extract summary (EN, one-liner)
    └─ Task 3: Format as JSON
    ↓
Supabase [save ceramic_items]
    ↓
LINE Bot API [send Flex Message]
    ↓
User's LINE app [notification received]


WEB APP NAVIGATION FLOW:
═════════════════════════════════════════════════════════════════════

app.py (Home/Welcome)
    ↓ (Streamlit auto-navigation)
    ├─ pages/00_home.py ──→ [Display latest or selected artwork]
    │                        ↓ [Click history item in sidebar]
    │                        └─ [Show selected artwork]
    │
    └─ pages/01_history.py ──→ [Browse grid of all artworks]
                               ↓ [Click "View Details"]
                               └─ [Navigate to Home with selection]


SIDEBAR INTERACTION FLOW:
═════════════════════════════════════════════════════════════════════

render_sidebar()
├─ Language Toggle Button
│   └─ toggle_language() → st.rerun()
├─ Art Appreciation Counter
│   └─ Query: MIN(created_at) → Calculate days
├─ Quick Access History
│   └─ Query: Last 5 artworks
│       └─ Click item → st.session_state.selected_id = id
│           → st.switch_page("pages/00_home.py")
"""

# ============================================================================
# COMMON TASKS
# ============================================================================
"""
Add a new Streamlit page:
─────────────────────────
1. Create pages/02_analysis.py
2. Start with:
   import streamlit as st
   import sys, os
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))
   from cerabase.ui_helpers import init_session_state, render_sidebar, LANG_DICT
   st.set_page_config(page_title="...", page_icon="...", layout="wide")
   init_session_state()
   render_sidebar()
   # Your page content

Change AI description language:
──────────────────────────────
1. Edit src/cerabase/tasks.py
2. Modify task descriptions to request new language
3. Update main.py to save new language fields in db_data

Add new UI labels:
────────────────
1. Add to LANG_DICT in src/cerabase/ui_helpers.py
2. Use as: L = LANG_DICT[st.session_state.lang]; L["your_key"]

Customize LINE Flex Message:
────────────────────────────
1. Edit src/cerabase/line_utils.py
2. Modify build_flex_message_contents() function
3. Change colors, sizes, buttons, layout

Schedule daily automation:
────────────────────────
macOS/Linux crontab:
  0 9 * * * cd /path/to/CeraBase && source cerabase_venv/bin/activate && python main.py

Windows Task Scheduler:
  Create task running: python C:\\path\\to\\CeraBase\\main.py
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================
"""
Problem: "Import cerabase.* could not be resolved"
Solution: Check sys.path.insert() is present in page files
          sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

Problem: Supabase connection fails
Solution: Verify .env has SUPABASE_URL and SUPABASE_KEY
         Check network connectivity
         Verify Supabase table "ceramic_items" exists

Problem: LINE message not sending
Solution: Check LINE_CHANNEL_ACCESS_TOKEN is valid
         Verify LINE_USER_ID is correct
         Check LINE Bot is activated in LINE Developer Console

Problem: No artwork fetched from API
Solution: Check internet connection
         Verify The Met API is responding
         Check if your IP is blocked (unlikely)

Problem: AI analysis fails with timeout
Solution: Increase max_execution_time in agents.py (default: 120s)
         Check Cerebras API status and quota
         Verify CEREBRAS_API_KEY is valid
"""

# ============================================================================
# NEXT STEPS (OPTIONAL ENHANCEMENTS)
# ============================================================================
"""
Feature Ideas:
✅ Daily scheduling (cron/systemd)
✅ Streamlit Cloud deployment
✅ User authentication & personalization
✅ Favorite/bookmark artworks
✅ Category filters (pottery type, culture, date range)
✅ Analytics dashboard (most viewed, engagement metrics)
✅ Email subscriptions (alternative to LINE)
✅ Mobile-responsive refinements
✅ Performance optimizations (caching, pagination)
✅ Accessibility improvements (WCAG compliance)
"""

# ============================================================================
# SUPPORT & RESOURCES
# ============================================================================
"""
Documentation:
- README.md: Full project documentation
- IMPLEMENTATION.md: Implementation details
- This file: Quick reference guide

Official Resources:
- The Met Museum API: https://metmuseum.org/about-the-met/policies-and-documents/open-access
- LINE Bot API: https://developers.line.biz/en/services/line-bot/
- Streamlit Docs: https://docs.streamlit.io/
- Supabase Docs: https://supabase.com/docs
- CrewAI Docs: https://docs.crewai.com/

GitHub (if available):
- Project Repository: [URL]
- Issues & Feature Requests: [URL]
- Discussions: [URL]
"""

print(__doc__)
