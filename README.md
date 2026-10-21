# Thailand Highland Climate × Provincial Rainfall × Rubber Yield (2024–2025)
## โครงงาน: การวิเคราะห์ลักษณะทางสถิติและแนวโน้มสภาพภูมิอากาศบนพื้นที่สูงของประเทศไทย ปี 2024–2025 และความสัมพันธ์กับผลผลิตทางการเกษตร

ระบบ Interactive Web Dashboard สำหรับวิเคราะห์ลักษณะทางสถิติ แนวโน้มสภาพภูมิอากาศบนพื้นที่สูง 9 จังหวัด เทียบกับปริมาณน้ำฝนเชิงพื้นที่ระดับจังหวัด และสำรวจความสัมพันธ์กับผลผลิตยางพารา พัฒนาด้วย **Python Backend (Plotly Dash) + Dash Bootstrap Components + Plotly** ตามข้อกำหนดทางธุรกิจและมาตรฐานข้อมูลใน `BRD.md` และ `DATA_DESCRIPTION.md`

---

## 1. วัตถุประสงค์โครงการ (Project Objectives)

1. **สำรวจแนวโน้มและความแปรปรวนของภูมิอากาศพื้นที่สูง (Tab 1):** ติดตามค่าเฉลี่ย ความผันผวน และการกระจายตัวของอุณหภูมิ (`TEMP`), ความชื้นสัมพัทธ์ (`HUMIDITY`), ความเร็วลม (`WIND_SPEED`) และปริมาณน้ำฝน (`RAINFALL`) ระดับสถานีและระดับจังหวัด
2. **วิเคราะห์เปรียบเทียบปริมาณฝนและผลผลิตยางพารา (Tab 2):** เปรียบเทียบฝนเฉลี่ยเชิงพื้นที่ระดับจังหวัด (HII) และผลผลิตยางพารา (OAE) ทั้งในมิติปริมาณรวม (ตัน) และสัดส่วนฤดูกาล (%) ใน 9 จังหวัด
3. **สำรวจความสัมพันธ์เชิงสถิติ (Tab 3):** สำรวจความสัมพันธ์ระหว่างฝนพื้นที่สูง (HRDI) กับฝนระดับจังหวัด (HII) และความสัมพันธ์ระหว่างฝนกับผลผลิตยางพารา (Pearson $r$ และ Spearman $\rho$) พร้อมวิเคราะห์ผลกระทบจากการเหลื่อมเวลา (Time Lag 0–3 เดือน)
4. **ความโปร่งใสและคุณภาพข้อมูล (Data Integrity & Provenance):** บังคับใช้เกณฑ์การคัดกรองคุณภาพข้อมูล (Coverage Threshold $\ge 90\%$, ธง Provisional, การปิดกั้นการลบหน่วยต่างกันโดยมิชอบ) และแสดงข้อจำกัดทางสถิติอย่างชัดเจน ไม่ด่วนสรุปความเป็นเหตุเป็นผล (Correlation $\neq$ Causation)

---

## 2. ทะเบียนแหล่งข้อมูล Open Data (Data Registry)

โครงงานนี้ใช้เฉพาะชุดข้อมูล CSV 3 ไฟล์ที่ผ่านการทำความสะอาด (Data Cleaning) แล้วเท่านั้น โดยไม่มีการสังเคราะห์ข้อมูลเทียม (No Mock Data) หรือเติมค่าว่างโดยพลการ:

