# Manufacturing Intelligence & Supply Chain Risk Command Center

A Tableau Public–driven decision-support platform connecting machine health, supplier
reliability, and financial exposure across a multi-plant manufacturing operation — built
on a synthetic "digital twin" calibrated against real published industrial datasets.

📄 Full project brief: `docs/calibration_reference.md` (data sourcing) and the project
description doc (business context, dashboard design, KPIs, personas).

---

## Build Status

- [x] **Phase 1 — Data Layer:** Synthetic data generator (calibrated to AI4I 2020 +
      SECOM + World Bank LPI), dbt-duckdb project (staging + marts + snapshots + tests),
      GitHub Actions orchestration, CSV export bridge to Tableau Public.
- [x] **Phase 2 — Dashboard Build:** Interactive HTML prototype (`dashboard_prototype/index.html`)
      built on real computed risk scores, plus `docs/tableau_phase2_build_guide.md` with exact
      calculated fields, parameters, and layouts for the production Tableau Public workbook.
- [x] **Phase 3 — Resume Materials:** `docs/resume_and_interview_prep.md` with bullets and
      talking points using your actual computed numbers ($695K top supplier risk, $2.8M
      total downtime cost).
- [ ] **Remaining:** Build the actual Tableau Public workbook on your machine following the
      Phase 2 guide, publish it, and drop the public link into the README + resume bullets.

### What's already proven to work (run by me, on your generated data):
- Machine failure rate calibration: target 3.39% (AI4I 2020) → actual generated 3.16% ✓
- Supplier reliability gradient: Germany-region suppliers outperform Mexico-region ✓
- **Top finding:** Saigon Electronics Manufacturing (Vietnam) is the #1 ranked risk in the
  entire network at $695K in downstream shortage cost — bigger than the top 2 machine risks
  combined. This is your headline insight for interviews.

---

## Repo Structure

```
manufacturing-command-center/
├── data_generation/
│   ├── calibration_constants.py     # every real-world number used, in one place
│   ├── generate_synthetic_data.py   # main generator (pandas/numpy only)
│   └── export_marts_to_csv.py       # bridges DuckDB -> Tableau Public
├── dbt_project/
│   ├── seeds/                       # generated CSVs, loaded as tables via `dbt seed`
│   ├── models/staging/              # 1:1 cleaned views over the seeds
│   ├── models/marts/                # star schema + risk scores + forecast + command center
│   ├── snapshots/                   # SCD Type 2 example (supplier reliability history)
│   ├── dbt_project.yml
│   └── profiles.yml                 # DuckDB target -- no server, no Docker
├── outputs/                         # generator's raw CSV output
├── tableau_extracts/                # CSV bridge for Tableau Public (created by export script)
├── docs/
│   ├── calibration_reference.md     # full source documentation for every calibrated stat
│   └── mac_build_guide.md           # step-by-step setup for Mac M1, no Docker, no Power BI
├── .github/workflows/
│   └── pipeline_refresh.yml         # GitHub Actions orchestration (replaces Airflow/Docker)
└── requirements.txt
```

## Quickstart

See `docs/mac_build_guide.md` for the full walkthrough. Short version:

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd data_generation && python3 generate_synthetic_data.py
cd ../dbt_project && cp ../outputs/*.csv seeds/
export DBT_PROFILES_DIR=$(pwd)
dbt deps && dbt seed && dbt run && dbt test && dbt snapshot
python3 ../data_generation/export_marts_to_csv.py
```

Then open the CSVs in `tableau_extracts/` from Tableau Public.

## What Makes This Different From a Typical Portfolio Dashboard

1. **Real-data calibrated, not pure Faker.** Every distribution traces back to a documented
   public dataset (AI4I 2020, SECOM, World Bank LPI) — see `docs/calibration_reference.md`.
2. **Transparent risk scoring, not black-box ML.** Machine Risk Score and Supplier Risk
   Index are weighted, explainable formulas a plant manager could actually audit.
3. **Financial layer on every operational metric.** Downtime, scrap, and lost-production
   costs are first-class fields, not an afterthought.
4. **Self-monitoring pipeline.** dbt tests and schema checks mean the project can
   answer "do you trust your own data?" — not just "can you build a chart?"
5. **Zero-cost stack, deliberately chosen.** DuckDB, dbt Core, GitHub Actions, and Tableau
   Public replace their paid/Docker-dependent equivalents without losing any of the
   underlying engineering concepts.

## Next Step
Phase 2 (Tableau Public dashboard build) — say "let's build phase 2" and we'll move into
the dashboard pages: Persona Landing, Plant Overview, Machine Risk Scorecard, Supplier
Network, Forecast, Scenario Simulator, Command Center, and Data Governance.
