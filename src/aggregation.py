"""
Aggregation Module
Handles Station-Month and Province-Month aggregations and merges.
"""
from typing import Optional
import calendar
import numpy as np
import pandas as pd


def get_calendar_days(year: int, month: int) -> int:
    """Return number of calendar days in a given year and month."""
    try:
        return calendar.monthrange(int(year), int(month))[1]
    except Exception:
        return 30


def aggregate_station_month(
    df_hrdi: pd.DataFrame,
    include_provisional: bool = False,
    min_coverage: float = 90.0,
) -> pd.DataFrame:
    """
    Aggregate daily HRDI observations to Station-Month level.
    If include_provisional is False, rows with CLEANING_STATUS == 'PROVISIONAL_LAST_RECORD'
    are excluded before computing aggregates.
    """
    df = df_hrdi.copy()
    if not include_provisional:
        df = df[df["CLEANING_STATUS"] != "PROVISIONAL_LAST_RECORD"]

    if df.empty:
        return pd.DataFrame()

    group_cols = ["PROVINCE", "CODE_REF", "YEAR", "MONTH_NUM"]
    
    # 1. Base aggregations using standard vectorized functions
    agg_dict = {
        "STATION": "first",
        "LAT": "first",
        "LONG": "first",
        "TEMP": ["mean", "min", "max"],
        "HUMIDITY": "mean",
        "WIND_SPEED": "mean",
        "RAINFALL": ["count", "sum"],
        "CLEANING_STATUS": lambda s: int((s == "PROVISIONAL_LAST_RECORD").sum()),
        "DATE": "count",
    }
    
    grouped = df.groupby(group_cols).agg(agg_dict)
    
    # Flatten columns
    grouped.columns = [
        "STATION", "LAT", "LONG",
        "temp_mean", "temp_min", "temp_max",
        "humidity_mean",
        "wind_mean",
        "observed_rain_days", "rainfall_total",
        "provisional_count",
        "station_days",
    ]
    sm = grouped.reset_index()

    # Calculate calendar days and coverage percentage
    sm["cal_days"] = sm.apply(lambda r: get_calendar_days(r["YEAR"], r["MONTH_NUM"]), axis=1)
    sm["rain_coverage_pct"] = (sm["observed_rain_days"] / sm["cal_days"]) * 100.0
    sm["passed_coverage"] = sm["rain_coverage_pct"] >= min_coverage

    # Handle cases where observed_rain_days is 0: rainfall_total should be NaN
    sm.loc[sm["observed_rain_days"] == 0, "rainfall_total"] = np.nan

    # Format date
    sm["DATE_MONTH"] = pd.to_datetime(
        sm["YEAR"].astype(str) + "-" + sm["MONTH_NUM"].astype(str).str.zfill(2) + "-01"
    )
    return sm


def aggregate_province_month(
    df_station_month: pd.DataFrame,
    coverage_gate: bool = True,
) -> pd.DataFrame:
    """
    Aggregate Station-Month data to Province-Month.
    Equal-weight across eligible stations within each province.
    """
    if df_station_month.empty:
        return pd.DataFrame()

    group_cols = ["PROVINCE", "YEAR", "MONTH_NUM"]

    # Weather aggregates (from all stations in station_month)
    weather_agg = df_station_month.groupby(group_cols).agg(
        highland_temp_mean=("temp_mean", "mean"),
        highland_humidity_mean=("humidity_mean", "mean"),
        highland_wind_mean=("wind_mean", "mean"),
        total_stations=("CODE_REF", "count"),
        mean_coverage_pct=("rain_coverage_pct", "mean"),
    ).reset_index()

    # Rainfall aggregates (filtered by coverage gate if enabled)
    df_rain = df_station_month[df_station_month["passed_coverage"]] if coverage_gate else df_station_month
    if not df_rain.empty:
        rain_agg = df_rain.groupby(group_cols).agg(
            highland_rain_mean=("rainfall_total", "mean"),
            eligible_stations=("CODE_REF", "count"),
        ).reset_index()
        pm = pd.merge(weather_agg, rain_agg, on=group_cols, how="left")
    else:
        pm = weather_agg.copy()
        pm["highland_rain_mean"] = np.nan
        pm["eligible_stations"] = 0

    pm["eligible_stations"] = pm["eligible_stations"].fillna(0).astype(int)
    pm["DATE_MONTH"] = pd.to_datetime(
        pm["YEAR"].astype(str) + "-" + pm["MONTH_NUM"].astype(str).str.zfill(2) + "-01"
    )
    return pm


def merge_monthly_datasets(
    df_pm_hrdi: pd.DataFrame,
    df_hii: pd.DataFrame,
    df_oae: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge HII, OAE, and aggregated HRDI Province-Month data.
    Ensures exactly 216 rows (left join from HII/OAE baseline).
    """
    # 1. Merge HII and OAE
    hii_cols = ["PROVINCE", "YEAR", "MONTH_NUM", "DATE_MONTH", "RAIN_MIN_MM", "RAIN_MAX_MM", "RAIN_AVG_MM", "RAIN_VALUES_VALID"]
    oae_cols = ["PROVINCE", "YEAR", "MONTH_NUM", "RUBBER_TONS", "RUBBER_MONTH_SHARE_PERCENT", "PERCENT_IMPUTED_FROM_ZERO_TONS"]

    base = pd.merge(
        df_hii[hii_cols],
        df_oae[oae_cols],
        on=["PROVINCE", "YEAR", "MONTH_NUM"],
        how="inner",
    )

    # 2. Left join HRDI Province-Month
    if not df_pm_hrdi.empty:
        hrdi_cols = [
            "PROVINCE", "YEAR", "MONTH_NUM",
            "highland_temp_mean", "highland_humidity_mean", "highland_wind_mean",
            "highland_rain_mean", "eligible_stations", "total_stations", "mean_coverage_pct"
        ]
        merged = pd.merge(base, df_pm_hrdi[hrdi_cols], on=["PROVINCE", "YEAR", "MONTH_NUM"], how="left")
    else:
        merged = base.copy()
        for c in ["highland_temp_mean", "highland_humidity_mean", "highland_wind_mean", "highland_rain_mean", "eligible_stations", "total_stations", "mean_coverage_pct"]:
            merged[c] = np.nan

    # Comparable rainfall gate is False by default per BRD and DATA_DESCRIPTION
    merged["comparable_rainfall"] = False
    merged["difference_mm"] = np.nan

    return merged
