# Mac M1 Setup Guide — Zero Paid Tools, No Docker

This guide assumes: MacBook Air M1, Python 3 already installed, no Docker, no Power BI.
Everything below is free and runs natively on Apple Silicon.

## 1. Set up a virtual environment (keeps this project's packages isolated)

```bash
cd manufacturing-command-center      # this project folder
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If `dbt-duckdb` fails to build on M1, it's almost always a stale pip — fix with:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## 2. Generate the synthetic dataset

```bash
cd data_generation
python3 generate_synthetic_data.py
```

You should see output confirming row counts for each table, all written to `../outputs/`.

## 3. Load the data into DuckDB via dbt (no server, no Docker — just a local file)

```bash
cd ../dbt_project
cp ../outputs/*.csv seeds/        # refresh seeds with the latest generated data
export DBT_PROFILES_DIR=$(pwd)    # tells dbt to use the profiles.yml in this folder

dbt deps      # installs dbt_utils + elementary packages
dbt seed      # loads the CSVs into DuckDB as tables
dbt run       # builds all staging + mart models
dbt test      # runs the data quality tests (null checks, relationships, range checks)
dbt snapshot  # establishes the SCD2 baseline (see snapshots/HOW_TO_DEMONSTRATE_SCD2.md)
```

If everything passes, you now have a local file `manufacturing_command_center.duckdb`
sitting in `dbt_project/` containing the full star schema — fact tables, dimension
tables, risk scores, forecasts, and the Command Center risk ranking — all queryable
with plain SQL.

**Quick sanity check — open it directly:**
```bash
python3 -c "
import duckdb
con = duckdb.connect('manufacturing_command_center.duckdb')
print(con.execute('select * from fct_command_center_top_risks').fetchdf())
"
```
You should see a ranked top-10 risk list with dollar impacts and recommended actions.

## 4. Bridge to Tableau Public

```bash
python3 ../data_generation/export_marts_to_csv.py
```
This exports the key mart tables to `tableau_extracts/*.csv` — open these directly in
Tableau Public (Connect → Text File). This sidesteps any DuckDB-connector version issues
entirely.

(If your Tableau Public version *does* support a DuckDB connector, you can also connect
directly to `manufacturing_command_center.duckdb` for a live-query experience instead of
static extracts — try it, and fall back to the CSV export if it's not available.)

## 5. Optional: view dbt's auto-generated documentation (genuinely impressive for a portfolio)

```bash
dbt docs generate
dbt docs serve
```
This opens an interactive site in your browser showing your full star schema, column-level
lineage, and test coverage — screenshot this for your portfolio/LinkedIn. It's free, it's
built into dbt, and almost nobody at entry level includes it.

## 6. Automating refreshes without Docker or Airflow

The GitHub Actions workflow in `.github/workflows/pipeline_refresh.yml` runs this entire
pipeline (steps 2–3) on a schedule, entirely on GitHub's free tier — nothing needs to run
on your Mac for the "automated daily refresh" story to be true. To activate it:
1. Push this project to a public GitHub repo.
2. Go to the repo's **Actions** tab and enable workflows.
3. Trigger it manually once via "Run workflow" to confirm it passes.
4. From then on it runs automatically every day at 06:00 UTC.

## Troubleshooting
If `dbt run` errors on a specific model, copy the error and we'll debug it together —
DuckDB's SQL dialect is close to PostgreSQL but not identical (e.g. `regr_slope` syntax,
date functions), so minor adjustments are normal on a first run.
