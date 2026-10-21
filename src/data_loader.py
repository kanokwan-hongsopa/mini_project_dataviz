"""
Data Loader Module
Reads and standardizes CSV data files for HRDI, HII, and OAE.
"""
from pathlib import Path
from typing import Dict, Tuple
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

TARGET_PROVINCES = [
    "เชียงใหม่",
    "เชียงราย",
    "น่าน",
    "ตาก",
    "กำแพงเพชร",
    "พิษณุโลก",
    "เพชรบูรณ์",
    "กาญจนบุรี",
    "แม่ฮ่องสอน",
]

EXPECTED_SHAPES = {
    "hrdi": (22356, 42),
    "hii": (216, 9),
    "oae": (216, 10),
}


def load_hrdi(data_path: Path | str | None = None) -> pd.DataFrame:
    """Load HRDI highland climate station-day dataset."""
    path = Path(data_path) if data_path else DATA_DIR / "hrdi_clean_provisional.csv"
    if not path.exists():
        raise FileNotFoundError(f"HRDI data file not found at {path}")

    df = pd.read_csv(
        path,
        dtype={
            "CODE_REF": str,
            "PRESSURE": str,
            "PROVINCE": str,
            "STATION": str,
            "STA_TH": str,
        },
        low_memory=False,
    )

    # Standardize string fields
    for col in ["PROVINCE", "CODE_REF", "STATION", "STA_TH", "DATA_SOURCE"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Convert dates and numeric types
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
    df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce").astype("Int64")
    df["MONTH_NUM"] = pd.to_numeric(df["MONTH_NUM"], errors="coerce").astype("Int64")
    df["DAY"] = pd.to_numeric(df["DAY"], errors="coerce").astype("Int64")

    numeric_cols = [
        "TEMP", "TEMP_MIN", "TEMP_MAX", "HUMIDITY",
        "WIND_SPEED", "WIND_DEG", "RAINFALL", "RAINDAY",
        "PRESSURE_HPA", "DEW_POINT", "FEELS_LIKE", "CLOUDS",
        "LAT", "LONG"
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Boolean columns
    bool_cols = ["WAS_DUPLICATE_KEY", "TEMP_ORDER_VALID", "RAIN_MISSING", "NEEDS_SOURCE_VERIFICATION"]
    for b in bool_cols:
        if b in df.columns:
            df[b] = df[b].astype(bool)

    return df


def load_hii(data_path: Path | str | None = None) -> pd.DataFrame:
    """Load HII provincial spatial rainfall dataset."""
    path = Path(data_path) if data_path else DATA_DIR / "hii_clean.csv"
    if not path.exists():
        raise FileNotFoundError(f"HII data file not found at {path}")

    df = pd.read_csv(path)
    df["PROVINCE"] = df["PROVINCE"].astype(str).str.strip()
    df["DATE_MONTH"] = pd.to_datetime(df["DATE_MONTH"], errors="coerce")
    df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce").astype("Int64")
    df["MONTH_NUM"] = pd.to_numeric(df["MONTH_NUM"], errors="coerce").astype("Int64")

    for col in ["RAIN_MIN_MM", "RAIN_MAX_MM", "RAIN_AVG_MM"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if "RAIN_VALUES_VALID" in df.columns:
        df["RAIN_VALUES_VALID"] = df["RAIN_VALUES_VALID"].astype(bool)

    return df


def load_oae(data_path: Path | str | None = None) -> pd.DataFrame:
    """Load OAE provincial rubber yield dataset."""
    path = Path(data_path) if data_path else DATA_DIR / "oae_clean.csv"
    if not path.exists():
        raise FileNotFoundError(f"OAE data file not found at {path}")

    df = pd.read_csv(path)
    df["PROVINCE"] = df["PROVINCE"].astype(str).str.strip()
    df["DATE_MONTH"] = pd.to_datetime(df["DATE_MONTH"], errors="coerce")
    df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce").astype("Int64")
    df["MONTH_NUM"] = pd.to_numeric(df["MONTH_NUM"], errors="coerce").astype("Int64")

    df["RUBBER_TONS"] = pd.to_numeric(df["RUBBER_TONS"], errors="coerce")
    df["RUBBER_MONTH_SHARE_PERCENT"] = pd.to_numeric(df["RUBBER_MONTH_SHARE_PERCENT"], errors="coerce")

    bool_cols = ["PERCENT_IMPUTED_FROM_ZERO_TONS", "RUBBER_TONS_VALID", "RUBBER_PERCENT_VALID"]
    for b in bool_cols:
        if b in df.columns:
            df[b] = df[b].astype(bool)

    return df


def load_all_datasets(data_dir: Path | str | None = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all three datasets and verify shapes."""
    base = Path(data_dir) if data_dir else DATA_DIR
    df_hrdi = load_hrdi(base / "hrdi_clean_provisional.csv")
    df_hii = load_hii(base / "hii_clean.csv")
    df_oae = load_oae(base / "oae_clean.csv")

    return df_hrdi, df_hii, df_oae
