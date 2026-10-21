# Business Requirements Document (BRD)

## โครงงาน: การวิเคราะห์ลักษณะทางสถิติและแนวโน้มสภาพภูมิอากาศบนพื้นที่สูงของประเทศไทย ปี 2024–2025 และความสัมพันธ์กับผลผลิตทางการเกษตร

**เวอร์ชัน:** 1.0 | **วันที่:** 21 ตุลาคม 2026  
**สำหรับ:** ส่งต่อ Antigravity เพื่อพัฒนา Dashboard ด้วย **Python Backend + Plotly**  
**สถานะ:** ข้อกำหนดพัฒนาจากข้อมูลที่แนบจริง ยังไม่ได้พัฒนา Dashboard ตาม BRD นี้  
**เอกสารอ้างอิงภายใน:** `DATA_DESCRIPTION.md`, `HANDOFF.md` (เอกสารก่อนหน้านี้อาจใช้ Chart.js; **ให้ BRD นี้มีลำดับความสำคัญเหนือกว่าในส่วนเทคโนโลยี**)

---

## 1. ความเป็นมาและเป้าหมายธุรกิจ (Business Context)

ต้องการวิเคราะห์สภาพภูมิอากาศจากสถานีพื้นที่สูงใน 9 จังหวัด เทียบกับฝนเฉลี่ยรายเดือนระดับจังหวัด และสำรวจรูปแบบฤดูกาลของผลผลิตยางพารา เพื่อสื่อสารความแตกต่างเชิงพื้นที่/เวลา รวมถึง **ความสัมพันธ์เชิงสถิติ ไม่ใช่การอ้างเหตุและผล** จาก Open Data ที่ทีมทำความสะอาดแล้วเท่านั้น

**เป้าหมายหลัก**
1. สำรวจแนวโน้ม ค่าเฉลี่ย ความแปรปรวน และเหตุการณ์สูงผิดปกติของภูมิอากาศระดับสถานี/จังหวัด
2. เปรียบเทียบการกระจายฝนรายเดือนและผลผลิตยางพาราใน 9 จังหวัดอย่างตรวจสอบได้
3. เปรียบเทียบ **รูปแบบ** ฝน HRDI กับ HII โดยไม่ตีความว่าเป็นเครื่องวัดพื้นที่เดียวกัน
4. ตรวจสอบ Pearson/Spearman correlation ระหว่างฝน HII กับยาง OAE ภายใต้ตัวกรองเดียวกัน พร้อมจำนวนคู่ข้อมูลและข้อจำกัด
5. ให้ผู้ใช้สำรวจข้อมูลด้วยการเลือกจากกราฟและกรองข้อมูล โดยกราฟทั้งหมดใน **Tab เดียวกันต้องอัปเดตตาม selection/filter เดียวกัน**

**ผู้ใช้เป้าหมาย:** นักศึกษา อาจารย์ และผู้สนใจสภาพภูมิอากาศ/เกษตร  
**ผลลัพธ์:** เว็บ Dashboard 3 Tabs พร้อม Python backend, Plotly interactive figures, คำอธิบายวิธีคำนวณ/ที่มาข้อมูล/ข้อจำกัด และคู่มือรัน

## 2. ขอบเขตข้อมูล (Data Scope)

ใช้ **เฉพาะไฟล์ CSV แนบมา** ไม่ดาวน์โหลดไฟล์ใหม่ ไม่สร้าง mock/synthetic data ไม่เติมค่าว่างเอง

| ไฟล์ | Grain / ขนาดจริง | เวลาและความครอบคลุม | ตัวแปรสำคัญ |
|---|---|---|---|
| `hrdi_clean_provisional.csv` | สถานี-วัน; **22,356 แถว × 42 คอลัมน์**, 48 สถานี | **1 ก.ย. 2024 – 31 ธ.ค. 2025**; ปี 2024 มี 44 สถานี | `CODE_REF`, `STATION`, `PROVINCE`, `DATE`, `YEAR`, `MONTH_NUM`, `TEMP`, `TEMP_MIN`, `TEMP_MAX`, `HUMIDITY`, `WIND_SPEED`, `RAINFALL`, `CLEANING_STATUS`, `NEEDS_SOURCE_VERIFICATION`, `TEMP_ORDER_VALID` |
| `hii_clean.csv` | จังหวัด-เดือน; **216 × 9** | ม.ค. 2024 – ธ.ค. 2025 ครบ 9 จังหวัด × 24 เดือน | `PROVINCE`, `YEAR`, `MONTH_NUM`, `DATE_MONTH`, `RAIN_MIN_MM`, `RAIN_MAX_MM`, `RAIN_AVG_MM`, `RAIN_VALUES_VALID` |
| `oae_clean.csv` | จังหวัด-เดือน; **216 × 10** | ม.ค. 2024 – ธ.ค. 2025 ครบ 9 จังหวัด × 24 เดือน | `PROVINCE`, `YEAR`, `MONTH_NUM`, `DATE_MONTH`, `RUBBER_TONS`, `RUBBER_MONTH_SHARE_PERCENT`, `PERCENT_IMPUTED_FROM_ZERO_TONS`, `RUBBER_TONS_VALID`, `RUBBER_PERCENT_VALID` |

