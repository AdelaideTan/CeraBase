"""
Home Page: Daily Ceramic Artwork Display
Main entry point showing the current day's featured artwork.
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
    display_artwork_card,
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

init_session_state()
L = LANG_DICT[st.session_state.lang]

st.set_page_config(
    page_title=f"CeraBase - {L['page_title_home']}",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# INITIALIZATION
# ============================================================================

supabase = get_supabase_client()
render_sidebar()

# ============================================================================
# PAGE CONTENT
# ============================================================================

L = LANG_DICT[st.session_state.lang]
lang_suffix = st.session_state.lang

# Page title
st.title(L["page_title_home"])

st.markdown("---")

# ============================================================================
# DISPLAY ARTWORK
# ============================================================================

try:
    query = supabase.table("ceramic_items").select("*")
    
    # If a specific artwork is selected from history, show it
    if st.session_state.selected_id:
        response = query.eq("id", st.session_state.selected_id).execute()
    else:
        # Otherwise, show the latest artwork
        response = query.order("id", desc=True).limit(1).execute()
    
    if response.data:
        item = response.data[0]
        display_artwork_card(item, lang_suffix, L)
        
        # Metadata footer
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"🆔 Object ID: {item.get('object_id', 'N/A')}")
        with col2:
            created_at = item.get("created_at", "N/A")
            if created_at:
                st.caption(f"📅 Added: {created_at[:10]}")
        with col3:
            st.caption(f"🏛️ Collection: The Metropolitan Museum of Art")
    else:
        st.info(L["no_data"])
        st.info("💡 Run `python main.py` to fetch and save the daily artwork.")

except Exception as e:
    st.error(f"❌ Error fetching data: {str(e)}")
    with st.expander("Debug Info"):
        st.write(f"Error details: {e}")
