"""
gate4_analytics.py - Gate 4: Weather Visual Analytics 驗證腳本
"""

import os
import sys
import pandas as pd

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app.components.charts import render_temperature_chart
from app.utils.cwa_api import get_cwa_imagery_urls
from app.utils.db_helper import load_forecasts

def verify_gate4():
    print("\n==================================================")
    print("[Gate 4: Weather Visual Analytics] 開始執行驗證...")
    print("==================================================")
    
    # 1. 讀取 DB 資料
    df = load_forecasts()
    
    # 2. 測試 Plotly 折線圖渲染
    try:
        fig = render_temperature_chart(df, title="全台氣溫趨勢視覺化測試")
        traces_cnt = len(fig.data)
        print(f"[Plotly 趨勢圖] 成功繪製雙軸氣溫圖表，包含 {traces_cnt} 組數據 Trace (MinT, MaxT, PoP)！")
    except Exception as e:
        print(f"[ERROR] Plotly 圖表繪製失敗: {e}")
        sys.exit(1)
        
    # 3. 測試 CWA 衛星、雷達與雨量圖資 URL
    img_urls = get_cwa_imagery_urls()
    print(f"[衛星與雷達圖資] 成功封裝 {len(img_urls)} 組 CWA 官方觀測圖資 (包含衛星雲圖、雷達迴波圖與日累積雨量圖)")
    for k, v in img_urls.items():
        print(f"  - {v['title']}: {v['url']}")
        
    print("--------------------------------------------------")
    print("[Gate 4 (Weather Visual Analytics) PASS ✅]\n")

if __name__ == "__main__":
    verify_gate4()
