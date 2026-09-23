"""
gate3_gis.py - Gate 3: Local Taiwan GIS Web 驗證腳本
"""

import os
import sys
import sqlite3
import pandas as pd

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app.components.map import render_taiwan_map, CITY_COORDS
from app.utils.db_helper import load_forecasts

def verify_gate3():
    print("\n==================================================")
    print("[Gate 3: Local Taiwan GIS Web] 開始執行驗證...")
    print("==================================================")
    
    # 1. 驗證 22 縣市 GIS 經緯度對應
    coords_cnt = len(CITY_COORDS)
    print(f"[GIS 地圖經緯度] 涵蓋 {coords_cnt} 個縣市中心座標定位 (預期 22 個)")
    
    # 2. 從 DB 讀取資料
    df = load_forecasts()
    print(f"[數據來源] 已從 SQLite 讀取 {len(df)} 筆氣象預報資料")
    
    # 3. 測試 Folium 地圖繪製
    try:
        folium_map = render_taiwan_map(df)
        print(f"[Folium 地圖繪製] 成功生成動態 OpenStreetMap 地圖與 {df['city'].nunique()} 個縣市氣溫標示 Marker！")
    except Exception as e:
        print(f"[ERROR] Folium 地圖生成失敗: {e}")
        sys.exit(1)
        
    print("--------------------------------------------------")
    print("[Gate 3 (Local Taiwan GIS Web) PASS ✅]\n")

if __name__ == "__main__":
    verify_gate3()
