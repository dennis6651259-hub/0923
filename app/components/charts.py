"""
charts.py - Plotly 圖表繪製模組 (支援單一縣市時序折線圖 & 全台/多縣市整齊對比長條圖)
"""

import plotly.graph_objects as go
import pandas as pd

def render_temperature_chart(df: pd.DataFrame, title: str = "氣溫預報趨勢圖", show_apparent: bool = True) -> go.Figure:
    """
    智慧判斷繪製模式 (支援實際溫度與體感溫度雙重比較)：
    1. 單一縣市：繪製 36 小時時段折線圖 (實際最高/最低 + 體感最高/最低 + 降雨機率)
    2. 全部/多縣市：繪製各縣市實際與體感氣溫對比長條圖
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
    # 模式 A：單一縣市 (時序折線趨勢與體感對比)
    # -------------------------------------------------------------
    if len(cities) == 1:
        city_name = cities[0]
        fig = go.Figure()
        
        x_labels = []
        for idx, row in df.iterrows():
            st_time = str(row["startTime"])
            short_time = st_time[5:16] if len(st_time) >= 16 else st_time
            wx = row.get("weather", "")
            x_labels.append(f"{short_time}<br>({wx})")
            
        # 1. 實際最低溫折線
        fig.add_trace(go.Scatter(
            x=x_labels,
            y=df["minT"],
            mode="lines+markers+text",
            name="實際最低溫 (MinT)",
            text=[f"<b>{t}°C</b>" for t in df["minT"]],
            textposition="bottom center",
            textfont=dict(color="#38bdf8", size=12),
            line=dict(color="#0284c7", width=3, shape="spline"),
            marker=dict(size=8, color="#0284c7", line=dict(color="#ffffff", width=1))
        ))
        
        # 2. 體感最低溫折線 (選填)
        if show_apparent and "apparentMinT" in df.columns:
            fig.add_trace(go.Scatter(
                x=x_labels,
                y=df["apparentMinT"],
                mode="lines+markers",
                name="體感最低溫 (Apparent MinT)",
                line=dict(color="#38bdf8", width=2, dash="dash", shape="spline"),
                marker=dict(size=6, color="#38bdf8", symbol="diamond"),
                hovertemplate="體感最低: %{y}°C<extra></extra>"
            ))
            
        # 3. 實際最高溫折線
        fig.add_trace(go.Scatter(
            x=x_labels,
            y=df["maxT"],
            mode="lines+markers+text",
            name="實際最高溫 (MaxT)",
            text=[f"<b>{t}°C</b>" for t in df["maxT"]],
            textposition="top center",
            textfont=dict(color="#f43f5e", size=12),
            line=dict(color="#f43f5e", width=3, shape="spline"),
            marker=dict(size=8, color="#e11d48", line=dict(color="#ffffff", width=1))
        ))
        
        # 4. 體感最高溫折線 (選填)
        if show_apparent and "apparentMaxT" in df.columns:
            fig.add_trace(go.Scatter(
                x=x_labels,
                y=df["apparentMaxT"],
                mode="lines+markers+text",
                name="體感最高溫 (Apparent MaxT)",
                text=[f"<b>({t}°)</b>" for t in df["apparentMaxT"]],
                textposition="top right",
                textfont=dict(color="#fb923c", size=11),
                line=dict(color="#fb923c", width=2.5, dash="dash", shape="spline"),
                marker=dict(size=7, color="#f97316", symbol="star"),
                hovertemplate="體感最高: %{y}°C<extra></extra>"
            ))
            
        # 5. 降雨機率柱狀圖
        if "pop" in df.columns:
            fig.add_trace(go.Bar(
                x=x_labels,
                y=df["pop"],
                name="降雨機率 (%)",
                text=[f"{p}%" if p > 0 else "" for p in df["pop"]],
                textposition="outside",
                textfont=dict(color="#93c5fd", size=11),
                marker_color="rgba(56, 189, 248, 0.25)",
                marker_line=dict(color="rgba(56, 189, 248, 0.7)", width=1),
                yaxis="y2"
            ))
            
        fig.update_layout(
            title=dict(
                text=f"🌡️ {city_name} — 實際溫度 vs 體感溫度趨勢比較",
                font=dict(size=18, color="#ffffff", family="Outfit, Segoe UI, sans-serif")
            ),
            paper_bgcolor="rgba(15, 23, 42, 0.95)",
            plot_bgcolor="rgba(30, 41, 59, 0.6)",
            font=dict(color="#f8fafc", family="Segoe UI, sans-serif"),
            hovermode="x unified",
            margin=dict(l=40, r=40, t=70, b=60),
            legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1, bgcolor="rgba(15, 23, 42, 0.6)"),
            xaxis=dict(
                title="預報時段",
                gridcolor="rgba(255, 255, 255, 0.07)",
                zeroline=False
            ),
            yaxis=dict(
                title="氣溫 (°C)",
                gridcolor="rgba(255, 255, 255, 0.07)",
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
    # 模式 B：全部縣市 / 多縣市 (各縣市實際與體感對比長條圖)
    # -------------------------------------------------------------
    summary_df = df.groupby("city").first().reset_index()
    summary_df = summary_df.sort_values(by="maxT", ascending=False)
    
    fig = go.Figure()
    
    # 實際最高溫
    fig.add_trace(go.Bar(
        x=summary_df["city"],
        y=summary_df["maxT"],
        name="實際最高溫 (MaxT)",
        text=[f"{t}°" for t in summary_df["maxT"]],
        textposition="outside",
        textfont=dict(color="#fda4af", size=10),
        marker_color="#f43f5e"
    ))
    
    # 體感最高溫
    if "apparentMaxT" in summary_df.columns:
        fig.add_trace(go.Bar(
            x=summary_df["city"],
            y=summary_df["apparentMaxT"],
            name="體感最高溫 (Feels Like)",
            text=[f"{t}°" for t in summary_df["apparentMaxT"]],
            textposition="outside",
            textfont=dict(color="#fdba74", size=10),
            marker_color="#f97316"
        ))
        
    # 實際最低溫
    fig.add_trace(go.Bar(
        x=summary_df["city"],
        y=summary_df["minT"],
        name="實際最低溫 (MinT)",
        text=[f"{t}°" for t in summary_df["minT"]],
        textposition="outside",
        textfont=dict(color="#7dd3fc", size=10),
        marker_color="#0284c7"
    ))
    
    # 降雨機率
    if "pop" in summary_df.columns:
        fig.add_trace(go.Scatter(
            x=summary_df["city"],
            y=summary_df["pop"],
            mode="lines+markers",
            name="降雨機率 (%)",
            line=dict(color="#38bdf8", width=2, dash="dot"),
            marker=dict(size=6, color="#38bdf8"),
            yaxis="y2"
        ))
        
    fig.update_layout(
        title=dict(
            text=f"📊 {title}（實際氣溫 vs 體感氣溫全台對比）",
            font=dict(size=18, color="#ffffff")
        ),
        paper_bgcolor="rgba(15, 23, 42, 0.95)",
        plot_bgcolor="rgba(30, 41, 59, 0.6)",
        font=dict(color="#f8fafc", family="Segoe UI, sans-serif"),
        barmode="group",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=70, b=80),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1, bgcolor="rgba(15, 23, 42, 0.6)"),
        xaxis=dict(
            title="縣市名稱",
            gridcolor="rgba(255, 255, 255, 0.07)",
            tickangle=-35
        ),
        yaxis=dict(
            title="氣溫 (°C)",
            gridcolor="rgba(255, 255, 255, 0.07)",
            range=[0, max(summary_df["maxT"].max(), summary_df.get("apparentMaxT", summary_df["maxT"]).max()) + 7]
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

def render_apparent_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """
    專屬圖表：體感溫度與實際溫度之溫差排行與悶熱/涼爽程度分析
    """
    if df.empty or "tempDiff" not in df.columns:
        fig = go.Figure()
        return fig

    summary_df = df.groupby("city").first().reset_index()
    summary_df = summary_df.sort_values(by="tempDiff", ascending=False)

    colors = []
    for diff in summary_df["tempDiff"]:
        if diff >= 3.0:
            colors.append("#ef4444") # 鮮紅 (極悶熱)
        elif diff >= 1.5:
            colors.append("#f97316") # 鮮橘 (悶熱)
        elif diff > -1.5:
            colors.append("#10b981") # 綠色 (舒適)
        else:
            colors.append("#38bdf8") # 藍色 (偏涼)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=summary_df["city"],
        y=summary_df["tempDiff"],
        marker_color=colors,
        text=[f"{'+' if d > 0 else ''}{d}°C" for d in summary_df["tempDiff"]],
        textposition="outside",
        textfont=dict(color="#ffffff", size=11, family="Arial"),
        hovertemplate="<b>%{x}</b><br>溫差 (體感-實際): %{y}°C<br>天氣: %{customdata[0]}<extra></extra>",
        customdata=summary_df[["weather"]]
    ))

    fig.update_layout(
        title=dict(
            text="🔥 體感溫度 vs 實際氣溫 溫差幅度排行 (高出實測代表濕熱悶感)",
            font=dict(size=17, color="#ffffff")
        ),
        paper_bgcolor="rgba(15, 23, 42, 0.95)",
        plot_bgcolor="rgba(30, 41, 59, 0.6)",
        font=dict(color="#f8fafc", family="Segoe UI, sans-serif"),
        margin=dict(l=40, r=40, t=60, b=80),
        xaxis=dict(
            title="縣市",
            gridcolor="rgba(255, 255, 255, 0.07)",
            tickangle=-35
        ),
        yaxis=dict(
            title="溫差 ΔT (°C)",
            gridcolor="rgba(255, 255, 255, 0.07)",
            zerolinecolor="rgba(255, 255, 255, 0.3)",
            zerolinewidth=2
        )
    )

    return fig
