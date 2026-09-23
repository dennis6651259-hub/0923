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

from app.utils.cwa_api import fetch_weather_forecast, get_cwa_imagery_urls, get_api_key
from app.utils.db_helper import save_forecasts, load_forecasts
from app.components.charts import render_temperature_chart
from app.components.map import render_taiwan_map
from streamlit_folium import st_folium

# 頁面配置
st.set_page_config(
    page_title="Taiwan Weather Dashboard 🌤️",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂 CSS 樣式
st.markdown("""
<style>
    /* 全域暗色系背景與漸層 */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-label {
        font-size: 14px;
        color: #94a3b8;
    }
    .header-title {
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.2rem;
    }
    .status-badge {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        padding: 10px 14px;
        border-radius: 8px;
        color: #34d399;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 15px;
    }
    .img-card {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)


def main():
    # 標頭區
    st.markdown('<h1 class="header-title">🌤️ 台灣天氣預報 AI × Data 儀表板</h1>', unsafe_allow_html=True)
    st.markdown("##### 中央氣象署 (CWA) Open Data × SQLite 本地資料庫 × Google Maps 衛星與即時圖資")
    st.markdown("---")

    # 側邊欄配置
    st.sidebar.header("⚙️ 系統狀態與控制")
    
    # 綠色安全連線狀態標籤 (不顯示 API Key 明文)
    st.sidebar.markdown("""
    <div class="status-badge">
        🟢 CWA API 狀態: 已配對 (.env 秘密金鑰)
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🔄 執行爬蟲更新資料庫", use_container_width=True):
        with st.spinner("正從中央氣象署抓取最新預報並寫入 SQLite..."):
            try:
                api_key = get_api_key()
                raw_df = fetch_weather_forecast(api_key=api_key)
                count = save_forecasts(raw_df)
                st.sidebar.success(f"✅ 爬蟲成功！更新 {count} 筆預報資料。")
            except Exception as e:
                st.sidebar.error(f"❌ 爬蟲失敗: {e}")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 數據過濾選單")
    
    # 從 DB 載入資料
    df_all = load_forecasts()
    
    if df_all.empty:
        st.warning("⚠️ 目前 SQLite 資料庫尚無數據，請點擊側邊欄【🔄 執行爬蟲更新資料庫】按鈕！")
        return

    # 選單
    region_options = ["全部地區"] + sorted(list(df_all["regionGroup"].dropna().unique()))
    selected_region = st.sidebar.selectbox("選擇大區域", region_options)
    
    filtered_by_region = df_all if selected_region == "全部地區" else df_all[df_all["regionGroup"] == selected_region]
    city_options = ["全部縣市"] + sorted(list(filtered_by_region["city"].dropna().unique()))
    selected_city = st.sidebar.selectbox("選擇縣市", city_options)

    # 最終篩選資料
    final_df = load_forecasts(
        city=selected_city if selected_city != "全部縣市" else None,
        region_group=selected_region if selected_region != "全部地區" else None
    )

    # 關鍵指標列 (Metrics Row)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        max_temp = final_df["maxT"].max() if not final_df.empty else 0
        st.markdown(f'<div class="metric-card"><div class="metric-label">🔥 全區最高溫</div><div class="metric-value">{max_temp}°C</div></div>', unsafe_allow_html=True)
    with m2:
        min_temp = final_df["minT"].min() if not final_df.empty else 0
        st.markdown(f'<div class="metric-card"><div class="metric-label">❄️ 全區最低溫</div><div class="metric-value">{min_temp}°C</div></div>', unsafe_allow_html=True)
    with m3:
        avg_pop = int(final_df["pop"].mean()) if not final_df.empty and "pop" in final_df else 0
        st.markdown(f'<div class="metric-card"><div class="metric-label">💧 平均降雨機率</div><div class="metric-value">{avg_pop}%</div></div>', unsafe_allow_html=True)
    with m4:
        total_rows = len(final_df)
        st.markdown(f'<div class="metric-card"><div class="metric-label">📊 預報紀錄筆數</div><div class="metric-value">{total_rows}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 主分頁
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 氣溫趨勢圖", 
        "🗺️ 台灣天氣地圖 (Google Maps)", 
        "🛰️ 衛星與雷達觀測", 
        "🗄️ SQLite 數據明細"
    ])

    # Tab 1: 折線圖
    with tab1:
        st.subheader(f"📈 氣溫與降雨趨勢 — [{selected_region} / {selected_city}]")
        fig = render_temperature_chart(final_df, title=f"{selected_region} - {selected_city} 氣溫變化")
        st.plotly_chart(fig, use_container_width=True)

    # Tab 2: Google Maps 風格氣溫地圖
    with tab2:
        col_m1, col_m2 = st.columns([3, 1])
        with col_m1:
            st.subheader("🗺️ 台灣各縣市即時氣溫分布圖 (Google Maps 風格)")
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

    # Tab 3: 衛星與雷達圖觀測
    with tab3:
        st.subheader("🛰️ 中央氣象署 (CWA) 官方即時氣象觀測圖資")
        st.caption("自動串接 CWA 衛星雲圖、雷達迴波合成圖與即時累積雨量圖")
        
        img_dict = get_cwa_imagery_urls()
        
        sub_tab1, sub_tab2, sub_tab3 = st.tabs([
            "📡 衛星雲圖 (Satellite)",
            "🌧️ 雷達迴波圖 (Radar)",
            "☔ 全台累積雨量圖 (Rainfall)"
        ])
        
        cache_bust = datetime.datetime.now().strftime("%Y%m%d%H%M")
        
        with sub_tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"#### 🛰️ {img_dict['satellite_infrared']['title']}")
                st.info(img_dict['satellite_infrared']['desc'])
                st.image(f"{img_dict['satellite_infrared']['url']}?v={cache_bust}", use_container_width=True)
            with col2:
                st.markdown(f"#### 🌍 {img_dict['satellite_vis']['title']}")
                st.info(img_dict['satellite_vis']['desc'])
                st.image(f"{img_dict['satellite_vis']['url']}?v={cache_bust}", use_container_width=True)
                
        with sub_tab2:
            st.markdown(f"#### 🌩️ {img_dict['radar_composite']['title']}")
            st.info(img_dict['radar_composite']['desc'])
            st.image(f"{img_dict['radar_composite']['url']}?v={cache_bust}", use_container_width=True)

        with sub_tab3:
            st.markdown(f"#### 🌧️ {img_dict['rainfall_daily']['title']}")
            st.info(img_dict['rainfall_daily']['desc'])
            st.image(f"{img_dict['rainfall_daily']['url']}?v={cache_bust}", use_container_width=True)

    # Tab 4: SQLite 明細
    with tab4:
        st.subheader("🗄️ SQLite 資料庫即時查詢 (TemperatureForecasts)")
        st.dataframe(final_df, use_container_width=True)
        
        # 下載 CSV 功能
        csv_data = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下載 CSV 資料集",
            data=csv_data,
            file_name="taiwan_weather_forecast.csv",
            mime="text/csv"
        )

    st.markdown("---")
    st.caption("💡 煥哥 AI × Data 24堂課實作專案 | Google Maps 地圖 x 獨立爬蟲 crawler.py x 衛星雷達觀測")

if __name__ == "__main__":
    main()
