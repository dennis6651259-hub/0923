"""
cwa_api.py - 中央氣象署 (CWA) Open Data API 串接與資料解析模組
"""

import os
import requests
import pandas as pd
import urllib3

# 停用 SSL 警告 (相容部份環境 Certificate 檢驗問題)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

def fetch_weather_forecast(api_key: str = None) -> pd.DataFrame:
    """
    呼叫 CWA F-C0032-001 API 取得全台各縣市預報資料。
    
    :param api_key: CWA API 授權碼，若未傳入則嘗試讀取環境變數 CWA_API_KEY
    :return: 包含縣市、大區域、日期時間、最低溫、最高溫、天氣現象與降雨機率的 DataFrame
    """
    if not api_key:
        api_key = os.getenv("CWA_API_KEY", DEFAULT_CWA_KEY)
        
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
            
            # 以 MinT 的時間點為基準
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
