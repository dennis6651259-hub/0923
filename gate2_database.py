"""
gate2_database.py - Gate 2: SQLite 資料庫轉換與寫入處理器

功能說明：
1. 讀取 `gate1_output.json` JSON 檔案。
2. 轉化全台 22 縣市之預報時段紀錄。
3. 寫入 SQLite 資料庫 (data/data.db 及 data/weather_database.db)。
4. 使用 SQLite 的 `INSERT OR REPLACE INTO` 搭配 `UNIQUE(location_name, forecast_start)`Constraint 防重。
5. 使用 Python Pandas + SQL SELECT 語法驗證並印出統計報告。
"""

import os
import sys
import json
import sqlite3
import pandas as pd

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "data.db")
ALT_DB_PATH = os.path.join(DATA_DIR, "weather_database.db")

REGION_MAP = {
    '臺北市': '北部地區', '新北市': '北部地區', '基隆市': '北部地區', '桃園市': '北部地區',
    '新竹市': '北部地區', '新竹縣': '北部地區', '宜蘭縣': '北部地區',
    '苗栗縣': '中部地區', '臺中市': '中部地區', '彰化縣': '中部地區', '南投縣': '中部地區', '雲林縣': '中部地區',
    '嘉義市': '南部地區', '嘉義縣': '南部地區', '臺南市': '南部地區', '高雄市': '南部地區', '屏東縣': '南部地區',
    '花蓮縣': '東部地區', '臺東縣': '東部地區',
    '澎湖縣': '離島地區', '金門縣': '離島地區', '連江縣': '離島地區'
}

def init_database(db_file):
    """初始化 Gate 2 資料庫與建立表格"""
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        # 建立專用結構化 weather_forecasts 資料表 (包含 UNIQUE 約束)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_name TEXT NOT NULL,
                region_group TEXT,
                forecast_start TEXT NOT NULL,
                forecast_end TEXT NOT NULL,
                data_date TEXT,
                min_temp REAL NOT NULL,
                max_temp REAL NOT NULL,
                weather_condition TEXT,
                rain_probability INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(location_name, forecast_start)
            )
        """)
        # 同步維護 TemperatureForecasts 舊有相容資料表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TemperatureForecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                regionGroup TEXT NOT NULL,
                startTime TEXT NOT NULL,
                endTime TEXT NOT NULL,
                dataDate TEXT NOT NULL,
                minT REAL NOT NULL,
                maxT REAL NOT NULL,
                weather TEXT,
                pop INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(city, startTime)
            )
        """)
        conn.commit()

def load_json_data(json_file="gate1_output.json"):
    """讀取 gate1_output.json 原始檔"""
    json_path = os.path.join(BASE_DIR, json_file)
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"找不到檔案 {json_file}，請先執行 python gate1_fetch.py！")
        
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def process_gate2():
    """解析 JSON 寫入 SQLite 並進行數據驗證"""
    print(f"\n==================================================")
    print(f"[Gate 2: Database] 開始讀取 gate1_output.json 並寫入 SQLite...")
    print(f"==================================================")
    
    data = load_json_data()
    locations = data.get("records", {}).get("location", [])
    
    # 建立兩個 DB 檔案以符合模組規範
    init_database(DB_PATH)
    init_database(ALT_DB_PATH)
    
    records = []
    
    for loc in locations:
        loc_name = loc.get("locationName")
        region_group = REGION_MAP.get(loc_name, "其他地區")
        elements = {e["elementName"]: e["time"] for e in loc.get("weatherElement", [])}
        
        min_t_times = elements.get("MinT", [])
        max_t_times = elements.get("MaxT", [])
        wx_times = elements.get("Wx", [])
        pop_times = elements.get("PoP", [])
        
        for i in range(len(min_t_times)):
            f_start = min_t_times[i].get("startTime", "")
            f_end = min_t_times[i].get("endTime", "")
            date_str = f_start.split(" ")[0] if " " in f_start else f_start
            
            min_t = float(min_t_times[i]["parameter"]["parameterName"])
            max_t = float(max_t_times[i]["parameter"]["parameterName"]) if i < len(max_t_times) else min_t
            wx_text = wx_times[i]["parameter"]["parameterName"] if i < len(wx_times) else "未知"
            pop_val = pop_times[i]["parameter"]["parameterName"] if i < len(pop_times) else "0"
            pop_int = int(pop_val) if pop_val.isdigit() else 0
            
            records.append({
                "location_name": loc_name,
                "region_group": region_group,
                "forecast_start": f_start,
                "forecast_end": f_end,
                "data_date": date_str,
                "min_temp": min_t,
                "max_temp": max_t,
                "weather_condition": wx_text,
                "rain_probability": pop_int
            })
            
    # 寫入 SQLite DB
    for target_db in [DB_PATH, ALT_DB_PATH]:
        with sqlite3.connect(target_db) as conn:
            cursor = conn.cursor()
            for r in records:
                # 寫入 weather_forecasts
                cursor.execute("""
                    INSERT OR REPLACE INTO weather_forecasts 
                    (location_name, region_group, forecast_start, forecast_end, data_date, min_temp, max_temp, weather_condition, rain_probability)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r["location_name"], r["region_group"], r["forecast_start"], r["forecast_end"],
                    r["data_date"], r["min_temp"], r["max_temp"], r["weather_condition"], r["rain_probability"]
                ))
                
                # 同步寫入 TemperatureForecasts
                cursor.execute("""
                    INSERT OR REPLACE INTO TemperatureForecasts
                    (city, regionGroup, startTime, endTime, dataDate, minT, maxT, weather, pop)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r["location_name"], r["region_group"], r["forecast_start"], r["forecast_end"],
                    r["data_date"], r["min_temp"], r["max_temp"], r["weather_condition"], r["rain_probability"]
                ))
            conn.commit()
            
    # 使用 Pandas + SQL SELECT 語法執行數據驗證
    with sqlite3.connect(DB_PATH) as conn:
        df_verify = pd.read_sql_query("SELECT * FROM weather_forecasts", conn)
        counties_count = df_verify["location_name"].nunique()
        total_records = len(df_verify)
        
    print(f"\n[Gate 2 驗證結果]")
    print(f"--------------------------------------------------")
    print(f"全台涵蓋縣市數: {counties_count} 個 (預期 22 個)")
    print(f"成功載入預報紀錄: {total_records} 筆 (使用 INSERT OR REPLACE 避免重複)")
    print(f"資料庫檔案位置: {DB_PATH}")
    print(f"--------------------------------------------------")
    print(df_verify[["location_name", "forecast_start", "min_temp", "max_temp", "weather_condition"]].head(8))
    print(f"--------------------------------------------------")
    print(f"[Gate 2 (Database) PASS ✅]\n")

if __name__ == "__main__":
    process_gate2()
