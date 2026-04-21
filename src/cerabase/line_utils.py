"""
LINE Bot Integration Module
Provides Flex Message templates and notification sending functions.
"""

import os
import json
from linebot import LineBotApi  # type: ignore
from linebot.models import FlexSendMessage, TextSendMessage  # type: ignore


from cerabase.constants import LINE_LABELS

def build_flex_message_contents(report_data, lang="en"):
    """
    Build a Flex Message JSON structure for LINE.
    """
    lang_labels = LINE_LABELS.get(lang, LINE_LABELS["en"])
    lang_suffix = lang
    
    # Get streamlit app URL from env or use placeholder
    streamlit_url = os.getenv("STREAMLIT_APP_URL", "").rstrip('/')
    
    # 2. 【防呆檢查】如果環境變數抓不到，至少給它一個 https 開頭的假網址
    # 否則 Line 看到 "/?lang=zh..." 會直接報 400 Invalid URI
    if not streamlit_url.startswith("http"):
        # 這裡印出 Log 讓你在 Render 後台能看到警告
        print(f"⚠️ 警告: Render 環境變數 STREAMLIT_APP_URL 讀取失敗或格式錯誤: '{streamlit_url}'")
        temp_base_url = "https://your-app.streamlit.app" 
    else:
        temp_base_url = streamlit_url

    # 3. 統一作品 ID
    obj_id = report_data.get('object_id') or report_data.get('id') or ""

    # 4. 重新定義你的按鈕連結
    # 這是給「查看完整介紹」用的
    app_view_uri = f"{temp_base_url}/?lang={lang}&id={obj_id}"

    # Build switch URL with language parameter
    # switch_url = f"{streamlit_url}/?lang={lang_labels['switch_lang']}"
    
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
                        "uri": app_view_uri
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
