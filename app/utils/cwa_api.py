"""
cwa_api.py - 中央氣象署 (CWA) Open Data API 串接、圖資與資料解析模組
"""

import os
import requests
import pandas as pd
import urllib3

# 停用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def _ensure_env_loaded():
    """確保 .env 檔案中的變數載入至 os.environ"""
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip("'\"")

# 區域分類地圖
REGION_MAP = {
    '臺北市': '北部地區', '新北市': '北部地區', '基隆市': '北部地區', '桃園市': '北部地區',
    '新竹市': '北部地區', '新竹縣': '北部地區', '宜蘭縣': '北部地區',
    '苗栗縣': '中部地區', '臺中市': '中部地區', '彰化縣': '中部地區', '南投縣': '中部地區', '雲林縣': '中部地區',
    '嘉義市': '南部地區', '嘉義縣': '南部地區', '臺南市': '南部地區', '高雄市': '南部地區', '屏東縣': '南部地區',
    '花蓮縣': '東部地區', '臺東縣': '東部地區',
    '澎湖縣': '離島地區', '金門縣': '離島地區', '連江縣': '離島地區'
}

DEFAULT_CWA_KEY = "CWA-223C5412-50E5-418B-89EE-B6C402197BF8"

def get_api_key() -> str:
    """取得授權的 CWA API Key"""
    _ensure_env_loaded()
    key = os.getenv("CWA_API_KEY")
    return key if key else DEFAULT_CWA_KEY

def fetch_weather_forecast(api_key: str = None) -> pd.DataFrame:
    """
    呼叫 CWA F-C0032-001 API 取得全台各縣市預報資料。
    
    :param api_key: CWA API 授權碼，若未傳入則自動從 .env / 環境變數獲取
    :return: 包含縣市、大區域、日期時間、最低溫、最高溫、天氣現象與降雨機率的 DataFrame
    """
    if not api_key:
        api_key = get_api_key()
        
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": api_key,
        "format": "JSON"
    }
    
    try:
        response = requests.get(url, params=params, verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success") == "true":
            raise ValueError(f"CWA API 回傳失敗: {data}")
            
        locations = data.get("records", {}).get("location", [])
        records = []
        
        for loc in locations:
            city_name = loc.get("locationName")
            region_group = REGION_MAP.get(city_name, "其他地區")
            
            elements = {e["elementName"]: e["time"] for e in loc.get("weatherElement", [])}
            
            min_t_times = elements.get("MinT", [])
            max_t_times = elements.get("MaxT", [])
            wx_times = elements.get("Wx", [])
            pop_times = elements.get("PoP", [])
            
            for i in range(len(min_t_times)):
                start_time = min_t_times[i].get("startTime", "")
                end_time = min_t_times[i].get("endTime", "")
                date_str = start_time.split(" ")[0] if " " in start_time else start_time
                
                min_t = float(min_t_times[i]["parameter"]["parameterName"])
                max_t = float(max_t_times[i]["parameter"]["parameterName"]) if i < len(max_t_times) else min_t
                wx_text = wx_times[i]["parameter"]["parameterName"] if i < len(wx_times) else "未知"
                pop_val = pop_times[i]["parameter"]["parameterName"] if i < len(pop_times) else "0"
                
                records.append({
                    "city": city_name,
                    "regionGroup": region_group,
                    "startTime": start_time,
                    "endTime": end_time,
                    "dataDate": date_str,
                    "minT": min_t,
                    "maxT": max_t,
                    "weather": wx_text,
                    "pop": int(pop_val) if pop_val.isdigit() else 0
                })
                
        df = pd.DataFrame(records)
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"[CWA API 錯誤] 連線失敗: {e}")
        raise

def get_cwa_imagery_urls() -> dict:
    """
    提供中央氣象署 (CWA) 官方即時衛星雲圖、雷達迴波圖與日累積雨量圖資連結
    """
    return {
        "satellite_infrared": {
            "title": "東亞紅外線彩色衛星雲圖",
            "url": "https://www.cwa.gov.tw/Data/satellite/LCC_IR1_CR_1024/LCC_IR1_CR_1024.jpg",
            "desc": "即時觀測東亞與台灣上空雲層覆蓋與系統發展狀態"
        },
        "satellite_vis": {
            "title": "台灣區域真實色衛星圖",
            "url": "https://www.cwa.gov.tw/Data/satellite/LCC_VIS_TRGB_1024/LCC_VIS_TRGB_1024.jpg",
            "desc": "高解析度真實色彩衛星雲圖，清晰呈現積雨雲與對流細節"
        },
        "radar_composite": {
            "title": "全台灣雷達迴波合成圖",
            "url": "https://www.cwa.gov.tw/Data/radar/CV1_3600.png",
            "desc": "即時雷達迴波強度，數值越高 (綠/黃/紅) 代表對流雨帶越強烈"
        },
        "rainfall_daily": {
            "title": "今日全台累積雨量分布圖",
            "url": "https://www.cwa.gov.tw/Data/rainfall/QPESUMS_FC.jpg",
            "desc": "中央氣象署 QPESUMS 自動氣象站一日累積雨量即時分析"
        }
    }
