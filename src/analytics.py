"""
Analytics Engine Module
Provides statistical functions: Pearson/Spearman correlation, time-lagging,
IQR outlier detection, wind SD, rubber concentration, and matched-months logic.
"""
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats


def compute_correlations(
    x: pd.Series | np.ndarray,
    y: pd.Series | np.ndarray,
) -> Dict[str, Any]:
    """
    Compute Pearson and Spearman correlation coefficients.
    Returns structured dict with n, r, p_value, spearman_rho, spearman_p, and is_valid.
    """
    s_x = pd.Series(x).dropna()
    s_y = pd.Series(y).dropna()

    # Align indexes
    common_idx = s_x.index.intersection(s_y.index)
    val_x = s_x.loc[common_idx].to_numpy(dtype=float)
    val_y = s_y.loc[common_idx].to_numpy(dtype=float)

    # Filter out NaNs/Infs
    mask = np.isfinite(val_x) & np.isfinite(val_y)
    val_x = val_x[mask]
    val_y = val_y[mask]
    n = len(val_x)

    if n < 3:
        return {
            "n": n,
            "pearson_r": None,
            "pearson_p": None,
            "spearman_rho": None,
            "spearman_p": None,
            "is_valid": False,
            "reason": f"ข้อมูลไม่เพียงพอ (n = {n} < 3)",
        }

    var_x = float(np.var(val_x, ddof=1))
    var_y = float(np.var(val_y, ddof=1))

    if var_x == 0 or var_y == 0:
        return {
            "n": n,
            "pearson_r": None,
            "pearson_p": None,
            "spearman_rho": None,
            "spearman_p": None,
            "is_valid": False,
            "reason": "ค่าตัวแปรคงที่ ไม่มีความแปรปรวน (variance = 0)",
        }

    try:
        p_res = stats.pearsonr(val_x, val_y)
        pearson_r = float(p_res.statistic)
        pearson_p = float(p_res.pvalue)
    except Exception:
        pearson_r, pearson_p = None, None

    try:
        s_res = stats.spearmanr(val_x, val_y)
        spearman_rho = float(s_res.statistic)
        spearman_p = float(s_res.pvalue)
    except Exception:
        spearman_rho, spearman_p = None, None

    return {
        "n": n,
        "pearson_r": pearson_r,
        "pearson_p": pearson_p,
        "spearman_rho": spearman_rho,
        "spearman_p": spearman_p,
        "is_valid": (pearson_r is not None),
        "reason": "ปกติ",
    }


def compute_lagged_pairs(
    df_merged: pd.DataFrame,
    lag_months: int = 0,
    provinces: Optional[List[str]] = None,
    year: Optional[int] = None,
) -> pd.DataFrame:
    """
    Generate lagged pairs for Rainfall (HII) vs Rubber Yield (OAE).
    If lag_months = k, rubber yield at month M is paired with rainfall at month M - k
    within the same province.
    """
    df = df_merged.copy()
    if provinces:
        df = df[df["PROVINCE"].isin(provinces)]

    # Sort strictly by province and date
    df = df.sort_values(["PROVINCE", "DATE_MONTH"]).reset_index(drop=True)

    if lag_months == 0:
        res = df[["PROVINCE", "YEAR", "MONTH_NUM", "DATE_MONTH", "RAIN_AVG_MM", "RUBBER_TONS", "RUBBER_MONTH_SHARE_PERCENT"]].copy()
        res["LAGGED_RAIN_MM"] = res["RAIN_AVG_MM"]
        res["lag_display"] = "Lag 0 เดือน (เดือนเดียวกัน)"
    else:
        # Create shifted rain using calendar date continuity
        records = []
        for prov, group in df.groupby("PROVINCE"):
            group = group.sort_values("DATE_MONTH").reset_index(drop=True)
            date_to_rain = dict(zip(group["DATE_MONTH"], group["RAIN_AVG_MM"]))

            for _, row in group.iterrows():
                target_date = row["DATE_MONTH"]
                # Look back k months
                lagged_date = target_date - pd.DateOffset(months=lag_months)
                lagged_rain = date_to_rain.get(lagged_date, np.nan)

                records.append({
                    "PROVINCE": prov,
                    "YEAR": row["YEAR"],
                    "MONTH_NUM": row["MONTH_NUM"],
                    "DATE_MONTH": target_date,
                    "RAIN_AVG_MM": row["RAIN_AVG_MM"],
                    "LAGGED_RAIN_MM": lagged_rain,
                    "RUBBER_TONS": row["RUBBER_TONS"],
                    "RUBBER_MONTH_SHARE_PERCENT": row["RUBBER_MONTH_SHARE_PERCENT"],
                    "lag_display": f"ฝนย้อนหลัง {lag_months} เดือน",
                })
        res = pd.DataFrame(records)

    # Filter year if requested
    if year is not None:
        res = res[res["YEAR"] == year]

    # Filter non-null pairs
    res = res.dropna(subset=["LAGGED_RAIN_MM", "RUBBER_TONS"])
    return res


