#fetch_art
import requests
import random
from bs4 import BeautifulSoup

def scrape_met_description(url):
    """
    從大都會博物館官網爬取詳細描述與 Artwork Details.
    回傳 (curatorial_text, artwork_details_text)
    """
    if not url or url == "No URL":
        return "", ""
    
    curatorial_text = ""
    artwork_details_text = ""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 抓取詳細文字敘述
            target = soup.find("div", {"data-testid": "read-more-content"})
            if target:
                curatorial_text = target.get_text(separator=" ", strip=True)
                
            # 抓取 Artwork Details
            details_header = soup.find(lambda tag: tag.name == "h2" and "Artwork Details" in tag.text)
            if details_header:
                parent = details_header.find_parent("section") or details_header.find_parent("div")
                if parent:
                    # 抓取所有的 li 項目（如 Title:, Date:, Culture: 等）
                    lis = parent.find_all("li")
                    details_list = [li.get_text(separator=" ", strip=True) for li in lis if ":" in li.text]
                    artwork_details_text = " | ".join(details_list)
                    
        return curatorial_text, artwork_details_text
    except Exception as e:
        print(f"⚠️ 網頁爬取失敗: {e}")
        return "", ""

def get_random_pottery():
    """
    高品質隨機抓取：確保抽到的陶瓷一定有圖且資訊豐富。
    """
    # 這裡加入『品質保證』的迴圈
    max_retries = 50
    attempt = 0
    
    search_url = "https://collectionapi.metmuseum.org/public/collection/v1/search?q=ceramics&medium=Ceramics&hasImages=true"
    
    try:
        # 先抓取所有的 ID 清單
        response = requests.get(search_url, timeout=15)
        response.raise_for_status()
        search_data = response.json()
        object_ids = search_data.get('objectIDs', [])
        if not object_ids: return None

        while attempt < max_retries:
            attempt += 1
            # 隨機挑選 ID
            random_id = random.choice(object_ids[:2000]) # 範圍擴大一點增加多樣性
            
            detail_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{random_id}"
            art_response = requests.get(detail_url, timeout=10)
            if art_response.status_code != 200: continue
            
            art_data = art_response.json()

            # 🛑 品質檢查門檻 🛑
            img_url = art_data.get('primaryImage')
            title = art_data.get('title', '').lower()
            
            # 如果沒圖，或是標題只是無聊的 "fragment (碎片)"，就重新抽
            if not img_url or "fragment" in title:
                print(f"⏭️  第 {attempt} 次抽取品質不符（沒圖或僅為碎片），重新抽取中...")
                continue

            # --- 走到這代表品質合格，開始抓取細節 ---
            obj_url = art_data.get('objectURL')
            
            web_curatorial_desc, web_artwork_details = scrape_met_description(obj_url)
            
            if not web_curatorial_desc and not web_artwork_details:
                print(f"⏭️  第 {attempt} 次抽取沒有發現官方詳細介紹，重新抽取中...")
                continue
                
            print(f"✨ 成功抽到高品質作品！(嘗試次數: {attempt})")
            print(f"🔎 正在同步爬取官網細節: {obj_url}")

            # 建立技術事實上下文 (API 與網頁版混集)
            info_bits = [
                f"API Title: {art_data.get('title')}",
                f"API Date: {art_data.get('objectDate')}",
                f"API Medium: {art_data.get('medium')}",
                f"API Culture: {art_data.get('culture')}",
                f"Website Specs: {web_artwork_details}"
            ]
            api_context = " | ".join([bit for bit in info_bits if "None" not in bit and "N/A" not in bit and bit])

            # 合併大補帖
            final_description_raw = f"【官方詳細敘述】：\n{web_curatorial_desc}\n\n【技術數據碎片】：\n{api_context}"

            return {
                "objectID": str(random_id),
                "title": art_data.get('title', 'Untitled'),
                "date": art_data.get('objectDate', 'Unknown Date'),
                "culture": art_data.get('culture', 'Unknown Culture'),
                "medium": art_data.get('medium', 'Ceramics'),
                "image_url": img_url, 
                "description_raw": final_description_raw,
                "met_url": obj_url,
                "curatorial_department": art_data.get('repository', 'Ceramics')
            }
            
        print("⚠️ 達到重試上限，回傳最後一次抓取結果。")
        return None
        
    except Exception as e:
        print(f"❌ Fetch Error: {e}")
        return None