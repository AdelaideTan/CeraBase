# 🏺 CeraBase: Daily Ceramic Artwork Recommendation

A cross-platform service that delivers daily ceramic artwork recommendations from The Metropolitan Museum of Art through LINE Bot and Streamlit web app. Features bilingual support (English & Traditional Chinese), AI-powered descriptions, and artwork history tracking.

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [Configuration](#configuration)
- [API Integration](#api-integration)
- [Development](#development)

---

## 📖 Overview

### What is CeraBase?

CeraBase automates the discovery and sharing of beautiful ceramic artworks. Every day, it:

1. **Fetches** a high-quality ceramic artwork from The Met's collection
2. **Analyzes** it using AI to generate professional bilingual descriptions
3. **Stores** the metadata in a cloud database
4. **Distributes** it through:
   - **LINE Bot**: Push notifications with rich Flex Messages
   - **Streamlit Web App**: Detailed exploration with browsing history

### Key Features

- ✨ **Daily Automation**: Scheduled artwork selection with quality checks
- 🌍 **Bilingual Support**: English & Traditional Chinese (Taiwan)
- 🤖 **AI-Powered Analysis**: Professional descriptions via Cerebras LLM
- 📱 **LINE Integration**: Rich Flex Messages with images and quick links
- 🌐 **Web Dashboard**: Multi-page Streamlit app with responsive design
- 📊 **History Tracking**: Browse and revisit past collections
- 🔗 **Cross-platform**: Seamless experience on mobile and desktop

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CeraBase System                         │
└─────────────────────────────────────────────────────────────┘

┌─── Data Sources ──────────────────────────────────────────┐
│  The Metropolitan Museum of Art Open Access API           │
│  (Ceramic collection with high-res images)                │
└───────────────────────┬───────────────────────────────────┘
                        │
          ┌─────────────▼──────────────┐
          │   main.py (Data Pipeline)  │
          │  ├─ Fetch artwork          │
          │  ├─ Quality checks         │
          │  ├─ Duplicate detection    │
          │  ├─ AI analysis (CrewAI)   │
          │  └─ Save to database       │
          └──────────┬─────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌──────────┐   ┌──────────┐   ┌──────────────┐
│ Supabase │   │ LINE API │   │ Streamlit    │
│ Database │   │  (Push)  │   │  (Display)   │
└──────────┘   └──────────┘   └──────────────┘
    │                │                │
    └────────────────┼────────────────┘
                     │
    ┌────────────────┴────────────────┐
    │      Users/Collectors           │
    │  (Web App + LINE Bot)           │
    └─────────────────────────────────┘
```

### Components

| Component | Role | Technology |
|-----------|------|-----------|
| **main.py** | Daily automation & data pipeline | Python, CrewAI, Cerebras LLM |
| **app.py** | Streamlit app entry point | Streamlit |
| **pages/00_home.py** | Daily artwork display | Streamlit |
| **pages/01_history.py** | Past collections grid | Streamlit |
| **src/cerabase/fetch_art.py** | API fetching logic | Requests, BeautifulSoup |
| **src/cerabase/agents.py** | AI agent configuration | CrewAI |
| **src/cerabase/tasks.py** | AI task definitions | CrewAI |
| **src/cerabase/line_utils.py** | LINE Bot integration | LineBot SDK |
| **src/cerabase/ui_helpers.py** | Shared UI components | Streamlit |
| **Supabase** | Database & storage | PostgreSQL |

---

## 📁 Project Structure

```
CeraBase/
├── app.py                          # Streamlit app entry point
├── main.py                         # Daily automation pipeline
├── .env                            # Environment variables (not in git)
├── pyproject.toml                  # Python package config
├── README.md                       # This file
├── cerabase_venv/                  # Python virtual environment
├── pages/                          # Streamlit multi-page directory
│   ├── 00_home.py                  # Daily artwork display
│   └── 01_history.py               # Past collections grid
└── src/
    └── cerabase/                   # Main package
        ├── __init__.py
        ├── ui_helpers.py           # Shared Streamlit components
        ├── fetch_art.py            # The Met API integration
        ├── agents.py               # CrewAI agent configuration
        ├── tasks.py                # CrewAI task definitions
        ├── line_utils.py           # LINE Bot Flex Message templates
        └── __pycache__/
```

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.11+
- Virtual environment manager (venv, conda, etc.)
- Git
- API keys/credentials:
  - **Supabase** URL & API Key
  - **Cerebras API** Key (for LLM)
  - **LINE Channel** Access Token & User ID

### Step 1: Activate Virtual Environment

```bash
source cerabase_venv/bin/activate  # macOS/Linux
# or
cerabase_venv\Scripts\activate  # Windows
```

### Step 2: Install Dependencies

```bash
pip install python-dotenv crewai cerebras-cloud-sdk supabase line-bot-sdk requests beautifulsoup4 streamlit pydantic
```

### Step 3: Configure Environment Variables

Create/update `.env` file:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_api_key
CEREBRAS_API_KEY=your_cerebras_api_key
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_USER_ID=your_line_user_id
STREAMLIT_APP_URL=https://your-streamlit-app.streamlit.app/
```

### Step 4: Set Up Supabase Database

Create table `ceramic_items` with columns:
- object_id, title_zh, title_en, date_zh, date_en
- culture_zh, culture_en, medium_zh, medium_en
- description_zh, description_en, materials_zh, materials_en
- summary_en, summary_zh, image_url, met_url
- created_at, updated_at

---

## 🏃 Running the Application

### Backend: Daily Automation

```bash
python main.py
```

Fetches → Analyzes → Stores → Notifies (LINE + Database)

### Frontend: Web Dashboard

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

**Available Pages:**
- **Home** (`pages/00_home.py`): Today's featured artwork
- **History** (`pages/01_history.py`): Browse all saved artworks

---

## ⚙️ Configuration

### Language Toggle

Users can switch between English and Traditional Chinese in the sidebar.

### LINE Flex Message

Customize in `src/cerabase/line_utils.py`:
- Message template and styling
- Button labels and URLs
- Summary text formatting

### Artwork Selection

Modify `src/cerabase/fetch_art.py`:
- Museum API endpoint
- Quality filters (images, not fragments, etc.)
- Search parameters

---

## 🔌 API Integrations

### The Met API
- **Endpoint**: `https://collectionapi.metmuseum.org/public/collection/v1/`
- **Usage**: Search ceramics, fetch object details

### LINE Bot API
- **Features**: Push messages, Flex Message templates
- **Auth**: Channel Access Token

### Cerebras LLM
- **Model**: `cerebras/qwen-3-235b-a22b-instruct-2507`
- **Purpose**: Bilingual description generation

---

## 🚀 Deployment & Automation

### 1. Daily Automation (`main.py`) via GitHub Actions

This project contains a GitHub Actions workflow to automatically run the daily fetch and LINE push notification script. 
This is safer than GitHub Pages because it runs securely in the background without exposing your API keys.

1. Go to your GitHub repository.
2. Navigate to **Settings** > **Secrets and variables** > **Actions**.
3. Click **New repository secret** and add the following keys from your `.env.example`:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `CEREBRAS_API_KEY`
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_USER_ID`
   - `STREAMLIT_APP_URL`
4. The GitHub Action will now automatically run every day at 00:00 UTC.

### 2. Streamlit Dashboard

*Note: Streamlit apps run a Python backend, so they cannot be deployed as static sites to **GitHub Pages**.*

The recommended, free way to deploy the Streamlit Web App is **Streamlit Community Cloud**:
1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Connect your GitHub account and select this repository.
3. Set the Main file path to `about.py`.
4. In Advanced Settings, paste the contents of your `.env` into the `Secrets` box.
5. Click **Deploy**.

---

## 🔧 Development

### Adding a Page

Create `pages/02_newpage.py`:

```python
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from cerabase.ui_helpers import init_session_state, render_sidebar, LANG_DICT

st.set_page_config(page_title="New Page", page_icon="📊", layout="wide")
init_session_state()
render_sidebar()

# Your content here
```

### Modifying AI Tasks

Edit `src/cerabase/tasks.py`:
- Task descriptions (what AI should do)
- Expected outputs
- Context from previous tasks

### Adding Language Support

1. Update `LANG_DICT` in `src/cerabase/ui_helpers.py`
2. Update LINE labels in `src/cerabase/line_utils.py`
3. Modify task descriptions in `src/cerabase/tasks.py`

---

## 📚 References

- [The Met Museum API](https://metmuseum.org/about-the-met/policies-and-documents/open-access)
- [LINE Bot API](https://developers.line.biz/en/services/line-bot/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Supabase Docs](https://supabase.com/docs)
- [CrewAI Docs](https://docs.crewai.com/)

---

**Version**: 0.1.0 | **Last Updated**: April 2026

