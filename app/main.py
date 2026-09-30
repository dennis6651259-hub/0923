"""
main.py - Taiwan Weather Dashboard (Streamlit 主程式)
"""

import sys
import os
import streamlit as st
import pandas as pd
import datetime

# 將專案根目錄加入路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.cwa_api import fetch_weather_forecast, get_api_key, get_cwa_imagery_urls
from app.utils.db_helper import save_forecasts, load_forecasts
from app.components.charts import render_temperature_chart, render_apparent_comparison_chart
from app.components.map import render_taiwan_map
from streamlit_folium import st_folium

# 頁面配置
st.set_page_config(
    page_title="台灣天氣與體感氣溫 AI 儀表板 🌤️",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂高質感 Glassmorphism CSS 視覺系統
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Segoe UI', system-ui, sans-serif;
    }

    /* 全域暗色背景與柔和漸層 */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #1e1b4b 0%, #0f172a 45%, #020617 100%);
        color: #f8fafc;
    }

    /* 頂部炫彩 Title */
    .header-container {
        padding: 10px 0 20px 0;
        margin-bottom: 10px;
    }
    .header-title {
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.3rem;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
        font-family: 'Outfit', sans-serif;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 0.98rem;
        font-weight: 500;
    }

    /* 玻璃擬態 Card 樣式 */
    .glass-card {
        background: rgba(30, 41, 59, 0.55);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.35);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
    }
    .glass-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
        transform: translateY(-3px);
        box-shadow: 0 14px 35px -5px rgba(56, 189, 248, 0.15);
    }

    /* Metrics 指標欄位 */
    .metric-title {
        font-size: 0.88rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .metric-primary {
        font-size: 1.85rem;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 0.82rem;
        margin-top: 6px;
        color: #cbd5e1;
        font-weight: 500;
    }

    /* 狀態 Accent Badge */
    .status-badge {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.25));
        border: 1px solid rgba(52, 211, 153, 0.4);
        padding: 10px 14px;
        border-radius: 12px;
        color: #34d399;
        font-weight: 600;
        font-size: 0.88rem;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* 洞察 Alert Card */
    .insight-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
        border-left: 4px solid #38bdf8;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 20px;
        font-size: 0.92rem;
        color: #e2e8f0;
    }

    /* 圖片 Card */
    .img-box {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 12px;
        text-align: center;
    }
    .img-box img {
        border-radius: 8px;
        max-width: 100%;
    }

    /* Streamlit Tab 樣式客製化 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.4);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 18px;
        font-weight: 600;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
    }
</style>
""", unsafe_allow_html=True)


def main():
    # 頂部 Title 區
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🌤️ 台灣氣候 AI × Data 視覺化儀表板</div>
        <div class="header-subtitle">中央氣象署 (CWA) Open Data × 體感溫度 (Apparent Temp) 演算法 × Google Maps 衛星圖資</div>
    </div>
    """, unsafe_allow_html=True)

    # 側邊欄配置
    st.sidebar.markdown("### ⚙️ 系統控制台")
    
    st.sidebar.markdown("""
    <div class="status-badge">
        🟢 CWA API 狀態: 已連線 (.env)
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🔄 執行爬蟲更新氣象資料庫", use_container_width=True):
        with st.spinner("正從中央氣象署抓取最新預報並計算體感數據..."):
            try:
                api_key = get_api_key()
                raw_df = fetch_weather_forecast(api_key=api_key)
                count = save_forecasts(raw_df)
                st.sidebar.success(f"✅ 爬蟲成功！更新 {count} 筆預報與體感資料。")
            except Exception as e:
                st.sidebar.error(f"❌ 爬蟲失敗: {e}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 數據過濾器")
    
    # 載入 DB 資料
    df_all = load_forecasts()
    
    if df_all.empty:
        st.warning("⚠️ 目前 SQLite 資料庫尚無數據，請點擊側邊欄【🔄 執行爬蟲更新氣象資料庫】按鈕！")
        return

    # 區域與縣市過濾
    region_options = ["全部地區"] + sorted(list(df_all["regionGroup"].dropna().unique()))
    selected_region = st.sidebar.selectbox("選擇大區域", region_options)
    
    filtered_by_region = df_all if selected_region == "全部地區" else df_all[df_all["regionGroup"] == selected_region]
    city_options = ["全部縣市"] + sorted(list(filtered_by_region["city"].dropna().unique()))
    selected_city = st.sidebar.selectbox("選擇縣市", city_options)

    # 最終篩選數據
    final_df = load_forecasts(
        city=selected_city if selected_city != "全部縣市" else None,
        region_group=selected_region if selected_region != "全部地區" else None
    )

    # 關鍵指標列 (Metrics Row - 包含實際溫度與體感溫度對比)
    c1, c2, c3, c4 = st.columns(4)
    
    if not final_df.empty:
        # 最高實際與體感溫
        max_t_row = final_df.loc[final_df["maxT"].idxmax()]
        max_temp = max_t_row["maxT"]
        max_app = max_t_row.get("apparentMaxT", max_temp)
        max_city = max_t_row["city"]
        
        # 最低實際與體感溫
        min_t_row = final_df.loc[final_df["minT"].idxmin()]
        min_temp = min_t_row["minT"]
        min_app = min_t_row.get("apparentMinT", min_temp)
        min_city = min_t_row["city"]

        # 最大體感溫差
        diff_row = final_df.loc[final_df["tempDiff"].idxmax()] if "tempDiff" in final_df.columns else max_t_row
        max_diff = diff_row.get("tempDiff", 0.0)
        diff_city = diff_row["city"]
        diff_desc = diff_row.get("comfortDesc", "")

        avg_pop = int(final_df["pop"].mean()) if "pop" in final_df.columns else 0
    else:
        max_temp = max_app = min_temp = min_app = max_diff = avg_pop = 0
        max_city = min_city = diff_city = diff_desc = "-"

    with c1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">🔥 區域最高氣溫 vs 體感</div>
            <div class="metric-primary" style="color: #f43f5e;">{max_temp}°C</div>
            <div class="metric-sub">🧍 體感高溫: <strong style="color: #fb923c;">{max_app}°C</strong> ({max_city})</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">❄️ 區域最低氣溫 vs 體感</div>
            <div class="metric-primary" style="color: #38bdf8;">{min_temp}°C</div>
            <div class="metric-sub">🧍 體感低溫: <strong style="color: #7dd3fc;">{min_app}°C</strong> ({min_city})</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">⚡ 最大體感與實際溫差</div>
            <div class="metric-primary" style="color: #a855f7;">+{max_diff}°C</div>
            <div class="metric-sub">📍 {diff_city} — {diff_desc[:12]}...</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">💧 平均降雨機率</div>
            <div class="metric-primary" style="color: #34d399;">{avg_pop}%</div>
            <div class="metric-sub">📊 資料筆數: <strong>{len(final_df)}</strong> 筆紀錄</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 體感與氣候速報 Insight Banner
    st.markdown(f"""
    <div class="insight-card">
        <strong>💡 氣候體感洞察：</strong> 當前選取區域 [{selected_region} / {selected_city}] 之中，
        <strong>{diff_city}</strong> 受到空氣濕度與風速綜合效應影響，體感溫度與實際實測溫差最大（高出 <strong>+{max_diff}°C</strong>）。
        在外活動請參考體感溫度做穿著調配！
    </div>
    """, unsafe_allow_html=True)

    # 主分頁頁籤
    tab1, tab2, tab3 = st.tabs([
        "📈 實際與體感溫度對比圖", 
        "🗺️ 台灣即時天氣與體感地圖", 
        "🗄️ SQLite 資料庫明細"
    ])

    # Tab 1: 折線圖與溫差分析
    with tab1:
        st.subheader(f"📈 實際溫度 vs 體感溫度趨勢分析 — [{selected_region} / {selected_city}]")
        show_app_toggle = st.toggle("顯示體感溫度曲線 (Apparent Temp)", value=True)
        
        fig1 = render_temperature_chart(final_df, title=f"{selected_region} - {selected_city}", show_apparent=show_app_toggle)
        st.plotly_chart(fig1, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🔥 各縣市體感與實際溫差排行 (溫差愈大代表高濕悶熱或風寒效應顯著)")
        fig2 = render_apparent_comparison_chart(final_df)
        st.plotly_chart(fig2, use_container_width=True)

    # Tab 2: Google Maps 風格地圖
    with tab2:
        col_m1, col_m2 = st.columns([3, 1])
        with col_m1:
            st.subheader("🗺️ 台灣各縣市即時氣溫與體感分布圖 (Google Maps 風格)")
        with col_m2:
            map_style = st.selectbox(
                "地圖底圖風格",
                ["Google Roadmap", "Google Hybrid", "Google Terrain", "OpenStreetMap"],
                format_func=lambda x: {
                    "Google Roadmap": "🗺️ Google Maps (標準街道)",
                    "Google Hybrid": "🛰️ Google Maps (衛星混合)",
                    "Google Terrain": "🏔️ Google Maps (地形圖)",
                    "OpenStreetMap": "🌐 OpenStreetMap (經典)"
                }.get(x, x)
            )
        map_obj = render_taiwan_map(final_df, style_key=map_style)
        st_folium(map_obj, width=1100, height=540)

    # Tab 3: SQLite 明細與下載
    with tab3:
        st.subheader("🗄️ SQLite 資料庫即時查詢 (TemperatureForecasts 表格)")
        st.markdown("包含：實際最低溫 (minT)、實際最高溫 (maxT)、平均溫 (avgT)、體感最低溫 (apparentMinT)、體感最高溫 (apparentMaxT)、體感溫差 (tempDiff) 與體感提示 (comfortDesc)")
        st.dataframe(final_df, use_container_width=True)
        
        csv_data = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下載全台氣候與體感 CSV 資料集",
            data=csv_data,
            file_name="taiwan_weather_apparent_temp.csv",
            mime="text/csv"
        )

    st.markdown("---")
    st.caption("💡 煥哥 AI × Data 24堂課實作專案 | Google Maps 地圖 x 獨立爬蟲 crawler.py x SQLite 資料庫 x 體感溫度 (Apparent Temp) 比較")

if __name__ == "__main__":
    main()

