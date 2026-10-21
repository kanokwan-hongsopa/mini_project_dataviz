"""
Streamlit Web Application: Rainfall & Agricultural Production Dashboard
วิเคราะห์ความสัมพันธ์ระหว่างปริมาณน้ำฝนและผลผลิตทางการเกษตร รายเดือน รายจังหวัด
Accurately implements the exact 4-view dashboard structure, theme, and visualizations.
"""
import calendar
import json
import unicodedata
import re
import requests
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from src.data_loader import load_all_datasets, TARGET_PROVINCES
from src.aggregation import aggregate_station_month, aggregate_province_month, merge_monthly_datasets
from src.analytics import compute_correlations, compute_lagged_pairs

# -------------------------------------------------------------
# 1. PAGE CONFIG & CUSTOM THEME CSS
# -------------------------------------------------------------
st.set_page_config(
    page_title="Rainfall & Agricultural Production Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS matching the mockup's forest green aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Prompt', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Banner Header */
    .dashboard-banner {
        background: linear-gradient(135deg, #064e3b 0%, #047857 50%, #065f46 100%);
        border-radius: 12px;
        padding: 20px 24px;
        color: white;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 12px rgba(6, 78, 59, 0.2);
    }
    .banner-title {
        font-size: 1.65rem;
        font-weight: 700;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .banner-subtitle {
        font-size: 0.95rem;
        opacity: 0.9;
        margin: 0;
    }
    .banner-slogan {
        background: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 8px 16px;
        border-radius: 9999px;
        font-size: 0.88rem;
        font-style: italic;
        white-space: nowrap;
    }
    
    /* Section Badge Header */
    .section-badge {
        display: inline-block;
        background: #064e3b;
        color: white;
        font-size: 1.05rem;
        font-weight: 600;
        padding: 6px 18px;
        border-radius: 9999px;
        margin-bottom: 16px;
    }
    .section-badge-orange {
        background: #c2410c;
    }
    .section-badge-purple {
        background: #6b21a8;
    }
    .section-badge-blue {
        background: #0369a1;
    }
    
    /* Filter Bar Container */
    .filter-bar-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 20px;
    }
    .kpi-box {
        background: white;
        border-radius: 10px;
        padding: 16px 18px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .kpi-icon {
        width: 48px;
        height: 48px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    .kpi-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748b;
        margin-bottom: 2px;
    }
    .kpi-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 0.78rem;
        margin-top: 2px;
    }
    .kpi-sub-green { color: #16a34a; font-weight: 600; }
    
    /* Info Summary Callout */
    .summary-card {
        border-radius: 8px;
        padding: 12px 18px;
        font-size: 0.88rem;
        margin-top: 14px;
        display: flex;
        gap: 10px;
        align-items: center;
    }
    .summary-blue {
        background: #f0f9ff;
        border-left: 4px solid #0284c7;
        color: #0369a1;
    }
    .summary-orange {
        background: #fff7ed;
        border-left: 4px solid #ea580c;
        color: #9a3412;
    }
    .summary-purple {
        background: #faf5ff;
        border-left: 4px solid #9333ea;
        color: #6b21a8;
    }

    /* Compact, nature-themed dashboard inspired by the supplied reference */
    .stApp {background: #f3f9fc; color: #12304a;}
    .block-container {max-width: 1600px; padding-top: .75rem; padding-bottom: 2rem;}
    [data-testid="stSidebar"] {background: linear-gradient(180deg,#053c42 0%,#075e57 58%,#063b47 100%);}
    [data-testid="stSidebar"] * {color: #f0fffd !important;}
    [data-testid="stSidebar"] [role="radiogroup"] label {padding: .5rem .55rem; border-radius: 9px;}
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {background: #0b8a80;}
    .dashboard-banner {
        background: linear-gradient(90deg,rgba(2,53,54,.96),rgba(3,86,69,.84),rgba(5,73,93,.72)),
                    url('https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?auto=format&fit=crop&w=1800&q=80') center 46%/cover;
        border-radius: 12px; padding: 20px 26px; margin-bottom: 14px;
        border: 1px solid rgba(255,255,255,.18); box-shadow: 0 4px 16px rgba(10,70,78,.14);
    }
    .section-badge {border-radius: 10px 10px 4px 4px; padding: 9px 18px; background:linear-gradient(90deg,#00584e,#0b8676);}
    .section-badge-blue {background:linear-gradient(90deg,#0664a2,#1290cb);}
    .section-badge-orange {background:linear-gradient(90deg,#e36a2d,#fb9651);}
    .section-badge-purple {background:linear-gradient(90deg,#6935b8,#9b5bd5);}
    .kpi-box {min-height:116px; border:1px solid #cde7f0; background:linear-gradient(145deg,#fff,#f1fbfd); border-radius:10px; box-shadow:0 2px 8px rgba(13,87,102,.07);}
    .kpi-number {color:#064e6e; font-size:1.4rem;}
    [data-testid="stVerticalBlockBorderWrapper"] {border-color:#d6e9f3; border-radius:12px;}
    [data-testid="stPlotlyChart"] {background:white; border:1px solid #d7e9f3; border-radius:10px; padding:8px;}
    [data-testid="stDataFrame"] {border:1px solid #d7e9f3; border-radius:10px;}
    [data-testid="stSelectbox"] label,[data-testid="stMultiSelect"] label {color:#075d86; font-weight:600; font-size:.82rem;}
    @media (max-width: 850px) {
      .dashboard-banner {padding:16px;}
      .banner-title {font-size:1.2rem;}
      .banner-slogan {display:none;}
      .kpi-box {min-height:95px;}
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. DATA CACHING & PREPARATION
# -------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_source_data():
    """Load raw source data once; quality settings are applied separately."""
    return load_all_datasets()


@st.cache_data(show_spinner=False)
def get_dashboard_data(min_coverage=90.0, include_provisional=False):
    """Rebuild station/province/monthly joins for the chosen quality gate."""
    df_hrdi, df_hii, df_oae = get_source_data()
    sm = aggregate_station_month(
        df_hrdi, include_provisional=include_provisional,
        min_coverage=float(min_coverage),
    )
    pm = aggregate_province_month(sm, coverage_gate=True)
    merged = merge_monthly_datasets(pm, df_hii, df_oae)
    return sm, pm, merged


df_hrdi, df_hii, df_oae = get_source_data()

# Province Coordinates for Map
PROVINCE_COORDS = {
    "เชียงใหม่": {"lat": 18.7883, "lon": 98.9853},
    "เชียงราย": {"lat": 19.9072, "lon": 99.8325},
    "น่าน": {"lat": 18.7756, "lon": 100.7730},
    "ตาก": {"lat": 16.8837, "lon": 99.1258},
    "กำแพงเพชร": {"lat": 16.4828, "lon": 99.5227},
    "พิษณุโลก": {"lat": 16.8211, "lon": 100.2659},
    "เพชรบูรณ์": {"lat": 16.4190, "lon": 101.1566},
    "กาญจนบุรี": {"lat": 14.0228, "lon": 99.5328},
    "แม่ฮ่องสอน": {"lat": 19.3020, "lon": 97.9654},
}

# Alternate Thai and English province spellings used by ADM1 GeoJSON providers.
PROVINCE_ALIASES = {
    "เชียงใหม่": ("chiang mai", "chiangmai", "chang mai"),
    "เชียงราย": ("chiang rai", "chiangrai", "chang rai"),
    "น่าน": ("nan", "nan province"),
    "ตาก": ("tak", "tak province"),
    "กำแพงเพชร": ("kamphaeng phet", "kamphaengphet", "kamphaeng pet", "kampangphet"),
    "พิษณุโลก": ("phitsanulok", "phitsanuloke", "pitsanulok"),
    "เพชรบูรณ์": ("phetchabun", "phetchaboon", "petchabun"),
    "กาญจนบุรี": ("kanchanaburi", "kanchanaburee"),
    "แม่ฮ่องสอน": ("mae hong son", "maehongson", "mae hong sorn"),
}


def normalize_province_name(value):
    value = unicodedata.normalize("NFKD", str(value or "")).casefold().strip()
    value = re.sub(r"[\W_]+", " ", value, flags=re.UNICODE)
    return " ".join(value.split())


PROVINCE_NAME_LOOKUP = {
    normalize_province_name(alias): province
    for province, aliases in PROVINCE_ALIASES.items()
    for alias in (province, *aliases)
}


def province_from_properties(props):
    """Check all likely name fields, not just the first nonempty one."""
    for key in ("shapeName", "NAME_1", "NAME_1_EN", "name", "NAME", "province",
                "PROVINCE", "PROV_NAM_T", "PROV_NAM_E", "ADM1_EN", "ADM1_TH",
                "name_en", "name_th", "NL_NAME_1", "VARNAME_1"):
        raw = props.get(key)
        if not raw:
            continue
        candidates = re.split(r"[/|,;]", str(raw))
        for candidate in candidates:
            normalized = normalize_province_name(candidate)
            normalized = re.sub(r"^(province|changwat|จังหวัด)\s*", "", normalized)
            normalized = re.sub(r"\s+province$", "", normalized)
            if normalized in PROVINCE_NAME_LOOKUP:
                return PROVINCE_NAME_LOOKUP[normalized]
    return None


def select_nine_provinces(geo):
    """Return the real polygons for the nine provinces, or a diagnostic."""
    features = []
    observed = []
    for feature in geo.get("features", []):
        props = feature.get("properties") or {}
        observed.append(str(props.get("shapeName") or props.get("NAME_1") or props.get("name") or ""))
        province = province_from_properties(props)
        if province in TARGET_PROVINCES and feature.get("geometry"):
            features.append({"type": "Feature", "geometry": feature["geometry"],
                             "properties": {"PROVINCE_TH": province}})
    found = {f["properties"]["PROVINCE_TH"] for f in features}
    missing = set(TARGET_PROVINCES) - found
    if missing:
        return None, ("ไม่พบขอบเขตจังหวัด: " + ", ".join(sorted(missing))
                      + ". ตรวจสอบชื่อฟิลด์และรูปแบบชื่อจังหวัดใน GeoJSON "
                      + f"(ตัวอย่างชื่อที่พบ: {', '.join(observed[:5])})")
    return {"type": "FeatureCollection", "features": features}, None



def geometry_bounds(geometry):
    """Return (min_lon, min_lat, max_lon, max_lat) from Polygon/MultiPolygon."""
    points = []
    def collect(item):
        if isinstance(item, (list, tuple)):
            if len(item) >= 2 and all(isinstance(v, (int, float)) for v in item[:2]):
                lon, lat = item[:2]
                if -180 <= lon <= 180 and -90 <= lat <= 90:
                    points.append((float(lon), float(lat)))
            else:
                for part in item:
                    collect(part)
    collect(geometry.get("coordinates", []))
    if not points:
        raise ValueError("GeoJSON ไม่พบพิกัด Polygon ที่ถูกต้อง")
    return (min(x for x, y in points), min(y for x, y in points),
            max(x for x, y in points), max(y for x, y in points))


def nine_province_bounds(geojson):
    """Calculate a fixed geographic viewport from ALL nine real boundaries."""
    bounds = [geometry_bounds(f["geometry"]) for f in geojson["features"]]
    return (min(b[0] for b in bounds), min(b[1] for b in bounds),
            max(b[2] for b in bounds), max(b[3] for b in bounds))


@st.cache_data(ttl=86400, show_spinner=False)
def get_nine_province_geojson():
    """Prefer real local ADM1 polygons, otherwise retrieve a trusted remote source."""
    from pathlib import Path
    local_dir = Path(__file__).resolve().parent / "data"
    candidates = [local_dir / "thailand_provinces.geojson",
                  local_dir / "thailand_provinces.json",
                  local_dir / "thai_provinces.geojson",
                  local_dir / "thailand_adm1.geojson"]
    errors = []
    for local_path in candidates:
        if local_path.is_file():
            try:
                geo = json.loads(local_path.read_text(encoding="utf-8-sig"))
                result, err = select_nine_provinces(geo)
                if result is not None:
                    return result, None
                errors.append(f"{local_path.name}: {err}")
            except (OSError, ValueError, TypeError) as exc:
                errors.append(f"{local_path.name}: {exc}")
    try:
        api = "https://www.geoboundaries.org/api/current/gbOpen/THA/ADM1/"
        response = requests.get(api, timeout=15)
        response.raise_for_status()
        metadata = response.json()
        for key in ("simplifiedGeometryGeoJSON", "gjDownloadURL"):
            url = metadata.get(key)
            if not url:
                continue
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                result, err = select_nine_provinces(response.json())
                if result is not None:
                    # Persist the real source so subsequent runs work offline.
                    try:
                        local_dir.mkdir(parents=True, exist_ok=True)
                        (local_dir / "thailand_provinces.geojson").write_text(
                            json.dumps(response.json(), ensure_ascii=False), encoding="utf-8")
                    except OSError:
                        pass
                    return result, None
                errors.append(f"geoBoundaries {key}: {err}")
            except (requests.RequestException, ValueError) as exc:
                errors.append(f"geoBoundaries {key}: {exc}")
    except (requests.RequestException, ValueError, KeyError) as exc:
        errors.append(f"เชื่อมต่อ geoBoundaries ไม่ได้: {exc}")
    return None, " | ".join(errors) + " กรุณาวาง GeoJSON ขอบเขตจังหวัดจริง (ADM1) ใน data/thailand_provinces.geojson"


# -------------------------------------------------------------
# 3. TOP BANNER HEADER
# -------------------------------------------------------------
st.markdown("""
<div class="dashboard-banner">
    <div>
        <div class="banner-title">
            <span>🌿</span> Rainfall & Agricultural Production Dashboard
        </div>
        <p class="banner-subtitle">
            วิเคราะห์ความสัมพันธ์ระหว่างปริมาณน้ำฝนและผลผลิตทางการเกษตร รายเดือน รายจังหวัด
        </p>
    </div>
    <div class="banner-slogan">
        "ฝน...ไม่ใช่แค่ปริมาณน้ำ แต่คือจังหวะของผลผลิต" 🍃
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. SIDEBAR NAVIGATION
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧭 เมนูการวิเคราะห์")
    nav_choice = st.radio(
        "เลือกมุมมองที่ต้องการสำรวจ:",
        options=[
            "1. ภาพรวม (Overview)",
            "2. ปริมาณน้ำฝน (Rainfall Comparison)",
            "3. ผลผลิตทางการเกษตร (Agricultural Production)",
            "4. เปรียบเทียบฝนกับผลผลิต (Rainfall & Production)",
        ],
        index=0,
    )
    
    st.markdown("---")
    with st.expander("⚙️ Advanced Settings — คุณภาพข้อมูล", expanded=False):
        min_coverage = st.slider("Rainfall Coverage Gate:", min_value=50, max_value=100, value=90, step=5, format="%d%%")
        include_provisional = st.toggle("รวม HRDI Provisional Records", value=False)
        st.caption("ตัวเลือกนี้คำนวณข้อมูล HRDI ระดับสถานี/เดือนใหม่ และส่งผลต่อกราฟที่ใช้ข้อมูลสรุปดังกล่าว")
    
    st.markdown("---")
    st.markdown("#### 📂 แหล่งข้อมูลต้นทาง")
    st.caption("• **HRDI:** สถาบันวิจัยและพัฒนาพื้นที่สูง")
    st.caption("• **HII:** สถาบันสารสนเทศทรัพยากรน้ำ")
    st.caption("• **OAE:** สำนักงานเศรษฐกิจการเกษตร")
    st.caption("🛡️ ป้องกันความคลาดเคลื่อนทางสถิติ: Correlation ≠ Causation")

# Recalculate HRDI station/month and all dependent aggregates with the selected gate.
sm, pm, merged = get_dashboard_data(min_coverage, include_provisional)

# -------------------------------------------------------------
# 5. GLOBAL FILTER BAR (Common across views)
# -------------------------------------------------------------
with st.container():
    col_yr, col_prov, col_crop, col_season, col_month = st.columns([1.5, 2.5, 1.5, 2, 1.5])
    
    with col_yr:
        selected_years = st.multiselect("ปี (Year)", options=[2024, 2025], default=[2024, 2025])
        if not selected_years:
            st.warning("กรุณาเลือกอย่างน้อยหนึ่งปี")
            
    with col_prov:
        selected_provinces = st.multiselect("จังหวัด (Province)", options=TARGET_PROVINCES, default=TARGET_PROVINCES)
        if not selected_provinces:
            st.warning("กรุณาเลือกอย่างน้อยหนึ่งจังหวัด")
            
    with col_crop:
        selected_crop = st.selectbox("ชนิดพืช (Crop)", options=["ยางพารา (Para Rubber)"], index=0)
        
    with col_season:
        season_choice = st.selectbox(
            "ฤดูกาล (Season)",
            options=["ทั้งหมด", "ฤดูร้อน (มี.ค. - พ.ค.)", "ฤดูฝน (มิ.ย. - ต.ค.)", "ฤดูหนาว (พ.ย. - ก.พ.)"],
            index=0,
        )
        
    with col_month:
        month_options = ["ทั้งหมด"] + [f"เดือน {m}" for m in range(1, 13)]
        month_choice = st.selectbox("เดือน (Month)", options=month_options, index=0)

# Filter logic based on global controls
if month_choice != "ทั้งหมด":
    filtered_months = [int(month_choice.replace("เดือน ", ""))]
elif season_choice == "ฤดูร้อน (มี.ค. - พ.ค.)":
    filtered_months = [3, 4, 5]
elif season_choice == "ฤดูฝน (มิ.ย. - ต.ค.)":
    filtered_months = [6, 7, 8, 9, 10]
elif season_choice == "ฤดูหนาว (พ.ย. - ก.พ.)":
    filtered_months = [11, 12, 1, 2]
else:
    filtered_months = list(range(1, 13))

# Filter merged dataset
df_view = merged[
    (merged["YEAR"].isin(selected_years)) &
    (merged["MONTH_NUM"].isin(filtered_months)) &
    (merged["PROVINCE"].isin(selected_provinces))
].copy()

# Filter HRDI daily & station month
df_hrdi_view = df_hrdi[
    (df_hrdi["YEAR"].isin(selected_years)) &
    (df_hrdi["MONTH_NUM"].isin(filtered_months)) &
    (df_hrdi["PROVINCE"].isin(selected_provinces))
].copy()

sm_view = sm[
    (sm["YEAR"].isin(selected_years)) &
    (sm["MONTH_NUM"].isin(filtered_months)) &
    (sm["PROVINCE"].isin(selected_provinces))
].copy()

# Theme helper for consistent Plotly chart looks
PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Prompt, sans-serif", color="#1e293b", size=12),
    margin=dict(l=42, r=24, t=46, b=46),
)

# =============================================================
# VIEW 1: 1. ภาพรวม (OVERVIEW)
# =============================================================
if nav_choice == "1. ภาพรวม (Overview)":
    st.markdown('<div class="section-badge">1. ภาพรวม (Overview)</div>', unsafe_allow_html=True)
    
    # 4 KPI Cards
    total_rain_val = df_view["RAIN_AVG_MM"].sum() if not df_view.empty else 0.0
    total_rubber_val = df_view["RUBBER_TONS"].sum() if not df_view.empty else 0.0
    
    # Highest rain and rubber provinces
    if not df_view.empty:
        rain_by_p = df_view.groupby("PROVINCE")["RAIN_AVG_MM"].sum()
        max_rain_prov = rain_by_p.idxmax()
        max_rain_amt = rain_by_p.max()
        
        rub_by_p = df_view.groupby("PROVINCE")["RUBBER_TONS"].sum()
        max_rub_prov = rub_by_p.idxmax()
        max_rub_amt = rub_by_p.max()
    else:
        max_rain_prov, max_rain_amt = "-", 0.0
        max_rub_prov, max_rub_amt = "-", 0.0
        
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-icon" style="background: #e0f2fe; color: #0284c7;">💧</div>
            <div>
                <div class="kpi-title">ปริมาณน้ำฝนรวม (ทั้ง {len(selected_provinces)} จังหวัด)</div>
                <div class="kpi-number">{total_rain_val:,.1f} <span style="font-size: 0.9rem; font-weight: normal;">มม.</span></div>
                <div class="kpi-sub kpi-sub-green">↑ ข้อมูลเชิงพื้นที่ HII</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi2:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-icon" style="background: #dcfce7; color: #16a34a;">🍃</div>
            <div>
                <div class="kpi-title">ผลผลิตยางพารารวม (ทั้ง {len(selected_provinces)} จังหวัด)</div>
                <div class="kpi-number">{total_rubber_val:,.0f} <span style="font-size: 0.9rem; font-weight: normal;">ตัน</span></div>
                <div class="kpi-sub kpi-sub-green">↑ ข้อมูลสถิติ OAE</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi3:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-icon" style="background: #e0e7ff; color: #4338ca;">☁️</div>
            <div>
                <div class="kpi-title">จังหวัดที่มีฝนมากที่สุด</div>
                <div class="kpi-number" style="font-size: 1.25rem;">{max_rain_prov}</div>
                <div class="kpi-sub" style="color: #64748b;">{max_rain_amt:,.1f} มม. สะสม</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi4:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-icon" style="background: #fef3c7; color: #d97706;">🌳</div>
            <div>
                <div class="kpi-title">จังหวัดที่มีผลผลิตสูงสุด</div>
                <div class="kpi-number" style="font-size: 1.25rem;">{max_rub_prov}</div>
                <div class="kpi-sub" style="color: #64748b;">{max_rub_amt:,.0f} ตัน รวม</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    # 2 Main Visuals
    c_left, c_right = st.columns([7, 5])
    
    with c_left:
        st.markdown("##### แนวโน้มปริมาณน้ำฝนและผลผลิตรายเดือน (ตามจังหวัดที่เลือก)")
        # Aggregate monthly
        monthly_trend = df_view.groupby(["DATE_MONTH", "YEAR", "MONTH_NUM"], as_index=False).agg(
            rain_sum=("RAIN_AVG_MM", "sum"),
            rubber_sum=("RUBBER_TONS", "sum")
        ).sort_values("DATE_MONTH")
        
        fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Bar: Rain
        fig_combo.add_trace(
            go.Bar(
                x=monthly_trend["DATE_MONTH"],
                y=monthly_trend["rain_sum"],
                name="ฝน HII (มม.)",
                marker_color="#38bdf8",
                opacity=0.85,
                hovertemplate="เดือน: %{x|%Y-%m}<br>ปริมาณฝน: %{y:,.1f} มม.<extra></extra>",
            ),
            secondary_y=False,
        )
        # Line: Rubber
        fig_combo.add_trace(
            go.Scatter(
                x=monthly_trend["DATE_MONTH"],
                y=monthly_trend["rubber_sum"],
                name="ผลผลิตยาง (ตัน)",
                mode="lines+markers",
                line=dict(color="#15803d", width=3),
                marker=dict(size=7, color="#15803d"),
                hovertemplate="เดือน: %{x|%Y-%m}<br>ผลผลิตยาง: %{y:,.0f} ตัน<extra></extra>",
            ),
            secondary_y=True,
        )
        
        fig_combo.update_layout(
            **PLOTLY_THEME,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=430,
        )
        fig_combo.update_yaxes(title_text="ปริมาณฝนรวม (มม.)", secondary_y=False, title_font=dict(color="#0284c7"))
        fig_combo.update_yaxes(title_text="ผลผลิตยางรวม (ตัน)", secondary_y=True, title_font=dict(color="#15803d"))
        st.plotly_chart(fig_combo, use_container_width=True)
        
    with c_right:
        st.markdown("##### ผลผลิตรวมรายจังหวัด (ตัน)")
        # Choropleth: real administrative boundaries of only the nine study provinces.
        # A missing value stays missing (grey); never replace it with zero.
        province_values = (
            df_view.groupby("PROVINCE", as_index=False)["RUBBER_TONS"]
            .sum(min_count=1)
        )
        province_values = province_values[province_values["PROVINCE"].isin(selected_provinces)]
        geojson, geo_error = get_nine_province_geojson()

        if geojson is None:
            st.error(f"ไม่สามารถโหลดขอบเขตแผนที่ 9 จังหวัดได้: {geo_error}")
            st.info("ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต หรือวางไฟล์ GeoJSON ของจังหวัดไทยไว้ที่ data/thailand_provinces.geojson")
        elif not geojson["features"]:
            st.warning("ไม่พบขอบเขต 9 จังหวัดใน GeoJSON ที่โหลดมา")
        else:
            # Always render the complete nine-province study area.
            # Selection only changes highlighting and values, not the map extent.
            map_df = pd.DataFrame({"PROVINCE": list(TARGET_PROVINCES)})
            map_df = map_df.merge(province_values, on="PROVINCE", how="left")
            map_df["SELECTED"] = map_df["PROVINCE"].isin(selected_provinces)
            map_df.loc[~map_df["SELECTED"], "RUBBER_TONS"] = np.nan

            fig_map = go.Figure()
            # Background: all nine provinces in neutral grey (no invented values).
            fig_map.add_trace(go.Choropleth(
                geojson=geojson,
                locations=list(TARGET_PROVINCES),
                featureidkey="properties.PROVINCE_TH",
                z=[1] * len(TARGET_PROVINCES),
                colorscale=[[0, "#e2e8f0"], [1, "#e2e8f0"]],
                zmin=0, zmax=1,
                showscale=False,
                marker_line_color="#ffffff", marker_line_width=1.5,
                hoverinfo="skip", name="ขอบเขต 9 จังหวัด",
            ))
            valid_map_df = map_df.dropna(subset=["RUBBER_TONS"])
            if not valid_map_df.empty:
                fig_map.add_trace(go.Choropleth(
                    geojson=geojson,
                    locations=valid_map_df["PROVINCE"],
                    featureidkey="properties.PROVINCE_TH",
                    z=valid_map_df["RUBBER_TONS"],
                    colorscale=[[0, "#e8f5e9"], [0.35, "#81c784"],
                                [0.7, "#2e7d32"], [1, "#064e3b"]],
                    colorbar=dict(title="ผลผลิต (ตัน)", thickness=12,
                                  len=0.72, x=1.01, xanchor="left"),
                    marker_line_color="#ffffff", marker_line_width=1.5,
                    hovertemplate="<b>%{location}</b><br>ผลผลิตยาง: %{z:,.0f} ตัน<extra></extra>",
                    name="ผลผลิตยางพารา",
                ))

            # Fit the viewport to ALL polygons in the GeoJSON, not only the
            # provinces with valid rubber production. The previous manual
            # lonaxis/lataxis ranges can clip choropleth geometries in Plotly.
            # "geojson" explicitly considers the full feature collection.
            try:
                feature_names = {f["properties"]["PROVINCE_TH"] for f in geojson["features"]}
                if feature_names != set(TARGET_PROVINCES):
                    st.error("GeoJSON มีขอบเขตจังหวัดไม่ครบ 9 จังหวัด: "
                             + ", ".join(sorted(set(TARGET_PROVINCES) - feature_names)))
                    st.stop()
                individual_bounds = [geometry_bounds(f["geometry"]) for f in geojson["features"]]
                # Catch bad GeoJSON where several named features accidentally
                # contain the same polygon.
                if len({tuple(round(v, 4) for v in bounds) for bounds in individual_bounds}) != 9:
                    st.error("GeoJSON มีรูปทรงจังหวัดซ้ำกัน กรุณาตรวจสอบไฟล์ขอบเขตจังหวัด")
                    st.stop()
                fig_map.update_geos(
                    fitbounds="geojson", visible=False,
                    projection_type="mercator",
                    showcoastlines=False, showcountries=False,
                    showland=False, showlakes=False,
                    bgcolor="rgba(0,0,0,0)",
                )
            except (KeyError, ValueError, TypeError) as exc:
                st.error(f"ตรวจสอบขอบเขตแผนที่ไม่ได้: {exc}")
                st.stop()

            fig_map.update_layout(
                **{**PLOTLY_THEME, "margin": dict(l=0, r=24, t=8, b=0)},
                height=480,
                showlegend=False,
                geo=dict(bgcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig_map, use_container_width=True)
            st.caption("แสดงขอบเขตจริงครบ 9 จังหวัด • สีเขียว = ผลผลิตยางจาก OAE ในช่วงที่เลือก • สีเทา = ไม่ได้เลือกหรือไม่มีข้อมูล • ขอบเขต geoBoundaries ADM1")

    st.markdown("""
    <div class="summary-card summary-blue">
        <span>ℹ️</span>
        <div><b>สรุปภาพรวม:</b> กราฟแสดงข้อมูลตามปี จังหวัด และเดือนที่เลือก โปรดตรวจสอบแนวโน้มและค่าจริงจากกราฟก่อนสรุปผล</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================
# VIEW 2: 2. ปริมาณน้ำฝน (RAINFALL COMPARISON)
# =============================================================
elif nav_choice == "2. ปริมาณน้ำฝน (Rainfall Comparison)":
    st.markdown('<div class="section-badge section-badge-blue">2. ปริมาณน้ำฝน (Rainfall Comparison)</div>', unsafe_allow_html=True)
    
    col_t2_1, col_t2_2 = st.columns(2)
    
    with col_t2_1:
        st.markdown("##### เปรียบเทียบปริมาณน้ำฝนรายเดือน (HRDI vs จังหวัด)")
        monthly_rain = df_view.groupby("DATE_MONTH", as_index=False).agg(
            hrdi_rain=("highland_rain_mean", "mean"),
            hii_rain=("RAIN_AVG_MM", "mean"),
        ).sort_values("DATE_MONTH")
        
        fig_r_line = go.Figure()
        fig_r_line.add_trace(go.Scatter(
            x=monthly_rain["DATE_MONTH"],
            y=monthly_rain["hrdi_rain"],
            name="HRDI (พื้นที่สูง)",
            mode="lines+markers",
            line=dict(color="#0284c7", width=2.5),
            marker=dict(size=6),
            hovertemplate="เดือน: %{x|%Y-%m}<br>HRDI: %{y:.1f} (รอตรวจหน่วย)<extra></extra>",
        ))
        fig_r_line.add_trace(go.Scatter(
            x=monthly_rain["DATE_MONTH"],
            y=monthly_rain["hii_rain"],
            name="ระดับจังหวัด (HII)",
            mode="lines+markers",
            line=dict(color="#16a34a", width=2.5),
            marker=dict(size=6),
            hovertemplate="เดือน: %{x|%Y-%m}<br>HII: %{y:.1f} มม.<extra></extra>",
        ))
        fig_r_line.update_layout(
            **PLOTLY_THEME,
            yaxis_title="ปริมาณฝนเฉลี่ย",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=340,
        )
        st.plotly_chart(fig_r_line, use_container_width=True)
        
    with col_t2_2:
        st.markdown("##### ปริมาณน้ำฝนสะสมรายปี (แยกแหล่งข้อมูล)")
        prov_rain = df_view.groupby("PROVINCE", as_index=False).agg(
            hrdi_sum=("highland_rain_mean", "sum"),
            hii_sum=("RAIN_AVG_MM", "sum"),
        ).sort_values("hii_sum", ascending=True)
        
        fig_r_bar = go.Figure()
        fig_r_bar.add_trace(go.Bar(
            y=prov_rain["PROVINCE"],
            x=prov_rain["hrdi_sum"],
            name="HRDI (พื้นที่สูง)",
            orientation="h",
            marker_color="#38bdf8",
        ))
        fig_r_bar.add_trace(go.Bar(
            y=prov_rain["PROVINCE"],
            x=prov_rain["hii_sum"],
            name="ระดับจังหวัด (HII)",
            orientation="h",
            marker_color="#15803d",
        ))
        fig_r_bar.update_layout(
            **PLOTLY_THEME,
            barmode="group",
            xaxis_title="ปริมาณฝนสะสม",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=340,
        )
        st.plotly_chart(fig_r_bar, use_container_width=True)
        
    col_b2_1, col_b2_2, col_b2_3 = st.columns([5, 4, 3])
    
    with col_b2_1:
        st.markdown("##### Heatmap ปริมาณน้ำฝนรายเดือน (HII) (มม.)")
        pivot_rain = df_view.pivot_table(index="PROVINCE", columns="MONTH_NUM", values="RAIN_AVG_MM", aggfunc="mean")
        fig_hmap = go.Figure(data=go.Heatmap(
            z=pivot_rain.values,
            x=[f"ด.{m}" for m in pivot_rain.columns],
            y=pivot_rain.index,
            colorscale="Blues",
            colorbar=dict(title="มม."),
        ))
        fig_hmap.update_layout(**PLOTLY_THEME, height=340)
        st.plotly_chart(fig_hmap, use_container_width=True)
        
    with col_b2_2:
        st.markdown("##### การกระจายของปริมาณน้ำฝน (รายจังหวัด)")
        fig_box = px.box(
            df_view,
            x="PROVINCE",
            y="RAIN_AVG_MM",
            color_discrete_sequence=["#0284c7"],
        )
        fig_box.update_layout(**PLOTLY_THEME, xaxis_tickangle=-45, height=340, yaxis_title="ปริมาณฝน (มม.)")
        st.plotly_chart(fig_box, use_container_width=True)
        
    with col_b2_3:
        st.markdown("""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; height: 100%;">
            <h6 style="color: #0369a1; font-weight: 700; margin-bottom: 8px;">📌 ข้อสังเกตข้อมูลฝน</h6>
            <ul style="font-size: 0.82rem; color: #475569; padding-left: 18px; margin: 0;">
                <li style="margin-bottom: 8px;">ข้อมูลสถานีบนพื้นที่สูง (HRDI) ไม่ได้เป็นตัวแทนปริมาณฝนของทั้งจังหวัด</li>
                <li style="margin-bottom: 8px;">ฝน HII เป็นค่าเฉลี่ยเชิงพื้นที่ด้วยวิธี IDW สำหรับระดับจังหวัด</li>
                <li>ยังคงปิดกั้นการหักลบปริมาณฝนหน่วยมิลลิเมตร HRDI−HII จนกว่าจะได้รับการยืนยันหน่วยสะสมรายวัน</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# =============================================================
# VIEW 3: 3. ผลผลิตทางการเกษตร (AGRICULTURAL PRODUCTION)
# =============================================================
elif nav_choice == "3. ผลผลิตทางการเกษตร (Agricultural Production)":
    st.markdown('<div class="section-badge section-badge-orange">3. ผลผลิตทางการเกษตร (Agricultural Production)</div>', unsafe_allow_html=True)
    
    col_t3_1, col_t3_2, col_t3_3 = st.columns([5, 4, 3])
    
    with col_t3_1:
        st.markdown("##### ปริมาณผลผลิตรายจังหวัด (ตัน)")
        prov_yr_rubber = df_view.groupby(["PROVINCE", "YEAR"], as_index=False)["RUBBER_TONS"].sum()
        fig_yr_bar = px.bar(
            prov_yr_rubber,
            x="PROVINCE",
            y="RUBBER_TONS",
            color="YEAR",
            barmode="group",
            color_discrete_map={2024: "#1e3a8a", 2025: "#16a34a"},
        )
        fig_yr_bar.update_layout(
            **PLOTLY_THEME,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis_title="ผลผลิตยางพารา (ตัน)",
            xaxis_tickangle=-30,
            height=340,
        )
        st.plotly_chart(fig_yr_bar, use_container_width=True)
        
    with col_t3_2:
        st.markdown("##### แนวโน้มผลผลิตรายเดือน (ตามจังหวัดที่เลือก)")
        m_rubber_yr = df_view.groupby(["YEAR", "MONTH_NUM"], as_index=False)["RUBBER_TONS"].sum()
        fig_m_line = px.line(
            m_rubber_yr,
            x="MONTH_NUM",
            y="RUBBER_TONS",
            color="YEAR",
            markers=True,
            color_discrete_map={2024: "#1e3a8a", 2025: "#ea580c"},
        )
        fig_m_line.update_layout(
            **PLOTLY_THEME,
            xaxis=dict(tickmode="linear", tick0=1, dtick=1, title="เดือน"),
            yaxis_title="ผลผลิตยางพารา (ตัน)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=340,
        )
        st.plotly_chart(fig_m_line, use_container_width=True)
        
    with col_t3_3:
        st.markdown("##### สัดส่วนผลผลิตตามจังหวัด (ปี 2024–2025)")
        prov_share = df_view.groupby("PROVINCE", as_index=False)["RUBBER_TONS"].sum()
        fig_tree = px.treemap(
            prov_share,
            path=["PROVINCE"],
            values="RUBBER_TONS",
            color="RUBBER_TONS",
            color_continuous_scale="Blues",
        )
        fig_tree.update_layout(**PLOTLY_THEME, height=340)
        st.plotly_chart(fig_tree, use_container_width=True)
        
    st.markdown("##### ตารางข้อมูลผลผลิตรายเดือน (ตัวอย่าง)")
    pivot_rub = df_view.pivot_table(index="PROVINCE", columns="MONTH_NUM", values="RUBBER_TONS", aggfunc="sum").fillna(0)
    pivot_rub.columns = [f"ด.{m}" for m in pivot_rub.columns]
    st.dataframe(pivot_rub.style.format("{:,.0f}"), use_container_width=True)
    
    st.markdown("""
    <div class="summary-card summary-orange">
        <span>🌾</span>
        <div><b>สรุปผลผลิตยางพารา:</b> แนวโน้มผลผลิตขึ้นอยู่กับจังหวัดและช่วงเวลาที่เลือก โปรดดูกราฟและตรวจสอบหน่วยข้อมูลก่อนสรุป</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================
# VIEW 4: 4. เปรียบเทียบฝนกับผลผลิต (RAINFALL & PRODUCTION)
# =============================================================
elif nav_choice == "4. เปรียบเทียบฝนกับผลผลิต (Rainfall & Production)":
    st.markdown('<div class="section-badge section-badge-purple">4. เปรียบเทียบฝนกับผลผลิต (Rainfall & Production)</div>', unsafe_allow_html=True)
    
    col_t4_1, col_t4_2 = st.columns([7, 5])
    
    with col_t4_1:
        st.markdown("##### ความสัมพันธ์ระหว่างปริมาณน้ำฝนและผลผลิต (รายจังหวัด)")
        # Scatter Rain vs Rubber
        corr_res = compute_correlations(df_view["RAIN_AVG_MM"], df_view["RUBBER_TONS"])
        r_txt = f"r = {corr_res['pearson_r']:.2f}" if corr_res['pearson_r'] is not None else "N/A"
        p_txt = f"p = {corr_res['pearson_p']:.3f}" if corr_res['pearson_p'] is not None else ""
        
        fig_scatter = px.scatter(
            df_view,
            x="RAIN_AVG_MM",
            y="RUBBER_TONS",
            color="PROVINCE",
            trendline="ols" if len(df_view) >= 3 else None,
            labels={"RAIN_AVG_MM": "ปริมาณน้ำฝน HII (มม.)", "RUBBER_TONS": "ผลผลิตยาง (ตัน)", "PROVINCE": "จังหวัด"},
        )
        fig_scatter.add_annotation(
            text=f"<b>ค่าความสัมพันธ์ HII:</b> {r_txt} ({p_txt})",
            xref="paper", yref="paper", x=0.03, y=0.95,
            showarrow=False,
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="#cbd5e1",
        )
        fig_scatter.update_layout(**PLOTLY_THEME, height=360)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_t4_2:
        st.markdown("##### ค่าสัมประสิทธิ์สหสัมพันธ์ (รายจังหวัด)")
        corr_list = []
        for p in selected_provinces:
            p_sub = df_view[df_view["PROVINCE"] == p]
            c_hii = compute_correlations(p_sub["RAIN_AVG_MM"], p_sub["RUBBER_TONS"])
            c_hrdi = compute_correlations(p_sub["highland_rain_mean"], p_sub["RUBBER_TONS"])
            corr_list.append({
                "จังหวัด": p,
                "HRDI (พื้นที่สูง)": c_hrdi["pearson_r"],
                "ระดับจังหวัด (HII)": c_hii["pearson_r"],
            })
        df_corr_table = pd.DataFrame(corr_list).set_index("จังหวัด")
        
        fig_corr_hmap = px.imshow(
            df_corr_table,
            color_continuous_scale="RdBu_r",
            zmin=-1.0, zmax=1.0,
            text_auto=".2f",
            aspect="auto",
        )
        fig_corr_hmap.update_layout(**PLOTLY_THEME, height=360)
        st.plotly_chart(fig_corr_hmap, use_container_width=True)
        
    col_b4_1, col_b4_2, col_b4_3 = st.columns([4, 5, 3])
    
    with col_b4_1:
        st.markdown("##### เปรียบเทียบฝนจากแหล่งข้อมูล (รายจังหวัด)")
        prov_src_rain = df_view.groupby("PROVINCE", as_index=False).agg(
            hrdi_m=("highland_rain_mean", "mean"),
            hii_m=("RAIN_AVG_MM", "mean")
        )
        fig_bar_src = px.bar(
            prov_src_rain,
            x="PROVINCE",
            y=["hrdi_m", "hii_m"],
            barmode="group",
            color_discrete_map={"hrdi_m": "#0284c7", "hii_m": "#16a34a"},
            labels={"value": "ฝนเฉลี่ย", "PROVINCE": "จังหวัด", "variable": "แหล่งข้อมูล"}
        )
        fig_bar_src.update_layout(**PLOTLY_THEME, height=330, showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig_bar_src, use_container_width=True)
        
    with col_b4_2:
        lag_prov = st.selectbox("เลือกจังหวัดสำหรับวิเคราะห์ Lag:", options=selected_provinces, index=0)
        st.markdown(f"##### ฝนย้อนหลัง 1–3 เดือน กับผลผลิต ({lag_prov})")
        
        # Prepare lag 0, 1, 2, 3
        sub_lag_prov = merged[merged["PROVINCE"] == lag_prov].sort_values("DATE_MONTH").reset_index(drop=True)
        
        fig_lag = make_subplots(specs=[[{"secondary_y": True}]])
        # Bar: Rubber
        fig_lag.add_trace(
            go.Bar(
                x=sub_lag_prov["DATE_MONTH"],
                y=sub_lag_prov["RUBBER_TONS"],
                name="ผลผลิตยาง (ตัน)",
                marker_color="#cbd5e1",
                opacity=0.7,
            ),
            secondary_y=False
        )
        # Line: Lag 0
        fig_lag.add_trace(
            go.Scatter(
                x=sub_lag_prov["DATE_MONTH"],
                y=sub_lag_prov["RAIN_AVG_MM"],
                name="ฝนปัจจุบัน (Lag 0)",
                line=dict(color="#0284c7", width=2),
            ),
            secondary_y=True
        )
        # Line: Lag 1
        lag1_series = sub_lag_prov["RAIN_AVG_MM"].shift(1)
        fig_lag.add_trace(
            go.Scatter(
                x=sub_lag_prov["DATE_MONTH"],
                y=lag1_series,
                name="ฝนย้อนหลัง 1 เดือน",
                line=dict(color="#d97706", width=2, dash="dash"),
            ),
            secondary_y=True
        )
        # Line: Lag 2
        lag2_series = sub_lag_prov["RAIN_AVG_MM"].shift(2)
        fig_lag.add_trace(
            go.Scatter(
                x=sub_lag_prov["DATE_MONTH"],
                y=lag2_series,
                name="ฝนย้อนหลัง 2 เดือน",
                line=dict(color="#16a34a", width=2, dash="dot"),
            ),
            secondary_y=True
        )
        
        fig_lag.update_layout(
            **PLOTLY_THEME,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
            height=330,
        )
        fig_lag.update_yaxes(title_text="ผลผลิต (ตัน)", secondary_y=False)
        fig_lag.update_yaxes(title_text="ฝน HII (มม.)", secondary_y=True)
        st.plotly_chart(fig_lag, use_container_width=True)
        
    with col_b4_3:
        st.markdown("""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; height: 100%;">
            <h6 style="color: #6b21a8; font-weight: 700; margin-bottom: 8px;">📊 สรุปผลการวิเคราะห์</h6>
            <ul style="font-size: 0.82rem; color: #475569; padding-left: 18px; margin: 0;">
                <li style="margin-bottom: 8px;">ความแรงของสหสัมพันธ์ต้องประเมินจากค่า r และจำนวนคู่ข้อมูลที่มีจริง</li>
                <li style="margin-bottom: 8px;">กราฟ Lag แสดงฝนย้อนหลังเพื่อสำรวจรูปแบบเท่านั้น ไม่ยืนยันผลกระทบต่อผลผลิต</li>
                <li>ความสัมพันธ์เชิงสถิติ (Correlation) ไม่ได้พิสูจน์ความเป็นเหตุเป็นผล (Causation)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
