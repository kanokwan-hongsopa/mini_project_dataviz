"""
Layouts Module
Provides layout components: Header, Global Filter Bar, Tab 1, Tab 2, Tab 3, and Footer.
"""
import dash_bootstrap_components as dbc
from dash import dcc, html
from .data_loader import TARGET_PROVINCES


def create_header() -> html.Div:
    """Render application header with provenance badges."""
    return html.Div(
        className="dashboard-header",
        children=[
            dbc.Container(
                fluid=True,
                children=[
                    html.Div(
                        className="d-flex justify-content-between align-items-center flex-wrap gap-2",
                        children=[
                            html.Div([
                                html.H1(
                                    "Thailand Highland Climate × Provincial Rainfall × Rubber Yield (2024–2025)",
                                    className="h3 fw-bold mb-1 text-white",
                                ),
                                html.P(
                                    "การวิเคราะห์ลักษณะทางสถิติและแนวโน้มสภาพภูมิอากาศบนพื้นที่สูง 9 จังหวัด เทียบกับปริมาณน้ำฝนเชิงพื้นที่ และผลผลิตยางพารา",
                                    className="mb-0 text-slate-300 small",
                                ),
                            ]),
                            html.Div(
                                className="d-flex gap-2 flex-wrap",
                                children=[
                                    html.Span("⚠️ HRDI: Provisional Data", className="badge-prov"),
                                    html.Span("ℹ️ OAE 2025: Verification Pending", className="badge-prov"),
                                    html.Span("🛡️ Rainfall Gating: Active", className="badge-gate"),
                                    html.Span("✅ HII: IDW Validated", className="badge-verified"),
                                ]
                            ),
                        ]
                    )
                ]
            )
        ]
    )


def create_global_filters(station_options: list) -> html.Div:
    """Render global filter controls."""
    return html.Div(
        className="filter-section mx-3 mb-4",
        children=[
            dbc.Row(
                className="g-3 align-items-end",
                children=[
                    # Year Selector
                    dbc.Col(
                        md=2, sm=6,
                        children=[
                            html.Label("📅 ปี ค.ศ. (Years):", className="fw-semibold small text-muted mb-1"),
                            dcc.Dropdown(
                                id="global-filter-year",
                                options=[
                                    {"label": "ปี 2024 (HRDI ก.ย.-ธ.ค.)", "value": 2024},
                                    {"label": "ปี 2025 (ครบ 12 เดือน)", "value": 2025},
                                ],
                                value=[2024, 2025],
                                multi=True,
                                placeholder="เลือกปี",
                                clearable=False,
                            ),
                        ]
                    ),
                    # Month Selector
                    dbc.Col(
                        md=3, sm=6,
                        children=[
                            html.Label("🗓️ เดือน (Months):", className="fw-semibold small text-muted mb-1"),
                            dcc.Dropdown(
                                id="global-filter-month",
                                options=[{"label": f"เดือน {m}", "value": m} for m in range(1, 13)],
                                value=list(range(1, 13)),
                                multi=True,
                                placeholder="เลือกเดือน (ทั้งหมด)",
                            ),
                        ]
                    ),
                    # Province Selector
                    dbc.Col(
                        md=4, sm=12,
                        children=[
                            html.Label("📍 จังหวัด (9 Provinces):", className="fw-semibold small text-muted mb-1"),
                            dcc.Dropdown(
                                id="global-filter-province",
                                options=[{"label": p, "value": p} for p in TARGET_PROVINCES],
                                value=TARGET_PROVINCES,
                                multi=True,
                                placeholder="เลือกจังหวัด (ทั้งหมด)",
                            ),
                        ]
                    ),
                    # Reset Button
                    dbc.Col(
                        md=3, sm=12,
                        className="text-end",
                        children=[
                            dbc.Button(
                                "🔄 ล้างตัวกรอง (Reset All Filters)",
                                id="btn-reset-filters",
                                color="light",
                                className="border text-dark fw-semibold small w-100",
                            ),
                        ]
                    ),
                ]
            ),
            html.Hr(className="my-3"),
            # Quality & Coverage Gates
            dbc.Row(
                className="g-3 align-items-center small",
                children=[
                    dbc.Col(
                        md=5,
                        children=[
                            html.Span("เกณฑ์ความครอบคลุมข้อมูลฝน (Rainfall Coverage Gate): ", className="fw-semibold text-muted"),
                            html.Span(id="label-coverage-threshold", className="fw-bold text-primary", children="≥ 90%"),
                            dcc.Slider(
                                id="filter-coverage-threshold",
                                min=50,
                                max=100,
                                step=5,
                                value=90,
                                marks={50: "50%", 70: "70%", 90: "90% (เกณฑ์โครงงาน)", 100: "100%"},
                                className="mt-1",
                            ),
                        ]
                    ),
                    dbc.Col(
                        md=4,
                        children=[
                            dbc.Checklist(
                                id="filter-include-provisional",
                                options=[{"label": " รวมข้อมูลชั่วคราว (Include HRDI Provisional Records)", "value": "include"}],
                                value=[],
                                switch=True,
                                className="fw-semibold text-muted",
                            ),
                            html.Div("ค่าเริ่มต้น: ปิดไว้เพื่อความมั่นใจสูงสุดทางสถิติ", className="text-secondary", style={"fontSize": "0.75rem"}),
                        ]
                    ),
                    dbc.Col(
                        md=3,
                        className="text-end text-muted small",
                        children=[
                            html.Span(id="filter-active-summary", children="กำลังใช้งานตัวกรองมาตรฐาน"),
                        ]
                    ),
                ]
            ),
        ]
    )


