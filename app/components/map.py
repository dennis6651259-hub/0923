"""
map.py - Google Maps 風格 Folium 地圖視覺化模組
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

def get_temp_color(temp: float) -> str:
    """根據溫度傳回顏色碼"""
    if temp < 18:
        return "blue"
    elif temp < 24:
        return "green"
    elif temp < 28:
        return "orange"
    else:
        return "red"

def render_taiwan_map(df: pd.DataFrame, style_key: str = "Google Roadmap") -> folium.Map:
    """
    創建 Google Maps 風格的全台氣溫分佈 Folium 地圖。
    
    :param df: 包含氣溫的 DataFrame
    :param style_key: 地圖風格 ('Google Roadmap', 'Google Hybrid', 'Google Terrain', 'OpenStreetMap')
    """
    # 預設以台灣中心點建構 Folium 地圖
    m = folium.Map(location=[23.7, 120.95], zoom_start=7, tiles=None)
    
    # 1. 建立預設 Google Maps 圖層
    tile_info = GOOGLE_TILES.get(style_key, GOOGLE_TILES["Google Roadmap"])
    
    folium.TileLayer(
        tiles=tile_info["url"],
        attr=tile_info["attr"],
        name=tile_info["name"],
        overlay=False,
        control=True
    ).add_to(m)
    
    # 2. 加入其他 Google Maps 與 OpenStreetMap 圖層供使用者在右上方隨時切換
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
        # 取最新一個時間區段或以縣市為單位
        latest_df = df.groupby("city").first().reset_index()
        
        for _, row in latest_df.iterrows():
            city = row["city"]
            min_t = row["minT"]
            max_t = row["maxT"]
            wx = row.get("weather", "")
            pop = row.get("pop", 0)
            
            coords = CITY_COORDS.get(city)
            if not coords:
                continue
                
            color = get_temp_color(max_t)
            
            popup_html = f"""
            <div style="font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; width: 170px; color: #0f172a; padding: 4px;">
                <h4 style="margin: 0 0 6px 0; color: #1d4ed8; font-weight: 700;">📍 {city}</h4>
                <div style="margin-bottom: 4px;"><b>🌤️ 天氣狀態:</b> {wx}</div>
                <div style="margin-bottom: 4px;"><b>🌡️ 氣溫預報:</b> <span style="color:#dc2626; font-weight:bold;">{min_t}°C</span> ~ <span style="color:#b91c1c; font-weight:bold;">{max_t}°C</span></div>
                <div><b>💧 降雨機率:</b> <span style="color:#0284c7; font-weight:bold;">{pop}%</span></div>
            </div>
            """
            
            # 建立地標 Marker
            folium.CircleMarker(
                location=coords,
                radius=13,
                popup=folium.Popup(popup_html, max_width=220),
                tooltip=f"📍 {city}: {min_t}°C ~ {max_t}°C ({wx})",
                color="#ffffff",
                weight=2,
                fill=True,
                fill_color=color,
                fill_opacity=0.85
            ).add_to(m)
            
    # 加入右上方圖層切換選單 (LayerControl)
    folium.LayerControl(position="topright").add_to(m)
    
    return m
