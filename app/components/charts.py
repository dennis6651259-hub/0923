"""
charts.py - Plotly 圖表繪製模組
"""

import plotly.graph_objects as go
import pandas as pd

def render_temperature_chart(df: pd.DataFrame, title: str = "氣溫預報趨勢圖") -> go.Figure:
    """
    繪製雙軸氣溫（最高溫 / 最低溫）與降雨機率趨勢圖。
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="尚無數據")
        return fig
        
    fig = go.Figure()
    
    # 建立時間軸標籤
    x_labels = df["startTime"].astype(str) + "<br>" + df["city"]
    
    # 最低溫折線
    fig.add_trace(go.Scatter(
        x=x_labels,
        y=df["minT"],
        mode="lines+markers+text",
        name="最低氣溫 (MinT)",
        text=df["minT"].astype(str) + "°C",
        textposition="bottom center",
        line=dict(color="#00b4d8", width=3, shape="spline"),
        marker=dict(size=8, color="#0077b6")
    ))
    
    # 最高溫折線
    fig.add_trace(go.Scatter(
        x=x_labels,
        y=df["maxT"],
        mode="lines+markers+text",
        name="最高氣溫 (MaxT)",
        text=df["maxT"].astype(str) + "°C",
        textposition="top center",
        line=dict(color="#ff4d6d", width=3, shape="spline"),
        marker=dict(size=8, color="#c1121f")
    ))
    
    # 降雨機率柱狀圖
    if "pop" in df.columns:
        fig.add_trace(go.Bar(
            x=x_labels,
            y=df["pop"],
            name="降雨機率 (%)",
            marker_color="rgba(100, 149, 237, 0.4)",
            yaxis="y2"
        ))
    
    fig.update_layout(
        title=dict(text=f"🌡️ {title}", font=dict(size=20, color="#ffffff")),
        paper_bgcolor="rgba(15, 23, 42, 0.9)",
        plot_bgcolor="rgba(30, 41, 59, 0.7)",
        font=dict(color="#f8fafc"),
        hovermode="x unified",
        margin=dict(l=40, r=40, t=60, b=80),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            title="預報時段 / 縣市",
            gridcolor="rgba(255, 255, 255, 0.1)",
            tickangle=-25
        ),
        yaxis=dict(
            title="氣溫 (°C)",
            gridcolor="rgba(255, 255, 255, 0.1)",
            zerolinecolor="rgba(255, 255, 255, 0.2)"
        ),
        yaxis2=dict(
            title="降雨機率 (%)",
            overlaying="y",
            side="right",
            range=[0, 100],
            showgrid=False
        )
    )
    
    return fig
