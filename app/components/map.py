"""
map.py - Folium 地圖視覺化模組
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

def render_taiwan_map(df: pd.DataFrame) -> folium.Map:
    """
    創建全台氣溫分佈 Folium 地圖。
    """
    # 台灣地理中心點
    m = folium.Map(location=[23.7, 120.95], zoom_start=7, tiles="CartoDB dark_matter")
    
    if df.empty:
        return m
        
    # 取最新一個時間區段或以縣市平均
    latest_df = df.groupby("city").first().reset_index()
    
    for _, row in latest_df.iterrows():
        city = row["city"]
        min_t = row["minT"]
        max_t = row["maxT"]
        avg_t = (min_t + max_t) / 2
        wx = row.get("weather", "")
        pop = row.get("pop", 0)
        
        coords = CITY_COORDS.get(city)
        if not coords:
            continue
            
        color = get_temp_color(max_t)
        
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 13px; width: 160px; color: #1e293b;">
            <h4 style="margin: 0 0 5px 0; color: #0284c7;">📍 {city}</h4>
            <b>🌤️ 天氣:</b> {wx}<br/>
            <b>🌡️ 氣溫:</b> {min_t}°C ~ {max_t}°C<br/>
            <b>💧 降雨機率:</b> {pop}%
        </div>
        """
        
        folium.CircleMarker(
            location=coords,
            radius=12,
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{city}: {min_t}°C ~ {max_t}°C ({wx})",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8
        ).add_to(m)
        
    return m
