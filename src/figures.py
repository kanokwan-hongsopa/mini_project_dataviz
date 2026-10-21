"""
Figure Generators Module
Produces Plotly figures for Tab 1 (T1-01..T1-04), Tab 2 (T2-01..T2-04), and Tab 3 (T3-01..T3-03).
"""
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .analytics import compute_correlations, compute_lagged_pairs

# Consistent color palette
PALETTE = {
    "primary": "#1e3a8a",      # Navy blue
    "secondary": "#0284c7",    # Sky blue
    "accent": "#0d9488",       # Teal
    "rubber": "#d97706",       # Amber
    "rain": "#2563eb",         # Royal blue
    "temp": "#ea580c",         # Warm orange
    "humidity": "#06b6d4",     # Cyan
    "wind": "#8b5cf6",         # Violet
    "background": "#ffffff",
    "paper": "#f8fafc",
    "grid": "#e2e8f0",
    "text": "#1e293b",
}

THEME_LAYOUT = dict(
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    font=dict(family="Prompt, Sarabun, -apple-system, sans-serif", color=PALETTE["text"], size=12),
    margin=dict(l=50, r=30, t=50, b=50),
    xaxis=dict(showgrid=True, gridcolor=PALETTE["grid"], zeroline=False),
    yaxis=dict(showgrid=True, gridcolor=PALETTE["grid"], zeroline=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)


def empty_figure(message: str = "ไม่มีข้อมูลตามเงื่อนไขที่เลือก") -> go.Figure:
    """Return an empty figure with user-friendly notification."""
    fig = go.Figure()
    fig.add_annotation(
        text=f"ℹ️ {message}",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14, color="#64748b"),
    )
    fig.update_layout(**THEME_LAYOUT)
    return fig


# -------------------------------------------------------------
# TAB 1 FIGURES: HIGHLAND CLIMATE
# -------------------------------------------------------------

def create_t1_01_weather_bars(df_pm: pd.DataFrame) -> go.Figure:
    """
    T1-01: Grouped bar / small multiples for TEMP, HUMIDITY, and WIND_SPEED across provinces.
    Uses 3 subplots because units differ.
    """
    if df_pm.empty:
        return empty_figure()

    # Aggregate by province
    agg = df_pm.groupby("PROVINCE", as_index=False).agg(
        temp_mean=("highland_temp_mean", "mean"),
        humidity_mean=("highland_humidity_mean", "mean"),
        wind_mean=("highland_wind_mean", "mean"),
        eligible_st=("eligible_stations", "max"),
    )

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=(
            "อุณหภูมิเฉลี่ย (°C คาดว่า)",
            "ความชื้นสัมพัทธ์เฉลี่ย (% คาดว่า)",
            "ความเร็วลมเฉลี่ย (หน่วยตามไฟล์ รอการยืนยัน)"
        ),
        shared_yaxes=False,
    )

    fig.add_trace(
        go.Bar(
            x=agg["PROVINCE"],
            y=agg["temp_mean"],
            name="อุณหภูมิ",
            marker_color=PALETTE["temp"],
            hovertemplate="<b>%{x}</b><br>อุณหภูมิเฉลี่ย: %{y:.2f} °C<extra></extra>",
        ),
        row=1, col=1,
    )

    fig.add_trace(
        go.Bar(
            x=agg["PROVINCE"],
            y=agg["humidity_mean"],
            name="ความชื้น",
            marker_color=PALETTE["humidity"],
            hovertemplate="<b>%{x}</b><br>ความชื้นสัมพัทธ์: %{y:.2f} %<extra></extra>",
        ),
        row=1, col=2,
    )

    fig.add_trace(
        go.Bar(
            x=agg["PROVINCE"],
            y=agg["wind_mean"],
            name="ความเร็วลม",
            marker_color=PALETTE["wind"],
            hovertemplate="<b>%{x}</b><br>ความเร็วลม: %{y:.2f}<extra></extra>",
        ),
        row=1, col=3,
    )

    fig.update_layout(
        **THEME_LAYOUT,
        showlegend=False,
        title_text="T1-01: ค่าเฉลี่ยสภาพภูมิอากาศรายจังหวัด (แยก 3 ตัวแปรตามหน่วยวัด)",
        height=380,
    )
    return fig


