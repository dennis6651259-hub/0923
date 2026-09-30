"""
crawler.py - 每日天氣數據自動爬蟲腳本

說明：
本腳本為獨立運行的爬蟲程式，可搭配 Cron / Windows 工作排程器每日自動執行。
自動讀取同目錄下的 .env 檔案中的 CWA_API_KEY，向中央氣象署 (CWA) 抓取最新全台氣象預報，
並清洗結構化後儲存/更新至 SQLite 資料庫 (data/data.db)。
"""

import os
import sys
import datetime

# 將專案根目錄加入 Python 搜尋路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# 解決 Windows console UTF-8 輸出編碼問題
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def load_env_file(env_path: str = None):
    """手動解析 .env 檔案以載入環境變數"""
    if env_path is None:
        env_path = os.path.join(BASE_DIR, ".env")
        
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    os.environ[key] = val
        print(f"[INFO] 已成功載入環境變數檔案: {env_path}")
    else:
        print(f"[WARN] 未找到 .env 檔案，將使用預設或系統環境變數")

from app.utils.cwa_api import fetch_weather_forecast
from app.utils.db_helper import save_forecasts, load_forecasts

def run_daily_crawler():
    """執行每日氣象數據爬蟲全流程"""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n==================================================")
    print(f"[CWA 氣象爬蟲啟動] 時間: {now_str}")
    print(f"==================================================")
    
    # 1. 載入 .env 設定
    load_env_file()
    
    api_key = os.getenv("CWA_API_KEY")
    if not api_key:
        print("[ERROR] 錯誤：未找到 CWA_API_KEY！請在 .env 中設定。")
        sys.exit(1)
        
    print(f"[INFO] 正在連線中央氣象署 Open Data API (F-C0032-001)...")
    
    # 2. 爬取最新氣象預報
    try:
        df = fetch_weather_forecast(api_key=api_key)
        print(f"[SUCCESS] 氣象資料抓取成功！共取得 {len(df)} 筆全台縣市預報紀錄。")
    except Exception as e:
        print(f"[ERROR] 氣象 API 抓取失敗: {e}")
        sys.exit(1)
        
    # 3. 儲存/更新至 SQLite 資料庫
    try:
        updated_count = save_forecasts(df)
        print(f"[SUCCESS] 成功更新/寫入 {updated_count} 筆氣象資料至 SQLite (data/data.db)！")
    except Exception as e:
        print(f"[ERROR] SQLite 資料庫寫入失敗: {e}")
        sys.exit(1)
        
    # 4. 驗證 SQLite 當前累積紀錄
    try:
        total_records = len(load_forecasts())
        print(f"[INFO] 目前 SQLite 資料庫中共有 {total_records} 筆預報歷史數據。")
    except Exception as e:
        print(f"[WARN] 查詢 DB 統計時發生警告: {e}")
        
    print(f"==================================================")
    print(f"[CWA 氣象爬蟲完成] 成功結束於 {datetime.datetime.now().strftime('%H:%M:%S')}")
    print(f"==================================================\n")

if __name__ == "__main__":
    run_daily_crawler()
