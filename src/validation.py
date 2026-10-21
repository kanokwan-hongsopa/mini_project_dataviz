"""
Validation and Quality Assurance Module
Performs schema, uniqueness, range, and baseline integrity checks.
"""
from typing import Dict, Any, List
import pandas as pd
from .data_loader import TARGET_PROVINCES, EXPECTED_SHAPES


def validate_hrdi_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate HRDI dataset against baseline and quality rules."""
    report: Dict[str, Any] = {"dataset": "hrdi", "is_valid": True, "errors": [], "warnings": []}

    # Shape
    if df.shape != EXPECTED_SHAPES["hrdi"]:
        report["warnings"].append(f"HRDI shape {df.shape} differs from expected {EXPECTED_SHAPES['hrdi']}")

    # Required columns
    required = ["CODE_REF", "PROVINCE", "DATE", "YEAR", "MONTH_NUM", "TEMP", "HUMIDITY", "WIND_SPEED", "RAINFALL", "CLEANING_STATUS"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        report["errors"].append(f"HRDI missing required columns: {missing}")
        report["is_valid"] = False

    # Key uniqueness: CODE_REF + DATE
    dups = df.duplicated(subset=["CODE_REF", "DATE"]).sum()
    if dups > 0:
        report["errors"].append(f"HRDI has {dups} duplicate CODE_REF + DATE pairs")
        report["is_valid"] = False
    report["unique_code_date_pairs"] = len(df) - dups

    # Province validation
    provinces = set(df["PROVINCE"].dropna().unique())
    invalid_provs = provinces - set(TARGET_PROVINCES)
    if invalid_provs:
        report["warnings"].append(f"HRDI contains unexpected provinces: {invalid_provs}")
    report["province_count"] = len(provinces)

    # Date bounds
    min_date = df["DATE"].min()
    max_date = df["DATE"].max()
    report["date_range"] = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
    report["distinct_dates"] = df["DATE"].nunique()

    # Quality metrics
    report["rainfall_null_count"] = int(df["RAINFALL"].isna().sum())
    report["humidity_null_count"] = int(df["HUMIDITY"].isna().sum())
    report["wind_null_count"] = int(df["WIND_SPEED"].isna().sum())
    report["provisional_count"] = int((df["CLEANING_STATUS"] == "PROVISIONAL_LAST_RECORD").sum())
    report["original_unique_count"] = int((df["CLEANING_STATUS"] == "ORIGINAL_UNIQUE").sum())

    return report


def validate_hii_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate HII dataset against baseline and quality rules."""
    report: Dict[str, Any] = {"dataset": "hii", "is_valid": True, "errors": [], "warnings": []}

    if df.shape != EXPECTED_SHAPES["hii"]:
        report["warnings"].append(f"HII shape {df.shape} differs from expected {EXPECTED_SHAPES['hii']}")

    # Key uniqueness: PROVINCE + YEAR + MONTH_NUM
    dups = df.duplicated(subset=["PROVINCE", "YEAR", "MONTH_NUM"]).sum()
    if dups > 0:
        report["errors"].append(f"HII has {dups} duplicate PROVINCE+YEAR+MONTH_NUM rows")
        report["is_valid"] = False

    # Value order: MIN <= AVG <= MAX
    violating = df[~((df["RAIN_MIN_MM"] <= df["RAIN_AVG_MM"] + 1e-5) & (df["RAIN_AVG_MM"] <= df["RAIN_MAX_MM"] + 1e-5))]
    if len(violating) > 0:
        report["errors"].append(f"HII has {len(violating)} rows where RAIN_MIN <= RAIN_AVG <= RAIN_MAX is violated")
        report["is_valid"] = False

    report["row_count"] = len(df)
    report["null_count"] = int(df.isna().sum().sum())
    return report


def validate_oae_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate OAE dataset against baseline and quality rules."""
    report: Dict[str, Any] = {"dataset": "oae", "is_valid": True, "errors": [], "warnings": []}

    if df.shape != EXPECTED_SHAPES["oae"]:
        report["warnings"].append(f"OAE shape {df.shape} differs from expected {EXPECTED_SHAPES['oae']}")

    dups = df.duplicated(subset=["PROVINCE", "YEAR", "MONTH_NUM"]).sum()
    if dups > 0:
        report["errors"].append(f"OAE has {dups} duplicate PROVINCE+YEAR+MONTH_NUM rows")
        report["is_valid"] = False

    # Non-negative tons
    neg_tons = (df["RUBBER_TONS"] < 0).sum()
    if neg_tons > 0:
        report["errors"].append(f"OAE has {neg_tons} negative RUBBER_TONS values")
        report["is_valid"] = False

    # Percent bounds [0, 100]
    bad_pct = ((df["RUBBER_MONTH_SHARE_PERCENT"] < 0) | (df["RUBBER_MONTH_SHARE_PERCENT"] > 100)).sum()
    if bad_pct > 0:
        report["errors"].append(f"OAE has {bad_pct} percent values outside [0, 100]")
        report["is_valid"] = False

    # Check zero tons
    report["zero_ton_count"] = int((df["RUBBER_TONS"] == 0).sum())
    report["imputed_percent_count"] = int(df["PERCENT_IMPUTED_FROM_ZERO_TONS"].sum()) if "PERCENT_IMPUTED_FROM_ZERO_TONS" in df.columns else 0

    return report


def run_full_validation(df_hrdi: pd.DataFrame, df_hii: pd.DataFrame, df_oae: pd.DataFrame) -> Dict[str, Any]:
    """Run all validation checks and return unified report."""
    hrdi_rep = validate_hrdi_schema(df_hrdi)
    hii_rep = validate_hii_schema(df_hii)
    oae_rep = validate_oae_schema(df_oae)

    all_valid = hrdi_rep["is_valid"] and hii_rep["is_valid"] and oae_rep["is_valid"]
    return {
        "all_valid": all_valid,
        "hrdi": hrdi_rep,
        "hii": hii_rep,
        "oae": oae_rep,
    }