def create_t1_02_temperature_trend(
    df_pm: pd.DataFrame,
    group_by: str = "PROVINCE",
) -> go.Figure:
    """
    T1-02: Monthly multi-line chart for temperature trend (2024–2025).
    Preserves true gaps for unobserved periods (e.g. 2024 Jan–Aug has no data).
    """
    if df_pm.empty:
        return empty_figure()

    fig = go.Figure()
    provinces = df_pm["PROVINCE"].unique()
    colors = px.colors.qualitative.Plotly

    for i, prov in enumerate(provinces):
        sub = df_pm[df_pm["PROVINCE"] == prov].sort_values("DATE_MONTH")
        fig.add_trace(
            go.Scatter(
                x=sub["DATE_MONTH"],
                y=sub["highland_temp_mean"],
                mode="lines+markers",
                name=prov,
                line=dict(width=2),
                marker=dict(size=6),
                connectgaps=False,  # Essential: Do not connect across missing months!
                hovertemplate="<b>%{data.name}</b><br>เดือน: %{x|%Y-%m}<br>อุณหภูมิ: %{y:.2f} °C<extra></extra>",
            )
        )

    fig.update_layout(
        **THEME_LAYOUT,
        title="T1-02: แนวโน้มอุณหภูมิพื้นที่สูงรายเดือน (ก.ย. 2024 – ธ.ค. 2025)",
        xaxis_title="ปี-เดือน (YYYY-MM)",
        yaxis_title="อุณหภูมิเฉลี่ย (°C)",
        height=400,
    )
    return fig


def create_t1_03_rainfall_boxplots(df_sm: pd.DataFrame, by_month: bool = True) -> go.Figure:
    """
    T1-03: True box plot with outlier points for station-month rainfall.
    Uses stations passing the coverage gate.
    """
    if df_sm.empty:
        return empty_figure()

    valid_sm = df_sm[df_sm["passed_coverage"] & df_sm["rainfall_total"].notna()].copy()
    if valid_sm.empty:
        return empty_figure("ไม่มีสถานีที่ผ่านเกณฑ์ Coverage สำหรับข้อมูลฝน")

    x_col = "MONTH_NUM" if by_month else "PROVINCE"
    x_title = "เดือน (1–12)" if by_month else "จังหวัด"

    if by_month:
        valid_sm["X_LABEL"] = valid_sm["MONTH_NUM"].astype(str) + " (" + valid_sm["YEAR"].astype(str) + ")"
        x_col = "X_LABEL"

    fig = go.Figure()
    fig.add_trace(
        go.Box(
            x=valid_sm[x_col],
            y=valid_sm["rainfall_total"],
            boxpoints="outliers",  # Shows true statistical outliers beyond 1.5 IQR
            marker_color=PALETTE["rain"],
            line=dict(color=PALETTE["primary"], width=1.5),
            text=valid_sm["STATION"],
            hovertemplate="<b>สถานี:</b> %{text}<br><b>กลุ่ม:</b> %{x}<br><b>ฝนสะสม:</b> %{y:.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        **THEME_LAYOUT,
        title="T1-03: การกระจายตัวและค่าฝนพื้นที่สูงผิดปกติ (True Boxplot + IQR Outliers)",
        xaxis_title=x_title,
        yaxis_title="ผลรวมค่า RAINFALL (หน่วยตามไฟล์ รอการยืนยัน)",
        height=420,
    )
    return fig


def create_t1_04_temperature_distribution(
    df_hrdi_filtered: pd.DataFrame,
    plot_type: str = "box",
) -> go.Figure:
    """
    T1-04: Temperature distribution (box or violin) by province.
    Calculated from valid daily records.
    """
    if df_hrdi_filtered.empty:
        return empty_figure()

    valid_daily = df_hrdi_filtered.dropna(subset=["TEMP"])
    if valid_daily.empty:
        return empty_figure()

    fig = go.Figure()
    provinces = valid_daily["PROVINCE"].unique()
    colors = px.colors.qualitative.Safe

    for i, prov in enumerate(provinces):
        sub = valid_daily[valid_daily["PROVINCE"] == prov]
        color = colors[i % len(colors)]
        if plot_type == "violin":
            fig.add_trace(
                go.Violin(
                    y=sub["TEMP"],
                    name=prov,
                    box_visible=True,
                    meanline_visible=True,
                    line_color=color,
                    hovertemplate=f"<b>{prov}</b><br>อุณหภูมิ: %{{y:.1f}} °C<extra></extra>",
                )
            )
        else:
            fig.add_trace(
                go.Box(
                    y=sub["TEMP"],
                    name=prov,
                    boxpoints=False,
                    marker_color=color,
                    hovertemplate=f"<b>{prov}</b><br>อุณหภูมิ: %{{y:.1f}} °C<extra></extra>",
                )
            )

    fig.update_layout(
        **THEME_LAYOUT,
        title=f"T1-04: การกระจายตัวของอุณหภูมิรายวัน ({'Violin Plot' if plot_type == 'violin' else 'Box Plot'})",
        yaxis_title="อุณหภูมิรายวัน (°C)",
        xaxis_title="จังหวัด",
        height=420,
        showlegend=False,
    )
    return fig


# -------------------------------------------------------------
# TAB 2 FIGURES: PROVINCIAL RAINFALL & RUBBER YIELD
# -------------------------------------------------------------

def create_t2_01_rainfall_trend(df_merged: pd.DataFrame) -> go.Figure:
    """
    T2-01: Line chart for HII provincial rainfall monthly trend (mm).
    """
    if df_merged.empty:
        return empty_figure()

    fig = go.Figure()
    provinces = df_merged["PROVINCE"].unique()
    colors = px.colors.qualitative.Set2

    for i, prov in enumerate(provinces):
        sub = df_merged[df_merged["PROVINCE"] == prov].sort_values("DATE_MONTH")
        fig.add_trace(
            go.Scatter(
                x=sub["DATE_MONTH"],
                y=sub["RAIN_AVG_MM"],
                mode="lines+markers",
                name=prov,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=5),
                hovertemplate="<b>%{data.name}</b><br>เดือน: %{x|%Y-%m}<br>ปริมาณฝน HII: %{y:.2f} มม.<extra></extra>",
            )
        )

    fig.update_layout(
        **THEME_LAYOUT,
        title="T2-01: แนวโน้มปริมาณน้ำฝนเชิงพื้นที่ HII รายเดือน (มม.)",
        xaxis_title="ปี-เดือน (YYYY-MM)",
        yaxis_title="ปริมาณฝนเฉลี่ยเชิงพื้นที่ (มม.)",
        height=400,
    )
    return fig