def create_kpi_card(title: str, value_id: str, subtitle: str, border_color: str = "#0284c7") -> dbc.Col:
    """Helper to create a standardized KPI metric card."""
    return dbc.Col(
        md=2, sm=4, xs=6,
        children=[
            html.Div(
                className="kpi-card",
                style={"borderLeftColor": border_color},
                children=[
                    html.Div(title, className="kpi-title"),
                    html.Div("...", id=value_id, className="kpi-value"),
                    html.Div(subtitle, className="kpi-subtitle"),
                ]
            )
        ]
    )


# -------------------------------------------------------------
# TAB 1 LAYOUT: HIGHLAND CLIMATE
# -------------------------------------------------------------

def create_tab1_layout() -> html.Div:
    """Tab 1: Highland Climate Analysis."""
    return html.Div(
        className="px-3",
        children=[
            # KPI Cards Row
            dbc.Row(
                className="g-3 mb-4",
                children=[
                    create_kpi_card("สถานีที่ผ่านเกณฑ์", "t1-kpi-stations", "สถานี HRDI", "#0284c7"),
                    create_kpi_card("วันบันทึกข้อมูล", "t1-kpi-days", "วัน (Station-days)", "#0d9488"),
                    create_kpi_card("อุณหภูมิเฉลี่ย", "t1-kpi-temp", "องศาเซลเซียส (°C)", "#ea580c"),
                    create_kpi_card("ความชื้นสัมพัทธ์", "t1-kpi-humidity", "เปอร์เซ็นต์ (%)", "#06b6d4"),
                    create_kpi_card("ความเร็วลมเฉลี่ย", "t1-kpi-wind", "หน่วยตามไฟล์ (รอตรวจ)", "#8b5cf6"),
                    create_kpi_card("Coverage ฝนเฉลี่ย", "t1-kpi-coverage", "เปอร์เซ็นต์วันบันทึก", "#2563eb"),
                ]
            ),
            # Local Control Bar
            dbc.Row(
                className="g-3 mb-3 align-items-center",
                children=[
                    dbc.Col(
                        md=4, sm=6,
                        children=[
                            html.Label("เลือกสถานีตรวจวัดเฉพาะ:", className="fw-semibold small text-muted"),
                            dcc.Dropdown(
                                id="t1-local-station",
                                placeholder="เลือกสถานี (ค่าเริ่มต้น: ทุกสถานีในจังหวัดที่เลือก)",
                                multi=True,
                            ),
                        ]
                    ),
                    dbc.Col(
                        md=3, sm=6,
                        children=[
                            html.Label("รูปแบบกราฟการกระจายอุณหภูมิ:", className="fw-semibold small text-muted"),
                            dbc.RadioItems(
                                id="t1-local-temp-plot-type",
                                options=[
                                    {"label": " Box Plot", "value": "box"},
                                    {"label": " Violin Plot", "value": "violin"},
                                ],
                                value="box",
                                inline=True,
                                className="small",
                            ),
                        ]
                    ),
                    dbc.Col(
                        md=5, sm=12,
                        children=[
                            dbc.Checklist(
                                id="t1-fair-yoy-comparison",
                                options=[{"label": " โหมดเปรียบเทียบข้ามปีอย่างเป็นธรรม (Matched Months ก.ย.-ธ.ค. และสถานีร่วม)", "value": "fair"}],
                                value=[],
                                switch=True,
                                className="fw-semibold small text-muted",
                            ),
                        ]
                    ),
                ]
            ),
            # Charts Row 1: T1-01
            html.Div(
                className="chart-card",
                children=[
                    dcc.Graph(id="fig-t1-01", config={"displayModeBar": True, "displaylogo": False}),
                ]
            ),
            # Charts Row 2: T1-02
            html.Div(
                className="chart-card",
                children=[
                    dcc.Graph(id="fig-t1-02", config={"displayModeBar": True, "displaylogo": False}),
                    html.Div(
                        "ℹ️ สังเกต: ช่วงเดือน ม.ค. – ส.ค. 2024 ไม่มีเส้นกราฟเชื่อมโยง เนื่องจากชุดข้อมูล HRDI เริ่มบันทึกในเดือนกันยายน 2024 จึงไม่มีการเชื่อมข้อมูลเทียมข้ามช่วงที่ขาดหาย",
                        className="text-muted small mt-2 ps-2 border-start border-3 border-info",
                    ),
                ]
            ),
            # Charts Row 3: T1-03 and T1-04
            dbc.Row(
                className="g-3",
                children=[
                    dbc.Col(
                        md=6, sm=12,
                        children=[
                            html.Div(
                                className="chart-card h-100",
                                children=[
                                    dcc.Graph(id="fig-t1-03", config={"displayModeBar": True, "displaylogo": False}),
                                    html.Div(
                                        "📌 จุด Outlier นอกเส้นประแสดงสถานี-เดือนที่มีฝนตกหนักผิดปกติทางสถิติตามเกณฑ์ 1.5 × IQR โดยคำนวณจากสถานีที่ผ่านเกณฑ์ Coverage ≥ 90%",
                                        className="text-muted small mt-1",
                                    ),
                                ]
                            )
                        ]
                    ),
                    dbc.Col(
                        md=6, sm=12,
                        children=[
                            html.Div(
                                className="chart-card h-100",
                                children=[
                                    dcc.Graph(id="fig-t1-04", config={"displayModeBar": True, "displaylogo": False}),
                                    html.Div(
                                        "📌 กราฟแสดงการกระจายตัวของอุณหภูมิรายวันจริงตามสถานีในแต่ละจังหวัด ไม่แทนค่าว่างด้วยศูนย์",
                                        className="text-muted small mt-1",
                                    ),
                                ]
                            )
                        ]
                    ),
                ]
            ),
        ]
    )


