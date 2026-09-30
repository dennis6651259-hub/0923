"""
map.py - Google Maps 風格與即時氣溫/天氣標章 Folium 地圖視覺化模組
"""

import folium
import pandas as pd

# 各縣市中心經緯度
CITY_COORDS = {
    '臺北市': (25.0330, 121.5654), '新北市': (24.9157, 121.6739), '基隆市': (25.1283, 121.7419),
    '桃園市': (24.9936, 121.3010), '新竹市': (24.8138, 120.9675), '新竹縣': (24.8383, 121.0177),
    '苗栗縣': (24.5602, 120.8214), '臺中市': (24.1477, 120.6736), '彰化縣': (24.0518, 120.5161),
    '南投縣': (23.9609, 120.9719), '雲林縣': (23.7092, 120.4313), '嘉義市': (23.4800, 120.4491),
    '嘉義縣': (23.4588, 120.5740), '臺南市': (22.9997, 120.2270), '高雄市': (22.6273, 120.3014),
    '屏東縣': (22.5519, 120.5487), '宜蘭縣': (24.7570, 121.7530), '花蓮縣': (23.9872, 121.6015),
    '臺東縣': (22.7613, 121.1444), '澎湖縣': (23.5711, 119.5793), '金門縣': (24.4493, 118.3766),
    '連江縣': (26.1505, 119.9499)
}

# Google Maps 地圖 Tiles 連結設定
GOOGLE_TILES = {
    "Google Roadmap": {
        "url": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        "name": "Google Maps (標準街道圖)",
        "attr": "Google Maps"
    },
    "Google Hybrid": {
        "url": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        "name": "Google Maps (衛星混合圖)",
        "attr": "Google Maps Hybrid"
    },
    "Google Terrain": {
        "url": "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
        "name": "Google Maps (地形圖)",
        "attr": "Google Maps Terrain"
    }
}

def get_weather_icon(wx_text: str) -> str:
    """根據天氣狀況文字回傳氣象 Emoji"""
    if "晴" in wx_text and "多雲" not in wx_text:
        return "☀️"
    elif "晴" in wx_text and "多雲" in wx_text:
        return "⛅"
    elif "多雲" in wx_text or "陰" in wx_text:
        return "☁️"
    elif "雷" in wx_text:
        return "🌩️"
    elif "雨" in wx_text:
        return "🌧️"
    return "🌤️"

def get_badge_bg(temp: float) -> str:
    """根據最高氣溫回傳漸層背景色"""
    if temp < 18:
        return "linear-gradient(135deg, #0284c7, #0369a1)"
    elif temp < 24:
        return "linear-gradient(135deg, #10b981, #047857)"
    elif temp < 29:
        return "linear-gradient(135deg, #f59e0b, #d97706)"
    else:
        return "linear-gradient(135deg, #ef4444, #b91c1c)"