def create_t2_02_ranked_bars(
    df_merged: pd.DataFrame,
    metric: str = "both",  # "rubber", "rain", or "both"
) -> go.Figure:
    """
    T2-02: Ranked horizontal bars for total rubber yield and total rainfall in selected period.
    Separates units into 2 panels so tons and mm are never mixed.
    """
    if df_merged.empty:
        return empty_figure()

    agg = df_merged.groupby("PROVINCE", as_index=False).agg(
        total_rubber=("RUBBER_TONS", "sum"),
        total_rain=("RAIN_AVG_MM", "sum"),
        month_count=("MONTH_NUM", "count"),
    )

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "อันดับผลผลิตยางพารารวม (ตัน)",
            "อันดับปริมาณน้ำฝนสะสม HII (มม.)"
        ),
        shared_yaxes=False,
    )

    # Sort for rubber
    agg_rubber = agg.sort_values("total_rubber", ascending=True)
    fig.add_trace(
        go.Bar(
            x=agg_rubber["total_rubber"],
            y=agg_rubber["PROVINCE"],
            orientation="h",
            name="ผลผลิตยางพารา",
            marker_color=PALETTE["rubber"],
            hovertemplate="<b>%{y}</b><br>ผลผลิตยาง: %{x:,.1f} ตัน<extra></extra>",
        ),
        row=1, col=1,
    )

    # Sort for rain
    agg_rain = agg.sort_values("total_rain", ascending=True)
    fig.add_trace(
        go.Bar(
            x=agg_rain["total_rain"],
            y=agg_rain["PROVINCE"],
            orientation="h",
            name="ปริมาณฝน HII",
            marker_color=PALETTE["rain"],
            hovertemplate="<b>%{y}</b><br>ฝนสะสม HII: %{x:,.1f} มม.<extra></extra>",
        ),
        row=1, col=2,
    )

    fig.update_layout(
        **THEME_LAYOUT,
        showlegend=False,
        title="T2-02: การจัดอันดับจังหวัดตามผลผลิตยางพาราและปริมาณฝน (ยอดรวมตามช่วงเวลาที่เลือก)",
        height=400,
    )
    return fig