| ไฟล์ชุดข้อมูล | หน่วยงานเจ้าของข้อมูล / แหล่งต้นทาง | หน้าระเบียนข้อมูล (Catalog URL) | ระดับข้อมูล (Grain) | จำนวนแถว × คอลัมน์ | หมายเหตุและการตรวจสอบ |
|---|---|---|---|---|---|
| `data/hrdi_clean_provisional.csv` | **สถาบันวิจัยและพัฒนาพื้นที่สูง (องค์การมหาชน) — HRDI** | [data.go.th: ข้อมูลสภาพภูมิอากาศบนพื้นที่สูง](https://data.go.th/dataset/hrdi_met) | สถานี–วัน (Station-Day) | 22,356 แถว × 42 คอลัมน์ | 48 สถานี ใน 9 จังหวัด; ปี 2024 มีข้อมูลเฉพาะ 1 ก.ย. – 31 ธ.ค. (44 สถานี); 6,028 แถวมีสถานะ Provisional; หน่วยฝน/ลมรอการยืนยัน |
| `data/hii_clean.csv` | **สถาบันสารสนเทศทรัพยากรน้ำ (องค์การมหาชน) — HII** | [data.go.th: ปริมาณฝนเชิงพื้นที่ รายเดือน รายจังหวัด](https://data.go.th/dataset/spatial-rain) | จังหวัด–เดือน (Province-Month) | 216 แถว × 9 คอลัมน์ | 9 จังหวัด × 24 เดือน (ม.ค. 2024 – ธ.ค. 2025) ครบถ้วน; หน่วยมิลลิเมตร (IDW) |
| `data/oae_clean.csv` | **สำนักงานเศรษฐกิจการเกษตร — OAE** | [oae.go.th: ร้อยละปริมาณผลผลิตยางพารา รายเดือน](https://catalog.oae.go.th/th/dataset/para_rubber_product_month) | จังหวัด–เดือน (Province-Month) | 216 แถว × 10 คอลัมน์ | 9 จังหวัด × 24 เดือน (ม.ค. 2024 – ธ.ค. 2025); หน่วยตันและร้อยละภายในจังหวัด-ปี; ข้อมูลปี 2025 มีสถานะ Source Verification Pending |

**9 จังหวัดศึกษา:** เชียงใหม่, เชียงราย, น่าน, ตาก, กำแพงเพชร, พิษณุโลก, เพชรบูรณ์, กาญจนบุรี, แม่ฮ่องสอน

---

## 3. สถาปัตยกรรมระบบและโครงสร้างไฟล์ (Project Architecture)

โปรเจกต์ถูกออกแบบตามหลัก Modular Architecture แยกส่วน Logic การประมวลผลข้อมูล, การตรวจสอบคุณภาพ, การสร้างกราฟ และ UI Callbacks ไว้อย่างชัดเจน:

```text
mini_project_dataviz/
├── app.py                     # Entry point หลักของ Dash Web Application
├── requirements.txt           # รายการ Python dependencies (dash, plotly, pandas, scipy, etc.)
├── README.md                  # เอกสารแนะนำและคู่มือการใช้งานระบบ
├── PROJECT_STATUS.md          # รายงานสถานะความคืบหน้าการพัฒนา step-by-step
├── .gitignore                 # กำหนดไฟล์ที่ไม่ติดตามใน Git (venv, __pycache__, ฯลฯ)
├── BRD.md                     # Business Requirements Document (เอกสารข้อกำหนดหลัก)
├── DATA_DESCRIPTION.md       # พจนานุกรมข้อมูลจริง กฎการแปลง และ baseline ทางสถิติ
├── HANDOFF.md                 # เอกสารข้อกำหนดด้าน visualization & data interaction
├── data/                      # ที่เก็บไฟล์ชุดข้อมูล CSV สะอาด 3 ชุด
│   ├── hrdi_clean_provisional.csv
│   ├── hii_clean.csv
│   └── oae_clean.csv
├── assets/                    # Static assets สำหรับ Dash (CSS, custom styling)
│   └── style.css
└── src/                       # โมดูลประมวลผลและตรรกะระบบ
    ├── __init__.py
    ├── data_loader.py         # อ่าน CSV, กำหนด data types, ตรวจสอบ baseline
    ├── validation.py          # ตรวจสอบ Data Quality, Schema QA, ความถูกต้องของคีย์
    ├── aggregation.py         # ETL: Station-Day → Station-Month → Province-Month
    ├── analytics.py           # สถิติวิเคราะห์: Pearson, Spearman, IQR outliers, Wind SD, Lag
    ├── figures.py             # Plotly Figure Generators (T1-01..T1-04, T2-01..T2-04, T3-01..T3-03)
    ├── callbacks.py           # Reactive Dash Callbacks จัดการ Cross-filter State ในแต่ละ Tab
    └── layouts.py             # Dash Layout Components (Header, Global Filters, 3 Tabs, Footer)
```

---

## 4. มาตรฐานข้อมูลและกฎการคำนวณ (Data & Statistical Rules)

1. **การรวมข้อมูลระดับสถานีก่อนเชื่อมโยง (Equal-weight Station Aggregation):**
   - ห้ามนำข้อมูลรายวัน HRDI ไปเชื่อมโยงกับ HII/OAE โดยตรง เพื่อป้องกันการเกิด row fan-out
   - คำนวณค่าเฉลี่ยรายเดือนของแต่ละสถานี (Station-Month) ก่อน
   - คำนวณค่าเฉลี่ยระดับจังหวัด-เดือน โดยเฉลี่ยจากค่าเฉลี่ยของสถานีที่ผ่านเกณฑ์แบบถ่วงน้ำหนักเท่ากัน (Equal-weight per station)
2. **เกณฑ์ความครอบคลุมของข้อมูลฝน (Rainfall Coverage Gate):**
   - คำนวณ `rain_coverage_pct = observed_rain_days / calendar_days * 100`
   - ค่าเริ่มต้นเกณฑ์คัดกรองคือ $\ge 90\%$ ของวันในเดือน หากไม่ผ่านเกณฑ์จะแสดงสถานะ *Insufficient Coverage*
   - ห้ามแทนค่าว่าง (`null`) ด้วย `0` เด็ดขาด
3. **การจัดการช่วงเวลาปี 2024:**
   - ข้อมูล HRDI ปี 2024 เริ่มต้นที่ 1 ก.ย. 2024 ห้ามเติมข้อมูล ม.ค.–ส.ค. เป็น 0
   - การเปรียบเทียบข้ามปี (YoY Fair Comparison) ต้องจำกัดเฉพาะช่วงเดือนที่ตรงกัน (ก.ย.–ธ.ค.) และสถานีร่วมกันเท่านั้น
4. **การควบคุมการเปรียบเทียบฝน (Rainfall Unit Gate):**
   - เนื่องจากหน่วยฝนรายวันของ HRDI ยังรอการยืนยันนิยามสะสม ใน Tab 3 จึงปิดการแสดงผลต่างหน่วยมิลลิเมตร (`difference_mm`) จนกว่าจะมีหลักฐานรับรอง เพื่อป้องกันความคลาดเคลื่อนทางวิชาการ
5. **สถิติความสัมพันธ์ (Correlation Analysis):**
   - รองรับ Pearson correlation ($r$) และ Spearman rank correlation ($\rho$)
   - ต้องมีจำนวนคู่ข้อมูลที่สมบูรณ์ $n \ge 3$ และทั้งสองตัวแปรต้องมีความแปรปรวน (Variance $> 0$) หากไม่เข้าเกณฑ์ให้แสดง `N/A`
   - รองรับการสำรวจผลกระทบจากการหน่วงเวลา (Lag 0–3 เดือน) โดยอิงตามเดือนปฏิทินจริง

---

## 5. ฟังก์ชันการทำงานของ Dashboard (3 Tabs Acceptance Mapping)

### Tab 1 — สภาพภูมิอากาศบนพื้นที่สูง (Highland Climate)
- **T1-01:** กราฟแท่งจัดกลุ่ม/แยกแผง (Grouped Bar / Small Multiples) แสดงค่าเฉลี่ยรายจังหวัดของ `TEMP`, `HUMIDITY`, `WIND_SPEED`
- **T1-02:** กราฟเส้นแนวโน้มรายเดือน (Monthly Multi-line Chart) อุณหภูมิปี 2024–2025 พร้อมเว้นช่วงข้อมูลที่ไม่มีจริง
- **T1-03:** กราฟ Box Plot ฝนพื้นที่สูงรายเดือนและรายจังหวัด พร้อมจุด Outlier ตามเกณฑ์ $1.5 \times \text{IQR}$
- **T1-04:** กราฟ Box/Violin Plot แสดงการกระจายตัวของอุณหภูมิและส่วนเบี่ยงเบนมาตรฐาน (SD)
- **KPIs & Filters:** จำนวนสถานีที่ผ่านเกณฑ์, จำนวนวันบันทึก, อุณหภูมิเฉลี่ย, ความชื้นเฉลี่ย, ลมเฉลี่ย, Coverage เฉลี่ย; ตัวกรองปี, เดือน, จังหวัด, สถานี, สวิตช์รวม/ไม่รวม Provisional, เกณฑ์ Coverage

### Tab 2 — ปริมาณน้ำฝนและผลผลิตยางพารา (Provincial Rainfall & Rubber Yield)
- **T2-01:** กราฟเส้นปริมาณฝนเชิงพื้นที่ HII รายเดือนแยกตามจังหวัด (หน่วย: มม.)
- **T2-02:** กราฟแท่งแนวนอนจัดอันดับ (Ranked Horizontal Bar) ผลผลิตยางพาราและปริมาณฝนรวม
- **T2-03:** กราฟ Heatmap จังหวัด × เดือน แสดงสัดส่วนผลผลิตยาง (`RUBBER_MONTH_SHARE_PERCENT`) และแท่งสรุป 3 เดือนพีค
- **T2-04:** กราฟเส้นแนวโน้มผลผลิตยางพารารายเดือน (ตัน หรือ %)
- **KPIs & Filters:** ปริมาณฝนเฉลี่ย, ผลผลิตยางรวม (ตัน), จังหวัดผลผลิตสูงสุด, เดือนพีคประจำปี; ตัวกรองปี, เดือน, จังหวัด, สลับหน่วยตัน/%

### Tab 3 — การเปรียบเทียบและความสัมพันธ์ (Comparative & Correlation Analysis)
- **T3-01:** กราฟเปรียบเทียบฝน 2 แผง (Dual-panel Line) ระหว่างฝนพื้นที่สูง (HRDI) และฝนระดับจังหวัด (HII) พร้อมการจำกัดสิทธิ์ (Gating)
- **T3-02:** กราฟ Scatter Plot ฝน HII vs ผลผลิตยาง OAE พร้อมเส้นแนวโน้มเชิงพรรณนาและตัวเลือก Time Lag (0–3 เดือน)
- **T3-03:** การ์ดสถิติและกราฟแท่งความสัมพันธ์ Pearson $r$ และ Spearman $\rho$ แยกรายจังหวัดและภาพรวม
- **KPIs & Filters:** จำนวนคู่ข้อมูลสมบูรณ์ ($n$), ค่าสหสัมพันธ์ $r$ และ $\rho$, ข้อความเตือนความสัมพันธ์ไม่ใช่เหตุผล; ตัวกรองปี, จังหวัด, Lag (0–3 เดือน)

---

## 6. ข้อกำหนดการตอบสนองเชื่อมโยง (Cross-filter Interaction Contract)

- **Single Canonical State:** ในแต่ละ Tab ข้อมูลตัวชี้วัด (KPIs) และกราฟทุกชุดจะคำนวณและอัปเดตจากชุดข้อมูลที่ผ่านเงื่อนไขการกรองและการเลือกเดียวกันเสมอ
- **Interactive Selections:** การคลิกจุดบนกราฟ, การเลือกแท่งข้อมูล, หรือการตีกรอบข้อมูล (Box/Lasso Selection) จะส่งผลต่อตัวกรองเฉพาะ Tab นั้นอย่างราบรื่น
- **Clear & Reset:** มีปุ่ม Reset Filter เพื่อคืนค่าเริ่มต้นในทุก Tab ได้ทันที
- **Empty State Handling:** กรณีการกรองไม่พบข้อมูล ระบบจะแสดงการแจ้งเตือน *"ไม่มีข้อมูลตามเงื่อนไขที่เลือก"* แทนการแสดงกราฟว่างหรือค่าศูนย์ที่คลาดเคลื่อน

---

## 7. วิธีการติดตั้งและเปิดใช้งาน (Installation & Setup Guide)

### ความต้องการของระบบ (Prerequisites)
- Python 3.11 หรือใหม่กว่า
- Git

### ขั้นตอนการติดตั้ง
1. Clone หรือเปิดโฟลเดอร์โปรเจกต์:
   ```bash
   cd c:/Users/kanok/OneDrive/เอกสาร/mini_project_dataviz
   ```

2. สร้าง Virtual Environment (แนะนำ):
   ```bash
   python -m venv venv
   # บน Windows:
   venv\Scripts\activate
   ```

3. ติดตั้ง Dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. ตรวจสอบชุดข้อมูลในโฟลเดอร์ `data/`:
   - `data/hrdi_clean_provisional.csv` (22,356 แถว)
   - `data/hii_clean.csv` (216 แถว)
   - `data/oae_clean.csv` (216 แถว)

5. รัน Web Application:
   - **เวอร์ชัน Streamlit (ตามตัวอย่าง Mockup):**
     ```bash
     streamlit run streamlit_app.py
     ```
     เปิดเว็บเบราว์เซอร์ที่: `http://localhost:8501`

   - **เวอร์ชัน Plotly Dash (ตามข้อกำหนด BRD):**
     ```bash
     python app.py
     ```
     เปิดเว็บเบราว์เซอร์ที่: `http://127.0.0.1:8050`

---

## 8. เอกสารอ้างอิงและประกาศข้อจำกัดความรับผิดชอบ (Disclaimers & References)

- **HRDI Open Data:** ข้อมูลสภาพภูมิอากาศบนพื้นที่สูง สถาบันวิจัยและพัฒนาพื้นที่สูง (องค์การมหาชน) [https://data.go.th/dataset/hrdi_met](https://data.go.th/dataset/hrdi_met)
- **HII Open Data:** ชุดข้อมูลปริมาณฝนเชิงพื้นที่ สถาบันสารสนเทศทรัพยากรน้ำ (องค์การมหาชน) [https://data.go.th/dataset/spatial-rain](https://data.go.th/dataset/spatial-rain)
- **OAE Open Data:** ข้อมูลร้อยละและปริมาณผลผลิตยางพารารายเดือน สำนักงานเศรษฐกิจการเกษตร [https://catalog.oae.go.th/th/dataset/para_rubber_product_month](https://catalog.oae.go.th/th/dataset/para_rubber_product_month)

> **ข้อสงวนสิทธิ์ทางวิชาการ:**  
> ข้อมูลทั้งหมดผ่านการทำความสะอาดและประมวลผลสำหรับโครงงานนี้ มิใช่ข้อมูลที่หน่วยงานต้นทางรับรองผลการวิเคราะห์ที่สร้างขึ้นใหม่ ข้อมูลสถานีพื้นที่สูง (HRDI) สะท้อนเฉพาะสภาพแวดล้อมเฉพาะจุดบนภูเขาสูง ไม่ใช่ภาพแทนเชิงพื้นที่ของทั้งจังหวัด ค่าสหสัมพันธ์ทางสถิติ (Correlation) แสดงถึงความสัมพันธ์ร่วมในมิติเวลาและฤดูกาลเท่านั้น มิได้พิสูจน์ถึงความสัมพันธ์เชิงเหตุและผล (Causation)
