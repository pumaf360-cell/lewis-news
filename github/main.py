import os
import sys
import warnings
import requests
from dotenv import load_dotenv

load_dotenv()

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

warnings.filterwarnings("ignore")

from tavily import TavilyClient
from google import genai
from apify_client import ApifyClient

# ==========================================
# 第一性原理思考：系統進化
# 1. 輸入：使用 Tavily AI Search / Apify 
# 2. 處理：使用 Google Gemini 2.5
# 3. 輸出：發送 Telegram / LINE Messaging API 到個人裝置
# ==========================================

def search_with_tavily(keyword, api_key):
    if not api_key:
        return "[錯誤] 缺少 Tavily API Key。"
    
    print(f"[系統] 🔍 正在啟動 Tavily 搜尋「{keyword}」的情報...")
    client = TavilyClient(api_key=api_key)
    try:
        response = client.search(query=keyword, search_depth="advanced", topic="news", max_results=5)
        news_list = []
        for result in response.get("results", []):
            news_list.append(f"標題: {result['title']}\n內容: {result['content']}\n")
        return news_list
    except Exception as e:
        print(f"[錯誤] Tavily 搜尋失敗: {e}")
        return []

def check_apify_engine(api_key):
    if not api_key:
        return ""
    return "[系統] 🕷️ Apify 引擎已掛載！具備突破動態網頁的潛力。"

def analyze_with_gemini(news_list, api_key):
    if not api_key:
        return "[錯誤] 缺少 Gemini API Key。"
        
    print("[系統] 🧠 正在將情報交給 Gemini AI 進行深度分析...")
    client = genai.Client(api_key=api_key)
    news_text = "\n".join(news_list)
    prompt = f"""
    你是一位專業的 F1 數據分析師。請根據以下搜集到的關於 Lewis Hamilton 的最新新聞，產生結構化的簡報。
    
    【分析要求】：
    1. 輿情情緒：給予 1~10 的熱度評分，並簡述情緒（正向/負向/中立/熱烈）。
    2. 近期動態：他最近在做什麼？轉會進度、賽道表現等。
    3. 重點摘要：用 3 個條列式重點總結。

    請一律使用「繁體中文」回答，排版乾淨。
    【Tavily 新聞內容】：
    {news_text}
    """
    try:
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text
    except Exception as e:
        return f"[錯誤] Gemini 分析過程中發生錯誤: {e}"

def send_telegram_message(message, bot_token, chat_id):
    if not bot_token or not chat_id or "獲取" in bot_token or "請填入" in bot_token:
        return "[系統] ⚠️ 尚未設定好 Telegram 金鑰與 Chat ID，跳過手機推播。"

    print("[系統] 🚀 正在把這份熱騰騰的報告發送到你的 Telegram 手機裡...")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return "[系統] ✅ Telegram 推播成功！"
        else:
            return f"[錯誤] Telegram 推播失敗: {response.text}"
    except Exception as e:
        return f"[錯誤] Telegram 網路連線發生問題: {e}"

def send_line_messaging_api(message, channel_token, user_id):
    """
    擴充模組：發送 LINE Messaging API 推播
    取代已被官方淘汰的 LINE Notify，改走正統 API 架構。
    """
    if not channel_token or not user_id or "請填入" in channel_token:
        return "[系統] ⚠️ 尚未配置 LINE Messaging API 金鑰，跳過 LINE 推播。"
        
    print("[系統] 🟢 正在透過 LINE 官方機器人發送報告到你的 APP 裡...")
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_token}"
    }
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": f"🏎️ **Lewis Hamilton 每日 AI 情報包**\n\n{message}"
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return "[系統] ✅ LINE Messaging API 推播成功！快去看 LINE！"
        else:
            return f"[錯誤] LINE 推播失敗，伺服器回答: {response.status_code} - {response.text}"
    except Exception as e:
        return f"[錯誤] LINE 網路連線發生問題: {e}"

if __name__ == "__main__":
    TARGET_KEYWORD = "Lewis Hamilton F1 recent news OR transfer Ferrari"
    
    TAVILY_KEY = os.getenv("TAVILY_API_KEY")
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    APIFY_KEY = os.getenv("APIFY_API_TOKEN") 
    
    TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    LINE_USER = os.getenv("LINE_USER_ID")
    
    if apify_msg := check_apify_engine(APIFY_KEY):
        print(apify_msg)
        
    news = search_with_tavily(TARGET_KEYWORD, TAVILY_KEY)
    
    if not news:
        print("[系統] ❌ 找不到資料或搜尋失敗。")
    else:
        report = analyze_with_gemini(news, GEMINI_KEY)
        print("\n" + "="*40 + " 自動化分析報告 " + "="*40)
        print(report)
        print("="*96 + "\n")
        
        # 啟動推播 (雙管齊下)
        print(send_telegram_message(report, TG_TOKEN, TG_CHAT_ID))
        print(send_line_messaging_api(report, LINE_TOKEN, LINE_USER))
