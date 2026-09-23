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
    """初始化資料庫表格"""
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
                weather TEXT,
                pop INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(city, startTime)
            )
        """)
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
            cursor.execute("""
                INSERT INTO TemperatureForecasts 
                (city, regionGroup, startTime, endTime, dataDate, minT, maxT, weather, pop)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(city, startTime) DO UPDATE SET
                    endTime = excluded.endTime,
                    dataDate = excluded.dataDate,
                    minT = excluded.minT,
                    maxT = excluded.maxT,
                    weather = excluded.weather,
                    pop = excluded.pop,
                    created_at = CURRENT_TIMESTAMP
            """, (
                row["city"], row["regionGroup"], row["startTime"], row["endTime"],
                row["dataDate"], row["minT"], row["maxT"], row["weather"], row["pop"]
            ))
            inserted_count += 1
        conn.commit()
    return inserted_count

def load_forecasts(city: str = None, region_group: str = None) -> pd.DataFrame:
    """
    從 SQLite 資料庫讀取氣象預報資料。
    
    :param city: 可選，過濾特定縣市
    :param region_group: 可選，過濾特定大區域 (北部地區/中部地區...)
    :return: DataFrame
    """
    init_db()
    query = "SELECT city, regionGroup, startTime, endTime, dataDate, minT, maxT, weather, pop, created_at FROM TemperatureForecasts"
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
    return df
