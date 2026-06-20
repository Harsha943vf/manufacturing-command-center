"""
export_marts_to_csv.py

Bridges the dbt-built DuckDB marts into CSV files Tableau Public can read directly.

Why this exists: Tableau Public's native connector support for DuckDB varies by version,
and a portfolio project shouldn't depend on a connector working or not working on the day
a recruiter opens it. CSV is universally supported by every Tableau Public version, so this
script is the guaranteed bridge from "data pipeline" to "BI tool."

Run this AFTER `dbt run` has built the marts into manufacturing_command_center.duckdb.

Usage:
    cd dbt_project
    python3 ../data_generation/export_marts_to_csv.py
"""

import duckdb
import os

DUCKDB_PATH = "manufacturing_command_center.duckdb"
EXPORT_DIR = "../tableau_extracts"

MART_TABLES = [
    "fct_oee_daily",
    "fct_production_run_enriched",
    "dim_machine_risk_score",
    "dim_supplier_risk_score",
    "fct_forecast_30day",
    "fct_command_center_top_risks",
]

def main():
    if not os.path.exists(DUCKDB_PATH):
        raise FileNotFoundError(
            f"Could not find {DUCKDB_PATH}. Run this script from inside dbt_project/ "
            f"after running `dbt run`."
        )

    os.makedirs(EXPORT_DIR, exist_ok=True)
    con = duckdb.connect(DUCKDB_PATH, read_only=True)

    for table in MART_TABLES:
        out_path = os.path.join(EXPORT_DIR, f"{table}.csv")
        try:
            con.execute(f"COPY {table} TO '{out_path}' (HEADER, DELIMITER ',')")
            print(f"  exported {table} -> {out_path}")
        except duckdb.CatalogException:
            print(f"  WARNING: table '{table}' not found -- did `dbt run` complete successfully?")

    con.close()
    print(f"\nDone. Open Tableau Public and connect to the CSVs in {EXPORT_DIR}/")

if __name__ == "__main__":
    main()
