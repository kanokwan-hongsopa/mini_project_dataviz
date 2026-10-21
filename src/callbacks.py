"""
Callbacks Module
Wires interactive Dash callbacks for reactive global filtering,
KPI calculations, dynamic station dropdowns, and figures updates for Tabs 1, 2, and 3.
"""
from typing import List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from dash import Dash, Input, Output, State, callback_context, no_update

from .analytics import (
    compute_correlations,
    compute_lagged_pairs,
    compute_rubber_concentration,
    filter_fair_hrdi_comparison,
)
from .figures import (
    create_t1_01_weather_bars,
    create_t1_02_temperature_trend,
    create_t1_03_rainfall_boxplots,
    create_t1_04_temperature_distribution,
    create_t2_01_rainfall_trend,
    create_t2_02_ranked_bars,
    create_t2_03_rubber_heatmap,
    create_t2_04_rubber_trend,
    create_t3_01_dual_rain_panel,
    create_t3_02_rain_rubber_scatter,
    create_t3_03_correlation_bars,
    empty_figure,
)
from .aggregation import (
    aggregate_station_month,
    aggregate_province_month,
    merge_monthly_datasets,
)
from .data_loader import TARGET_PROVINCES


def register_callbacks(
    app: Dash,
    df_hrdi: pd.DataFrame,
    df_hii: pd.DataFrame,
    df_oae: pd.DataFrame,
):
    """Register all reactive Dash callbacks."""

    # ---------------------------------------------------------
    # 0. RESET FILTERS CALLBACK
    # ---------------------------------------------------------
    @app.callback(
        [
            Output("global-filter-year", "value"),
            Output("global-filter-month", "value"),
            Output("global-filter-province", "value"),
            Output("filter-coverage-threshold", "value"),
            Output("filter-include-provisional", "value"),
        ],
        Input("btn-reset-filters", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(n_clicks):
        if n_clicks:
            return [2024, 2025], list(range(1, 13)), TARGET_PROVINCES, 90, []
        return no_update, no_update, no_update, no_update, no_update

    # ---------------------------------------------------------
    # 1. DYNAMIC STATION DROPDOWN FOR TAB 1
    # ---------------------------------------------------------
    @app.callback(
        [
            Output("t1-local-station", "options"),
            Output("label-coverage-threshold", "children"),
            Output("filter-active-summary", "children"),
        ],
        [
            Input("global-filter-province", "value"),
            Input("filter-coverage-threshold", "value"),
            Input("global-filter-year", "value"),
            Input("filter-include-provisional", "value"),
        ],
    )
    def update_station_options(selected_provinces, coverage_val, selected_years, prov_flag):
        provs = selected_provinces or TARGET_PROVINCES
        sub_hrdi = df_hrdi[df_hrdi["PROVINCE"].isin(provs)]
        
        # Unique stations
        stations = sub_hrdi[["CODE_REF", "STATION", "PROVINCE"]].drop_duplicates()
        options = [
            {"label": f"{r['STATION']} ({r['CODE_REF']} - {r['PROVINCE']})", "value": r["CODE_REF"]}
            for _, r in stations.iterrows()
        ]

        cov_text = f"≥ {coverage_val}%"
        prov_status = "รวม Provisional" if "include" in (prov_flag or []) else "คัดกรองเฉพาะข้อมูลมาตรฐาน"
        summary = f"ปี: {selected_years} | จังหวัด: {len(provs)} จ. | {prov_status}"

        return options, cov_text, summary

    # ---------------------------------------------------------
    # 2. TAB 1: HIGHLAND CLIMATE CALLBACKS
    # ---------------------------------------------------------
    @app.callback(
        [
            # KPIs
            Output("t1-kpi-stations", "children"),
            Output("t1-kpi-days", "children"),
            Output("t1-kpi-temp", "children"),
            Output("t1-kpi-humidity", "children"),
            Output("t1-kpi-wind", "children"),
            Output("t1-kpi-coverage", "children"),
            # Figures
            Output("fig-t1-01", "figure"),
            Output("fig-t1-02", "figure"),
            Output("fig-t1-03", "figure"),
            Output("fig-t1-04", "figure"),
        ],
        [
            Input("global-filter-year", "value"),
            Input("global-filter-month", "value"),
            Input("global-filter-province", "value"),
            Input("filter-coverage-threshold", "value"),
            Input("filter-include-provisional", "value"),
            Input("t1-local-station", "value"),
            Input("t1-local-temp-plot-type", "value"),
            Input("t1-fair-yoy-comparison", "value"),
        ],
    )
    def update_tab1(
        years, months, provinces, min_coverage, prov_switch,
        local_stations, temp_plot_type, fair_yoy
    ):
        years = years or [2024, 2025]
        months = months or list(range(1, 13))
        provinces = provinces or TARGET_PROVINCES
        include_prov = "include" in (prov_switch or [])
        is_fair_yoy = "fair" in (fair_yoy or [])

        # Filter base HRDI
        data = df_hrdi[
            (df_hrdi["YEAR"].isin(years)) &
            (df_hrdi["MONTH_NUM"].isin(months)) &
            (df_hrdi["PROVINCE"].isin(provinces))
        ].copy()

        if local_stations:
            data = data[data["CODE_REF"].isin(local_stations)]

        if is_fair_yoy:
            data = filter_fair_hrdi_comparison(data, matched_months_only=True, matched_stations_only=True)

        if data.empty:
            empty = empty_figure()
            return "0", "0", "N/A", "N/A", "N/A", "0%", empty, empty, empty, empty

        # Aggregations
        sm = aggregate_station_month(data, include_provisional=include_prov, min_coverage=float(min_coverage))
        pm = aggregate_province_month(sm, coverage_gate=True)

        # KPIs
        eligible_stations = sm[sm["passed_coverage"]]["CODE_REF"].nunique() if not sm.empty else 0
        total_obs_days = f"{len(data):,}"
        avg_temp = f"{data['TEMP'].mean():.1f} °C" if data["TEMP"].notna().any() else "N/A"
        avg_humidity = f"{data['HUMIDITY'].mean():.1f} %" if data["HUMIDITY"].notna().any() else "N/A"
        avg_wind = f"{data['WIND_SPEED'].mean():.2f}" if data["WIND_SPEED"].notna().any() else "N/A"
        mean_cov = f"{sm['rain_coverage_pct'].mean():.1f}%" if not sm.empty else "0%"

        # Figures
        f1 = create_t1_01_weather_bars(pm)
        f2 = create_t1_02_temperature_trend(pm)
        f3 = create_t1_03_rainfall_boxplots(sm, by_month=True)
        f4 = create_t1_04_temperature_distribution(data, plot_type=temp_plot_type)

        return (
            str(eligible_stations),
            total_obs_days,
            avg_temp,
            avg_humidity,
            avg_wind,
            mean_cov,
            f1, f2, f3, f4,
        )

    # ---------------------------------------------------------
    # 3. TAB 2: PROVINCIAL RAIN & RUBBER CALLBACKS
    # ---------------------------------------------------------
    @app.callback(
        [
            Output("t2-kpi-rain", "children"),
            Output("t2-kpi-rubber", "children"),
            Output("t2-kpi-top-province", "children"),
            Output("t2-kpi-peak-month", "children"),
            Output("t2-kpi-pairs", "children"),
            Output("t2-kpi-zero-tons", "children"),
            Output("fig-t2-01", "figure"),
            Output("fig-t2-02", "figure"),
            Output("fig-t2-03", "figure"),
            Output("fig-t2-04", "figure"),
        ],
        [
            Input("global-filter-year", "value"),
            Input("global-filter-month", "value"),
            Input("global-filter-province", "value"),
            Input("t2-local-heatmap-year", "value"),
            Input("t2-local-metric-type", "value"),
        ],
    )
    def update_tab2(years, months, provinces, heatmap_year, metric_type):
        years = years or [2024, 2025]
        months = months or list(range(1, 13))
        provinces = provinces or TARGET_PROVINCES

        # Filter HII & OAE baseline
        merged_base = pd.merge(
            df_hii,
            df_oae,
            on=["PROVINCE", "YEAR", "MONTH_NUM", "DATE_MONTH"],
            how="inner",
        )

        filtered = merged_base[
            (merged_base["YEAR"].isin(years)) &
            (merged_base["MONTH_NUM"].isin(months)) &
            (merged_base["PROVINCE"].isin(provinces))
        ].copy()

        if filtered.empty:
            empty = empty_figure()
            return "0 มม.", "0 ตัน", "N/A", "N/A", "0 คู่", "0 แถว", empty, empty, empty, empty

        # KPIs
        total_rain = f"{filtered['RAIN_AVG_MM'].sum():,.1f} มม."
        total_rubber = f"{filtered['RUBBER_TONS'].sum():,.0f} ตัน"

        prov_rubber = filtered.groupby("PROVINCE")["RUBBER_TONS"].sum()
        top_prov = prov_rubber.idxmax() if not prov_rubber.empty else "N/A"

        month_rubber = filtered.groupby("MONTH_NUM")["RUBBER_TONS"].sum()
        peak_month = f"เดือน {month_rubber.idxmax()}" if not month_rubber.empty else "N/A"

        pairs_count = f"{len(filtered)} คู่"
        zero_tons = f"{(filtered['RUBBER_TONS'] == 0).sum()} แถว"

        # Figures
        f1 = create_t2_01_rainfall_trend(filtered)
        f2 = create_t2_02_ranked_bars(filtered)
        f3 = create_t2_03_rubber_heatmap(filtered, year=int(heatmap_year or 2025))
        f4 = create_t2_04_rubber_trend(filtered, metric_type=metric_type)

        return (
            total_rain, total_rubber, top_prov, peak_month, pairs_count, zero_tons,
            f1, f2, f3, f4,
        )

    # ---------------------------------------------------------
    # 4. TAB 3: COMPARATIVE & CORRELATION CALLBACKS
    # ---------------------------------------------------------
    @app.callback(
        [
            Output("t3-kpi-n", "children"),
            Output("t3-kpi-pearson", "children"),
            Output("t3-kpi-spearman", "children"),
            Output("t3-kpi-difference", "children"),
            Output("t3-kpi-gate-status", "children"),
            Output("t3-kpi-lag-display", "children"),
            Output("fig-t3-01", "figure"),
            Output("fig-t3-02", "figure"),
            Output("fig-t3-03", "figure"),
        ],
        [
            Input("global-filter-year", "value"),
            Input("global-filter-month", "value"),
            Input("global-filter-province", "value"),
            Input("filter-coverage-threshold", "value"),
            Input("filter-include-provisional", "value"),
            Input("t3-local-lag", "value"),
            Input("t3-local-trendline", "value"),
        ],
    )
    def update_tab3(
        years, months, provinces, min_coverage, prov_switch,
        lag_val, trendline_switch
    ):
        years = years or [2024, 2025]
        months = months or list(range(1, 13))
        provinces = provinces or TARGET_PROVINCES
        include_prov = "include" in (prov_switch or [])
        lag = int(lag_val or 0)
        show_trend = "show" in (trendline_switch or [])

        # 1. Aggregate HRDI
        data_hrdi = df_hrdi[
            (df_hrdi["YEAR"].isin(years)) &
            (df_hrdi["MONTH_NUM"].isin(months)) &
            (df_hrdi["PROVINCE"].isin(provinces))
        ].copy()

        sm = aggregate_station_month(data_hrdi, include_provisional=include_prov, min_coverage=float(min_coverage))
        pm = aggregate_province_month(sm, coverage_gate=True)

        # 2. Merge with HII & OAE
        merged = merge_monthly_datasets(pm, df_hii, df_oae)
        merged_filtered = merged[
            (merged["YEAR"].isin(years)) &
            (merged["MONTH_NUM"].isin(months)) &
            (merged["PROVINCE"].isin(provinces))
        ].copy()

        # 3. Lagged pairs
        lagged = compute_lagged_pairs(merged_filtered, lag_months=lag, provinces=provinces)

        # 4. Correlations
        if not lagged.empty:
            corr = compute_correlations(lagged["LAGGED_RAIN_MM"], lagged["RUBBER_TONS"])
            n_str = f"{corr['n']} คู่"
            pearson_str = f"{corr['pearson_r']:.3f}" if corr["pearson_r"] is not None else "N/A"
            spearman_str = f"{corr['spearman_rho']:.3f}" if corr["spearman_rho"] is not None else "N/A"
        else:
            n_str = "0 คู่"
            pearson_str = "N/A"
            spearman_str = "N/A"

        diff_str = "DISABLED (รอตรวจหน่วย)"
        gate_str = "ACTIVE (ป้องกันเทียบข้ามหน่วย)"
        lag_display = f"Lag {lag} เดือน"

        # Figures
        f1 = create_t3_01_dual_rain_panel(merged_filtered)
        f2 = create_t3_02_rain_rubber_scatter(lagged, show_trendline=show_trend)
        f3 = create_t3_03_correlation_bars(lagged)

        return (
            n_str, pearson_str, spearman_str, diff_str, gate_str, lag_display,
            f1, f2, f3,
        )
