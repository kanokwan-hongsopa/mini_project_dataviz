"""
Main Entry Point: Thailand Highland Climate × Provincial Rainfall × Rubber Yield Dashboard
Plotly Dash Web Application with Python Backend
"""
import sys
from pathlib import Path
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

from src.data_loader import load_all_datasets
from src.validation import run_full_validation
from src.layouts import (
    create_header,
    create_global_filters,
    create_tab1_layout,
    create_tab2_layout,
    create_tab3_layout,
    create_footer,
)
from src.callbacks import register_callbacks

# 1. Initialize Dash application with modern theme and responsive viewport
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap",
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Thailand Highland Climate Analytics",
    suppress_callback_exceptions=True,
)
server = app.server

# 2. Load and validate baseline datasets
print("🚀 Loading clean datasets...")
df_hrdi, df_hii, df_oae = load_all_datasets()
qa_results = run_full_validation(df_hrdi, df_hii, df_oae)

if not qa_results["all_valid"]:
    print("⚠️ WARNING: Data validation reported potential issues:")
    print(qa_results)
else:
    print("✅ All datasets validated successfully against baseline specifications!")

# 3. Build application layout
app.layout = html.Div(
    id="main-app-container",
    children=[
        create_header(),
        dbc.Container(
            fluid=True,
            children=[
                create_global_filters([]),
                dbc.Tabs(
                    id="dashboard-tabs",
                    active_tab="tab-1",
                    className="nav-tabs mb-4 px-3",
                    children=[
                        dbc.Tab(
                            create_tab1_layout(),
                            tab_id="tab-1",
                            label="⛰️ Tab 1: สภาพภูมิอากาศบนพื้นที่สูง (HRDI)",
                            active_tab_class_name="fw-bold text-primary border-primary border-bottom-0",
                        ),
                        dbc.Tab(
                            create_tab2_layout(),
                            tab_id="tab-2",
                            label="🌧️ Tab 2: ปริมาณน้ำฝนและผลผลิตยางพารา (HII & OAE)",
                            active_tab_class_name="fw-bold text-primary border-primary border-bottom-0",
                        ),
                        dbc.Tab(
                            create_tab3_layout(),
                            tab_id="tab-3",
                            label="🔬 Tab 3: การเปรียบเทียบและความสัมพันธ์ (HRDI × HII × OAE)",
                            active_tab_class_name="fw-bold text-primary border-primary border-bottom-0",
                        ),
                    ],
                ),
            ],
        ),
        create_footer(),
    ],
)

# 4. Register reactive callbacks
register_callbacks(app, df_hrdi, df_hii, df_oae)

if __name__ == "__main__":
    port = 8050
    print(f"🌟 Starting Highland Climate Dashboard on http://127.0.0.1:{port}")
    app.run(debug=False, host="127.0.0.1", port=port)