**9 จังหวัดที่อนุญาต:** เชียงใหม่ เชียงราย น่าน ตาก กำแพงเพชร พิษณุโลก เพชรบูรณ์ กาญจนบุรี แม่ฮ่องสอน

**หมายเหตุคุณภาพข้อมูลสำคัญ:** HRDI มี `RAINFALL` ว่าง 2,400 แถว; `HUMIDITY` และ `WIND_SPEED` ว่างอย่างละ 181 แถว; 6,028 แถว `CLEANING_STATUS=PROVISIONAL_LAST_RECORD` และ `NEEDS_SOURCE_VERIFICATION=True` (ใช้ธงเพื่อเลือกแสดง/ไม่แสดง ไม่ลบจากต้นฉบับ). OAE มี `RUBBER_TONS=0` จำนวน 10 แถว เป็นศูนย์จริงตาม CSV ห้ามนับเป็น missing โดยอัตโนมัติ; `PERCENT_IMPUTED_FROM_ZERO_TONS=True` 2 แถว. HII/OAE ไม่มีค่า null ในไฟล์ที่แนบและคีย์ `PROVINCE+YEAR+MONTH_NUM` ไม่ซ้ำ

### 2.1 แหล่ง Open Data เดิม (อ้างอิงเท่านั้น ไม่ใช่คำสั่งโหลดใหม่)

| แหล่งข้อมูล | หน่วยงาน | หน้า Open Data |
|---|---|---|
| HRDI สภาพภูมิอากาศบนพื้นที่สูง | สถาบันวิจัยและพัฒนาพื้นที่สูง | https://data.go.th/dataset/hrdi_met |
| HII ปริมาณฝนเชิงพื้นที่ | สถาบันสารสนเทศทรัพยากรน้ำ (องค์การมหาชน) | https://data.go.th/dataset/spatial-rain |
| OAE ร้อยละปริมาณผลผลิตยางพารา | สำนักงานเศรษฐกิจการเกษตร | https://catalog.oae.go.th/th/dataset/para_rubber_product_month |

**คำเตือน provenance:** หน้าแค็ตตาล็อก OAE ที่เคยตรวจระบุถึงปี 2024 แต่ CSV ที่แนบมี 2025 ให้แสดง `Source verification pending` สำหรับ OAE 2025 ไม่อ้างว่าได้รับการยืนยันโดยหน่วยงาน; HRDI มีข้อมูลชั่วคราวและหน่วย `RAINFALL`/`WIND_SPEED` ยังต้องยืนยัน. ตรวจใบอนุญาตของแต่ละแหล่งก่อนเผยแพร่สาธารณะ และให้เครดิต/ลิงก์ทุก Tab

## 3. เทคโนโลยีและสถาปัตยกรรม (Technical Requirements)

- **Backend:** Python 3.11+ กับ `pandas` สำหรับอ่าน/validate/aggregate; ใช้ **Dash (Plotly Dash)** เป็นคำแนะนำหลักเพื่อให้ backend callbacks จัดการ linked cross-filter ได้โดยตรง. หากใช้ FastAPI + Plotly JS ต้องรักษาข้อกำหนด interaction เทียบเท่า
- **Charting:** Plotly เป็นหลัก (`plotly.express`, `plotly.graph_objects`); อาจใช้ Plotly Dash Bootstrap Components เพื่อจัด layout แต่ **ห้ามใช้ Chart.js เป็นเครื่องมือหลัก**
- **Data access:** โหลด CSV จากโฟลเดอร์ `data/` ในเครื่อง/รีโป; ไม่เรียก API ข้อมูลภายนอกและไม่โหลดชุดใหม่
- **Architecture:** `app.py` (entrypoint), `src/data_loader.py`, `src/validation.py`, `src/aggregation.py`, `src/analytics.py`, `src/figures.py`, `src/callbacks.py`, `assets/style.css`, `data/*.csv`, `requirements.txt`, `README.md`, `PROJECT_STATUS.md` (ปรับชื่อได้แต่แยก logic จาก UI)
- **Performance:** parse/validate/cache aggregate ในหน่วยความจำ และใช้ memoization เมื่อเหมาะสม; recompute เมื่อ filter state เปลี่ยน; รองรับ ~22k HRDI rows และ 216 rows อีก 2 ชุดได้สบาย
- **Startup:** เปิดด้วย `python app.py` (หรือคำสั่งที่ README ระบุ) และแสดง local URL; ไม่จำเป็นต้องใช้อินเทอร์เน็ตเพื่อโหลดข้อมูล; library ต้องติดตั้งก่อนรัน
- **Usability:** ภาษาไทย, responsive, ป้ายหน่วย/แหล่งที่มา/จำนวนข้อมูล, hover tooltip อธิบายค่าจริง, ไม่มีข้อมูลให้แสดง `ไม่มีข้อมูลตามเงื่อนไข`, ปุ่ม reset, ไม่ให้การเลือกกราฟวน trigger ตนเอง

