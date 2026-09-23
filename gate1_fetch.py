"""
gate1_fetch.py - Gate 1: 氣象署 Open Data API 資料抓取器
"""

import os
import sys
import json
import urllib3
import requests

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 停用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_env_key():
    """載入 .env 檔案中的 CWA_API_KEY"""
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip("'\"")
    return os.getenv("CWA_API_KEY", "CWA-223C5412-50E5-418B-89EE-B6C402197BF8")

def fetch_and_save_gate1(output_filename="gate1_output.json"):
    """從 CWA 抓取氣象 JSON 並存入檔案"""
    api_key = load_env_key()
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {"Authorization": api_key, "format": "JSON"}
    
    print(f"[Gate 1] 正在連線 CWA API 抓取天氣數據...")
    resp = requests.get(url, params=params, verify=False, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    
    output_path = os.path.join(BASE_DIR, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    locations_cnt = len(data.get("records", {}).get("location", []))
    print(f"[Gate 1 PASS] 成功抓取全台 {locations_cnt} 縣市氣象資料，已寫入 {output_filename}")
    return output_path

if __name__ == "__main__":
    fetch_and_save_gate1()
