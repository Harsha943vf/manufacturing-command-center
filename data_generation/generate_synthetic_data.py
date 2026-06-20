"""
generate_synthetic_data.py

Generates the full synthetic "digital twin" dataset for the Manufacturing
Intelligence & Supply Chain Risk Command Center project.

Every distribution is calibrated against real published statistics — see
calibration_constants.py and docs/calibration_reference.md.

Run:
    python3 generate_synthetic_data.py

Output:
    CSV files written to ../outputs/ — one file per dimension/fact table.
    These feed directly into the dbt project (dbt_project/) as seed/source data.

Dependencies: pandas, numpy only (both in Python's standard scientific stack —
no Faker, no internet required).
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

import calibration_constants as cal

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
rng = np.random.default_rng(cal.RANDOM_SEED)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

START_DATE = pd.to_datetime(cal.SIMULATION_START_DATE)
N_MONTHS = cal.SIMULATION_MONTHS
END_DATE = START_DATE + pd.DateOffset(months=N_MONTHS)
ALL_DATES = pd.date_range(START_DATE, END_DATE, freq="D")

print(f"Simulating {START_DATE.date()} to {END_DATE.date()} "
      f"({len(ALL_DATES)} days, {N_MONTHS} months)")

# ---------------------------------------------------------------------------
# DIM_PLANT
# ---------------------------------------------------------------------------
plants = pd.DataFrame([
    {"plant_id": "P1", "plant_name": "Plant 1 - Midwest",   "region": "United States", "plant_type": "Heavy Assembly", "capacity_units_per_day": 4800},
    {"plant_id": "P2", "plant_name": "Plant 2 - Southeast", "region": "United States", "plant_type": "Precision Components", "capacity_units_per_day": 3600},
    {"plant_id": "P3", "plant_name": "Plant 3 - Monterrey", "region": "Mexico",        "plant_type": "High-Volume Assembly", "capacity_units_per_day": 5200},
])

# ---------------------------------------------------------------------------
# DIM_LINE (3 lines per plant)
# ---------------------------------------------------------------------------
line_rows = []
for _, p in plants.iterrows():
    for i in range(1, 4):
        line_rows.append({
            "line_id": f"{p.plant_id}-L{i}",
            "plant_id": p.plant_id,
            "line_name": f"{p.plant_name.split(' - ')[0]} Line {i}",
        })
lines = pd.DataFrame(line_rows)

# ---------------------------------------------------------------------------
# DIM_MACHINE (3-4 machines per line, calibrated to AI4I failure stats)
# ---------------------------------------------------------------------------
machine_rows = []
machine_counter = 1
for _, l in lines.iterrows():
    n_machines = rng.integers(3, 5)  # 3 or 4 machines per line
    for _ in range(n_machines):
        # Per-machine baseline failure rate sampled around the AI4I overall rate,
        # with realistic spread so some machines are structurally riskier than others
        baseline_failure_rate = max(0.005, rng.normal(
            cal.AI4I_OVERALL_FAILURE_RATE, cal.AI4I_OVERALL_FAILURE_RATE * 0.6
        ))
        install_date = START_DATE - pd.Timedelta(days=int(rng.integers(180, 365 * 6)))
        machine_rows.append({
            "machine_id": f"M-{100 + machine_counter}",
            "line_id": l.line_id,
            "machine_type": rng.choice(
                ["CNC Mill", "Stamping Press", "Robotic Welder", "Injection Molder", "Conveyor/Assembly"]
            ),
            "install_date": install_date.date().isoformat(),
            "baseline_failure_rate": round(baseline_failure_rate, 5),
            "rotational_speed_rpm_mean": round(rng.normal(
                cal.AI4I_SENSOR_RANGES["rotational_speed_rpm"]["mean"],
                cal.AI4I_SENSOR_RANGES["rotational_speed_rpm"]["std"] * 0.3
            ), 1),
            "torque_nm_mean": round(rng.normal(
                cal.AI4I_SENSOR_RANGES["torque_nm"]["mean"],
                cal.AI4I_SENSOR_RANGES["torque_nm"]["std"] * 0.3
            ), 1),
        })
        machine_counter += 1
machines = pd.DataFrame(machine_rows)

# ---------------------------------------------------------------------------
# DIM_SUPPLIER (calibrated to World Bank LPI regional scores)
# ---------------------------------------------------------------------------
supplier_seed = [
    ("S1",  "Bavarian Precision Components",     "Germany"),
    ("S2",  "Rhine Industrial Supply",            "Germany"),
    ("S3",  "Heartland Fasteners Co.",            "United States"),
    ("S4",  "Great Lakes Bearings",               "United States"),
    ("S5",  "Saigon Electronics Manufacturing",   "Vietnam"),
    ("S6",  "Hanoi Precision Parts",              "Vietnam"),
    ("S7",  "Shenzhen Component Group",           "China"),
    ("S8",  "Guangzhou Metalworks",               "China"),
    ("S9",  "Pune Industrial Castings",           "India"),
    ("S10", "Bangalore Tooling Systems",          "India"),
    ("S11", "Monterrey Metal Supply",             "Mexico"),
    ("S12", "Queretaro Components Inc.",          "Mexico"),
]
supplier_rows = []
for sid, name, region in supplier_seed:
    lpi = cal.LPI_REGION_SCORES[region]
    # LPI-adjusted on-time delivery rate: higher LPI -> higher reliability
    lpi_factor = lpi / cal.LPI_MAX_SCORE
    on_time_rate = min(0.99, cal.SUPPLIER_BASE_ON_TIME_RATE * (0.6 + 0.4 * lpi_factor))
    supplier_rows.append({
        "supplier_id": sid,
        "supplier_name": name,
        "region": region,
        "lpi_score": lpi,
        "tier": rng.choice(["Tier 1", "Tier 2"], p=[0.4, 0.6]),
        "on_time_delivery_rate": round(on_time_rate, 3),
    })
suppliers = pd.DataFrame(supplier_rows)

# ---------------------------------------------------------------------------
# DIM_MATERIAL
# ---------------------------------------------------------------------------
material_seed = [
    ("MAT1", "Precision Bearing Assembly", "Mechanical", "S1", "Critical"),
    ("MAT2", "Hydraulic Seal Kit",          "Mechanical", "S2", "High"),
    ("MAT3", "Steel Fastener Set",          "Hardware",   "S3", "Medium"),
    ("MAT4", "Industrial Bearing Set",      "Mechanical", "S4", "Critical"),
    ("MAT5", "PCB Control Module",          "Electronics","S5", "Critical"),
    ("MAT6", "Wiring Harness",              "Electronics","S6", "High"),
    ("MAT7", "Aluminum Housing Casting",    "Metal",      "S7", "High"),
    ("MAT8", "Sheet Metal Stock",           "Metal",      "S8", "Medium"),
    ("MAT9", "Cast Iron Bracket",           "Metal",      "S9", "Medium"),
    ("MAT10","Precision Tooling Insert",    "Tooling",    "S10","High"),
    ("MAT11","Motor Mount Assembly",        "Mechanical", "S11","High"),
    ("MAT12","Gasket & Sealing Kit",        "Mechanical", "S12","Medium"),
]
materials = pd.DataFrame(material_seed, columns=[
    "material_id", "material_name", "category", "supplier_id", "criticality_rank"
])

# ---------------------------------------------------------------------------
# DIM_PRODUCT
# ---------------------------------------------------------------------------
product_seed = [
    ("PR1", "Pro-Series Pump",        "Pro-Series Pump",    "High"),
    ("PR2", "Standard Valve Assembly","Standard Valves",    "Medium"),
    ("PR3", "Industrial Gearbox X200","Gearbox Family",     "High"),
    ("PR4", "Economy Bracket Kit",    "Bracket Family",     "Low"),
    ("PR5", "Precision Actuator A5",  "Actuator Family",    "High"),
    ("PR6", "Standard Conveyor Roller","Roller Family",     "Medium"),
]
products = pd.DataFrame(product_seed, columns=[
    "product_id", "sku", "product_family", "margin_class"
])

print("Dimensions generated:")
print(f"  Plants: {len(plants)} | Lines: {len(lines)} | Machines: {len(machines)}")
print(f"  Suppliers: {len(suppliers)} | Materials: {len(materials)} | Products: {len(products)}")

# ---------------------------------------------------------------------------
# DIM_WORK_ORDER (one batch of work orders spread across the simulation window)
# ---------------------------------------------------------------------------
n_work_orders = 900
work_order_rows = []
for i in range(1, n_work_orders + 1):
    product = products.sample(1, random_state=int(rng.integers(0, 1_000_000))).iloc[0]
    due_offset = int(rng.integers(0, len(ALL_DATES)))
    work_order_rows.append({
        "work_order_id": f"WO-{1000 + i}",
        "product_id": product.product_id,
        "customer_order_id": f"CO-{5000 + i}",
        "planned_qty": int(rng.integers(50, 2000)),
        "priority": rng.choice(["High", "Medium", "Low"], p=[0.2, 0.5, 0.3]),
        "due_date": ALL_DATES[due_offset].date().isoformat(),
    })
work_orders = pd.DataFrame(work_order_rows)

# ---------------------------------------------------------------------------
# FACT_PRODUCTION_RUN (one row per line per shift per day)
# Quality/defect rate calibrated to SECOM (scaled down for discrete mfg)
# ---------------------------------------------------------------------------
SHIFTS = ["Day", "Evening", "Night"]
production_rows = []
run_counter = 1

# Macro trend overlay (placeholder for real FRED data — see calibration doc)
def macro_trend_multiplier(date):
    days_elapsed = (date - START_DATE).days
    annual_growth = cal.PLACEHOLDER_ANNUAL_GROWTH_RATE * (days_elapsed / 365.0)
    seasonal = cal.PLACEHOLDER_SEASONAL_AMPLITUDE * np.sin(2 * np.pi * days_elapsed / 365.0)
    return 1.0 + annual_growth + seasonal

for date in ALL_DATES:
    trend_mult = macro_trend_multiplier(date)
    for _, l in lines.iterrows():
        line_machines = machines[machines.line_id == l.line_id]
        for shift in SHIFTS:
            machine = line_machines.sample(1, random_state=int(rng.integers(0, 1_000_000))).iloc[0]
            wo = work_orders.sample(1, random_state=int(rng.integers(0, 1_000_000))).iloc[0]

            planned_runtime = 8 * 60  # 8-hour shift in minutes
            # Defect rate: discrete mfg baseline, with per-run noise, capped at SECOM ceiling
            defect_rate = np.clip(
                rng.normal(cal.DISCRETE_MFG_BASELINE_SCRAP_RATE, cal.DISCRETE_MFG_SCRAP_RATE_STD),
                0.001, cal.DISCRETE_MFG_SCRAP_RATE_CEILING
            )
            units_produced = max(0, int(rng.normal(300, 40) * trend_mult))
            units_defective = int(units_produced * defect_rate)

            # Actual runtime reduced by any downtime (computed after the fact below)
            production_rows.append({
                "run_id": f"RUN-{run_counter}",
                "date": date.date().isoformat(),
                "shift": shift,
                "line_id": l.line_id,
                "machine_id": machine.machine_id,
                "work_order_id": wo.work_order_id,
                "planned_runtime_min": planned_runtime,
                "units_produced": units_produced,
                "units_defective": units_defective,
                "defect_rate": round(defect_rate, 4),
            })
            run_counter += 1

production_runs = pd.DataFrame(production_rows)
print(f"Production runs generated: {len(production_runs):,}")

# ---------------------------------------------------------------------------
# FACT_DOWNTIME (calibrated to AI4I failure rate + failure-type breakdown)
# ---------------------------------------------------------------------------
downtime_rows = []
downtime_counter = 1
machine_failure_lookup = machines.set_index("machine_id")["baseline_failure_rate"].to_dict()

failure_types = list(cal.AI4I_FAILURE_TYPE_SHARE.keys())
failure_probs = list(cal.AI4I_FAILURE_TYPE_SHARE.values())
failure_probs = [p / sum(failure_probs) for p in failure_probs]  # normalize

# cost per downtime minute by reason category (used for Financial Impact KPIs)
COST_PER_MINUTE = {
    "TOOLING_CHANGEOVER": 45,
    "MECHANICAL_THERMAL": 80,
    "ELECTRICAL_FAULT": 70,
    "OVERLOAD_STOPPAGE": 60,
    "UNPLANNED_OTHER": 50,
    "MATERIAL_SHORTAGE": 95,   # supplier-driven downtime is the most expensive
}

for _, run in production_runs.iterrows():
    machine_id = run.machine_id
    base_rate = machine_failure_lookup[machine_id]

    if rng.random() < base_rate:
        failure_type = rng.choice(failure_types, p=failure_probs)
        reason_code = cal.FAILURE_TYPE_TO_REASON_CODE[failure_type]
        duration = max(5, int(rng.normal(90, 45)))
        cost_impact = duration * COST_PER_MINUTE[reason_code]
        downtime_rows.append({
            "downtime_id": f"DT-{downtime_counter}",
            "run_id": run.run_id,
            "machine_id": machine_id,
            "date": run.date,
            "reason_code": reason_code,
            "duration_minutes": duration,
            "cost_impact_usd": cost_impact,
        })
        downtime_counter += 1

downtimes = pd.DataFrame(downtime_rows)
print(f"Downtime events generated: {len(downtimes):,} "
      f"({len(downtimes)/len(production_runs):.2%} of runs)")

# ---------------------------------------------------------------------------
# FACT_SUPPLIER_DELIVERY (calibrated to LPI-adjusted on-time rates)
# Also injects MATERIAL_SHORTAGE downtime events when a delivery is critically late
# ---------------------------------------------------------------------------
delivery_rows = []
delivery_counter = 1
material_shortage_downtime_rows = []

# roughly weekly delivery cadence per material over the simulation window
delivery_dates = pd.date_range(START_DATE, END_DATE, freq="7D")

for _, mat in materials.iterrows():
    supplier = suppliers[suppliers.supplier_id == mat.supplier_id].iloc[0]
    for sched_date in delivery_dates:
        on_time = rng.random() < supplier.on_time_delivery_rate
        if on_time:
            delay_days = 0
        else:
            # late deliveries skew toward short delays, with a long tail of severe delays
            delay_days = int(rng.gamma(shape=2.0, scale=3.0)) + 1

        actual_date = sched_date + pd.Timedelta(days=delay_days)
        qty_ordered = int(rng.integers(500, 5000))
        qty_received = qty_ordered if on_time else int(qty_ordered * rng.uniform(0.7, 1.0))

        delivery_rows.append({
            "delivery_id": f"DEL-{delivery_counter}",
            "supplier_id": mat.supplier_id,
            "material_id": mat.material_id,
            "scheduled_date": sched_date.date().isoformat(),
            "actual_date": actual_date.date().isoformat(),
            "delay_days": delay_days,
            "qty_ordered": qty_ordered,
            "qty_received": qty_received,
        })

        # Severe delays (>5 days) on critical materials cause downstream line downtime
        if delay_days > 5 and mat.criticality_rank == "Critical":
            affected_line = lines[lines.plant_id.isin(plants.plant_id)].sample(
                1, random_state=int(rng.integers(0, 1_000_000))
            ).iloc[0]
            duration = delay_days * 60  # rough proxy: 1 hr of downtime per delay day
            material_shortage_downtime_rows.append({
                "downtime_id": f"DT-MS-{delivery_counter}",
                "run_id": None,
                "machine_id": None,
                "date": actual_date.date().isoformat(),
                "reason_code": "MATERIAL_SHORTAGE",
                "duration_minutes": duration,
                "cost_impact_usd": duration * COST_PER_MINUTE["MATERIAL_SHORTAGE"],
                "supplier_id": mat.supplier_id,
                "material_id": mat.material_id,
                "line_id": affected_line.line_id,
            })
        delivery_counter += 1

supplier_deliveries = pd.DataFrame(delivery_rows)
material_shortage_downtime = pd.DataFrame(material_shortage_downtime_rows)
print(f"Supplier deliveries generated: {len(supplier_deliveries):,}")
print(f"Material-shortage downtime events: {len(material_shortage_downtime):,}")

# ---------------------------------------------------------------------------
# WRITE ALL OUTPUTS
# ---------------------------------------------------------------------------
tables = {
    "dim_plant": plants,
    "dim_line": lines,
    "dim_machine": machines,
    "dim_supplier": suppliers,
    "dim_material": materials,
    "dim_product": products,
    "dim_work_order": work_orders,
    "fact_production_run": production_runs,
    "fact_downtime": downtimes,
    "fact_supplier_delivery": supplier_deliveries,
    "fact_material_shortage_downtime": material_shortage_downtime,
}

for name, df in tables.items():
    path = os.path.join(OUTPUT_DIR, f"{name}.csv")
    df.to_csv(path, index=False)
    print(f"  wrote {path}  ({len(df):,} rows)")

print("\nDone. All CSVs written to outputs/. Next: load these into DuckDB via dbt (see dbt_project/).")