# -------------------------------------------------------------
# TAB 2 LAYOUT: PROVINCIAL RAINFALL & RUBBER YIELD
# -------------------------------------------------------------

def create_tab2_layout() -> html.Div:
    """Tab 2: Rainfall and Rubber Yield Analysis."""
    return html.Div(
        className="px-3",
        children=[
            # KPI Cards Row
            dbc.Row(
                className="g-3 mb-4",
                children=[
                    create_kpi_card("ปริมาณฝนสะสม HII", "t2-kpi-rain", "มิลลิเมตร (ตามช่วงกรอง)", "#2563eb"),
                    create_kpi_card("ผลผลิตยางพารารวม", "t2-kpi-rubber", "ตัน (ตามช่วงกรอง)", "#d97706"),
                    create_kpi_card("จังหวัดผลผลิตสูงสุด", "t2-kpi-top-province", "ยางพารา", "#059669"),
                    create_kpi_card("เดือนพีคประจำปี", "t2-kpi-peak-month", "ผลผลิตยางสูงสุด", "#dc2626"),
                    create_kpi_card("จำนวนคู่จังหวัด-เดือน", "t2-kpi-pairs", "ระเบียนที่กรอง", "#64748b"),
                    create_kpi_card("ข้อมูลศูนย์แท้ (0 ตัน)", "t2-kpi-zero-tons", "ระเบียนที่พบ 0 ตัน", "#94a3b8"),
                ]
            ),
            # Provenance Warning
            dbc.Alert(
                [
                    html.B("⚠️ ประกาศการตรวจสอบแหล่งข้อมูลต้นทาง (Provenance Notice): "),
                    "ชุดข้อมูล OAE ปี 2025 ใน CSV มี 108 แถว แต่ในหน้าแค็ตตาล็อก Open Data ทางการระบุระดับจังหวัดถึงปี 2567 (2024) เท่านั้น ข้อมูลปี 2025 จึงอยู่ในสถานะ Source Verification Pending",
                ],
                color="warning",
                className="py-2 small mb-3",
            ),
            # Charts Row 1: T2-01
            html.Div(
                className="chart-card",
                children=[
                    dcc.Graph(id="fig-t2-01", config={"displayModeBar": True, "displaylogo": False}),
                ]
            ),
            # Charts Row 2: T2-02
            html.Div(
                className="chart-card",
                children=[
                    dcc.Graph(id="fig-t2-02", config={"displayModeBar": True, "displaylogo": False}),
                    html.Div(
                        "📌 การจัดอันดับใช้ยอดรวมตามช่วงเวลาที่กรองจริง และแยกแผงระหว่างหน่วย 'ตัน' และ 'มิลลิเมตร' เพื่อป้องกันความสับสนทางหน่วยวัด",
                        className="text-muted small mt-1",
                    ),
                ]
            ),
            # Charts Row 3: T2-03 and T2-04
            dbc.Row(
                className="g-3",
                children=[
                    dbc.Col(
                        md=6, sm=12,
                        children=[
                            html.Div(
                                className="chart-card h-100",
                                children=[
                                    dbc.Row(
                                        className="align-items-center mb-2",
                                        children=[
                                            dbc.Col(html.Span("เลือกปีสำหรับ Heatmap ฤดูกาล:", className="fw-semibold small text-muted"), width="auto"),
                                            dbc.Col(
                                                dbc.RadioItems(
                                                    id="t2-local-heatmap-year",
                                                    options=[{"label": " 2024", "value": 2024}, {"label": " 2025", "value": 2025}],
                                                    value=2025,
                                                    inline=True,
                                                    className="small",
                                                ),
                                                width="auto",
                                            ),
                                        ]
                                    ),
                                    dcc.Graph(id="fig-t2-03", config={"displayModeBar": True, "displaylogo": False}),
                                    html.Div(
                                        "📌 ค่าเปอร์เซ็นต์ใน Heatmap เป็นสัดส่วนภายในจังหวัดและปีเดียวกัน (รวม 12 เดือน = 100%) ห้ามนำเปอร์เซ็นต์ต่างจังหวัดมาบวกกันโดยตรง",
                                        className="text-muted small mt-1",
                                    ),
                                ]
                            )
                        ]
                    ),
                    dbc.Col(
                        md=6, sm=12,
                        children=[
                            html.Div(
                                className="chart-card h-100",
                                children=[
                                    dbc.Row(
                                        className="align-items-center mb-2",
                                        children=[
                                            dbc.Col(html.Span("ตัวชี้วัดเส้นแนวโน้ม:", className="fw-semibold small text-muted"), width="auto"),
                                            dbc.Col(
                                                dbc.RadioItems(
                                                    id="t2-local-metric-type",
                                                    options=[
                                                        {"label": " ปริมาณตัน (Tons)", "value": "tons"},
                                                        {"label": " สัดส่วนร้อยละ (%)", "value": "percent"},
                                                    ],
                                                    value="tons",
                                                    inline=True,
                                                    className="small",
                                                ),
                                                width="auto",
                                            ),
                                        ]
                                    ),
                                    dcc.Graph(id="fig-t2-04", config={"displayModeBar": True, "displaylogo": False}),
                                ]
                            )
                        ]
                    ),
                ]
            ),
        ]
    )