def compute_iqr_outliers(series: pd.Series) -> Dict[str, Any]:
    """Compute quartiles, IQR, and statistical outlier thresholds."""
    s = series.dropna().to_numpy(dtype=float)
    if len(s) == 0:
        return {
            "n": 0,
            "q1": None,
            "median": None,
            "q3": None,
            "iqr": None,
            "lower_bound": None,
            "upper_bound": None,
            "outlier_count": 0,
        }

    q1, median, q3 = np.percentile(s, [25, 50, 75])
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = s[(s < lower_bound) | (s > upper_bound)]

    return {
        "n": len(s),
        "q1": float(q1),
        "median": float(median),
        "q3": float(q3),
        "iqr": float(iqr),
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound),
        "outlier_count": len(outliers),
    }


def compute_wind_statistics(series: pd.Series) -> Dict[str, Any]:
    """Compute wind speed mean, sample standard deviation (ddof=1), and sample size."""
    s = series.dropna().to_numpy(dtype=float)
    n = len(s)
    if n == 0:
        return {"n": 0, "mean": None, "sd": None, "sem": None}

    mean_val = float(np.mean(s))
    sd_val = float(np.std(s, ddof=1)) if n > 1 else None
    sem_val = float(sd_val / np.sqrt(n)) if sd_val is not None else None

    return {
        "n": n,
        "mean": mean_val,
        "sd": sd_val,
        "sem": sem_val,
    }


def compute_rubber_concentration(df_oae: pd.DataFrame) -> pd.DataFrame:
    """
    Compute peak month and top-3 months concentration ratio for each province and year.
    Only computes for province-years with complete 12 months.
    """
    records = []
    for (prov, yr), group in df_oae.groupby(["PROVINCE", "YEAR"]):
        if len(group) == 12:
            total_tons = group["RUBBER_TONS"].sum()
            if total_tons > 0:
                top3 = group.nlargest(3, "RUBBER_TONS")
                top3_tons = top3["RUBBER_TONS"].sum()
                top3_share = (top3_tons / total_tons) * 100.0
                peak_row = group.loc[group["RUBBER_TONS"].idxmax()]
                peak_month = int(peak_row["MONTH_NUM"])
                peak_tons = float(peak_row["RUBBER_TONS"])
            else:
                top3_share = 0.0
                peak_month = None
                peak_tons = 0.0

            records.append({
                "PROVINCE": prov,
                "YEAR": yr,
                "total_tons": total_tons,
                "top3_tons": top3_tons if total_tons > 0 else 0.0,
                "top3_share_pct": top3_share,
                "peak_month": peak_month,
                "peak_tons": peak_tons,
            })

    return pd.DataFrame(records)


def filter_fair_hrdi_comparison(
    df_hrdi: pd.DataFrame,
    matched_months_only: bool = True,
    matched_stations_only: bool = True,
) -> pd.DataFrame:
    """
    Filter HRDI dataset for fair YoY comparison between 2024 and 2025:
    - 2024 has data only for Sep-Dec (months 9-12).
    - Matched months: only months 9, 10, 11, 12 for both years.
    - Matched stations: only CODE_REFs present in both 2024 and 2025.
    """
    df = df_hrdi.copy()
    if matched_months_only:
        df = df[df["MONTH_NUM"].isin([9, 10, 11, 12])]

    if matched_stations_only:
        st_2024 = set(df[df["YEAR"] == 2024]["CODE_REF"].unique())
        st_2025 = set(df[df["YEAR"] == 2025]["CODE_REF"].unique())
        common_stations = st_2024.intersection(st_2025)
        df = df[df["CODE_REF"].isin(common_stations)]

    return df