## 4. มาตรฐานข้อมูลและวิธีคำนวณร่วมกัน

### 4.1 คีย์และกระบวนการเชื่อม (ETL / Data Model)

1. อ่าน CSV และ parse `DATE` เป็นวัน, `DATE_MONTH` เป็นเดือน; `YEAR`, `MONTH_NUM` เป็นจำนวนเต็ม; map ชื่อจังหวัดให้ตรงกันเฉพาะการสะกด ไม่เดาจังหวัดที่ไม่พบ
2. ตรวจ schema/types, ค่า null, ธง validity, จังหวัด, ขอบเขตวันที่ และ unique keys: HRDI `CODE_REF+DATE`; HII/OAE `PROVINCE+YEAR+MONTH_NUM`
3. ทำ **HRDI station-day → station-month → province-month** ก่อน join เพื่อไม่ให้จังหวัดที่มีสถานีมากมีน้ำหนักเกินโดยไม่ตั้งใจ
4. Join รายเดือนด้วย `PROVINCE`, `YEAR`, `MONTH_NUM` เฉพาะเมื่อการจับคู่ถูกต้อง โดย `hii_clean` และ `oae_clean` ใช้ one-to-one validated merge
5. เก็บ `observed_days`, `calendar_days`, `coverage_pct`, `station_count`, `n_valid`, `quality_flag` ของ HRDI ไว้ใน aggregate สำหรับ tooltip/การคัดกรอง
6. ห้าม join raw HRDI รายวันกับ HII/OAE รายเดือนแล้ว SUM หรือ AVG โดยตรง เพราะทำให้ข้อมูล HII/OAE ถูกนับซ้ำหลายครั้ง

### 4.2 KPI และสูตร

| ตัวชี้วัด | สูตรเชิงธุรกิจ | ข้อควรระวัง |
|---|---|---|
| อุณหภูมิเฉลี่ยรายสถานี-เดือน | `mean(TEMP)` ของแถวที่ไม่ null | จังหวัด-เดือน = ค่าเฉลี่ย **ค่าเฉลี่ยสถานี** ที่ผ่านเงื่อนไข ไม่ใช่เอาแถวทุกสถานีรวมกัน |
| ความชื้นเฉลี่ย | `mean(HUMIDITY)` แถวที่มีค่า | แสดงเป็น % หากนิยามจากต้นทางยืนยัน; แสดง n |
| ความเร็วลมเฉลี่ย | `mean(WIND_SPEED)` | หน่วยต้นทางยังไม่ยืนยัน ให้ระบุว่า `หน่วยตามไฟล์ (รอตรวจสอบ)` |
| ความกระจายอุณหภูมิ | `Q1`, median, `Q3`, IQR=Q3−Q1, sample SD (`ddof=1`) | ใช้ข้อมูลวัน/สถานีจริงตาม grain ที่ระบุ; ไม่สับสน SD กับ confidence interval |
| ฝน HRDI สถานี-เดือน | `sum(RAINFALL)` เฉพาะ non-null ต่อสถานี-เดือน | **ผลรวมค่าฝนตามไฟล์; หน่วย/นิยามสะสมรายวันยังไม่ยืนยัน** จึงยังห้ามอ้าง `mm/month` หรือเทียบผลต่าง mm กับ HII |
| Coverage ฝน | `observed non-null rainfall days / calendar days in month × 100` | `0` ที่มีข้อมูลนับเป็น observed; missing ไม่แทนศูนย์; default เกณฑ์ผ่าน **≥ 90%** เป็นเกณฑ์ของโครงงาน |
| ฝน HRDI จังหวัด-เดือน | `mean(station_month_rain)` ของสถานีที่ผ่าน coverage | แสดง station count; การเฉลี่ยสถานีไม่ใช่ค่าเฉลี่ยเชิงพื้นที่ของจังหวัด |
| ฝน HII จังหวัด-เดือน | `RAIN_AVG_MM` | มม. ตามความหมายของต้นทาง; รวมหลายเดือนใช้ `sum(RAIN_AVG_MM)` และต้องแสดงช่วงเดือนที่รวม |
| ยางพาราตัน | `RUBBER_TONS` รายจังหวัด-เดือน; รวมได้โดย `sum` | รวมเป็นผลผลิตปีได้ก็ต่อเมื่อมีครบ 12 เดือน; เปรียบเทียบจังหวัดใช้จำนวนตัน |
| สัดส่วนผลผลิตยาง | `RUBBER_MONTH_SHARE_PERCENT` | % ภายในจังหวัด-ปี ไม่ใช่สัดส่วนตลาดทั้งประเทศ; ห้าม SUM ข้ามจังหวัดเป็น % รวม |
| ระดับความกระจุกผลผลิต | สัดส่วน 3 เดือนที่มีตันมากสุดต่อยอดตันรวมของจังหวัด-ปี × 100; และ peak month | คำนวณเฉพาะปีที่เดือนครบ; ถ้าตันรวมเป็น 0 ให้ N/A |
| Pearson r | correlation ของคู่ (`RAIN_AVG_MM`,`RUBBER_TONS`) หลัง filter | `n>=3` และ x/y ต้องไม่ constant; แสดง n; Pearson ไม่ใช่เหตุและผล |
| Spearman ρ | rank correlation ของคู่เดียวกัน | ใช้เป็นมุมมองประกอบ; หาก n ไม่พอให้ N/A |