def create_t2_03_rubber_heatmap(
    df_merged: pd.DataFrame,
    year: int = 2025,
) -> go.Figure:
    """
    T2-03: Province × Month Heatmap of RUBBER_MONTH_SHARE_PERCENT.
    """
    sub = df_merged[df_merged["YEAR"] == year].copy()
    if sub.empty:
        return empty_figure(f"ไม่มีข้อมูลผลผลิตยางสำหรับปี {year}")

    pivot = sub.pivot(index="PROVINCE", columns="MONTH_NUM", values="RUBBER_MONTH_SHARE_PERCENT")
    pivot = pivot.fillna(0)

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=[f"ด.{m}" for m in pivot.columns],
            y=pivot.index,
            colorscale="YlOrBr",
            colorbar=dict(title="% สัดส่วน"),
            hovertemplate="<b>จังหวัด:</b> %{y}<br><b>เดือน:</b> %{x}<br><b>สัดส่วนในจังหวัด-ปี:</b> %{z:.2f}%<extra></extra>",
        )
    )

    fig.update_layout(
        **THEME_LAYOUT,
        title=f"T2-03: Heatmap สัดส่วนผลผลิตยางพารารายเดือน (ปี {year}) ภายในจังหวัด-ปี (%)",
        xaxis_title="เดือน",
        yaxis_title="จังหวัด",
        height=380,
    )
    return fig


def create_t2_04_rubber_trend(
    df_merged: pd.DataFrame,
    metric_type: str = "tons",  # "tons" or "percent"
) -> go.Figure:
    """
    T2-04: Monthly Rubber Trend (Tons or Month Share %).
    """
    if df_merged.empty:
        return empty_figure()

    y_col = "RUBBER_TONS" if metric_type == "tons" else "RUBBER_MONTH_SHARE_PERCENT"
    y_title = "ผลผลิตยางพารา (ตัน)" if metric_type == "tons" else "สัดส่วนผลผลิตภายในจังหวัด-ปี (%)"

    fig = go.Figure()
    provinces = df_merged["PROVINCE"].unique()
    colors = px.colors.qualitative.Dark24

    for i, prov in enumerate(provinces):
        sub = df_merged[df_merged["PROVINCE"] == prov].sort_values("DATE_MONTH")
        fig.add_trace(
            go.Scatter(
                x=sub["DATE_MONTH"],
                y=sub[y_col],
                mode="lines+markers",
                name=prov,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=5),
                hovertemplate=f"<b>%{{data.name}}</b><br>เดือน: %{{x|%Y-%m}}<br>{y_title}: %{{y:,.2f}}<extra></extra>",
            )
        )

    fig.update_layout(
        **THEME_LAYOUT,
        title=f"T2-04: แนวโน้มผลผลิตยางพารารายเดือน ({'จำนวนตัน' if metric_type == 'tons' else 'สัดส่วน %'})",
        xaxis_title="ปี-เดือน (YYYY-MM)",
        yaxis_title=y_title,
        height=400,
    )
    return fig


# -------------------------------------------------------------
# TAB 3 FIGURES: COMPARATIVE & CORRELATION ANALYSIS
# -------------------------------------------------------------

def create_t3_01_dual_rain_panel(df_merged: pd.DataFrame) -> go.Figure:
    """
    T3-01: Dual-panel line chart comparing HRDI Highland Rainfall with HII Provincial Rainfall.
    Gating: Unit difference bar is explicitly disabled until HRDI accumulation is verified.
    """
    if df_merged.empty:
        return empty_figure()

    sub = df_merged.sort_values("DATE_MONTH")

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=(
            "ฝนพื้นที่สูง HRDI (ค่าเฉลี่ยสถานีที่ผ่านเกณฑ์ Coverage - หน่วยรอยืนยัน)",
            "ฝนเชิงพื้นที่ระดับจังหวัด HII (RAIN_AVG_MM - มม.)"
        ),
    )

    provinces = sub["PROVINCE"].unique()
    colors = px.colors.qualitative.Vivid

    for i, prov in enumerate(provinces):
        p_data = sub[sub["PROVINCE"] == prov]
        color = colors[i % len(colors)]

        # HRDI
        fig.add_trace(
            go.Scatter(
                x=p_data["DATE_MONTH"],
                y=p_data["highland_rain_mean"],
                mode="lines+markers",
                name=f"{prov} (HRDI)",
                line=dict(color=color, width=2, dash="dash"),
                hovertemplate="<b>%{data.name}</b><br>เดือน: %{x|%Y-%m}<br>ฝน HRDI: %{y:.2f} (รอตรวจหน่วย)<extra></extra>",
            ),
            row=1, col=1,
        )

        # HII
        fig.add_trace(
            go.Scatter(
                x=p_data["DATE_MONTH"],
                y=p_data["RAIN_AVG_MM"],
                mode="lines+markers",
                name=f"{prov} (HII)",
                line=dict(color=color, width=2),
                hovertemplate="<b>%{data.name}</b><br>เดือน: %{x|%Y-%m}<br>ฝน HII: %{y:.2f} มม.<extra></extra>",
            ),
            row=2, col=1,
        )

    fig.update_layout(
        **THEME_LAYOUT,
        title="T3-01: เปรียบเทียบรูปแบบฝนพื้นที่สูง (HRDI) vs ฝนเชิงพื้นที่จังหวัด (HII) [แกนแยก]",
        height=520,
    )
    return fig


