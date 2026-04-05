"""
LINE Bot Integration Module
Provides Flex Message templates and notification sending functions.
"""

import os
import json
from linebot import LineBotApi  # type: ignore
from linebot.models import FlexSendMessage, TextSendMessage  # type: ignore


def build_flex_message_contents(report_data, lang="en"):
    """
    Build a Flex Message JSON structure for LINE.
    
    Args:
        report_data: Dictionary containing artwork information
        lang: Language code ("en" for English, "zh" for Chinese)
    
    Returns:
        Dictionary with Flex Message structure
    """
    # Language-specific labels
    labels = {
        "en": {
            "date_label": "Date",
            "culture_label": "Culture",
            "medium_label": "Medium",
            "met_button": "View on The Met",
            "app_button": "View Full Details",
            "switch_button": "閱覽中文版",
            "switch_lang": "zh",
        },
        "zh": {
            "date_label": "年代",
            "culture_label": "產地",
            "medium_label": "材質",
            "met_button": "前往 The Met",
            "app_button": "查看完整介紹",
            "switch_button": "Switch to English",
            "switch_lang": "en",
        }
    }
    
    lang_labels = labels.get(lang, labels["en"])
    lang_suffix = lang
    
    # Get streamlit app URL from env or use placeholder
    streamlit_url = os.getenv("STREAMLIT_APP_URL", "https://cerabase.streamlit.app").rstrip('/')
    
    # Build switch URL with language parameter
    switch_url = f"{streamlit_url}/?lang={lang_labels['switch_lang']}"
    
    flex_contents = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": report_data.get("image_url", "https://via.placeholder.com/1000x700"),
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": str(report_data.get(f"title_{lang_suffix}") or "Unknown Artwork"),
                    "weight": "bold",
                    "size": "xl",
                    "wrap": True,
                    "color": "#2D3436"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": lang_labels["date_label"],
                                    "color": "#999999",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": str(report_data.get(f"date_{lang_suffix}") or "N/A"),
                                    "wrap": True,
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 4
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": lang_labels["culture_label"],
                                    "color": "#999999",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": str(report_data.get(f"culture_{lang_suffix}") or "N/A"),
                                    "wrap": True,
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 4
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": lang_labels["medium_label"],
                                    "color": "#999999",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": str(report_data.get(f"medium_{lang_suffix}") or "N/A"),
                                    "wrap": True,
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 4
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": str(report_data.get(f"summary_{lang_suffix}") or report_data.get(f"description_{lang_suffix}", "")),
                            "size": "sm",
                            "color": "#666666",
                            "wrap": True,
                            "maxLines": 0,
                            "fontStyle": "italic"
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "md",
                    "action": {
                        "type": "uri",
                        "label": lang_labels["met_button"],
                        "uri": report_data.get("met_url") or "https://www.metmuseum.org/"
                    }
                },
                {
                    "type": "button",
                    "style": "primary",
                    "height": "md",
                    "color": "#8B4513",
                    "action": {
                        "type": "uri",
                        "label": lang_labels["app_button"],
                        "uri": f"{streamlit_url}/?lang={lang}&id={report_data.get('id') or report_data.get('object_id')}"
                    }
                },
                {
                    "type": "separator",
                    "margin": "sm"
                },
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": lang_labels["switch_button"],
                        "data": f"action=switch_lang&lang={lang_labels['switch_lang']}&object_id={report_data.get('objectID') or report_data.get('object_id', '')}",
                        "displayText": lang_labels["switch_button"]
                    }
                }
            ]
        }
    }
    
    return flex_contents


def send_line_daily_report(report_data, lang="en"):
    """
    Send daily ceramic artwork notification via LINE using Flex Message.
    
    Args:
        report_data: Dictionary containing artwork information
        lang: Language code ("en" for English, "zh" for Chinese)
    """
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.getenv("LINE_USER_ID")
    
    if not token or not user_id:
        print("⚠️ Warning: LINE_CHANNEL_ACCESS_TOKEN or LINE_USER_ID not configured")
        return
    
    try:
        line_bot_api = LineBotApi(token)
        flex_contents = build_flex_message_contents(report_data, lang)
        
        title = report_data.get(f"title_{lang}", "Daily Ceramic")
        message = FlexSendMessage(
            alt_text=f"🏺 Daily Ceramic: {title}",
            contents=flex_contents
        )
        
        line_bot_api.push_message(user_id, message)
        print(f"📲 LINE Flex Message ({lang.upper()}) sent successfully!")
        
    except Exception as e:
        print(f"❌ Failed to send LINE message: {e}")


def send_line_text_notification(title_zh, date_zh, culture_zh, summary_zh):
    """
    Send a simple text notification via LINE (fallback option).
    
    Args:
        title_zh: Artwork title in Chinese
        date_zh: Date in Chinese
        culture_zh: Culture/origin in Chinese
        summary_zh: Brief summary in Chinese
    """
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.getenv("LINE_USER_ID")
    
    if not token or not user_id:
        print("⚠️ Warning: LINE configuration missing")
        return
    
    try:
        line_bot_api = LineBotApi(token)
        message_text = (
            f"🏺 【今日陶瓷推薦】\n\n"
            f"名稱：{title_zh}\n"
            f"年代：{date_zh}\n"
            f"產地：{culture_zh}\n\n"
            f"✨ 簡評：\n{summary_zh[:100]}..."
        )
        
        message = TextSendMessage(text=message_text)
        line_bot_api.push_message(user_id, message)
        print("📲 LINE text message sent successfully!")
        
    except Exception as e:
        print(f"❌ Failed to send LINE text message: {e}")
