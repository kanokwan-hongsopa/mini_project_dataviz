# HANDOFF — Implementation Specification สำหรับ Interactive HTML Dashboard

**Project:** Thailand Highland Climate × Provincial Rainfall × Rubber Yield (2024–2025)  
**Status:** เอกสารส่งต่อเท่านั้น; **ยังไม่สร้าง Dashboard**  
**อ่าน `DATA_DESCRIPTION.md` ก่อนทุกครั้ง:** มีชื่อคอลัมน์จริง, รายการ null, ความแตกต่างช่วงเวลา, quality flags, แหล่งข้อมูล และข้อจำกัดที่บังคับใช้

## ทะเบียนแหล่งข้อมูล Open Data (ตรวจสอบจากหน้า Catalog วันที่ 21 ตุลาคม 2026)

ข้อมูลทั้งสามชุดมีรายการเผยแพร่บน **พอร์ทัลข้อมูลเปิดภาครัฐ / ระบบบัญชีข้อมูลหน่วยงาน** การระบุว่าเป็น Open Data ในที่นี้หมายถึง *ต้นทางเปิดเผยให้เข้าถึงได้* ไม่ได้หมายความว่าไฟล์ที่ผ่าน Cleaning เป็นสำเนาตรงทุกแถวจากทรัพยากรที่หน้าเว็บเผยแพร่ และต้องปฏิบัติตามสัญญาอนุญาตของแต่ละแหล่ง