# -------------------------------------------------------------
# TAB 3 LAYOUT: COMPARATIVE & CORRELATION ANALYSIS
# -------------------------------------------------------------

def create_tab3_layout() -> html.Div:
    """Tab 3: Comparative and Correlation Analysis."""
    return html.Div(
        className="px-3",
        children=[
            # KPI Cards Row
            dbc.Row(
                className="g-3 mb-4",
                children=[
                    create_kpi_card("จำนวนคู่ข้อมูล (n)", "t3-kpi-n", "จังหวัด-เดือนที่สมบูรณ์", "#0284c7"),
                    create_kpi_card("Pearson r", "t3-kpi-pearson", "สหสัมพันธ์เชิงเส้น", "#0d9488"),
                    create_kpi_card("Spearman ρ", "t3-kpi-spearman", "สหสัมพันธ์อันดับ", "#8b5cf6"),
                    create_kpi_card("ความต่างฝน HRDI-HII", "t3-kpi-difference", "DISABLED (รอตรวจหน่วย)", "#dc2626"),
                    create_kpi_card("สถานะ Gating", "t3-kpi-gate-status", "ป้องกันหน่วยต่างกัน", "#d97706"),
                    create_kpi_card("Lag ที่เลือก", "t3-kpi-lag-display", "เดือนหน่วงเวลา", "#64748b"),
                ]
            ),
            # Mandatory Rainfall Gating Alert Banner
            dbc.Alert(
                [
                    html.H5("🛡️ การปิดกั้นการคำนวณผลต่างหน่วยมิลลิเมตร (Rainfall Comparison Gated)", className="alert-heading h6 fw-bold mb-1"),
                    html.P(
                        "เนื่องจากหน่วยและนิยามการสะสมฝนรายวันของชุดข้อมูล HRDI ยังไม่ได้รับการยืนยันว่าเป็นมิลลิเมตร/วันสะสม ระบบจึงปิดการแสดงผลต่างเชิงตัวเลข (HRDI − HII ในหน่วย mm) ตามข้อกำหนดใน BRD และ DATA_DESCRIPTION เพื่อป้องกันข้อผิดพลาดทางวิชาการ โดยแสดงกราฟแยกแกน/แยกแผงสำหรับการสำรวจแนวโน้มเท่านั้น",
                        className="mb-0 small",
                    ),
                ],
                color="danger",
                className="mb-3 border-danger",
            ),
            # Local Control Bar: Lag & Trendline
            dbc.Row(
                className="g-3 mb-3 align-items-center",
                children=[
                    dbc.Col(
                        md=4, sm=6,
                        children=[
                            html.Label("สำรวจผลกระทบจากการหน่วงเวลา (Time Lag):", className="fw-semibold small text-muted"),
                            dcc.Dropdown(
                                id="t3-local-lag",
                                options=[
                                    {"label": "Lag 0 เดือน (ฝนและยางเดือนเดียวกัน)", "value": 0},
                                    {"label": "Lag 1 เดือน (ฝนก่อนหน้า 1 เดือน)", "value": 1},
                                    {"label": "Lag 2 เดือน (ฝนก่อนหน้า 2 เดือน)", "value": 2},
                                    {"label": "Lag 3 เดือน (ฝนก่อนหน้า 3 เดือน)", "value": 3},
                                ],
                                value=0,
                                clearable=False,
                            ),
                        ]
                    ),
                    dbc.Col(
                        md=4, sm=6,
                        children=[
                            dbc.Checklist(
                                id="t3-local-trendline",
                                options=[{"label": " แสดงเส้นแนวโน้มเชิงพรรณนา (Descriptive OLS Trendline)", "value": "show"}],
                                value=["show"],
                                switch=True,
                                className="fw-semibold small text-muted mt-3",
                            ),
                        ]
                    ),
                ]
            ),
            # Charts Row 1: T3-01
            html.Div(
                className="chart-card",
                children=[
                    dcc.Graph(id="fig-t3-01", config={"displayModeBar": True, "displaylogo": False}),
                ]
            ),
            # Charts Row 2: T3-02
            html.Div(
                className="chart-card",
                children=[
                    dcc.Graph(id="fig-t3-02", config={"displayModeBar": True, "displaylogo": False}),
                    html.Div(
                        "⚠️ คำเตือนทางสถิติ: Correlation ≠ Causation สหสัมพันธ์ระหว่างฝนกับผลผลิตยางพารารายเดือนที่พบอาจเป็นผลร่วมจากปัจจัยฤดูกาล (Seasonality) และขนาดพื้นที่ปลูกที่ต่างกันของแต่ละจังหวัด มิใช่ข้อพิสูจน์ถึงความสัมพันธ์เชิงเหตุและผล",
                        className="text-danger small mt-2 ps-2 border-start border-3 border-danger fw-semibold",
                    ),
                ]
            ),
            # Charts Row 3: T3-03
            html.Div(
                className="chart-card",
                children=[
                    dcc.Graph(id="fig-t3-03", config={"displayModeBar": True, "displaylogo": False}),
                    html.Div(
                        "📌 หากจำนวนคู่ข้อมูลของจังหวัดใดมี n < 3 หรือไม่มีความแปรปรวน (variance = 0) ระบบจะแสดงสถานะ N/A โดยไม่มีการแทนค่า r = 0 เทียม",
                        className="text-muted small mt-1",
                    ),
                ]
            ),
        ]
    )


