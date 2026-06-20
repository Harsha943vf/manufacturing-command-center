"""
calibration_constants.py

Single source of truth for every "real-world calibrated" number used by the
synthetic data generator. Keeping these separate from the generation logic means:
  1. You can cite this file directly in an interview ("here's exactly where each
     number came from").
  2. When you update LPI/FRED data with your own internet access, you only edit
     this one file.

See docs/calibration_reference.md for full source documentation.
"""

# ---------------------------------------------------------------------------
# 1. MACHINE FAILURE CALIBRATION (Source: AI4I 2020 Predictive Maintenance Dataset)
# ---------------------------------------------------------------------------
AI4I_OVERALL_FAILURE_RATE = 0.0339          # 339 / 10,000 records
AI4I_FAILURE_TYPE_SHARE = {                  # proportion of failures by type
    "tool_wear_failure": 46 / 339,
    "heat_dissipation_failure": 115 / 339,
    "power_failure": 95 / 339,
    "overstrain_failure": 98 / 339,
    "random_failure": 19 / 339,
}
AI4I_SENSOR_RANGES = {
    "air_temp_k": (295.0, 304.0),
    "process_temp_k": (305.7, 313.8),
    "rotational_speed_rpm": {"mean": 1538, "std": 179},
    "torque_nm": {"mean": 40.0, "std": 10.0},
    "tool_wear_min": (0, 253),
}

# Map AI4I failure types -> manufacturing downtime reason codes used in this project
FAILURE_TYPE_TO_REASON_CODE = {
    "tool_wear_failure": "TOOLING_CHANGEOVER",
    "heat_dissipation_failure": "MECHANICAL_THERMAL",
    "power_failure": "ELECTRICAL_FAULT",
    "overstrain_failure": "OVERLOAD_STOPPAGE",
    "random_failure": "UNPLANNED_OTHER",
}

# ---------------------------------------------------------------------------
# 2. QUALITY / DEFECT RATE CALIBRATION (Source: SECOM Manufacturing Dataset)
# ---------------------------------------------------------------------------
SECOM_FAIL_RATE = 104 / 1567                 # ~6.6% — semiconductor ceiling reference
DISCRETE_MFG_BASELINE_SCRAP_RATE = 0.028     # documented scale-down for discrete mfg
DISCRETE_MFG_SCRAP_RATE_STD = 0.012          # per-line variance
DISCRETE_MFG_SCRAP_RATE_CEILING = SECOM_FAIL_RATE  # worst-case lines approach this

# ---------------------------------------------------------------------------
# 3. SUPPLIER RELIABILITY CALIBRATION (Source: World Bank Logistics Performance Index)
#    NOTE: update these from https://lpi.worldbank.org with the current edition
# ---------------------------------------------------------------------------
LPI_REGION_SCORES = {
    "Germany": 4.2,
    "United States": 3.9,
    "Vietnam": 3.3,
    "China": 3.6,
    "India": 3.2,
    "Mexico": 3.1,
}
LPI_MAX_SCORE = 5.0   # LPI is scored 1 (low) to 5 (high)
SUPPLIER_BASE_ON_TIME_RATE = 0.85  # baseline before LPI adjustment

# ---------------------------------------------------------------------------
# 4. MACRO PRODUCTION TREND (Source: FRED Industrial Production Index — PLACEHOLDER)
#    This sandbox has no internet. Replace with real FRED data using
#    fetch_fred_benchmark.py on your own machine before finalizing.
# ---------------------------------------------------------------------------
PLACEHOLDER_ANNUAL_GROWTH_RATE = 0.02       # ~2% stylized annual growth
PLACEHOLDER_SEASONAL_AMPLITUDE = 0.04       # mild cyclical dips/peaks

# ---------------------------------------------------------------------------
# 5. SIMULATION SCOPE
# ---------------------------------------------------------------------------
SIMULATION_START_DATE = "2024-01-01"
SIMULATION_MONTHS = 18
RANDOM_SEED = 42   # reproducibility — same seed = same dataset every run