**การจัดการปี:** HRDI ปี 2024 มีเฉพาะ ก.ย.–ธ.ค. การเทียบข้ามปีต้องใช้ **เดือนตรงกัน (Sep–Dec)** และแนะนำกรองเฉพาะสถานีร่วมกัน (matched `CODE_REF`) สำหรับการตีความอย่างเป็นธรรม; HII และ OAE มีครบ 12 เดือนของทั้ง 2 ปี

**Rainfall comparison gate:** Tab 3 อนุญาตให้แสดง line/seasonal profile แบบมีหน่วยกำกับคนละชุด แต่ **ปิดการคำนวณ `HRDI−HII` ในหน่วย mm และปิด % difference** จนกว่าจะยืนยันหน่วยและนิยามการรวมฝน HRDI กับ coverage แล้ว; UI อธิบายว่าทำไมปิดอยู่ ห้ามแอบ normalize แล้วอ้างเป็นมิลลิเมตร

## 5. Business Questions และ Functional Requirements ราย Tab

### Tab 1 — สภาพภูมิอากาศบนพื้นที่สูง

**โจทย์:** ภูมิอากาศ 9 จังหวัดแตกต่างกันและเปลี่ยนตามเดือนอย่างไร? จังหวัด/เดือนไหนมีการกระจายหรือค่าฝนสูงผิดปกติ?

| ID | กราฟ / รูปแบบ Plotly | ตัวแปรและการคำนวณ | การเลือกเชื่อมโยง |
|---|---|---|---|
| T1-01 | **Grouped bar / small multiple** อุณหภูมิ ความชื้น ความเร็วลมแยก 3 panel เนื่องจากหน่วยต่างกัน | `TEMP`, `HUMIDITY`, `WIND_SPEED` → station-month mean → province-month mean; บอก `n_station` | คลิกจังหวัดใน bar → ตั้ง `selected_provinces` ให้กราฟ T1-02 ถึง T1-04 และ KPI อัปเดต |
| T1-02 | **Monthly multi-line chart** แนวโน้มอุณหภูมิ 2024–2025 | `DATE`, `TEMP`, `CODE_REF`, `PROVINCE` → mean รายเดือน; แกน x เป็น YYYY-MM; เว้นช่องจริงที่ไม่มีข้อมูล | คลิกจุด/เลือกช่วงเวลา → `selected_months`/date range และจังหวัดใช้กับทุกกราฟใน Tab |
| T1-03 | **Box plot + outlier points** ฝนตามจังหวัดและเดือน พร้อม tooltip ระดับสถานี | `RAINFALL`, `DATE`, `CODE_REF` → station-month total เมื่อผ่านเกณฑ์ coverage; box แยกจังหวัด/เดือน; IQR outlier = ค่านอก Q1−1.5IQR หรือ Q3+1.5IQR | คลิกจังหวัด/เดือน/จุดข้อมูล → cross-filter T1-01/02/04; แสดง `observed_days`, coverage และหมายเหตุหน่วยฝน |
| T1-04 | **Box/violin plot** การกระจายอุณหภูมิ และ SD/IQR ตามจังหวัด | `TEMP` จาก station-day ที่ผ่าน quality; median, Q1/Q3, SD และ n | คลิกจังหวัด/ช่วงเดือน → อัปเดตทุกกราฟ; สลับ `box`/`violin` ได้ |

