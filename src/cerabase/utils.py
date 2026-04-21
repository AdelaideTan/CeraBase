"""
Common Utility Functions for CeraBase
Provides shared database initialization and data cleaning functions.
"""

import os
import re
from supabase import create_client, Client
from dotenv import load_dotenv

def get_supabase_client() -> Client:
    """Initialize and return Supabase client using environment variables."""
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("❌ SUPABASE_URL or SUPABASE_KEY not found in environment.")
        
    return create_client(url, key)

def clean_data_string(text):
    """Clean and normalize string data for UI display and storage."""
    if not isinstance(text, str):
        return str(text)
    # Handle special characters (e.g., non-breaking hyphens)
    text = text.replace('\u001f', '–') 
    # Keep only printable characters and specific allowed ones
    text = "".join(char for char in text if char.isprintable() or char == '–')
    # Use consistent quotes
    text = text.replace('"', "'")
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def validate_and_trim_descriptions(data):
    """
    Validate and trim artwork descriptions to meet length constraints.
    - description_en: 150-250 words
    - description_zh: 300-500 characters
    """
    # Validate English description
    if "description_en" in data:
        desc_en = data["description_en"]
        words = desc_en.split()
        word_count = len(words)
        
        if word_count > 250:
            data["description_en"] = " ".join(words[:250]) + "..."
            print(f"⚠️ English description exceeded limit ({word_count} -> 250 words), truncated.")
    
    # Validate Chinese description
    if "description_zh" in data:
        desc_zh = data["description_zh"]
        char_count = len(desc_zh)
        
        if char_count > 500:
            data["description_zh"] = desc_zh[:500] + "..."
            print(f"⚠️ Chinese description exceeded limit ({char_count} -> 500 chars), truncated.")
            
    return data