def create_footer() -> html.Div:
    """Render footer with data sources, links, and limitations."""
    return html.Footer(
        className="footer-section",
        children=[
            dbc.Container(
                fluid=True,
                children=[
                    dbc.Row(
                        className="g-4",
                        children=[
                            dbc.Col(
                                md=4,
                                children=[
                                    html.H5("เกี่ยวกับโครงงานนี้", className="text-white h6 fw-bold mb-2"),
                                    html.P(
                                        "การวิเคราะห์ลักษณะทางสถิติและแนวโน้มสภาพภูมิอากาศบนพื้นที่สูงของประเทศไทย ปี 2024–2025 และความสัมพันธ์กับผลผลิตทางการเกษตร พัฒนาตาม Business Requirements Document (BRD.md)",
                                        className="small text-slate-400",
                                    ),
                                ]
                            ),
                            dbc.Col(
                                md=5,
                                children=[
                                    html.H5("ทะเบียนแหล่งข้อมูลเปิดภาครัฐ (Open Data)", className="text-white h6 fw-bold mb-2"),
                                    html.Ul(
                                        className="list-unstyled small text-slate-400 mb-0",
                                        children=[
                                            html.Li([
                                                "• HRDI: ",
                                                html.A("ข้อมูลสภาพภูมิอากาศบนพื้นที่สูง (สวพส.)", href="https://data.go.th/dataset/hrdi_met", target="_blank"),
                                                " [Open Data Common]"
                                            ]),
                                            html.Li([
                                                "• HII: ",
                                                html.A("ปริมาณฝนเชิงพื้นที่ รายเดือน รายจังหวัด (สสน.)", href="https://data.go.th/dataset/spatial-rain", target="_blank"),
                                                " [CC BY-NC]"
                                            ]),
                                            html.Li([
                                                "• OAE: ",
                                                html.A("ร้อยละปริมาณผลผลิตยางพารา รายเดือน (สศก.)", href="https://catalog.oae.go.th/th/dataset/para_rubber_product_month", target="_blank"),
                                                " [Non-Commercial]"
                                            ]),
                                        ]
                                    ),
                                ]
                            ),
                            dbc.Col(
                                md=3,
                                children=[
                                    html.H5("ข้อสงวนสิทธิ์ทางวิชาการ", className="text-white h6 fw-bold mb-2"),
                                    html.P(
                                        "ชุดข้อมูลผ่านการทำความสะอาดและประมวลผลสำหรับโครงงานนี้ ไม่ใช่ข้อมูลที่หน่วยงานต้นทางรับรองผลการคำนวณใหม่ และห้ามตีความค่าสหสัมพันธ์เป็นความสัมพันธ์เชิงสาเหตุ",
                                        className="small text-slate-400 mb-0",
                                    ),
                                ]
                            ),
                        ]
                    ),
                    html.Hr(className="border-secondary my-3"),
                    html.Div(
                        "© 2026 Thailand Highland Climate Analytics Dashboard | Built with Python, Plotly Dash & Dash Bootstrap Components",
                        className="text-center text-secondary small",
                    ),
                ]
            )
        ]
    )