**KPI บน Tab 1:** จำนวนสถานีจริงหลังกรอง, จำนวน station-day valid, อุณหภูมิเฉลี่ย, ความชื้นเฉลี่ย, ลมเฉลี่ย และ rainfall coverage เฉลี่ยพร้อมธงคุณภาพ.  
**Filters:** ปี (หลายค่า), เดือน (หลายค่า), จังหวัด (หลายค่า), สถานี (`CODE_REF`, dependent on จังหวัด), รวม/ไม่รวม provisional (default **ไม่รวม**), rainfall coverage threshold (default 90%), สลับการแสดงหน่วยเฉพาะที่หน่วยตรวจสอบแล้ว.  
**เหตุการณ์ฝนสูงผิดปกติ:** นิยาม outlier เชิงสถิติภายใน distribution หลังกรอง มิใช่คำเตือนภัยหรือเหตุการณ์อุตุนิยมวิทยาที่หน่วยงานรับรอง

### Tab 2 — ปริมาณน้ำฝนระดับจังหวัดและผลผลิตยางพารา

**โจทย์:** จังหวัดใดฝนมาก/น้อย? จังหวัดใดผลิตยางมากที่สุด? ยางออกมากในเดือนไหน และกระจุกตัวเพียงใด?

| ID | กราฟ / รูปแบบ Plotly | ตัวแปรและการคำนวณ | การเลือกเชื่อมโยง |
|---|---|---|---|
| T2-01 | **Line chart** ฝน HII รายเดือนแยกจังหวัด | `RAIN_AVG_MM` ตาม `DATE_MONTH`, `PROVINCE`; ถ้าสรุปหลายจังหวัดให้เลือก `mean across selected provinces` โดยระบุหน่วย | คลิกจังหวัดใน legend/จุด หรือ brush ช่วงเดือน → T2-02/03/04 กรองตาม |
| T2-02 | **Ranked horizontal bar** จังหวัดที่ผลิตยางสูงสุด | `sum(RUBBER_TONS)` ต่อจังหวัดจากช่วงเวลาที่กรอง; ถ้าเรียกว่า “ยอดทั้งปี” ต้องครบ 12 เดือน | คลิกแท่งจังหวัด → update T2-01/03/04 และ KPI; แสดงค่าตันจริง |
| T2-03 | **Heatmap จังหวัด × เดือน** สัดส่วนผลผลิต และ bar สรุป 3 เดือนสูงสุด | `RUBBER_MONTH_SHARE_PERCENT` เฉพาะจังหวัด-ปี; ตัวเลือกตัน; seasonal top-3 share จาก `RUBBER_TONS` | คลิก heatmap cell → ตั้งจังหวัด+เดือน (และปีเมื่อดู 2 ปี) แล้วอัปเดตอีก 3 กราฟ |
| T2-04 | **Multi-line/area (ไม่ stack ข้ามจังหวัดเมื่อ %)** แนวโน้มยางรายเดือน | `RUBBER_TONS` ต่อจังหวัด-เดือน; toggle แสดง `RUBBER_MONTH_SHARE_PERCENT` พร้อม label % ภายในจังหวัด-ปี | คลิกจุดบนเส้น → cross-filter ทุกกราฟ Tab 2 |

**KPI บน Tab 2:** ฝน HII ตามช่วงเดือนที่เลือก, ยางรวมตันในช่วงที่เลือก, จังหวัดที่ยางสูงสุดใน selection, เดือนพีคตามจังหวัด-ปี, จำนวน province-month pairs.  
**Filters:** ปี, เดือน, จังหวัด, ตัวชี้วัดยาง (ตัน / %), โหมดจัดอันดับ (ตามช่วงกรอง / เต็มปี), มี/ไม่มีแถวที่ `PERCENT_IMPUTED_FROM_ZERO_TONS=True` เมื่อแสดง %.  
**ข้อห้าม:** ห้ามเปรียบเทียบ % ต่อปีที่ไม่ครบ 12 เดือนเป็นความกระจุกตัวจริง; ห้ามรวม % ข้ามจังหวัด; เมื่อกรองเดือน ยอด rank ต้องระบุว่าเป็น **ยอดช่วงที่เลือก** ไม่ใช่ยอดรายปี

