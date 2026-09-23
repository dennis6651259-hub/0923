"""
charts.py - Plotly 圖表繪製模組 (支援單一縣市時序折線圖 & 全台/多縣市整齊對比長條圖)
"""

import plotly.graph_objects as go
import pandas as pd

def render_temperature_chart(df: pd.DataFrame, title: str = "氣溫預報趨勢圖") -> go.Figure:
    """
    智慧判斷繪製模式：
    1. 單一縣市：繪製 36 小時時段折線圖 (最高/最低溫 + 降雨機率柱狀)
    2. 全部/多縣市：繪製各縣市氣溫對比長條圖 (避免 66 筆數據折線雜亂交叉)
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="尚無數據",
            paper_bgcolor="rgba(15, 23, 42, 0.9)",
            font=dict(color="#f8fafc")
        )
        return fig
        
    cities = df["city"].unique()
    
    # -------------------------------------------------------------
    # 模式 A：單一縣市 (時序折線趨勢圖)
    # -------------------------------------------------------------
    if len(cities) == 1:
        city_name = cities[0]
        fig = go.Figure()
        
        # 整理時段標籤 (簡化時間格式)
        x_labels = []
        for idx, row in df.iterrows():
            st_time = str(row["startTime"])
            # 例如: "09/23 12:00"
            if len(st_time) >= 16:
                short_time = st_time[5:16]
            else:
                short_time = st_time
            wx = row.get("weather", "")
            x_labels.append(f"{short_time}<br>({wx})")
            
        # 最低溫折線
        fig.add_trace(go.Scatter(
            x=x_labels,
            y=df["minT"],
            mode="lines+markers+text",
            name="最低氣溫 (MinT)",
            text=[f"<b>{t}°C</b>" for t in df["minT"]],
            textposition="bottom center",
            textfont=dict(color="#38bdf8", size=13),
            line=dict(color="#38bdf8", width=3, shape="spline"),
            marker=dict(size=9, color="#0284c7", line=dict(color="#ffffff", width=1.5))
        ))
        
        # 最高溫折線
        fig.add_trace(go.Scatter(
            x=x_labels,
            y=df["maxT"],
            mode="lines+markers+text",
            name="最高氣溫 (MaxT)",
            text=[f"<b>{t}°C</b>" for t in df["maxT"]],
            textposition="top center",
            textfont=dict(color="#f43f5e", size=13),
            line=dict(color="#f43f5e", width=3, shape="spline"),
            marker=dict(size=9, color="#e11d48", line=dict(color="#ffffff", width=1.5))
        ))
        
        # 降雨機率柱狀圖
        if "pop" in df.columns:
            fig.add_trace(go.Bar(
                x=x_labels,
                y=df["pop"],
                name="降雨機率 (%)",
                text=[f"{p}%" if p > 0 else "" for p in df["pop"]],
                textposition="outside",
                textfont=dict(color="#93c5fd", size=11),
                marker_color="rgba(56, 189, 248, 0.35)",
                marker_line=dict(color="rgba(56, 189, 248, 0.8)", width=1),
                yaxis="y2"
            ))
            
        fig.update_layout(
            title=dict(
                text=f"🌡️ {city_name} — 36 小時預報氣溫與降雨趨勢",
                font=dict(size=18, color="#ffffff")
            ),
            paper_bgcolor="rgba(15, 23, 42, 0.9)",
            plot_bgcolor="rgba(30, 41, 59, 0.7)",
            font=dict(color="#f8fafc", family="Segoe UI, sans-serif"),
            hovermode="x unified",
            margin=dict(l=40, r=40, t=60, b=60),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(
                title="預報時段",
                gridcolor="rgba(255, 255, 255, 0.08)",
                zeroline=False
            ),
            yaxis=dict(
                title="氣溫 (°C)",
                gridcolor="rgba(255, 255, 255, 0.08)",
                zeroline=False
            ),
            yaxis2=dict(
                title="降雨機率 (%)",
                overlaying="y",
                side="right",
                range=[0, 120],
                showgrid=False
            )
        )
        return fig

    # -------------------------------------------------------------
    # 模式 B：全部縣市 / 多縣市 (整齊各縣市對比長條圖)
    # -------------------------------------------------------------
    # 取各縣市最新時段資料
    summary_df = df.groupby("city").first().reset_index()
    # 依照最高溫由高至低排序
    summary_df = summary_df.sort_values(by="maxT", ascending=False)
    
    fig = go.Figure()
    
    # 最高溫長條
    fig.add_trace(go.Bar(
        x=summary_df["city"],
        y=summary_df["maxT"],
        name="最高氣溫 (MaxT)",
        text=[f"{t}°" for t in summary_df["maxT"]],
        textposition="outside",
        textfont=dict(color="#fda4af", size=11),
        marker_color="#f43f5e"
    ))
    
    # 最低溫長條
    fig.add_trace(go.Bar(
        x=summary_df["city"],
        y=summary_df["minT"],
        name="最低氣溫 (MinT)",
        text=[f"{t}°" for t in summary_df["minT"]],
        textposition="outside",
        textfont=dict(color="#7dd3fc", size=11),
        marker_color="#0284c7"
    ))
    
    # 降雨機率 (折線/標記圖)
    if "pop" in summary_df.columns:
        fig.add_trace(go.Scatter(
            x=summary_df["city"],
            y=summary_df["pop"],
            mode="lines+markers",
            name="降雨機率 (%)",
            line=dict(color="#38bdf8", width=2.5, dash="dot"),
            marker=dict(size=7, color="#38bdf8"),
            yaxis="y2"
        ))
        
    fig.update_layout(
        title=dict(
            text=f"📊 {title}（依最高溫排序）",
            font=dict(size=18, color="#ffffff")
        ),
        paper_bgcolor="rgba(15, 23, 42, 0.9)",
        plot_bgcolor="rgba(30, 41, 59, 0.7)",
        font=dict(color="#f8fafc", family="Segoe UI, sans-serif"),
        barmode="group",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=60, b=80),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(
            title="各縣市名稱",
            gridcolor="rgba(255, 255, 255, 0.08)",
            tickangle=-35
        ),
        yaxis=dict(
            title="氣溫 (°C)",
            gridcolor="rgba(255, 255, 255, 0.08)",
            range=[0, max(summary_df["maxT"]) + 6]
        ),
        yaxis2=dict(
            title="降雨機率 (%)",
            overlaying="y",
            side="right",
            range=[0, 110],
            showgrid=False
        )
    )
    
    return fig
