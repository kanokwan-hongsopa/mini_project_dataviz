# รายงานสถานะความคืบหน้าโครงการ (PROJECT_STATUS.md)
## โครงงาน: การวิเคราะห์ลักษณะทางสถิติและแนวโน้มสภาพภูมิอากาศบนพื้นที่สูงของประเทศไทย ปี 2024–2025 และความสัมพันธ์กับผลผลิตทางการเกษตร

- **วันที่เริ่มต้น:** 21 ตุลาคม 2026
- **สถานะภาพรวม:** 🚀 In Progress (กำลังดำเนินการพัฒนาตามขั้นตอน)
- **เทคโนโลยีหลัก:** Python 3.11+, Plotly Dash, Dash Bootstrap Components, Pandas, Plotly Express/Graph Objects

---

## 1. ตารางติดตามขั้นตอนการพัฒนา (Implementation Milestones)

| ขั้นตอน (Step) | งานที่ต้องส่งมอบ (Deliverables) | สถานะ (Status) | วันที่/เวลาเสร็จ | หมายเหตุ / ผลการทดสอบ |
|:---|:---|:---:|:---:|:---|
| **Step 1: Project Init** | จัดทำ README.md, requirements.txt, .gitignore, ตรวจสอบ CSV 3 ชุด และ Initial Commit | ✅ เสร็จสิ้น | 2026-10-21 16:25 | ยืนยัน HRDI 22,356 แถว, HII 216 แถว, OAE 216 แถว |
| **Step 2: Data Pipeline** | โมดูล `data_loader.py`, `validation.py`, `aggregation.py` (Station-Month & Province-Month ETL) | ✅ เสร็จสิ้น | 2026-10-21 16:29 | ทดสอบผ่าน 100% (Merged 216 แถว, Coverage Gate >= 90% ทำงานถูกต้อง) |
| **Step 3: Analytics Engine** | โมดูล `analytics.py` (Pearson/Spearman, IQR Boxplot outliers, Wind SD, Time-lag) | 🔄 กำลังดำเนินการ | - | ทดสอบ edge cases (n<3, zero variance) |
| **Step 4: Tab 1 UI & Figures** | Highland Climate: T1-01, T1-02, T1-03, T1-04, KPI cards, filters & linked callbacks | ⏳ รอดำเนินการ | - | Matched-month YoY logic 2024 vs 2025 |
| **Step 5: Tab 2 UI & Figures** | Rain & Rubber: T2-01, T2-02, T2-03, T2-04, KPI cards, filters & unit toggle (Tons/%) | ⏳ รอดำเนินการ | - | Ranked bar, seasonal heatmap |
| **Step 6: Tab 3 UI & Figures** | Comparative & Correlation: T3-01, T3-02, T3-03, scatter, lag 0-3, unit comparison gate | ⏳ รอดำเนินการ | - | Gating difference mm, disclaimers |
| **Step 7: App Integration & QA** | รวม Layout ใน `app.py`, ทดสอบ Acceptance Criteria A01–A12, สรุปผล | ⏳ รอดำเนินการ | - | Full end-to-end smoke test |

---

## 2. การตรวจสอบเกณฑ์การยอมรับ (Acceptance Criteria Checklist)

- [x] **A01: Data Loading & Authenticity** — โหลดข้อมูลจาก `data/*.csv` จริง ไม่ใช้ dummy หรือ mock data
- [x] **A02: Schema & Key Integrity** — ตรวจสอบคีย์และโครงสร้างข้อมูล ไม่พบ row duplication หรือ fan-out
- [ ] **A03: Complete Visual Requirements** — ครบถ้วน 3 Tabs และ 11 Figures (T1-01..T1-04, T2-01..T2-04, T3-01..T3-03)
- [ ] **A04: Reactive Global Filtering** — เมื่อเปลี่ยน ปี/เดือน/จังหวัด ทุก KPI และกราฟใน Tab อัปเดตสอดคล้องกัน
- [ ] **A05: Cross-filter Selection** — คลิกจุด/แท่งกราฟแล้วส่งต่อไปยังตัวกรองภายใน Tab เดียวกัน พร้อมปุ่ม Reset
- [ ] **A06: HRDI 2024 Window Integrity** — ข้อมูลปี 2024 แสดงเฉพาะ ก.ย.–ธ.ค. ไม่เติม ม.ค.–ส.ค. เป็น 0
- [ ] **A07: Missing & Quality Handling** — ค่าว่างไม่ถูกแปลงเป็น 0, มี toggle กรอง Provisional flag
- [ ] **A08: Rubber Metric Integrity** — ยอดรวมยางตันถูกต้อง, สัดส่วน % คำนวณภายในจังหวัด-ปี ไม่บวกข้ามจังหวัด
- [ ] **A09: Rainfall Unit Comparison Gate** — ปิดกั้นการคำนวณผลต่างหน่วยมิลลิเมตร HRDI-HII จนกว่าจะมีหลักฐานยืนยัน
- [ ] **A10: Robust Correlation Math** — Pearson/Spearman แสดง $n$, กรณีข้อมูลไม่พอแสดง `N/A`
- [ ] **A11: Transparency & Provenance** — แสดงลิงก์ Open Data ชัดเจน พร้อมคำเตือน OAE 2025 และ HRDI provisional
- [ ] **A12: Reproducibility & Code Modularity** — โค้ดแบ่งแยกโมดูลอย่างเป็นระเบียบ ติดตั้งและรันได้ตามคู่มือ

---

## 3. บันทึกประวัติการดำเนินงาน (Change Log & Progress History)

### [2026-10-21 16:25] - Step 1: Project Initialization
- วิเคราะห์ข้อกำหนดจาก `BRD.md`, `DATA_DESCRIPTION.md`, และ `HANDOFF.md`
- สกัดและจัดเตรียมไฟล์ชุดข้อมูล CSV จาก Archive ลงโฟลเดอร์ `data/`:
  - `hrdi_clean_provisional.csv` (22,356 แถว × 42 คอลัมน์)
  - `hii_clean.csv` (216 แถว × 9 คอลัมน์)
  - `oae_clean.csv` (216 แถว × 10 คอลัมน์)
- สร้างโครงสร้างโครงการเบื้องต้น: `.gitignore`, `requirements.txt`, `README.md`
- ติดตั้ง dependencies เพิ่มเติม: `dash`, `dash-bootstrap-components`
- บันทึก Git Commit แรกสำหรับเอกสารและโครงสร้างโปรเจกต์

### [2026-10-21 16:29] - Step 2: Data Pipeline Implementation
- พัฒนา `src/data_loader.py`: จัดการ type conversion, dates, baseline assertions และ target provinces
- พัฒนา `src/validation.py`: ระบบ Schema QA, ตรวจ unique keys, baseline constraints, null/provisional counts
- พัฒนา `src/aggregation.py`: Station-Month aggregation, Province-Month equal-weighting, และ HII/OAE merged baseline (216 แถว)
- รันการทดสอบ Unit/Integration test สำหรับ Step 2 ผ่าน 100%