### Tab 3 — การเปรียบเทียบและความสัมพันธ์ระหว่างข้อมูล

**โจทย์:** รูปแบบฝนจากพื้นที่สูงต่างจากฝนเฉลี่ยจังหวัดอย่างไร? ฝน HII สัมพันธ์กับยาง OAE หรือไม่?

| ID | กราฟ / รูปแบบ Plotly | ตัวแปรและการคำนวณ | การเลือกเชื่อมโยง |
|---|---|---|---|
| T3-01 | **Dual panel line** แสดง HRDI และ HII แยก pane/แกน พร้อมภาพ seasonal pattern; tooltip แสดง coverage | HRDI station-month → province-month mean ที่ผ่าน quality/coverage; HII `RAIN_AVG_MM`; join on province-year-month **เท่านั้น**; ใช้แกนแยกจนกว่าหน่วย HRDI ยืนยัน | คลิกเดือน/จังหวัด → update T3-02/03 และ KPI; ห้ามลากกราฟเป็น difference mm เมื่อยังไม่ยืนยันหน่วย |
| T3-02 | **Scatter** X=ฝน HII, Y=ยางตัน สีแยกจังหวัด (marker รายจังหวัด-เดือน) | คู่ `RAIN_AVG_MM`, `RUBBER_TONS` หลัง validated one-to-one join; trendline เฉพาะเมื่อ n เหมาะสม; optionally lag 0–3 เดือนแบบชัดเจน | เลือกจุด scatter / lasso → filter `selected_pair_keys` แล้วกราฟ T3-01 และการ์ดสถิติอัปเดต; ปุ่ม Clear Selection |
| T3-03 | **Correlation cards + per-province bar/heatmap** ค่า Pearson, Spearman, n | Pearson r, Spearman ρ บนคู่ที่เลือก; แยกตามจังหวัดและ pooled มีเครื่องหมายต่างกัน; หาก n < 3 หรือ variance=0 ให้ N/A | คลิกจังหวัดใน correlation chart → กรอง T3-01/02 และแสดงสถิติใหม่ |

**KPI / interpretation:** จำนวน province-month pairs ที่นำคำนวณจริง, Pearson r, Spearman ρ, ช่วงเวลา, quality coverage ที่ผ่านมา, คำเตือน `correlation ≠ causation`; แสดงว่า correlation ที่คำนวณร่วมหลายจังหวัดอาจสะท้อนผลจากฤดูกาล/ขนาดจังหวัดได้.  
**Filters:** ปี (default 2025 แต่เลือก 2024/ทั้งสองได้), เดือน, จังหวัด, HRDI quality, HRDI coverage threshold, lag 0–3 เดือน (default 0), โหมดกลุ่มจังหวัด/แต่ละจังหวัด; เมื่อ lag ต้องเลื่อน **วันที่** ของ HII เทียบยาง ไม่ shift แถวแบบข้ามจังหวัดและข้ามเดือนที่ขาดโดยไม่อธิบาย  
**ข้อจำกัด:** จำนวนสถานีไม่เท่ากัน; HRDI ไม่แทนทั้งจังหวัด; HII เป็นเฉลี่ยเชิงพื้นที่ด้วย IDW; OAE ปี 2025 ต้องตรวจสอบต้นทาง; ความสัมพันธ์ไม่ใช่การพิสูจน์ผลของฝนต่อการผลิต

## 6. พฤติกรรมการเชื่อมกราฟ (Cross-filter Interaction Contract)

