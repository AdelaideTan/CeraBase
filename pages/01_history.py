"""
History Page: Past Collections Grid
Browse all previously saved ceramic artworks in a responsive grid layout.
"""

import streamlit as st  # type: ignore
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from cerabase.ui_helpers import (  # type: ignore
    init_session_state,
    toggle_language,
    LANG_DICT,
    get_supabase_client,
    render_sidebar,
    display_artwork_grid_item,
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="CeraBase - History",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# INITIALIZATION
# ============================================================================

init_session_state()
supabase = get_supabase_client()
render_sidebar()

# ============================================================================
# PAGE CONTENT
# ============================================================================

L = LANG_DICT[st.session_state.lang]
lang_suffix = st.session_state.lang

# Page title
st.title(L["page_title_history"])

st.markdown("---")

# ============================================================================
# FILTERING & SORTING OPTIONS
# ============================================================================

col1, col2, col3 = st.columns(3)

with col1:
    sort_by = st.selectbox(
        "Sort by",
        ["Latest", "Oldest", "Alphabetical"],
        key="history_sort"
    )

with col2:
    items_per_page = st.selectbox(
        "Items per page",
        [6, 12, 20],
        key="history_items"
    )

with col3:
    search_term = st.text_input(
        "Search title",
        placeholder="e.g., Vase, Bowl...",
        key="history_search"
    )

st.markdown("---")

# ============================================================================
# DISPLAY GRID
# ============================================================================

try:
    # Fetch all ceramics
    query = supabase.table("ceramic_items").select("*")
    
    # Apply sorting
    if sort_by == "Latest":
        response = query.order("id", desc=True).execute()
    elif sort_by == "Oldest":
        response = query.order("id", desc=False).execute()
    else:  # Alphabetical
        response = query.order(f"title_{lang_suffix}", desc=False).execute()
    
    if response.data:
        items = response.data
        
        # Filter by search term if provided
        if search_term:
            items = [
                item for item in items
                if search_term.lower() in item.get(f'title_{lang_suffix}', '').lower()
            ]
        
        if items:
            # Display count
            st.write(f"📊 Found **{len(items)}** artwork(s)")
            st.markdown("")
            
            # Render grid
            cols = st.columns(3)
            for idx, item in enumerate(items[:items_per_page]):  # type: ignore
                with cols[idx % 3]:
                    # 卡片內容和按鈕
                    clicked_id = display_artwork_grid_item(item, lang_suffix)
                    if clicked_id:
                        st.session_state.selected_id = clicked_id
                        st.switch_page("pages/00_home.py")
        else:
            st.info("❌ No artworks match your search.")
    else:
        st.info(L["no_data"])
        st.info("💡 Run `python main.py` to fetch and save artworks.")

except Exception as e:
    st.error(f"❌ Error fetching history: {str(e)}")
    with st.expander("Debug Info"):
        st.write(f"Error details: {e}")
