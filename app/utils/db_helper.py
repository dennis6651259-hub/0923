"""
db_helper.py - SQLite 資料庫操作模組
"""

import os
import sqlite3
import pandas as pd

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
DB_PATH = os.path.normpath(os.path.join(DB_DIR, "data.db"))

def get_connection():
    """取得 SQLite 資料庫連線，若目錄不存在則自動建立"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    """初始化資料庫表格並自動擴充體感溫度欄位"""
    with get_connection() as conn:
        cursor = conn.cursor()
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
                avgT REAL,
                apparentMinT REAL,
                apparentMaxT REAL,
                apparentAvgT REAL,
                tempDiff REAL,
                comfortDesc TEXT,
                weather TEXT,
                pop INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(city, startTime)
            )
        """)
        
        # 動態為舊 SQLite 資料庫擴充新欄位
        existing_cols = [col[1] for col in cursor.execute("PRAGMA table_info(TemperatureForecasts)").fetchall()]
        new_cols = {
            "avgT": "REAL",
            "apparentMinT": "REAL",
            "apparentMaxT": "REAL",
            "apparentAvgT": "REAL",
            "tempDiff": "REAL",
            "comfortDesc": "TEXT"
        }
        for col_name, col_type in new_cols.items():
            if col_name not in existing_cols:
                try:
                    cursor.execute(f"ALTER TABLE TemperatureForecasts ADD COLUMN {col_name} {col_type}")
                except Exception as e:
                    print(f"[DB Notice] Adding column {col_name}: {e}")
        conn.commit()

def save_forecasts(df: pd.DataFrame) -> int:
    """
    將 DataFrame 寫入/更新至 SQLite 資料庫。
    
    :param df: 包含氣象數據的 Pandas DataFrame
    :return: 插入或更新的筆數
    """
    if df.empty:
        return 0
        
    init_db()
    inserted_count = 0
    
    with get_connection() as conn:
        cursor = conn.cursor()
        for _, row in df.iterrows():
            min_t = float(row["minT"])
            max_t = float(row["maxT"])
            avg_t = float(row.get("avgT", round((min_t + max_t) / 2.0, 1)))
            app_min_t = float(row.get("apparentMinT", min_t))
            app_max_t = float(row.get("apparentMaxT", max_t))
            app_avg_t = float(row.get("apparentAvgT", round((app_min_t + app_max_t) / 2.0, 1)))
            temp_diff = float(row.get("tempDiff", round(app_avg_t - avg_t, 1)))
            comfort_desc = str(row.get("comfortDesc", ""))
            
            cursor.execute("""
                INSERT INTO TemperatureForecasts 
                (city, regionGroup, startTime, endTime, dataDate, minT, maxT, avgT, apparentMinT, apparentMaxT, apparentAvgT, tempDiff, comfortDesc, weather, pop)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(city, startTime) DO UPDATE SET
                    endTime = excluded.endTime,
                    dataDate = excluded.dataDate,
                    minT = excluded.minT,
                    maxT = excluded.maxT,
                    avgT = excluded.avgT,
                    apparentMinT = excluded.apparentMinT,
                    apparentMaxT = excluded.apparentMaxT,
                    apparentAvgT = excluded.apparentAvgT,
                    tempDiff = excluded.tempDiff,
                    comfortDesc = excluded.comfortDesc,
                    weather = excluded.weather,
                    pop = excluded.pop,
                    created_at = CURRENT_TIMESTAMP
            """, (
                row["city"], row["regionGroup"], row["startTime"], row["endTime"],
                row["dataDate"], min_t, max_t, avg_t, app_min_t, app_max_t, app_avg_t,
                temp_diff, comfort_desc, row["weather"], row["pop"]
            ))
            inserted_count += 1
        conn.commit()
    return inserted_count

def load_forecasts(city: str = None, region_group: str = None) -> pd.DataFrame:
    """
    從 SQLite 資料庫讀取氣象與體感預報資料。
    
    :param city: 可選，過濾特定縣市
    :param region_group: 可選，過濾特定大區域 (北部地區/中部地區...)
    :return: DataFrame
    """
    init_db()
    query = "SELECT city, regionGroup, startTime, endTime, dataDate, minT, maxT, avgT, apparentMinT, apparentMaxT, apparentAvgT, tempDiff, comfortDesc, weather, pop, created_at FROM TemperatureForecasts"
    conditions = []
    params = []
    
    if city and city != "全部縣市":
        conditions.append("city = ?")
        params.append(city)
        
    if region_group and region_group != "全部地區":
        conditions.append("regionGroup = ?")
        params.append(region_group)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " ORDER BY startTime ASC, city ASC"
    
    with get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=params)
        
    if not df.empty:
        # 若載入之舊資料無體感溫度，自動備援動態計算
        from app.utils.cwa_api import calculate_apparent_temp, get_comfort_description, COASTAL_CITIES
        
        for idx, row in df.iterrows():
            if pd.isna(row.get("apparentMaxT")) or row.get("apparentMaxT") is None or row.get("apparentMaxT") == 0:
                min_t = float(row["minT"])
                max_t = float(row["maxT"])
                pop_val = int(row.get("pop", 0))
                wx_text = str(row.get("weather", ""))
                is_coastal = row["city"] in COASTAL_CITIES
                
                app_min = calculate_apparent_temp(min_t, pop=pop_val, wx_text=wx_text, is_coastal=is_coastal)
                app_max = calculate_apparent_temp(max_t, pop=pop_val, wx_text=wx_text, is_coastal=is_coastal)
                avg_t = round((min_t + max_t) / 2.0, 1)
                app_avg = round((app_min + app_max) / 2.0, 1)
                t_diff = round(app_avg - avg_t, 1)
                
                df.at[idx, "avgT"] = avg_t
                df.at[idx, "apparentMinT"] = app_min
                df.at[idx, "apparentMaxT"] = app_max
                df.at[idx, "apparentAvgT"] = app_avg
                df.at[idx, "tempDiff"] = t_diff
                df.at[idx, "comfortDesc"] = get_comfort_description(t_diff, wx_text)

    return df