1. **แต่ละ Tab มี state เดียวกัน** ประกอบด้วย `years`, `months`, `provinces`, `stations` (Tab 1), `quality_mode`, `min_coverage`, `rubber_metric` (Tab 2), `lag_months`, `selected_pair_keys` (Tab 3) และ `selection_source`
2. เมื่อตัวกรองบนหน้า/คลิกแท่ง/คลิกจุด/brush/lasso → เขียนเข้า state (เช่น Dash `dcc.Store`) → **recompute ทุก KPI และทุก Figure ใน Tab นั้น** โดยใช้ dataset ที่ถูกคัดกรองชุดเดียวกัน; ห้ามให้แต่ละกราฟคำนวณคนละตัวกรอง
3. การคลิกอีกครั้งหรือกด Clear Selection/Reset Tab ต้องล้าง selection ได้; การเลือกหลายจังหวัดรองรับ toggle/multi-select; เมื่อเลือกจุดบนกราฟให้แสดง active filter chips
4. **หลีกเลี่ยง callback loop**: use one canonical reducer + figure rendering callbacks; distinguish user-generated selections from programmatic figure redraws; keep `uirevision` stable เท่าที่ทำได้
5. **Cross-tab filters:** ค่าเริ่มต้นใช้ global `year/province` ร่วมทั้งสาม Tab ได้ แต่ selection จากการคลิกจุดกราฟเป็น **tab-local** เพื่อไม่สับสน; ระบุสถานะที่ใช้บนจอเสมอ
6. **Empty selections:** อย่าแสดง 0 เมื่อไม่มีข้อมูลจริง; แสดง placeholder พร้อมปุ่ม reset; คำนวณค่า correlation เฉพาะ observed pairs เท่านั้น
7. **Hover/data label:** จังหวัด ปี-เดือน สถานี (เมื่อเกี่ยวข้อง) หน่วย สถานะข้อมูล จำนวนแถว/สถานี coverage และคำอธิบายสูตรที่ช่วยตีความ
8. ทุกกราฟต้องตอบสนองต่อ **อย่างน้อย** global filters + selections ที่รองรับใน Tab; cross-filter ด้วย Plotly `clickData`, `selectedData`, `relayoutData` หรือ equivalent Dash callbacks. เลือก legend isolate อาจใช้เพียง visual isolate ได้ แต่ไม่ควรอ้างว่าเป็น filter ถ้าไม่ได้ปรับ graph state อื่น

## 7. ธีม UX / การสื่อสาร

- ภาษาหลักไทย; ดีไซน์อ่านง่าย สีภูมิอากาศกับยางแยกกลุ่มอย่างสม่ำเสมอ
- ลำดับจอ: ชื่อโครงการ + dataset credit + quality badges (provisional, incomplete coverage, source verification) → global filters → 3 tab navigation → KPI → กราฟ → วิธีอ่านและข้อจำกัด
- กราฟคนละหน่วยต้องแยกแกนหรือแยก panel และระบุ unit ในแกนทุกครั้ง
- สามารถดาวน์โหลด PNG ของกราฟ (Plotly modebar), ตารางที่ผ่านการกรองเป็น CSV โดยคง provenance/units (ถ้าพัฒนา export)
- Footer ทุก Tab แสดงแหล่ง Open Data HRDI, HII, OAE พร้อม link และหมายเหตุว่า CSV ผ่านการ cleaning โดยทีม ไม่ใช่ข้อมูลที่หน่วยงานรับรองการคำนวณ

## 8. Non-functional Requirements และเกณฑ์ยอมรับ (Acceptance Criteria)

| ID | เกณฑ์ตรวจรับ | วิธีทดสอบ |
|---|---|---|
| A01 | โหลด CSV 3 ชุดจาก `data/` ได้ ไม่มี hardcoded dummy data | เปลี่ยนค่าทดสอบในสำเนา CSV แล้วผลแสดงเปลี่ยนตาม; ไม่มี mock data |
| A02 | ตรวจขนาด/คอลัมน์/คีย์และ error ข้อมูลผิดรูปแบบ | สร้างสำเนาทดสอบที่คอลัมน์หาย หรือคีย์ซ้ำ ต้องแจ้งปัญหาไม่คำนวณผิด |
| A03 | มี 3 Tabs และครบ T1-01..04, T2-01..04, T3-01..03 | เปิดหน้า dashboard และตรวจ 11 visual requirements |
| A04 | เปลี่ยนจังหวัด/เดือน/ปีแล้ว KPI และกราฟ **ทุกอันใน Tab** เปลี่ยนตามอย่างถูกต้อง | เลือกจังหวัดเดียว เดือนเดียว ตรวจค่ากับ `pandas` aggregation |
| A05 | คลิกกราฟ/เลือกจุด/brush แล้วกราฟอื่นใน Tab อัปเดต; reset แล้วกลับค่าเดิม | ทดสอบอย่างน้อย 1 interactive selection ต่อ visual / หรือ selection behavior ที่ระบุ |
| A06 | HRDI 2024 ไม่แสดง ม.ค.–ส.ค. เป็น 0 และไม่เปรียบเทียบ 4 กับ 12 เดือนแบบ YoY | เลือก 2024 ตรวจ missing segment และ matched-month logic |
| A07 | HRDI missing/quality/coverage ถูกจัดการตามสูตร | เทียบ count และ calculation กับ CSV; ไม่มี replace null with zero |
| A08 | OAE % ใช้ภายในจังหวัด-ปี; ตันรวมได้; ค่า zero ไม่กลายเป็น null | ตรวจจังหวัด-เดือนที่ zero และ % imputation flag |
| A09 | HRDI-HII ไม่แสดงผลต่าง mm จนกว่าหน่วย/นิยามรับรอง | เปิด Tab 3 ต้องเห็น gating และคำเตือน |
| A10 | Pearson/Spearman มี n และ N/A สำหรับข้อมูลไม่พอ/variance=0 | เลือก single point และตรวจ card |
| A11 | ที่มา/เครดิต/ข้อจำกัดเป็นข้อความเห็นได้จริง | ตรวจลิงก์ Open Data และ provisional/OAE-2025 notices |
| A12 | Python app รันได้โดยดู README; code modular, requirements lock/reproducible | ติดตั้งใน clean venv แล้วรัน smoke test |