def create_t3_02_rain_rubber_scatter(
    df_lagged: pd.DataFrame,
    show_trendline: bool = True,
) -> go.Figure:
    """
    T3-02: Scatter plot of Rainfall (X) vs Rubber Yield (Y) with optional Lag 0–3 months.
    """
    if df_lagged.empty:
        return empty_figure("ไม่มีคู่ข้อมูลฝน–ยางที่สมบูรณ์ตามเงื่อนไข")

    fig = px.scatter(
        df_lagged,
        x="LAGGED_RAIN_MM",
        y="RUBBER_TONS",
        color="PROVINCE",
        trendline="ols" if show_trendline and len(df_lagged) >= 3 else None,
        title="T3-02: สหสัมพันธ์ระหว่างปริมาณฝน (HII) กับผลผลิตยางพารา (OAE)",
        labels={
            "LAGGED_RAIN_MM": "ปริมาณน้ำฝน HII (มม.)",
            "RUBBER_TONS": "ผลผลิตยางพารา (ตัน)",
            "PROVINCE": "จังหวัด",
        },
        template="plotly_white",
        hover_data=["YEAR", "MONTH_NUM", "RUBBER_MONTH_SHARE_PERCENT"],
    )

    fig.update_layout(
        **THEME_LAYOUT,
        height=450,
    )
    return fig


def create_t3_03_correlation_bars(df_lagged: pd.DataFrame) -> go.Figure:
    """
    T3-03: Correlation cards/bars showing Pearson r and Spearman rho by province and pooled.
    """
    if df_lagged.empty:
        return empty_figure()

    records = []
    # 1. Per province
    for prov, group in df_lagged.groupby("PROVINCE"):
        c = compute_correlations(group["LAGGED_RAIN_MM"], group["RUBBER_TONS"])
        records.append({
            "scope": prov,
            "pearson_r": c["pearson_r"],
            "spearman_rho": c["spearman_rho"],
            "n": c["n"],
            "is_valid": c["is_valid"],
            "reason": c["reason"],
        })

    # 2. Pooled
    c_pool = compute_correlations(df_lagged["LAGGED_RAIN_MM"], df_lagged["RUBBER_TONS"])
    records.append({
        "scope": "รวมทุกจังหวัดที่เลือก (Pooled)",
        "pearson_r": c_pool["pearson_r"],
        "spearman_rho": c_pool["spearman_rho"],
        "n": c_pool["n"],
        "is_valid": c_pool["is_valid"],
        "reason": c_pool["reason"],
    })

    df_corr = pd.DataFrame(records)

    fig = go.Figure()
    # Filter valid for plotting
    df_valid = df_corr[df_corr["is_valid"]].copy()

    if not df_valid.empty:
        fig.add_trace(
            go.Bar(
                x=df_valid["scope"],
                y=df_valid["pearson_r"],
                name="Pearson r",
                marker_color=PALETTE["secondary"],
                hovertemplate="<b>%{x}</b><br>Pearson r: %{y:.3f}<br>(n = %{customdata})<extra></extra>",
                customdata=df_valid["n"],
            )
        )
        fig.add_trace(
            go.Bar(
                x=df_valid["scope"],
                y=df_valid["spearman_rho"],
                name="Spearman ρ",
                marker_color=PALETTE["accent"],
                hovertemplate="<b>%{x}</b><br>Spearman ρ: %{y:.3f}<br>(n = %{customdata})<extra></extra>",
                customdata=df_valid["n"],
            )
        )

    layout_dict = THEME_LAYOUT.copy()
    layout_dict.update(
        barmode="group",
        title="T3-03: ค่าสัมประสิทธิ์สหสัมพันธ์ (Pearson r และ Spearman ρ) แยกรายจังหวัดและภาพรวม",
        xaxis_title="ขอบเขตการวิเคราะห์",
        yaxis_title="Correlation Coefficient (-1 ถึง 1)",
        height=380,
    )
    fig.update_layout(**layout_dict)
    fig.update_yaxes(range=[-1, 1], zeroline=True, zerolinecolor="#64748b", zerolinewidth=1.5)
    return fig