def render_taiwan_map(df: pd.DataFrame, style_key: str = "Google Roadmap", **kwargs) -> folium.Map:
    """
    創建全台即時氣溫與天氣動態標章 Folium 地圖 (Google Maps 風格)。
    
    :param df: 包含氣溫與天氣的 DataFrame
    :param style_key: 地圖風格 ('Google Roadmap', 'Google Hybrid', 'Google Terrain', 'OpenStreetMap')
    """
    if "map_style" in kwargs:
        style_key = kwargs["map_style"]
    elif "style_name" in kwargs:
        style_key = kwargs["style_name"]

    # 預設以台灣中心點建構 Folium 地圖
    m = folium.Map(location=[23.7, 120.95], zoom_start=7.5, tiles=None)
    
    # 1. 建立預設 Google Maps 圖層
    tile_info = GOOGLE_TILES.get(style_key, GOOGLE_TILES["Google Roadmap"])
    
    folium.TileLayer(
        tiles=tile_info["url"],
        attr=tile_info["attr"],
        name=tile_info["name"],
        overlay=False,
        control=True
    ).add_to(m)
    
    # 2. 加入其他 Google Maps 與 OpenStreetMap 圖層供隨時切換
    for k, v in GOOGLE_TILES.items():
        if k != style_key:
            folium.TileLayer(
                tiles=v["url"],
                attr=v["attr"],
                name=v["name"],
                overlay=False,
                control=True
            ).add_to(m)
            
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="OpenStreetMap (經典街道)",
        overlay=False,
        control=True
    ).add_to(m)

    if not df.empty:
        # 取最新一個時間區段之縣市數據
        latest_df = df.groupby("city").first().reset_index()
        
        for _, row in latest_df.iterrows():
            city = row["city"]
            min_t = row["minT"]
            max_t = row["maxT"]
            app_min = row.get("apparentMinT", min_t)
            app_max = row.get("apparentMaxT", max_t)
            temp_diff = row.get("tempDiff", 0.0)
            comfort_desc = row.get("comfortDesc", "")
            wx = row.get("weather", "")
            pop = row.get("pop", 0)
            
            coords = CITY_COORDS.get(city)
            if not coords:
                continue
                
            wx_icon = get_weather_icon(wx)
            badge_bg = get_badge_bg(max_t)
            
            # 溫差標籤顏色
            diff_str = f"+{temp_diff}°C" if temp_diff > 0 else f"{temp_diff}°C"
            diff_color = "#f87171" if temp_diff >= 2.0 else "#34d399" if temp_diff >= -1.0 else "#60a5fa"
            
            # HTML 即時氣溫與體感溫度標章 (DivIcon)
            icon_html = f"""
            <div style="
                background: {badge_bg};
                border: 2px solid #ffffff;
                border-radius: 20px;
                padding: 4px 10px;
                color: #ffffff;
                font-weight: 700;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                white-space: nowrap;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45);
                display: inline-flex;
                align-items: center;
                gap: 6px;
                text-shadow: 0 1px 2px rgba(0,0,0,0.5);
            ">
                <span style="font-size: 15px;">{wx_icon}</span>
                <span style="font-size: 14px;">{int(max_t)}°C</span>
                <span style="font-size: 11px; background: rgba(0,0,0,0.25); padding: 1px 5px; border-radius: 8px;">體感 {int(app_max)}°</span>
            </div>
            """
            
            popup_html = f"""
            <div style="font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; width: 220px; color: #0f172a; padding: 6px;">
                <h4 style="margin: 0 0 6px 0; color: #1d4ed8; font-weight: 700; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px;">📍 {city} Weather</h4>
                <div style="margin-bottom: 5px;"><b>{wx_icon} 天氣狀況:</b> {wx}</div>
                <div style="margin-bottom: 5px;"><b>🌡️ 實際氣溫:</b> <span style="color:#2563eb; font-weight:bold;">{min_t}°C</span> ~ <span style="color:#dc2626; font-weight:bold;">{max_t}°C</span></div>
                <div style="margin-bottom: 5px;"><b>🧍 體感氣溫:</b> <span style="color:#0284c7; font-weight:bold;">{app_min}°C</span> ~ <span style="color:#ea580c; font-weight:bold;">{app_max}°C</span></div>
                <div style="margin-bottom: 5px;"><b>🔥 體感溫差:</b> <span style="color:{diff_color}; font-weight:bold;">{diff_str}</span></div>
                <div style="margin-bottom: 5px; font-size: 11px; color: #475569;"><b>🏷️ 舒適體感:</b> {comfort_desc}</div>
                <div><b>💧 降雨機率:</b> <span style="color:#0284c7; font-weight:bold;">{pop}%</span></div>
            </div>
            """
            
            # 建立 Marker
            folium.Marker(
                location=coords,
                icon=folium.DivIcon(
                    html=icon_html,
                    icon_size=(135, 38),
                    icon_anchor=(67, 19)
                ),
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"📍 {city}: 實際 {max_t}°C | 體感 {app_max}°C ({comfort_desc})"
            ).add_to(m)
            
    # 加入右上方圖層切換選單 (LayerControl)
    folium.LayerControl(position="topright").add_to(m)
    
    return m