## 9. ความเสี่ยงและข้อจำกัดในการตีความ

- HRDI เป็นสถานีบนพื้นที่สูง **ไม่ใช่ค่าเฉลี่ยแทนพื้นที่จังหวัด**; จำนวนสถานีไม่เท่ากัน
- ปี 2024 ของ HRDI มีเพียง ก.ย.–ธ.ค.; ค่าว่างและ provisional records อาจมี bias
- หน่วยฝน/ลม HRDI ยังไม่ยืนยัน; ห้ามเปรียบเทียบฝนกับ HII แบบ same-unit difference จนยืนยัน
- ฝน HII เป็น **ฝนเชิงพื้นที่เฉลี่ยรายเดือน** ต่างจากผลรวมรายสถานี HRDI
- ตัวชี้วัด % OAE เป็นสัดส่วนภายในจังหวัด-ปี; ปริมาณตันไม่บอกผลผลิตต่อพื้นที่เพาะปลูก และชุดข้อมูลไม่มีเนื้อที่เพาะปลูก/การจัดการสวน/ราคา
- ข้อมูล OAE 2025 ใน CSV ยังต้องยืนยันว่าได้จากรุ่นต้นทางใด
- Correlation อาจได้รับอิทธิพลจากฤดูกาล/ขนาดพื้นที่ปลูก/ความแตกต่างจังหวัด ไม่ใช่ความสัมพันธ์เชิงสาเหตุ

## 10. แผนส่งมอบให้ Antigravity

**อินพุต:** `BRD.md` (ไฟล์นี้), `HANDOFF.md`, `DATA_DESCRIPTION.md`, และ CSV 3 ไฟล์ใน `data/`. หากเอกสารเก่าระบุ Chart.js/HTML-only ให้ยึด BRD นี้ในส่วน **Python + Plotly + Dash**; นิยามหน่วย/ข้อจำกัดข้อมูลให้ยึด DATA_DESCRIPTION เป็นหลัก

**ลำดับทำงาน:**
1. อ่านเอกสารและ inspect CSV จริง → จัดทำ `README.md` แผนโครงสร้างโปรเจกต์ และ `PROJECT_STATUS.md`
2. พัฒนา data validation + reproducible aggregation + unit tests ก่อนเริ่มกราฟ
3. สร้าง UI/global filters + canonical shared selection state และ Tab 1–3 ทีละส่วน
4. สร้าง/ตรวจ Plotly figures, callbacks และ cross-filter พร้อม tooltip/empty states
5. Test ทุก acceptance criterion เทียบค่า pandas กับ CSV; จัดทำ run instructions และ source/limitations notice
6. บันทึกความคืบหน้าใน `PROJECT_STATUS.md` และ commit เมื่อเสร็จแต่ละระยะ (เมื่ออยู่ใน Git repository)

**ขอบเขตการส่งมอบ:** โค้ดเว็บที่รันได้จริง, คำสั่งติดตั้ง/รัน, requirements, validation tests, เอกสารข้อจำกัด และบันทึกผลการทดสอบ; **ไม่ใช้ข้อมูลจำลองแม้ในกราฟตัวอย่างบน Dashboard**

---

### Prompt สั้นสำหรับ Antigravity

> Read `BRD.md`, `DATA_DESCRIPTION.md`, and `HANDOFF.md` and inspect the three provided cleaned CSVs. Implement a complete Thai-language Plotly Dash dashboard with Python backend. The BRD overrides older HTML/Chart.js technology requirements. Build 3 tabs, all listed charts, shared cross-filter callbacks within each tab, validated province-month joins, statistics and coverage controls, and explicit data-quality/provenance warnings. Use only the provided real CSVs; never generate mock data or invent findings. Create README and PROJECT_STATUS first, keep modules editable, test all acceptance criteria, and document known limitations.
