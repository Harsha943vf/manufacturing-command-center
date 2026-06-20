# Calibration Reference — Real-World Statistics Used in Synthetic Data Generation

This project does **not** generate purely random synthetic data. Every distribution used
in `generate_synthetic_data.py` is calibrated against published statistics from real,
publicly available datasets. This document records exactly which numbers came from where,
so you can defend every parameter choice in an interview.

> **Why this matters:** generic Faker-based portfolio data invites the question
> "were these insights realistic?" This document is the answer to that question.

---

## 1. Machine Failure Calibration
**Source:** AI4I 2020 Predictive Maintenance Dataset (UCI Machine Learning Repository / Kaggle)
- 10,000 machine operating records
- Overall machine failure rate: **3.39%** (339 / 10,000 records)
- Failure type breakdown (approximate, some overlap between types):
  - Tool Wear Failure (TWF): ~46 cases
  - Heat Dissipation Failure (HDF): ~115 cases
  - Power Failure (PWF): ~95 cases
  - Overstrain Failure (OSF): ~98 cases
  - Random Failure (RNF): ~19 cases
- Sensor ranges used as realistic envelopes:
  - Air temperature: 295–304 K
  - Process temperature: 305.7–313.8 K
  - Rotational speed: mean ≈ 1538 rpm, std ≈ 179 rpm
  - Torque: mean ≈ 40 Nm, std ≈ 10 Nm
  - Tool wear: 0–253 minutes

**How it's used:** `baseline_failure_rate` per machine in `dim_machine` is sampled around
3.39%, with failure-type proportions mapped to manufacturing downtime reason codes
(Tool Wear → changeover/tooling, HDF → mechanical/thermal, PWF → electrical,
OSF → overload, RNF → random/other).

---

## 2. Quality / Defect Rate Calibration
**Source:** SECOM Manufacturing Dataset (UCI / Kaggle — semiconductor production line)
- 1,567 production records, 590 sensor features
- Fail rate: **6.6%** (104 / 1,567)

**How it's used:** SECOM is semiconductor manufacturing (very high-precision, naturally
higher fail-rate tolerance). Discrete manufacturing (this project's domain) typically runs
lower scrap rates. SECOM's 6.6% is used as a **documented upper bound**, scaled down to a
baseline scrap/defect rate of **2–4%** per production run, with deliberate per-line variance
so some lines run close to the SECOM ceiling (signal for investigation) and most run well
below it.

---

## 3. Supplier Reliability Calibration
**Source:** World Bank Logistics Performance Index (LPI), most recent published edition
- LPI is scored 1 (low) to 5 (high) by country, based on customs, infrastructure, timeliness, etc.
- Approximate published band scores used as regional proxies:
  - Germany: ~4.2
  - United States: ~3.9
  - Vietnam: ~3.3
  - China: ~3.6
  - India: ~3.2
  - Mexico: ~3.1

**How it's used:** Each synthetic supplier is assigned a region, and that region's LPI band
becomes a multiplier on the supplier's baseline on-time delivery probability — so a
German supplier is generated with structurally better reliability than a Mexican-region
supplier, mirroring real-world logistics performance patterns rather than random assignment.

> ⚠️ LPI scores are periodically updated by the World Bank. Before finalizing your project,
> pull the current edition's scores (free, public) at:
> https://lpi.worldbank.org and update the constants in `calibration_constants.py`.

---

## 4. Macro Production Trend Calibration
**Source:** FRED Industrial Production Index (Federal Reserve Economic Data — free public API)
- Used as a stylized basis for seasonality + trend overlay on production volume
- This sandbox build uses a **placeholder trend** (≈1–3% annual growth with mild cyclical
  dips) because this environment has no internet access to call the live FRED API.

**Action for you (you have internet, I don't, in this sandbox):**
Run `fetch_fred_benchmark.py` (provided) on your own machine with a free FRED API key
(https://fred.stlouisfed.org/docs/api/api_key.html) to pull the real Industrial Production
Index and replace the placeholder trend. This is a 5-minute step and meaningfully
strengthens your "real-world calibrated" claim.

---

## 5. How to Strengthen This Further (Optional, On Your Machine)
Since you have internet and I don't in this build environment, consider:
1. Downloading the actual AI4I and SECOM CSVs from Kaggle/UCI and running
   `validate_against_real_data.py` (provided) to statistically compare your synthetic
   output's distributions against the real datasets (e.g., KS-test on failure rates).
2. Pulling current World Bank LPI scores and FRED data to replace placeholder constants.
3. Including a short section in your README/portfolio writeup showing the side-by-side
   comparison — this is the single strongest piece of evidence against the
   "is this realistic?" objection.