| ไฟล์ที่ใช้ในโปรเจกต์ | ชื่อ Open Data / หน่วยงาน | หน้าชุดข้อมูลทางการและทางเข้าไฟล์ต้นทาง | ความถี่และหน่วยที่หน่วยงานอธิบาย | สิทธิการใช้งานที่หน้า Catalog ระบุ | สถานะการตรวจสอบ |
|---|---|---|---|---|---|
| `hrdi_clean_provisional.csv` | [ข้อมูลสภาพภูมิอากาศบนพื้นที่สูง](https://data.go.th/dataset/hrdi_met) — สถาบันวิจัยและพัฒนาพื้นที่สูง (HRDI) | [หน้าชุดข้อมูลและทรัพยากรรายวัน](https://data.go.th/dataset/hrdi_met), [เว็บข้อมูลสภาพอากาศ HRDI](https://weather.hrdi.or.th/) | มีทรัพยากรสถิติรายวัน; หน่วยรายตัวแปรในไฟล์ Cleaning ยังต้องตรวจสอบ | **Open Data Common**; เข้าถึงแบบสาธารณะ | ยืนยันหน้า Open Data ได้ แต่ข้อมูล Cleaning ยังเป็น provisional และหน่วยฝนยังไม่ยืนยัน |
| `hii_clean.csv` | [ปริมาณฝนเชิงพื้นที่](https://data.go.th/dataset/spatial-rain) — สถาบันสารสนเทศทรัพยากรน้ำ (องค์การมหาชน), HII | [หน้าชุดข้อมูล/ทรัพยากร “ปริมาณฝนเชิงพื้นที่ รายเดือน รายจังหวัด”](https://data.go.th/dataset/spatial-rain) | รายเดือนระดับจังหวัด; **มิลลิเมตร (mm)**; วิธี IDW | **Creative Commons Attribution Non-Commercial (CC BY-NC)** | ยืนยันแหล่งชุดข้อมูลและหน่วยได้; ใช้ค่าจาก CSV แนบเท่านั้น |
| `oae_clean.csv` | [ร้อยละปริมาณผลผลิตยางพารา](https://catalog.oae.go.th/th/dataset/para_rubber_product_month) — สำนักงานเศรษฐกิจการเกษตร (OAE) | [หน้าชุดข้อมูล](https://catalog.oae.go.th/th/dataset/para_rubber_product_month), [ทรัพยากรระดับจังหวัด XLSX](https://catalog.oae.go.th/th/dataset/para_rubber_product_month/resource/e5449572-e464-4f28-82ce-183e43fd6ebb) | รายเดือนระดับจังหวัด; **ร้อยละ (%) และตัน** แยกตาม `item`/`unit` | Catalog ระบุ “Creative Commons Attributions Non-Commercial” ใน metadata ระดับชุดข้อมูล แต่หน้าทรัพยากรระบุ “อื่นๆ”; **ต้องตรวจข้อกำหนดฉบับที่ใช้จริง** | **ปี 2025 ยังไม่ยืนยันต้นทาง**: Catalog ระบุทรัพยากรระดับจังหวัดถึงปี 2567 (2024) แต่ CSV มีปี 2025 |

**วิธีดาวน์โหลด/ตรวจสอบ:** เข้า URL หน้าชุดข้อมูลของแต่ละหน่วยงาน แล้วเลือกทรัพยากรรายวัน (HRDI), รายเดือน–รายจังหวัด (HII), หรือ XLSX ระดับจังหวัด (OAE) จากรายการบนหน้านั้น ไม่ใส่ direct-file URL ที่ยังไม่ยืนยัน การแสดง URL มีไว้ให้ตรวจที่มาและอ้างอิง **ห้ามแทนไฟล์ Cleaning ของโครงการด้วยไฟล์ที่เพิ่งดาวน์โหลดโดยอัตโนมัติ**

**รูปแบบการอ้างอิงใน Dashboard:** ทุกแท็บควรแสดง “ที่มา: HRDI / HII / OAE (Open Data)” พร้อมลิงก์ Catalog คลิกได้, ระดับข้อมูล, ช่วงเวลาที่มีจริง, หน่วยและคุณภาพข้อมูล; ที่ Footer มีรายการแหล่งข้อมูลครบสามชุดและระบุว่า “ผ่านการทำความสะอาด/ประมวลผลสำหรับโครงงานนี้” ไม่อ้างว่าหน่วยงานรับรองผลวิเคราะห์ที่คำนวณขึ้นใหม่ และต้องคงหมายเหตุ OAE 2025 และ HRDI provisional ให้เห็นชัดเจน

**ข้อจำกัดสิทธิการใช้ซ้ำ:** แหล่ง HII/OAE ระบุเงื่อนไขแบบไม่ใช้เพื่อการค้า (Non-Commercial) จึงไม่ควรอนุมานว่านำข้อมูลไปใช้เชิงพาณิชย์ได้โดยไม่ขออนุญาต; ให้ใส่เครดิตและลิงก์ตามเงื่อนไขจริงของแหล่งนั้น

## 1. เป้าหมายและกฎเด็ดขาด

พัฒนา Interactive Dashboard ภาษาไทยด้วย **HTML5 + Tailwind CSS + JavaScript + Chart.js** โดยใช้เพียง `hrdi_clean_provisional.csv`, `hii_clean.csv`, `oae_clean.csv` ที่ผู้ใช้ให้มา. ห้ามใช้ข้อมูลตัวอย่าง/จำลอง, hardcode ผลการวิเคราะห์, ใช้ตัวเลขที่แสดงใน mockup แทนผลคำนวณ, เติมช่องว่างด้วยตัวเลข, หรือดึงชุดข้อมูลวิเคราะห์ใหม่. ห้ามอ้างว่า dashboard พิสูจน์เหตุ-ผลได้. ข้อมูล HRDI เป็น provisional; ต้องคงธงคุณภาพและข้อความเตือน. ให้ทำเป็นโค้ดแยกไฟล์เพื่อแก้ต่อได้ง่าย

**Baseline ที่ต้อง assert:** HRDI `22356 × 42`; HII `216 × 9`; OAE `216 × 10`; HRDI 48 `CODE_REF`, 9 จังหวัด, 475 distinct dates (`2024-09-01` ถึง `2025-12-31`); HII/OAE จังหวัด×เดือน 216 แถว. หากไม่ตรง ให้แจ้ง diagnostic ไม่เดาข้อมูล

## 2. โครงสร้างโปรเจกต์แนะนำ

```text
project/
  index.html
  assets/
    styles.css                # optional custom styling
  src/
    main.js                  # init, loading and navigation
    config.js                # labels, color palette, metric metadata
    loadData.js              # CSV loading/parsing (PapaParse optional)
    validateData.js          # schema/QA and warnings
    transform.js             # typed rows, station-month, province-month, joins
    metrics.js               # aggregations, descriptive stats, Pearson/Spearman/IQR
    filters.js               # one global reactive filter state
    charts/
      highland.js            # tab 1
      rubberRain.js          # tab 2
      relationships.js       # tab 3
    ui.js                    # error, empty-state, source notes, accessibility
  data/
    hrdi_clean_provisional.csv
    hii_clean.csv
    oae_clean.csv
  docs/
    DATA_DESCRIPTION.md
    HANDOFF.md
  README.md
```

Tailwind CSS ใช้จัดเลย์เอาต์; Chart.js ใช้กราฟหลัก; อ่าน CSV ใน browser ด้วย `fetch` และ CSV parser เช่น PapaParse ที่รองรับ quote/UTF-8/BOM; ไม่ให้ browser อ่าน CSV ด้วย `split(',')`. เมื่อใช้ `fetch()` ต้องเสิร์ฟด้วย local web server ไม่ใช่เปิด `file://` โดยตรง. อาจใช้ Chart.js plugin สำหรับ boxplots/error bars **เฉพาะการเรนเดอร์** ไม่ใช่ชุดข้อมูลเพิ่ม. ถ้าไม่ใช้ plugin ให้ render สัญลักษณ์ error bars อย่างแม่นยำด้วย custom Chart.js plugin. ไม่จำเป็นต้องมี backend; หลีกเลี่ยงการ embed 22k records เป็น inline HTML ที่ดูแลยาก

## 3. Design direction

Dashboard แนว modern academic/data storytelling: โทนกรมท่า–ฟ้า–เขียวอ่อน, พื้นขาว/เทาอ่อน, ฟอนต์อ่านภาษาไทยชัด (เช่น system UI และ Thai font ที่ได้รับอนุญาต), contrast ดี, ไม่รก. Header หัวข้อโครงงาน + ช่วงเวลา + summary แหล่งข้อมูล; ถัดมา global filter bar, tabs, KPI cards, insight text ที่คำนวณจากข้อมูลจริง, chart grid, data quality & methodology section, footer ลิงก์ที่มา. Responsive desktop/tablet/mobile. ใช้สีแหล่ง HRDI และ HII ตรงกันทุก tab และใช้ legend ทุกกราฟ. แสดง loading, errors และ no data states ชัดเจน

## 4. 3 Tabs และการ mapping คำถาม

### Tab 1 — การวิเคราะห์ภูมิอากาศบนพื้นที่สูง

Q1 แนวโน้ม `TEMP` / `RAINFALL` / `HUMIDITY` / `WIND_SPEED` รายเดือน: line chart และเลือกตัวแปร, จังหวัด, สถานี, ปี; ระบุหน่วยที่ยืนยันแล้วหรือ `หน่วยรอตรวจสอบ`. กรณีเลือกเปรียบเทียบปี ให้ใช้เฉพาะ matched months ก.ย.–ธ.ค. และ matched station IDs ตามสมควร.  
Q5 ฝนผิดปกติ: true boxplot จาก station-month rainfall ที่ผ่าน QA/coverage; label n/Q1/median/Q3/outlier count; no fake boxes.  
Q6 ความชื้น vs ฝน: scatter station-month, tooltip สถานี–เดือน–จังหวัด, Pearson/Spearman เมื่อ n เพียงพอและยืนยัน RAINFALL.  
Q7 ความเร็วลม: bar per month mean station monthly wind ± sample SD พร้อม n.

KPIs: valid station count, observation days, average temp, average humidity, measured rainfall coverage; KPI dynamic. ต้องไม่แทน null เป็น 0

### Tab 2 — การวิเคราะห์ปริมาณน้ำฝนและผลผลิตยางพารา

HII rainfall monthly trend (mm) และ OAE monthly rubber output (ตัน) เป็น **กราฟแยกหน่วย**, ไม่ overlay ด้วยแกนเดียว.  
Q4 Ranking ปี 2025: ฝนสะสมตาม HII `SUM(RAIN_AVG_MM)` และผลผลิตยาง `SUM(RUBBER_TONS)` สำหรับจังหวัดที่ครบ 12 เดือน; chart horizontal ranked bar สองกราฟคนละหน่วย, เห็นสูงสุด/ต่ำสุดจากข้อมูลหลังกรอง.  
ฤดูกาลยาง: monthly line/bar `RUBBER_TONS` และ heatmap จังหวัด×เดือน สำหรับ `RUBBER_MONTH_SHARE_PERCENT` (% ภายในจังหวัด-ปี). หากรวมหลายจังหวัดใช้ตันบวกกันได้ แต่เปอร์เซ็นต์ต้องคำนวณใหม่จากยอดตันรวมของกลุ่มเดียวกัน ไม่ `sum(percent)`. การรวมข้ามปีต้องกำหนดเป็นค่าเฉลี่ยรายเดือนหรือแยกปี ไม่รวมร้อยละโดยไม่อธิบาย.

KPIs: selected HII rainfall, total rubber tons, month count, province count, count of 0-ton records, provenance warning สำหรับ OAE ปี 2025. ไม่เรียกฝนเฉลี่ยรายเดือนเป็นยอดปี

### Tab 3 — การเปรียบเทียบความสัมพันธ์ระหว่างข้อมูล

Q2 paired comparison HRDI highland vs HII province rainfall (เดือนเดียวกัน, จังหวัดเดียวกัน): line 2 series / diverging difference bar หลัง unit & coverage gates.  
Q3 scatter HII `RAIN_AVG_MM` vs OAE `RUBBER_TONS`, filter 2025 เป็นค่าเริ่มต้นสำหรับโจทย์นี้; Pearson/Spearman, n, per-province facet/selection, optional lag 0–3 months.  
Q8 ranking provinces by mean absolute monthly HRDI–HII difference, เฉพาะคู่ที่ผ่าน QA; heatmap จังหวัด×เดือนของ `difference_mm` พร้อม legend หน่วย มม.  
KPI `valid paired months`, `missing/unmatched months`, selected Pearson r หรือ N/A, largest difference with context. **หากหน่วยฝน HRDI ไม่ได้รับการรับรอง ให้ปิดตัวเลขความต่างหน่วย มม. (disabled) พร้อมบอกเหตุผล** แทนการคำนวณเหมือนหน่วยเดียวกัน.

## 5. คำถามทั้ง 8 ข้อ (acceptance mapping)

| Q | จุดตอบ | ต้องมี |
|---|---|---|
| Q1 | Tab 1 | Trend 4 weather variables; monthly data; coverage; correct 2024 window |
| Q2 | Tab 3 | Paired HRDI/HII monthly rainfall + difference with unit gate |
| Q3 | Tab 3 | Rain vs rubber paired scatter + correlation + n + lag optional |
| Q4 | Tab 2 | 2025 rain and rubber rankings separately |
| Q5 | Tab 1 | Genuine monthly rainfall boxplots + IQR outliers |
| Q6 | Tab 1 | Humidity/rain correlation at matched station-month level |
| Q7 | Tab 1 | Wind mean and SD by month |
| Q8 | Tab 3 | Provinces with largest mean absolute rain gap; matching-month counts |

## 6. Pipeline เชิงโค้ด (ห้ามเปลี่ยนลำดับเชิงตรรกะ)

1. `fetch` files → parse CSV → trim strings and handle empty as null → convert numeric/date/bool with explicit rules; record parsing diagnostics. `PRESSURE` อาจมี comma แต่ไม่ได้ใช้เป็น metric หลัก.
2. `validateData`: required column sets, 9 provinces, year/month bounds, month date consistency, code/date uniqueness HRDI; province/year/month uniqueness HII/OAE; flag totals, null/zero distributions; HII rain min≤avg≤max; OAE nonnegative tons, %∈[0,100], per province-year percentage sums to approx 100. Do not silently discard bad rows.
3. `makeStationMonths`: one station+year+month, compute mean TEMP/HUMIDITY/WIND_SPEED; rainfall sum **only with verified daily accumulation definition**; n nonnull, expected days, coverage, selected provisional policy; notes for incomplete periods. In 2024 no data before September.
4. `makeProvinceMonths`: equal-weight station-month values per province (default) with number of eligible stations; keep list of stations / quality flags. Do not average all raw daily rows across provinces.
5. `joinProvinceMonths`: join station aggregates to HII/OAE with `PROVINCE`, `YEAR`, `MONTH_NUM`; may use left join from HII/OAE to reveal months HRDI absent; HII/OAE alone has 216 complete keys, HRDI partial. No multiplication of OAE/HII records.
6. `filterState` → compute derived metrics and chart datasets anew (or cache by stable filter key); use null-safe math; never insert synthetic data for missing periods. Do not connect missing points as if observed.
7. Render with Chart.js; destroy/reuse previous chart instances correctly, update visual states and explanations on filter changes.

Example conceptual data shapes (field names **derived by transformation**, not input CSV columns):

```js
// Keys and computed values, no fabricated observations
stationMonth = {
  province, stationCode, year, month,
  tempMean, humidityMean, windMean, rainfallTotal,
  observedRainDays, expectedDays, rainCoveragePct,
  provisionalRowCount, includedByQualityGate
};
provinceMonth = {
  province, year, month,
  highlandTempMean, highlandHumidityMean, highlandWindMean,
  highlandRainMean, eligibleStationCount,
  hiiRainAvgMm, rubberTons, rubberMonthSharePercent,
  differenceMm, comparableRainfall, flags
};
```

`comparableRainfall` ต้องเป็น false ตราบที่หน่วย/ความหมายฝน HRDI ยังไม่ยืนยัน; ข้อมูลที่อยู่ในไฟล์ยังนำเสนอแบบแยกแหล่งได้โดยไม่บวกหรือลบข้ามแหล่ง

## 7. Filter contract

**Global:** ปี (2024, 2025, หรือเลือกทั้งสอง); เดือน multi-select; จังหวัด multi-select; HRDI provisional policy (`verified-only` default / `include-provisional`), rainfall coverage threshold (default 90%; เป็นมาตรการคัดกรองของโครงการ ไม่ใช่เกณฑ์จากผู้ให้ข้อมูล).  
**Local:** สถานี และ metric (Tab 1); ยางตัน/% และการจัดกลุ่ม (Tab 2); lag 0–3, correlation method, difference/rank mode (Tab 3).  
สภาวะของ filters ต้องมี state เดียวและทุกกราฟ/KPI/ตารางใน tab ที่ active สอดคล้องกัน; cross-filter จาก legend/คลิกจุดทำได้ถ้ากลับคืนได้ง่ายด้วย reset. เมื่อกรองเหลือ 0 จุดแสดง `ไม่มีข้อมูลตามเงื่อนไขที่เลือก`.

เมื่อเลือกหลายจังหวัด: totals ของ `RUBBER_TONS` อาจ sum ได้; ค่าเฉลี่ย rainfall ข้ามจังหวัดเป็น **simple unweighted average ของจังหวัดที่เลือก** และต้องบอกวิธี (ไม่ใช่ฝนเฉลี่ยเชิงพื้นที่รวม 9 จังหวัด). Scatter หนึ่งจุด = หนึ่ง province-month, ไม่เพิ่ม sample size ด้วยการทำซ้ำ row.

## 8. Statistical logic & labels

- Pearson correlation ใช้ covariance/std จาก matched non-null pairs; Spearman ใช้ ranked values (average ranks สำหรับ ties). หาก n<3 หรือ variance=0: `N/A` พร้อมเหตุผล
- IQR Q1, Q3 ที่คำนวณจากชุดข้อมูลคัดกรองเดียวกัน; ระบุ quartile algorithm ของ JS ที่เลือกและใช้ให้คงที่. Count samples และ outlier threshold ตาม `DATA_DESCRIPTION.md`
- Wind error bars ±1 sample SD; SD เมื่อ n=1 = N/A; ยืนยันหน่วยก่อนใส่ใน axis
- Regression line/trendline มีไว้ช่วยสำรวจ ไม่อนุมานสาเหตุ, ไม่อ้าง p-value หากไม่ได้คำนวณอย่างถูกต้อง
- ทุก tooltip มี province/station/month/year, n/coverage, exact value + unit/verification status; ค่า null แสดง `ไม่มีข้อมูล` ไม่เป็น 0
- ระบุแหล่งใต้กราฟเป็น **HRDI / HII / OAE** ตามการใช้จริง และลิงก์ catalog ที่อยู่ใน DATA_DESCRIPTION
- Dashboard ต้องมี persistent disclaimer: HRDI ไม่ใช่ภาพแทนทั้งจังหวัด; OAE 2025 provenance ยังรอยืนยัน; ปี 2024 HRDI มีเฉพาะ ก.ย.–ธ.ค.; ห้ามตีความสัมพันธ์เป็นเหตุ-ผล

## 9. Visualization / technical constraints

Charts ใช้ Chart.js: line, scatter, bar, stacked/grouped bar, heatmap แบบ custom render หรือ plugin, boxplots ผ่าน plugin/custom. Tailwind layout grid และ sidebar/filter bar. ทุกกราฟ legend/tooltip และ keyboard-friendly controls. Charts update on filters, resize and destroy safely. ทุกกราฟใช้จริงจาก CSV; อย่าใส่ hardcoded summary cards ที่ไม่เปลี่ยนตาม filter.

**แผนที่:** ทั้งสาม CSV ไม่มี polygon จังหวัด. ห้ามโหลดขอบเขตแผนที่อื่นโดยพลการ. สามารถใช้ **scatter ตำแหน่งสถานีจริง** ด้วย `LAT`, `LONG` แบบ x-y scatter (ติด label) หรือใช้ bar/heatmap จังหวัดแทน choropleth. หาก requirement ภายหลังต้องการ choropleth จริงให้ทีมจัดหา/อนุมัติ GeoJSON ที่อ้างอิงแหล่งได้ก่อน.

## 10. Development milestones และ acceptance tests

- **M1 Read & Validate:** โหลด 3 CSV และตรวจ baseline; CSV malformed/UTF-8/null/provisional diagnostics ที่เห็นได้
- **M2 Transform:** 1 HRDI station-day key → station-month → province-month; 216 keys HII/OAE; no fanout; year 2024 HRDI no Jan–Aug values
- **M3 Tab 1:** Q1,Q5,Q6,Q7 แสดงจากข้อมูลจริง, quality toggle ทำงาน, coverage ใน tooltip
- **M4 Tab 2:** Q4/ยางฤดูกาล ทำงาน, หน่วยถูกต้อง, no 2024 HRDI contamination
- **M5 Tab 3:** Q2,Q3,Q8 ทำงานหรือ disabled พร้อมเหตุผลถ้าการเทียบหน่วยยังไม่ได้ยืนยัน; n ถูกต้องและ lag ห้ามสร้างเดือนเทียม
- **M6 QA:** เปลี่ยน province/year/month แล้วทุก chart + KPI เปลี่ยนตามจริง; no-data display; reset; responsive; ตรวจ source footnotes; ไม่พบ mock data

**Specific regression tests:**

1. HRDI 2024 บน UI **ไม่มี** Jan–Aug; 2025 ครบทั้ง 12 เดือนตามวันที่ในไฟล์
2. HRDI มี 2,400 ค่า `RAINFALL` null ซึ่งไม่กลายเป็น zero; provisional flag 6,028 แถวแสดงตรงตามการกรอง
3. HII/OAE join ไม่มี fan-out: ทุก province-month เป็นคีย์เดี่ยว; OAE มี 10 zero-ton records และ 2 flagged rows
4. Q4 เมื่อเลือก 2025 และ 9 จังหวัด ใช้ 12 เดือนต่อจังหวัดและ metric คนละหน่วย
5. เมื่อเลือกเทียบปี 2024 vs 2025 ของ HRDI ใช้เดือน ก.ย.–ธ.ค. เหมือนกัน + matched stations หากตั้งโหมด fair comparison
6. ปี 2025 ของ OAE มี warning บน Tab 2/3 เกี่ยวกับ catalog provenance
7. Q2/Q8 difference/rank ไม่มีคำอ้างหน่วย มม. หาก rainfall definition ยังไม่ผ่านการยืนยัน

## 11. Done criteria

ส่งมอบ `index.html` + แยก JavaScript modules / CSS ตามโครงสร้าง, `README.md` วิธีเปิดด้วย local server, อ้างอิง `DATA_DESCRIPTION.md`, metadata/notes, และ test log. Dashboard แสดง Q1–Q8 ใน 3 tabs, โต้ตอบได้, ไม่มี data fabrication และมีคำเตือนตามจริง. **เอกสารฉบับนี้ยังไม่ได้สั่งให้สร้างผลลัพธ์เหล่านั้นในขั้นตอนปัจจุบัน**.
